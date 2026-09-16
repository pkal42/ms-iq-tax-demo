targetScope = 'subscription'

@minLength(3)
param environmentName string
param location string
param principalId string = ''

var resourceGroupName = 'rg-${environmentName}'

resource resourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: location
  tags: {
    'azd-env-name': environmentName
    workload: 'meridian-iq-demo'
    dataClassification: 'synthetic-demo'
  }
}

module resources './resources.bicep' = {
  name: 'meridian-resources'
  scope: resourceGroup
  params: {
    environmentName: environmentName
    location: location
    principalId: principalId
  }
}

output AZURE_LOCATION string = location
output AZURE_RESOURCE_GROUP string = resourceGroup.name
output AZURE_AI_PROJECT_ENDPOINT string = resources.outputs.projectEndpoint
output FOUNDRY_PROJECT_ENDPOINT string = resources.outputs.projectEndpoint
output FOUNDRY_MODEL_DEPLOYMENT_NAME string = resources.outputs.modelDeploymentName
output AI_SEARCH_PROJECT_CONNECTION_ID string = resources.outputs.searchConnectionId
output AI_SEARCH_INDEX_NAME string = resources.outputs.searchIndexName
output AI_SEARCH_ENDPOINT string = resources.outputs.searchEndpoint
output BING_PROJECT_CONNECTION_NAME string = resources.outputs.bingConnectionName
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = resources.outputs.containerRegistryEndpoint
output AZURE_CONTAINER_ENVIRONMENT_NAME string = resources.outputs.containerAppsEnvironmentName
output AZURE_CONTAINER_APP_NAME string = resources.outputs.containerAppName
