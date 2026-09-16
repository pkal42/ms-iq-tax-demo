param environmentName string
param location string
param principalId string = ''

var suffix = uniqueString(subscription().id, resourceGroup().id, environmentName)
var compact = take(replace(toLower(environmentName), '-', ''), 10)
var prefix = 'miq-${take(toLower(environmentName), 12)}'
var searchIndexName = 'meridian-tax-knowledge'
var modelDeploymentName = 'gpt-5-mini'
var searchConnectionName = 'meridian-search'
var bingConnectionName = 'meridian-bing'

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${prefix}-logs'
  location: location
  properties: {
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

resource insights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${prefix}-appi'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logs.id
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'st${compact}${take(suffix, 8)}'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    allowSharedKeyAccess: false
    defaultToOAuthAuthentication: true
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'kv-${compact}-${take(suffix, 6)}'
  location: location
  properties: {
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enablePurgeProtection: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    publicNetworkAccess: 'Enabled'
    sku: {
      family: 'A'
      name: 'standard'
    }
  }
}

resource search 'Microsoft.Search/searchServices@2024-03-01-preview' = {
  name: 'srch-${compact}-${take(suffix, 6)}'
  location: location
  sku: {
    name: 'basic'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http403'
      }
    }
    disableLocalAuth: true
    hostingMode: 'default'
    partitionCount: 1
    publicNetworkAccess: 'enabled'
    replicaCount: 1
    semanticSearch: 'free'
  }
}

resource foundry 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: 'aif-${compact}-${take(suffix, 6)}'
  location: location
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    allowProjectManagement: true
    customSubDomainName: 'aif-${compact}-${take(suffix, 6)}'
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
  }
}

resource project 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  parent: foundry
  name: 'meridian-iq'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    displayName: 'Meridian IQ Demo'
    description: 'Four-IQ grounding demo using synthetic tax client data'
  }
}

resource model 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: foundry
  name: modelDeploymentName
  sku: {
    name: 'GlobalStandard'
    capacity: 10
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-5-mini'
      version: '2025-08-07'
    }
    versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
  }
}

resource bing 'Microsoft.Bing/accounts@2020-06-10' = {
  name: 'bing-${compact}-${take(suffix, 6)}'
  location: 'global'
  kind: 'Bing.Grounding'
  sku: {
    name: 'S1'
  }
  properties: {}
}

resource searchConnection 'Microsoft.CognitiveServices/accounts/projects/connections@2025-06-01' = {
  parent: project
  name: searchConnectionName
  properties: {
    authType: 'AAD'
    category: 'CognitiveSearch'
    target: 'https://${search.name}.search.windows.net'
    metadata: {
      ApiType: 'Azure'
      ResourceId: search.id
      location: location
    }
  }
}

// Grounding with Bing currently requires an API-key project connection.
// The key is evaluated by ARM and stored only in the connection; it is never output.
resource bingConnection 'Microsoft.CognitiveServices/accounts/projects/connections@2025-06-01' = {
  parent: project
  name: bingConnectionName
  properties: {
    authType: 'ApiKey'
    category: 'ApiKey'
    target: 'https://api.bing.microsoft.com'
    credentials: {
      key: bing.listKeys().key1
    }
    metadata: {
      ApiType: 'Azure'
      ResourceId: bing.id
      location: 'global'
    }
  }
}

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: 'cr${compact}${take(suffix, 8)}'
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
    dataEndpointEnabled: false
    policies: {
      exportPolicy: {
        status: 'enabled'
      }
      quarantinePolicy: {
        status: 'disabled'
      }
      retentionPolicy: {
        days: 7
        status: 'disabled'
      }
      trustPolicy: {
        type: 'Notary'
        status: 'disabled'
      }
    }
    publicNetworkAccess: 'Enabled'
  }
}

resource containerEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${prefix}-cae'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logs.properties.customerId
        sharedKey: logs.listKeys().primarySharedKey
      }
    }
  }
}

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: '${prefix}-web'
  location: location
  tags: {
    'azd-env-name': environmentName
    'azd-service-name': 'web'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    environmentId: containerEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8080
        transport: 'auto'
      }
    }
    template: {
      containers: [
        {
          name: 'web'
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          env: [
            {
              name: 'MERIDIAN_MODE'
              value: 'mock'
            }
            {
              name: 'FOUNDRY_PROJECT_ENDPOINT'
              value: 'https://${foundry.name}.services.ai.azure.com/api/projects/${project.name}'
            }
            {
              name: 'FOUNDRY_MODEL_DEPLOYMENT_NAME'
              value: model.name
            }
            {
              name: 'AI_SEARCH_PROJECT_CONNECTION_ID'
              value: searchConnection.id
            }
            {
              name: 'AI_SEARCH_INDEX_NAME'
              value: searchIndexName
            }
            {
              name: 'BING_PROJECT_CONNECTION_NAME'
              value: bingConnection.name
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 2
        rules: [
          {
            name: 'http'
            http: {
              metadata: {
                concurrentRequests: '20'
              }
            }
          }
        ]
      }
    }
  }
}

var searchIndexDataContributor = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
)
var searchServiceContributor = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
)
var storageBlobDataContributor = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
)
var keyVaultSecretsUser = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '4633458b-17de-408a-b874-0445c86b69e6'
)
var acrPull = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '7f951dda-4ed3-4680-a7ca-43fe172d538d'
)
var foundryUser = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '53ca6127-db72-4b80-b1b0-d745d6d5456d'
)

resource projectSearchData 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(search.id, project.id, searchIndexDataContributor)
  scope: search
  properties: {
    principalId: project.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: searchIndexDataContributor
  }
}

resource projectSearchService 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(search.id, project.id, searchServiceContributor)
  scope: search
  properties: {
    principalId: project.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: searchServiceContributor
  }
}

resource appStorage 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storage.id, containerApp.id, storageBlobDataContributor)
  scope: storage
  properties: {
    principalId: containerApp.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: storageBlobDataContributor
  }
}

resource appVault 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, containerApp.id, keyVaultSecretsUser)
  scope: keyVault
  properties: {
    principalId: containerApp.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: keyVaultSecretsUser
  }
}

resource appAcrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(registry.id, containerApp.id, acrPull)
  scope: registry
  properties: {
    principalId: containerApp.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: acrPull
  }
}

resource appFoundryUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(project.id, containerApp.id, foundryUser)
  scope: project
  properties: {
    principalId: containerApp.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: foundryUser
  }
}

resource deployerFoundryUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(principalId)) {
  name: guid(project.id, principalId, 'foundry-user')
  scope: project
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: foundryUser
  }
}

resource deployerSearchService 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(principalId)) {
  name: guid(search.id, principalId, searchServiceContributor)
  scope: search
  properties: {
    principalId: principalId
    roleDefinitionId: searchServiceContributor
  }
}

resource deployerSearchData 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(principalId)) {
  name: guid(search.id, principalId, searchIndexDataContributor)
  scope: search
  properties: {
    principalId: principalId
    roleDefinitionId: searchIndexDataContributor
  }
}

output projectEndpoint string = 'https://${foundry.name}.services.ai.azure.com/api/projects/${project.name}'
output modelDeploymentName string = model.name
output searchConnectionId string = searchConnection.id
output searchIndexName string = searchIndexName
output searchEndpoint string = 'https://${search.name}.search.windows.net'
output bingConnectionName string = bingConnection.name
output containerRegistryEndpoint string = registry.properties.loginServer
output containerAppsEnvironmentName string = containerEnvironment.name
output containerAppName string = containerApp.name
