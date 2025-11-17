Secretive thinks like connection strings or keys must not be hardcoded source code otherwise they will be visible to readers of your GitHub repository. They must be hidden outside the source code and retrieved with encryption during runtime. To accomplish this we use two levels of indirection. The idea is to store the connection strings as Secrets in Azure Key Vault where we service apps that are securely identified and authorized can retrieve them. The Secrets are Name/Value pairs loaded into the Key Vault via the Azure Portal. Our Key Vault is named "AzureStorageConnections." In there we have four secrets containing the connection strings our four Azure storage accounts. You can find your storage account's connection strings in the Azure portal. Navigate to Security + networking > Access keys in your storage account's settings to see connection strings for both primary and secondary access keys.StorageAccount>>AccessKeys>>ShowKeys.If you are using a Primary Access Key then you can copy/paste the connection string under Key 1 and if you are using Secondary Access Key then you can use the connection string under Key 2.

Secret Name: coldstorage 		Secret Value: cut/paste from box entitled Connection String 
Secret Name: customerkelso 		Secret Value: cut/paste from box entitled Connection String 
Secret Name: customertester 		Secret Value: cut/paste from box entitled Connection String 
Secret Name: systemrezultzlevel1 	Secret Value: cut/paste from box entitled Connection String 	

To add these name/value pairs in the Azure Portal, go the Key Vault tab select AzureStorageConnections>Objects>Secrets>Generate/Import. The second level of indirection is to not mention secret names in source code, but rather in environment variables. We use a second name/value pair for this. For each webbapp running in App Services, go Settings>Environment variables>Add. Create a name/value for the key vault and each secret.

Environment variable name:	KEYVAULT_01  	Vault name:  AzureStorageConnections
Environment variable name:	SECRET_01 	Secret name: coldstorage
Environment variable name:      SECRET_02 	Secret name: customerkelso
Environment variable name:      SECRET_03 	Secret name: customertester
Environment variable name:      SECRET_04	Secret name: systemrezultzlevel1

We create an identical suite of environmental variables for debugging the web apps. For each project go Project>Properties>Debug>Open debug launch profiles UI>Environment variables and ass the identical name value pairs for both http and https. I don't seem to need them for IIS for the Core web apps. The data is saved in Project>Properties>launchSettings.json within the environmentVariable section. The launchSettings.json file is only used on the local development machine, it is not deployed.

  "profiles": {
    "http": {
      "commandName": "Project",
      "launchBrowser": true,
      "launchUrl": "swagger",
      "environmentVariables": {
        "ASPNETCORE_ENVIRONMENT": "Development",
        "KEYVAULT_01": "AzureStorageConnections",
        "SECRET_01": "coldstorage",
        "SECRET_02": "customerkelso",
        "SECRET_03": "customertester",
        "SECRET_04": "systemrezultzlevel1"
      },
      "dotnetRunMessages": true,
      "applicationUrl": "http://localhost:5052"
    },
    "https": {
      "commandName": "Project",
      "launchBrowser": true,
      "launchUrl": "swagger",
      "environmentVariables": {
        "ASPNETCORE_ENVIRONMENT": "Development",
        "KEYVAULT_01": "AzureStorageConnections",
        "SECRET_01": "coldstorage",
        "SECRET_02": "customerkelso",
        "SECRET_03": "customertester",
        "SECRET_04": "systemrezultzlevel1"
      },
      "dotnetRunMessages": true,
      "applicationUrl": "https://localhost:7178;http://localhost:5052"
    },
    "IIS Express": {
      "commandName": "IISExpress",
      "launchBrowser": true,
      "launchUrl": "swagger",
      "environmentVariables": {
        "ASPNETCORE_ENVIRONMENT": "Development",
        "COMPlus_ReadyToRun": "0",
      }
    }
  },
 
We can reference environment variables from absolutely anywhere by way of the environment variable names, and use them to fetch secret data over the wire. We can do so in a webapp itself, in a console app, or indirectly in any standard class library no matter how many times removed from the parent app. In the Rezultz Solution, I centralise the encrypted pulling-in of Azure Storage Connection strings in a single class,  Jgh.ConnectionStrings.Mar2024.AzureStorageConnectionStrings.cs. Use two Nuget packages namely, Azure.Identity and Azure.Security.KeyVault.Secrets and then the following code snippet:

var azureConnectionStringsKeyVaultName = System.Environment.GetEnvironmentVariable("KEYVAULT_01");
var secretName01 = System.Environment.GetEnvironmentVariable("SECRET_01");
var keyVaultUri = $"https://{azureConnectionStringsKeyVaultName}.vault.azure.net/";
var client = new SecretClient(new Uri(keyVaultUri), new DefaultAzureCredential());
var response01 = await client.GetSecretAsync(secretName01);

If anything goes awry you get a fascinating error message, giving an inside peek of how DefaultAzureCredential() works under the hood. It searches in multiple different likely places for suitable credentials that authorise access to the key vault and if it comes up empty-handed it throws an aggregate exception. The aggregate exception error message explains what needs to be done. The point of failure for an improperly authenticated app is the call to client.GetSecretAsync(). This gets rejected unless it is accompanied by an authorised token. 

<***************************************************************************************************************>

Unhandled exception. 

Azure.Identity.CredentialUnavailableException: DefaultAzureCredential failed to retrieve a token from the included credentials. See the troubleshooting guide for more information. https://aka.ms/azsdk/net/identity/defaultazurecredential/troubleshoot

- EnvironmentCredential authentication unavailable. Environment variables are not fully configured. See the troubleshooting guide for more information. https://aka.ms/azsdk/net/identity/environmentcredential/troubleshoot

- WorkloadIdentityCredential authentication unavailable. The workload options are not fully configured. See the troubleshooting guide for more information. https://aka.ms/azsdk/net/identity/workloadidentitycredential/troubleshoot

- ManagedIdentityCredential authentication unavailable. No response received from the managed identity endpoint.

- Process "C:\Program Files\Microsoft Visual Studio\2022\Professional\Common7\IDE\CommonExtensions\Microsoft\Asal\TokenService\Microsoft.Asal.TokenService.exe" has failed with unexpected error: TS003: Error, TS001: This account 'john.gerald.hughes@outlook.com' needs re-authentication. Please go to Tools->Options->Azure Services Authentication, and re-authenticate the account you want to use..

- Azure CLI not installed
- Az.Accounts module >= 2.2.0 is not installed.
- Azure Developer CLI could not be found.

 ---> System.AggregateException: Multiple exceptions were encountered while attempting to authenticate. (EnvironmentCredential authentication unavailable. Environment variables are not fully configured. See the troubleshooting guide for more information. https://aka.ms/azsdk/net/identity/environmentcredential/troubleshoot) (WorkloadIdentityCredential authentication unavailable. The workload options are not fully configured. See the troubleshooting guide for more information. https://aka.ms/azsdk/net/identity/workloadidentitycredential/troubleshoot) (ManagedIdentityCredential authentication unavailable. No response received from the managed identity endpoint.) (Process "C:\Program Files\Microsoft Visual Studio\2022\Professional\Common7\IDE\CommonExtensions\Microsoft\Asal\TokenService\Microsoft.Asal.TokenService.exe" has failed with unexpected error: TS003: Error, TS001: This account 'john.gerald.hughes@outlook.com' needs re-authentication. Please go to Tools->Options->Azure Services Authentication, and re-authenticate the account you want to use..) (Azure CLI not installed) (Az.Accounts module >= 2.2.0 is not installed.) (Azure Developer CLI could not be found.)
 ---> Azure.Identity.CredentialUnavailableException: EnvironmentCredential authentication unavailable. Environment variables are not fully configured. See the troubleshooting guide for more information. https://aka.ms/azsdk/net/identity/environmentcredential/troubleshoot

<***************************************************************************************************************>

The authorisation problem needs to be fixed in two places. The Visual Studio development environment needs to authorised. "This account 'john.gerald.hughes@outlook.com' needs re-authentication. Please go to Tools->Options->Azure Services Authentication, and re-authenticate the account you want to use." When Visual Studio is authorised with a fresh certificate, you can proceed to Debug. To cater for production, use the Azure Portal to allocate the webapps a system-generated "managed identity" and then register the identities with key vault so that the key vault is accessible to the authorised webapps. First do the four webapps. Go App Services>{app}>Settings>Identity>System Assigned>Status->On>Save This autonmatically generates a GUID for the app's Object (Principal) ID and registers as a resource with Microsoft EntraIDas a managed Identity that can be configured to access other resources. Go Permissions>Azure Role Assignments>scroll down to select "Key Vault Secrets User". This works for key vaults that use the  'Azure role-based access control' permission model. Now return to the Portal's Home Page. Go {Key Vault}>Settings>Access Configuration>{Azure role-based access control}>Go to access control(IAM)>Role Assignments>Add>Role>Members>pick Managed Identity>Select members>in the side-bar Select Managed Identities and pick the app service you want from the drop down list. 

That's it. Simple as that. Your secretive thinks like connection strings or keys are now a million miles from your source code under lock and key. Only the identities you have authorised can access them.
 

 



