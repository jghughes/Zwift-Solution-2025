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

Repository: https://github.com/jghughes/Zwift-Solution-2025

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
|   +-- olympics_init.js (AG Grid setup)
|   +-- 404.html         (Error page)
|
+-- README.txt           (This file)

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
    http://127.0.0.1:8081/index.html


Step 4: Test the App

  * Verify the membership grid loads data
  * Test the filter input (top-left text box)
  * Test the "Toggle density" button
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

From the JghTable folder, run:

    az storage blob upload-batch ^
        --account-name customerzsun ^
        --destination "$web/membership" ^
        --source "./membership" ^
        --overwrite

NOTE: Use ^ for Windows CMD. For PowerShell, use ` (backtick) instead.


DEPLOY SINGLE APP - OLYMPICS
-----------------------------

    az storage blob upload-batch ^
        --account-name customerzsun ^
        --destination "$web/olympics" ^
        --source "./olympics" ^
        --overwrite


DEPLOY ALL APPS
---------------

Run both commands sequentially, or create a batch script.

================================================================================
VERIFICATION
================================================================================

PRODUCTION URLS
---------------
After deployment, test these URLs in your browser:

Membership App:
  https://customerzsun.blob.core.windows.net/$web/membership/

Olympics App:
  https://customerzsun.blob.core.windows.net/$web/olympics/

NOTE: Azure automatically serves index.html when accessing a folder URL.


VERIFY INDIVIDUAL ASSETS
-------------------------
Check that these files are accessible:

  https://customerzsun.blob.core.windows.net/$web/membership/index.css
  https://customerzsun.blob.core.windows.net/$web/membership/index.js
  https://customerzsun.blob.core.windows.net/$web/olympics/olympics_init.js

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
   * 404.html (optional error page)

3. Use relative paths in HTML:
   
   <link rel="stylesheet" href="./index.css">
   <script src="./index.js"></script>

4. Test locally (see testing steps above)

5. Deploy to Azure:
   
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


PROBLEM: Multiple blank grids appearing with "__adComponent" error
-------------------------------------------------------------------
SOLUTION:
  * This occurs when AG Grid is initialized multiple times
  * Check index.js for duplicate DOMContentLoaded listeners
  * Ensure grid is destroyed before reinitializing (toggleDensity function)
  * Verify index.html doesn't have duplicate <script src="./index.js"> tags
  * Add initialization guard flag: if (gridInitialized) return;
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

================================================================================
RELATED RESOURCES
================================================================================

AG Grid Documentation:
  https://www.ag-grid.com/javascript-data-grid/

Azure Blob Storage Static Websites:
  https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-static-website

Azure CLI Reference:
  https://learn.microsoft.com/en-us/cli/azure/storage/blob

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

================================================================================
END OF DOCUMENT
================================================================================