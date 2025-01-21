# Deployment Instructions

To deploy YazilimAI Assistant on Azure:
1. Set up your Azure environment:
   - Create an Azure App Service.
   - Configure an Azure SQL Database.
2. Update the `appsettings.json` file with your Azure credentials.
3. Publish the application using Visual Studio or the Azure CLI:
   ```bash
   az webapp deploy --name <your-app-name> --resource-group <your-resource-group>
