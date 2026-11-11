targetScope = 'resourceGroup'

@description('Region for all resources except the Static Web App.')
param location string = resourceGroup().location
param staticWebAppLocation string = 'eastus2'
param namePrefix string = 'hireready'

@description('Set false for the first deployment (before an image exists in ACR).')
param deployApps bool = false
@description('Full image reference, e.g. <acr>.azurecr.io/hireready-backend:<sha>.')
param backendImage string = ''

param entraIssuer string
param entraJwksUrl string
param entraAudience string

param chatModelName string = 'gpt-4.1-mini'
param chatModelVersion string = '2025-04-14'
param chatSkuName string = 'GlobalStandard'
param chatCapacity int = 50
param embeddingModelName string = 'text-embedding-3-small'
param embeddingModelVersion string = '1'
param embeddingSkuName string = 'Standard'
param embeddingCapacity int = 50

@secure()
param postgresAdminPassword string
@description('Your public IP to allow one-time psql setup. Leave empty to skip.')
param allowClientIp string = ''

param alertEmail string
param budgetAmount int = 30
@description('First day of the current month, yyyy-MM-01.')
param budgetStartDate string

var suffix = uniqueString(resourceGroup().id)
var roles = {
  acrPull: '7f951dda-4ed3-4680-a7ca-43fe172d538d'
  blobContributor: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
  queueContributor: '974c5e8b-45b9-4653-ba55-5f855dd0fb88'
  openAiUser: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
  kvSecretsUser: '4633458b-17de-408a-b874-0445c86b69e6'
}

resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${namePrefix}-id'
  location: location
}

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${namePrefix}-logs'
  location: location
  properties: { sku: { name: 'PerGB2018' }, retentionInDays: 30 }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${namePrefix}-appi'
  location: location
  kind: 'web'
  properties: { Application_Type: 'web', WorkspaceResourceId: logs.id }
}

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: '${namePrefix}acr${suffix}'
  location: location
  sku: { name: 'Basic' }
  properties: { adminUserEnabled: false }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: take('${namePrefix}st${suffix}', 24)
  location: location
  kind: 'StorageV2'
  sku: { name: 'Standard_LRS' }
  properties: { allowBlobPublicAccess: false, minimumTlsVersion: 'TLS1_2', supportsHttpsTrafficOnly: true }
}
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storage
  name: 'default'
}
resource resumesContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'resumes'
  properties: { publicAccess: 'None' }
}
resource queueService 'Microsoft.Storage/storageAccounts/queueServices@2023-05-01' = {
  parent: storage
  name: 'default'
}
resource tasksQueue 'Microsoft.Storage/storageAccounts/queueServices/queues@2023-05-01' = {
  parent: queueService
  name: 'tasks'
}
resource poisonQueue 'Microsoft.Storage/storageAccounts/queueServices/queues@2023-05-01' = {
  parent: queueService
  name: 'tasks-poison'
}

resource pg 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' = {
  name: '${namePrefix}-pg-${suffix}'
  location: location
  sku: { name: 'Standard_B1ms', tier: 'Burstable' }
  properties: {
    version: '16'
    administratorLogin: 'pgadmin'
    administratorLoginPassword: postgresAdminPassword
    storage: { storageSizeGB: 32 }
    backup: { backupRetentionDays: 7, geoRedundantBackup: 'Disabled' }
    highAvailability: { mode: 'Disabled' }
    authConfig: { activeDirectoryAuth: 'Enabled', passwordAuth: 'Enabled', tenantId: subscription().tenantId }
  }
}
resource pgDb 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2024-08-01' = {
  parent: pg
  name: 'hireready'
  properties: { charset: 'UTF8', collation: 'en_US.utf8' }
}
resource pgExtensions 'Microsoft.DBforPostgreSQL/flexibleServers/configurations@2024-08-01' = {
  parent: pg
  name: 'azure.extensions'
  properties: { value: 'VECTOR', source: 'user-override' }
  dependsOn: [ pgDb ]
}
resource pgAzureServices 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2024-08-01' = {
  parent: pg
  name: 'AllowAzureServices'
  properties: { startIpAddress: '0.0.0.0', endIpAddress: '0.0.0.0' }
  dependsOn: [ pgExtensions ]
}
resource pgClient 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2024-08-01' = if (!empty(allowClientIp)) {
  parent: pg
  name: 'OperatorClient'
  properties: { startIpAddress: allowClientIp, endIpAddress: allowClientIp }
  dependsOn: [ pgAzureServices ]
}
module pgEntraAdmin './modules/pg-admin.bicep' = {
  name: 'pg-entra-admin'
  params: {
    serverName: pg.name
    principalId: identity.properties.principalId
    principalName: identity.name
  }
  dependsOn: [ pgAzureServices, pgClient ]
}

resource kv 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: take('${namePrefix}-kv-${suffix}', 24)
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: { family: 'A', name: 'standard' }
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
  }
}
resource kvPgSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: kv
  name: 'postgres-admin-password'
  properties: { value: postgresAdminPassword }
}

resource aoai 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: '${namePrefix}-aoai-${suffix}'
  location: location
  kind: 'OpenAI'
  sku: { name: 'S0' }
  properties: { customSubDomainName: '${namePrefix}-aoai-${suffix}', publicNetworkAccess: 'Enabled', disableLocalAuth: true }
}
resource chatDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: aoai
  name: 'chat'
  sku: { name: chatSkuName, capacity: chatCapacity }
  properties: { model: { format: 'OpenAI', name: chatModelName, version: chatModelVersion } }
}
resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: aoai
  name: 'embedding'
  sku: { name: embeddingSkuName, capacity: embeddingCapacity }
  properties: { model: { format: 'OpenAI', name: embeddingModelName, version: embeddingModelVersion } }
  dependsOn: [ chatDeployment ]
}

resource raAcr 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, identity.id, roles.acrPull)
  scope: acr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.acrPull)
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}
resource raBlob 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storage.id, identity.id, roles.blobContributor)
  scope: storage
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.blobContributor)
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}
resource raQueue 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storage.id, identity.id, roles.queueContributor)
  scope: storage
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.queueContributor)
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}
resource raOpenAi 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aoai.id, identity.id, roles.openAiUser)
  scope: aoai
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.openAiUser)
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}
resource raKv 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(kv.id, identity.id, roles.kvSecretsUser)
  scope: kv
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roles.kvSecretsUser)
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource swa 'Microsoft.Web/staticSites@2023-12-01' = {
  name: '${namePrefix}-web'
  location: staticWebAppLocation
  sku: { name: 'Free', tier: 'Free' }
  properties: {}
}

resource env 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${namePrefix}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: { customerId: logs.properties.customerId, sharedKey: logs.listKeys().primarySharedKey }
    }
  }
}

var commonEnv = [
  { name: 'ENV', value: 'prod' }
  { name: 'DATABASE_URL', value: 'postgresql+asyncpg://${pg.properties.fullyQualifiedDomainName}:5432/hireready?ssl=require' }
  { name: 'DB_AUTH', value: 'entra' }
  { name: 'DB_ENTRA_USER', value: identity.name }
  { name: 'AZURE_CLIENT_ID', value: identity.properties.clientId }
  { name: 'AUTH_MODE', value: 'entra' }
  { name: 'ENTRA_ISSUER', value: entraIssuer }
  { name: 'ENTRA_JWKS_URL', value: entraJwksUrl }
  { name: 'ENTRA_AUDIENCE', value: entraAudience }
  { name: 'STORAGE_MODE', value: 'azure' }
  { name: 'AZURE_STORAGE_ACCOUNT_URL', value: storage.properties.primaryEndpoints.blob }
  { name: 'AZURE_QUEUE_ACCOUNT_URL', value: storage.properties.primaryEndpoints.queue }
  { name: 'QUEUE_MODE', value: 'azure' }
  { name: 'LLM_PROVIDER', value: 'azure_openai' }
  { name: 'AZURE_OPENAI_ENDPOINT', value: aoai.properties.endpoint }
  { name: 'AZURE_OPENAI_CHAT_DEPLOYMENT', value: chatDeployment.name }
  { name: 'CORS_ORIGINS', value: '["https://${swa.properties.defaultHostname}"]' }
  { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsights.properties.ConnectionString }
]
var registries = [ { server: acr.properties.loginServer, identity: identity.id } ]
var userIdentity = { type: 'UserAssigned', userAssignedIdentities: { '${identity.id}': {} } }

resource api 'Microsoft.App/containerApps@2024-03-01' = if (deployApps) {
  name: '${namePrefix}-api'
  location: location
  identity: userIdentity
  properties: {
    managedEnvironmentId: env.id
    configuration: {
      ingress: { external: true, targetPort: 8000, transport: 'auto', allowInsecure: false }
      registries: registries
    }
    template: {
      containers: [
        {
          name: 'api'
          image: backendImage
          resources: { cpu: json('0.5'), memory: '1Gi' }
          env: commonEnv
          probes: [ { type: 'Liveness', httpGet: { path: '/api/health', port: 8000 }, periodSeconds: 30 } ]
        }
      ]
      scale: { minReplicas: 1, maxReplicas: 3 }
    }
  }
  dependsOn: [ raAcr, raBlob, raQueue, raOpenAi, pgEntraAdmin ]
}

resource worker 'Microsoft.App/containerApps@2024-03-01' = if (deployApps) {
  name: '${namePrefix}-worker'
  location: location
  identity: userIdentity
  properties: {
    managedEnvironmentId: env.id
    configuration: {
      registries: registries
      secrets: [
        {
          name: 'queue-connection'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storage.name};AccountKey=${storage.listKeys().keys[0].value};EndpointSuffix=${environment().suffixes.storage}'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'worker'
          image: backendImage
          command: [ 'python', '-m', 'app.worker' ]
          resources: { cpu: json('1.0'), memory: '2Gi' }
          env: commonEnv
        }
      ]
      terminationGracePeriodSeconds: 300
      scale: {
        minReplicas: 0
        maxReplicas: 3
        rules: [
          {
            name: 'tasks-queue'
            azureQueue: {
              queueName: 'tasks'
              queueLength: 1
              auth: [ { secretRef: 'queue-connection', triggerParameter: 'connection' } ]
            }
          }
        ]
      }
    }
  }
  dependsOn: [ raAcr, raBlob, raQueue, raOpenAi, pgEntraAdmin ]
}

resource migrate 'Microsoft.App/jobs@2024-03-01' = if (deployApps) {
  name: '${namePrefix}-migrate'
  location: location
  identity: userIdentity
  properties: {
    environmentId: env.id
    configuration: {
      triggerType: 'Manual'
      replicaTimeout: 600
      replicaRetryLimit: 0
      manualTriggerConfig: { parallelism: 1, replicaCompletionCount: 1 }
      registries: registries
    }
    template: {
      containers: [
        {
          name: 'migrate'
          image: backendImage
          command: [ 'alembic', 'upgrade', 'head' ]
          resources: { cpu: json('0.5'), memory: '1Gi' }
          env: commonEnv
        }
      ]
    }
  }
  dependsOn: [ raAcr, pgEntraAdmin ]
}

resource actionGroup 'Microsoft.Insights/actionGroups@2023-01-01' = {
  name: '${namePrefix}-alerts'
  location: 'global'
  properties: {
    groupShortName: 'hireready'
    enabled: true
    emailReceivers: [ { name: 'owner', emailAddress: alertEmail, useCommonAlertSchema: true } ]
  }
}

resource poisonAlert 'Microsoft.Insights/scheduledQueryRules@2023-03-15-preview' = {
  name: '${namePrefix}-task-poisoned'
  location: location
  properties: {
    displayName: 'A task exhausted its retries'
    severity: 2
    enabled: true
    scopes: [ appInsights.id ]
    evaluationFrequency: 'PT15M'
    windowSize: 'PT1H'
    criteria: {
      allOf: [
        {
          query: 'traces | where message == "task_poisoned"'
          timeAggregation: 'Count'
          operator: 'GreaterThan'
          threshold: 0
          failingPeriods: { numberOfEvaluationPeriods: 1, minFailingPeriodsToAlert: 1 }
        }
      ]
    }
    actions: { actionGroups: [ actionGroup.id ] }
  }
}

resource failureRateAlert 'Microsoft.Insights/scheduledQueryRules@2023-03-15-preview' = {
  name: '${namePrefix}-task-failure-rate'
  location: location
  properties: {
    displayName: 'Task failure rate above 10%'
    severity: 2
    enabled: true
    scopes: [ appInsights.id ]
    evaluationFrequency: 'PT15M'
    windowSize: 'PT1H'
    criteria: {
      allOf: [
        {
          query: 'traces | where message == "task_finished" | summarize total = count(), failed = countif(tostring(customDimensions.status) == "failed") | where total >= 5 | extend rate = 100.0 * failed / total'
          metricMeasureColumn: 'rate'
          timeAggregation: 'Average'
          operator: 'GreaterThan'
          threshold: 10
          failingPeriods: { numberOfEvaluationPeriods: 1, minFailingPeriodsToAlert: 1 }
        }
      ]
    }
    actions: { actionGroups: [ actionGroup.id ] }
  }
}

resource budget 'Microsoft.Consumption/budgets@2023-05-01' = {
  name: '${namePrefix}-budget'
  properties: {
    category: 'Cost'
    amount: budgetAmount
    timeGrain: 'Monthly'
    timePeriod: { startDate: budgetStartDate }
    notifications: {
      actual80: { enabled: true, operator: 'GreaterThanOrEqualTo', threshold: 80, thresholdType: 'Actual', contactEmails: [ alertEmail ] }
      forecast100: { enabled: true, operator: 'GreaterThanOrEqualTo', threshold: 100, thresholdType: 'Forecasted', contactEmails: [ alertEmail ] }
    }
  }
}

output acrName string = acr.name
output acrLoginServer string = acr.properties.loginServer
output identityName string = identity.name
output postgresHost string = pg.properties.fullyQualifiedDomainName
output staticWebAppHost string = swa.properties.defaultHostname
output apiUrl string = deployApps ? 'https://${api!.properties.configuration.ingress.fqdn}' : ''
