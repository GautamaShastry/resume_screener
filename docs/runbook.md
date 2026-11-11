# HireReady — Azure runbook

One-time production setup, then how deploys, rollbacks and logs work. Commands use bash (Git Bash on Windows).

## 0. Prerequisites
- An Azure subscription where you are Owner (or Contributor + User Access Administrator).
- Azure CLI ≥ 2.60: `az login`, then `az account set --subscription <SUBSCRIPTION_ID>`.
- `az extension add --name containerapp --upgrade --yes`
- A `psql` client (step 5).

## 1. Resource group and model quota
```bash
az group create -n rg-hireready-prod -l eastus2
```
In Azure AI Foundry → **Quotas**, confirm quota in `eastus2` for the chat model (`gpt-4.1-mini`, GlobalStandard) and `text-embedding-3-small`. If unavailable, choose another model or region and pass `chatModelName`, `chatModelVersion` and `location` as deployment parameters.

## 2. Entra External ID (sign-in)
1. Azure portal → **Microsoft Entra External ID** → create an **external tenant** (for example subdomain `hireready`). Note the **tenant ID** and **subdomain**.
2. In the external tenant → **App registrations** → **New registration** "HireReady API":
   - **Expose an API** → Application ID URI `api://<API_APP_CLIENT_ID>` → add scope `access`.
   - **Manifest** → set `requestedAccessTokenVersion` to `2` (under `api`).
   - **Token configuration** → add optional claim `email` to the **access** token.
3. **New registration** "HireReady Web" (Single-page application):
   - Redirect URIs: `http://localhost:5173` now, and `https://<staticWebAppHost>` after step 6.
   - **API permissions** → add `HireReady API / access` → **Grant admin consent**.
4. **External Identities → User flows** → create "Sign up and sign in" with **Email with password**. Add **Google** as an identity provider (create an OAuth client in Google Cloud Console with redirect URI `https://<subdomain>.ciamlogin.com/<tenant-id>/federation/oauth2`, then paste its client ID and secret). Add **HireReady Web** to the user flow.
5. Fill `infra/main.parameters.json`: `entraIssuer`, `entraJwksUrl`, `entraAudience` (the API app's client ID), `alertEmail`, and `budgetStartDate` (first day of the current month).

Frontend values for step 7:
- `VITE_ENTRA_CLIENT_ID` = HireReady Web client ID
- `VITE_ENTRA_AUTHORITY` = `https://<subdomain>.ciamlogin.com/`
- `VITE_ENTRA_API_SCOPE` = `api://<API_APP_CLIENT_ID>/access`

## 3. First infrastructure deployment (no apps yet)
```bash
PG_PASSWORD=$(openssl rand -base64 24)
MY_IP=$(curl -s https://api.ipify.org)
az deployment group create -g rg-hireready-prod -f infra/main.bicep -p infra/main.parameters.json \
  -p postgresAdminPassword="$PG_PASSWORD" allowClientIp="$MY_IP" deployApps=false
az deployment group show -g rg-hireready-prod -n main --query properties.outputs
```
Record `acrName`, `acrLoginServer`, `identityName`, `postgresHost` and `staticWebAppHost`. The Postgres admin password is also stored in Key Vault as `postgres-admin-password`.

## 4. Build the first image
```bash
az acr build -r <acrName> -t hireready-backend:initial backend
```

## 5. One-time database grants
```bash
PGPASSWORD="$PG_PASSWORD" psql "host=<postgresHost> dbname=hireready user=pgadmin sslmode=require" <<'SQL'
CREATE EXTENSION IF NOT EXISTS vector;
GRANT ALL ON SCHEMA public TO "hireready-id";
GRANT CREATE ON DATABASE hireready TO "hireready-id";
SQL
```
`hireready-id` is `identityName`. Its database role exists because the deployment made the identity the server's Entra administrator.

## 6. Deploy the apps and run migrations
```bash
az deployment group create -g rg-hireready-prod -f infra/main.bicep -p infra/main.parameters.json \
  -p postgresAdminPassword="$PG_PASSWORD" deployApps=true \
     backendImage=<acrLoginServer>/hireready-backend:initial
az containerapp job start -n hireready-migrate -g rg-hireready-prod
az containerapp job execution list -n hireready-migrate -g rg-hireready-prod --query "[0].properties.status" -o tsv
API_URL=$(az deployment group show -g rg-hireready-prod -n main --query properties.outputs.apiUrl.value -o tsv)
curl -fsS "$API_URL/api/health"
```
Expected: the migration status is `Succeeded` and health returns `{"status":"ok"}`. Then add `https://<staticWebAppHost>` to the HireReady Web redirect URIs (step 2.3).

Remove the operator firewall rule afterwards:
```bash
az postgres flexible-server firewall-rule delete -g rg-hireready-prod \
  -n <pg-server-name> --rule-name OperatorClient --yes
```

## 7. GitHub Actions (OIDC, no stored Azure secret)
```bash
APP_ID=$(az ad app create --display-name hireready-github-deploy --query appId -o tsv)
az ad sp create --id "$APP_ID"
az role assignment create --assignee "$APP_ID" --role Contributor \
  --scope "$(az group show -n rg-hireready-prod --query id -o tsv)"
az ad app federated-credential create --id "$APP_ID" --parameters '{
  "name": "github-production",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:<GITHUB_OWNER>/<GITHUB_REPO>:environment:production",
  "audiences": ["api://AzureADTokenExchange"] }'
```
In GitHub → Settings → Environments, create `production`. Add these repository **variables**:
`AZURE_CLIENT_ID` (=`$APP_ID`), `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP` (=`rg-hireready-prod`), `ACR_NAME`, `ACR_LOGIN_SERVER`, `API_BASE_URL` (=`$API_URL`), `VITE_ENTRA_CLIENT_ID`, `VITE_ENTRA_AUTHORITY`, `VITE_ENTRA_API_SCOPE`.

## 8. Deploys
Every push to `main` runs CI, builds the backend image in ACR, runs migrations, updates `hireready-api` and `hireready-worker`, and deploys the frontend. Watch it under GitHub → Actions → **Deploy**.

## Rollback
```bash
az containerapp revision list -n hireready-api -g rg-hireready-prod -o table
az containerapp update -n hireready-api -g rg-hireready-prod \
  --image <acrLoginServer>/hireready-backend:<previous-sha>
az containerapp update -n hireready-worker -g rg-hireready-prod \
  --image <acrLoginServer>/hireready-backend:<previous-sha>
```
Migrations only go forward. Rolling back past a migration needs a new forward migration.

## Logs
Application Insights `hireready-appi` → Logs:
```kusto
traces | where message startswith "task_" | order by timestamp desc
```
