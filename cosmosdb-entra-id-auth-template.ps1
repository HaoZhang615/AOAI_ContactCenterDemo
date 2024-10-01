$resourceGroupName='<RG>'
$accountName='<CosmoDB-Account-Name>'

# Cosmos DB Built-in Data Contributor
$RoleDefinitionId='00000000-0000-0000-0000-000000000002'
# Cosmos DB Built-in Data Reader
# RoleDefinitionId='00000000-0000-0000-0000-000000000001' 

# For Service Principals make sure to use the Object ID as found in the Enterprise applications section of the Azure Active Directory portal blade.
$principalId='<Object-ID>'
az cosmosdb sql role assignment create --account-name $accountName --resource-group $resourceGroupName --scope "/" --principal-id $principalId --role-definition-id $RoleDefinitionId