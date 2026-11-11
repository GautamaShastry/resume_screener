// Makes a managed identity the Microsoft Entra administrator of a PostgreSQL flexible server.
// Lives in a module because the administrator's resource name is the identity's principal ID,
// which is only known after the identity is created.
param serverName string
param principalId string
param principalName string

resource pg 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' existing = {
  name: serverName
}

resource admin 'Microsoft.DBforPostgreSQL/flexibleServers/administrators@2024-08-01' = {
  parent: pg
  name: principalId
  properties: {
    principalType: 'ServicePrincipal'
    principalName: principalName
    tenantId: subscription().tenantId
  }
}
