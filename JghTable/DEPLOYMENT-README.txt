================================================================================
ZSUN CLUB WEB APPS - DEVELOPER GUIDE
================================================================================

PROJECT OVERVIEW
----------------
This repository contains multiple Single Page Applications (SPAs) hosted on 
Azure Blob Storage. Each app displays cycling data using AG Grid.

Current Apps:
  * Membership List - rider statistics and power data
  * Olympics Results - ZRL race results

Repository: https://github.com/jghhughes/Zwift-Solution-2025

================================================================================
PROJECT STRUCTURE
================================================================================

JghTable/
|
+-- membership/
|   +-- index.html       (Entry point)
|   +-- index.js         (AG Grid initialization & data fetching)
|   +-- index.css        (Custom styles)
|   +-- 404.html         (Error page)
|
+-- olympics/
|   +-- index.html       (Entry point)
|   +-- index.js         (AG Grid initialization & data fetching)
|   +-- index.css        (Custom styles)
|   +-- 404.html         (Error page)
|
+-- DEPLOYMENT-README.txt (This file)

================================================================================
LOCAL DEVELOPMENT & TESTING
================================================================================

PREREQUISITES (One-time setup)
------------------------------
Install Node.js http-server globally:

    npm install -g http-server


TESTING THE MEMBERSHIP APP
---------------------------

Step 1: Open Terminal in Correct Folder
  
  In VS Code:
    * Right-click on JghTable/membership folder
    * Select "Open in Integrated Terminal"
  
  Or navigate manually:
    cd C:\Users\johng\source\repos\Zwift-Solution-2025\JghTable\membership


Step 2: Launch Local Web Server

    http-server .

  Expected output:
    Starting up http-server, serving .
    Available on:
      http://127.0.0.1:8080
      http://192.168.1.x:8080
    Hit CTRL-C to stop the server


Step 3: Open in Browser

  Click the URL shown in terminal or navigate to:
    http://127.0.0.1:8080/index.html


Step 4: Test the App

  * Verify the membership grid loads data
  * Test the filter input functionality
  * Test cell copying (Ctrl+C or double-click)
  * Verify column sorting and resizing
  * Open browser console (F12) and check for errors


Step 5: Stop the Server

  Press CTRL+C in the terminal


TESTING THE OLYMPICS APP
-------------------------

Same steps as above, but use the olympics folder:

    cd C:\Users\johng\source\repos\Zwift-Solution-2025\JghTable\olympics
    http-server .

Then open: http://127.0.0.1:8080/index.html


ALTERNATIVE: Python HTTP Server (if Node.js not available)
-----------------------------------------------------------

    cd JghTable/membership
    python -m http.server 8080

Then open: http://127.0.0.1:8080/index.html

================================================================================
PRODUCTION DEPLOYMENT
================================================================================

PREREQUISITES (One-time setup)
------------------------------
1. Install Azure CLI:
   https://learn.microsoft.com/en-us/cli/azure/install-azure-cli

2. Login to Azure:
   az login


DEPLOY SINGLE APP - MEMBERSHIP
-------------------------------

OPTION A: Windows Command Prompt (CMD)
---------------------------------------
From the JghTable folder, run:

    az storage blob upload-batch ^
        --account-name customerzsun ^
        --destination "$web/membership" ^
        --source "./membership" ^
        --overwrite

NOTE: Use ^ for line continuation in CMD.


OPTION B: PowerShell
---------------------
From the JghTable folder, run:

    az storage blob upload-batch `
        --account-name customerzsun `
        --destination '$web/membership' `
        --source './membership' `
        --overwrite

NOTE: Use ` (backtick) for line continuation in PowerShell.
NOTE: Use single quotes around $web to prevent variable expansion.


DEPLOY SINGLE APP - OLYMPICS
-----------------------------

OPTION A: Windows Command Prompt (CMD)
---------------------------------------

    az storage blob upload-batch ^
        --account-name customerzsun ^
        --destination "$web/olympics" ^
        --source "./olympics" ^
        --overwrite


OPTION B: PowerShell
---------------------

    az storage blob upload-batch `
        --account-name customerzsun `
        --destination '$web/olympics' `
        --source './olympics' `
        --overwrite


DEPLOY ALL APPS
---------------

OPTION A: Windows Command Prompt (CMD) - Sequential
----------------------------------------------------
Run both commands sequentially:

    az storage blob upload-batch ^
        --account-name customerzsun ^
        --destination "$web/membership" ^
        --source "./membership" ^
        --overwrite

    az storage blob upload-batch ^
        --account-name customerzsun ^
        --destination "$web/olympics" ^
        --source "./olympics" ^
        --overwrite


OPTION B: PowerShell - Sequential
----------------------------------
Run both commands sequentially:

    az storage blob upload-batch `
        --account-name customerzsun `
        --destination '$web/membership' `
        --source './membership' `
        --overwrite

    az storage blob upload-batch `
        --account-name customerzsun `
        --destination '$web/olympics' `
        --source './olympics' `
        --overwrite


OPTION C: PowerShell Script (Recommended for multiple deployments)
-------------------------------------------------------------------
Create a file named deploy-all.ps1 in the JghTable folder:

    # Deploy all ZSUN web apps to Azure Blob Storage
    # Run from JghTable folder

    $account = "customerzsun"
    $apps = @("membership", "olympics")

    Write-Host "Starting deployment of all apps..." -ForegroundColor Green

    foreach ($app in $apps) {
        Write-Host "`nDeploying $app..." -ForegroundColor Yellow
        
        az storage blob upload-batch `
            --account-name $account `
            --destination "`$web/$app" `
            --source "./$app" `
            --overwrite
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "$app deployed successfully!" -ForegroundColor Green
        } else {
            Write-Host "$app deployment failed!" -ForegroundColor Red
        }
    }

    Write-Host "`nAll deployments complete!" -ForegroundColor Green

Run the script:

    cd C:\Users\johng\source\repos\Zwift-Solution-2025\JghTable
    .\deploy-all.ps1

NOTE: If you get an execution policy error, run:
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser


OPTION D: Batch Script (CMD alternative)
-----------------------------------------
Create a file named deploy-all.bat in the JghTable folder:

    @echo off
    echo Starting deployment of all apps...

    echo.
    echo Deploying membership...
    az storage blob upload-batch ^
        --account-name customerzsun ^
        --destination "$web/membership" ^
        --source "./membership" ^
        --overwrite

    echo.
    echo Deploying olympics...
    az storage blob upload-batch ^
        --account-name customerzsun ^
        --destination "$web/olympics" ^
        --source "./olympics" ^
        --overwrite

    echo.
    echo All deployments complete!
    pause

Run the script:

    cd C:\Users\johng\source\repos\Zwift-Solution-2025\JghTable
    deploy-all.bat

================================================================================
VERIFICATION
================================================================================

PRODUCTION URLS
---------------
After deployment, test these URLs in your browser:

Membership App:
  https://customerzsun.blob.core.windows.net/$web/membership/index.html

Olympics App:
  https://customerzsun.blob.core.windows.net/$web/olympics/index.html


VERIFY INDIVIDUAL ASSETS
-------------------------
Check that these files are accessible:

Membership:
  https://customerzsun.blob.core.windows.net/$web/membership/index.html
  https://customerzsun.blob.core.windows.net/$web/membership/index.css
  https://customerzsun.blob.core.windows.net/$web/membership/index.js
  https://customerzsun.blob.core.windows.net/$web/membership/404.html

Olympics:
  https://customerzsun.blob.core.windows.net/$web/olympics/index.html
  https://customerzsun.blob.core.windows.net/$web/olympics/index.css
  https://customerzsun.blob.core.windows.net/$web/olympics/index.js
  https://customerzsun.blob.core.windows.net/$web/olympics/404.html

================================================================================
DATA SOURCES
================================================================================

Both apps fetch JSON data from a separate Azure container:

Membership data:
  https://customerzsun.blob.core.windows.net/preprocessed/rider_stats_dto_as_list.json

Olympics data:
  https://customerzsun.blob.core.windows.net/preprocessed/wtrl-zrl-2025-26-round3race6-leaderboard-club.json

Data is updated by Python scripts in the Zsun01 project (separate from this repo).

================================================================================
COMMON DEVELOPMENT TASKS
================================================================================

MAKING CHANGES TO AN APP
-------------------------

1. Edit files in JghTable/[app-name]/
2. Test locally with http-server (see testing steps above)
3. Verify changes work correctly
4. Commit to Git:
   
   git add .
   git commit -m "Description of changes"
   git push origin master

5. Deploy to Azure (see deployment commands above)


ADDING A NEW APP
----------------

1. Create new folder: JghTable/[new-app-name]/

2. Add required files:
   * index.html (entry point)
   * index.js (your JavaScript)
   * index.css (your styles)
   * 404.html (error page)

3. Use relative paths in HTML:
   
   <link rel="stylesheet" href="./index.css">
   <script src="./index.js"></script>

4. Test locally (see testing steps above)

5. Deploy to Azure using PowerShell:
   
   az storage blob upload-batch `
       --account-name customerzsun `
       --destination '$web/[new-app-name]' `
       --source './[new-app-name]' `
       --overwrite

   Or using CMD:
   
   az storage blob upload-batch ^
       --account-name customerzsun ^
       --destination "$web/[new-app-name]" ^
       --source "./[new-app-name]" ^
       --overwrite

6. Access at:
   https://customerzsun.blob.core.windows.net/$web/[new-app-name]/

================================================================================
TROUBLESHOOTING
================================================================================

PROBLEM: "http-server: command not found"
------------------------------------------
SOLUTION: Install Node.js and http-server:
  npm install -g http-server


PROBLEM: "Access denied" when deploying to Azure
-------------------------------------------------
SOLUTION: Re-authenticate with Azure:
  az login


PROBLEM: PowerShell script execution policy error
--------------------------------------------------
SOLUTION: Allow script execution for current user:
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Or run script with bypass:
  powershell -ExecutionPolicy Bypass -File .\deploy-all.ps1


PROBLEM: PowerShell $web variable expansion error
--------------------------------------------------
SOLUTION: Use single quotes around $web:
  --destination '$web/membership'

NOT double quotes which cause variable expansion:
  --destination "$web/membership" (WRONG in PowerShell)


PROBLEM: Changes not showing on Azure after deployment
-------------------------------------------------------
SOLUTION: 
  * Clear browser cache or use incognito/private mode
  * Hard refresh: CTRL+F5 (Windows) or CMD+SHIFT+R (Mac)
  * Wait a few minutes for CDN cache to expire


PROBLEM: Grid not loading data
-------------------------------
SOLUTION:
  * Check browser console (F12 -> Console tab) for error messages
  * Verify data URL is correct in index.js
  * Check CORS settings on Azure Blob Storage (should allow public read)
  * Verify JSON file exists at the specified URL


PROBLEM: Styles not loading correctly
--------------------------------------
SOLUTION:
  * Verify index.css exists in the same folder as index.html
  * Check browser console (F12) for 404 errors
  * Ensure relative paths use ./ prefix: href="./index.css"
  * Clear browser cache and hard refresh


PROBLEM: JavaScript not executing
----------------------------------
SOLUTION:
  * Verify index.js exists in the same folder as index.html
  * Check browser console (F12) for syntax errors
  * Ensure relative paths use ./ prefix: src="./index.js"
  * Verify AG Grid CDN is accessible


PROBLEM: Multiple blank grids appearing with "__adComponent" error
-------------------------------------------------------------------
SOLUTION:
  * This occurs when AG Grid is initialized multiple times
  * Check index.js for duplicate DOMContentLoaded listeners
  * Verify index.html does not have duplicate <script src="./index.js"> tags
  * Clear browser cache completely and hard refresh (CTRL+SHIFT+DELETE)

================================================================================
BEST PRACTICES
================================================================================

[X] Always test locally before deploying to Azure
[X] Use relative paths (./file.css) for same-folder assets
[X] Use absolute URLs for external data sources
[X] Keep each app self-contained (no cross-folder dependencies)
[X] Commit and push changes to Git before deploying to Azure
[X] Document any configuration changes in this README
[X] Test in multiple browsers (Chrome, Firefox, Edge)
[X] Check mobile responsiveness if making UI changes
[X] Use PowerShell scripts for automated multi-app deployments
[X] Use single quotes in PowerShell around $web to prevent variable expansion

================================================================================
TECHNICAL DETAILS
================================================================================

HOW RELATIVE PATHS WORK
------------------------
This structure uses relative paths that work in both environments:

  <link rel="stylesheet" href="./index.css">
  <script src="./index.js"></script>

Local development:
  file:///C:/.../JghTable/membership/index.html
  -> ./index.css resolves to same folder

Azure production:
  https://customerzsun.blob.core.windows.net/$web/membership/
  -> Azure serves index.html automatically
  -> ./index.css resolves to same folder

Result: NO file editing required for deployment!


AZURE STATIC WEBSITE BEHAVIOR
------------------------------
Azure Blob Storage $web container automatically serves index.html:

  Request: /$web/membership/
  Serves:  /$web/membership/index.html

This is native Azure behavior - no configuration needed.


AG GRID VERSION
---------------
Current version: 29.3.4 (loaded from CDN)
Update all three references if upgrading:
  * ag-grid.css
  * ag-theme-alpine.css
  * ag-grid-community.min.js


POWERSHELL VS CMD SYNTAX
-------------------------
Key differences when using Azure CLI:

Line continuation:
  PowerShell: Use backtick `
  CMD:        Use caret ^

Quoting $web:
  PowerShell: Use single quotes '$web/app'
  CMD:        Use double quotes "$web/app"

Variables:
  PowerShell: $variable = "value"
  CMD:        set variable=value

================================================================================
RELATED RESOURCES
================================================================================

AG Grid Documentation:
  https://www.ag-grid.com/javascript-data-grid/

Azure Blob Storage Static Websites:
  https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-static-website

Azure CLI Reference:
  https://learn.microsoft.com/en-us/cli/azure/storage/blob

PowerShell Documentation:
  https://learn.microsoft.com/en-us/powershell/

Project Repository:
  https://github.com/jghughes/Zwift-Solution-2025

================================================================================
SUPPORT
================================================================================

For questions or issues:

1. Check browser console for JavaScript errors (press F12)
2. Review Azure Blob Storage logs in Azure Portal
3. Check this README for troubleshooting guidance
4. Contact: John Hughes (project maintainer)

================================================================================
MAINTENANCE LOG
================================================================================

2026-02-17: Initial README created
            - Documented local development workflow
            - Documented Azure deployment process
            - Added troubleshooting section

2026-02-17: Refactored both apps
            - Externalized CSS to index.css files
            - Renamed olympics_init.js to index.js for consistency
            - Simplified error handling (removed log viewer)
            - Reduced JavaScript code length by approximately 40%
            - Updated 404 pages to match app styling
            - Standardized file structure across all apps

2026-02-17: Enhanced deployment documentation
            - Added comprehensive PowerShell deployment instructions
            - Included PowerShell script template for multi-app deployment
            - Added Batch script alternative for CMD users
            - Documented PowerShell-specific troubleshooting
            - Added syntax comparison table for PowerShell vs CMD

================================================================================
END OF DOCUMENT
================================================================================