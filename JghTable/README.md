# ZSUN Club Web Apps - Developer Guide

## Project Overview

This repository contains multiple Single Page Applications (SPAs) hosted on Azure Blob Storage. Each app displays cycling data using AG Grid with shared framework code for maintainability.

**Current Apps:**
- **Membership List** - rider statistics and power data
- **Olympics Results** - ZRL race results

**Repository:** [https://github.com/jghughes/Zwift-Solution-2025](https://github.com/jghughes/Zwift-Solution-2025)

---

## Project Structure

```
JghTable/
?
??? shared-mastercopies/
?   ??? base-grid.css    # Master copy - Excel-style AG Grid layouts
?   ??? base-grid.js     # Master copy - Shared AG Grid framework
?
??? membership/
?   ??? index.html       # Entry point
?   ??? index.js         # App-specific configuration (~50 lines)
?   ??? index.css        # App-specific styles
?   ??? base-grid.css    # Deployed copy from shared-mastercopies
?   ??? base-grid.js     # Deployed copy from shared-mastercopies
?   ??? 404.html         # Error page
?
??? olympics/
?   ??? index.html       # Entry point
?   ??? index.js         # App-specific configuration (~50 lines)
?   ??? index.css        # App-specific styles
?   ??? base-grid.css    # Deployed copy from shared-mastercopies
?   ??? base-grid.js     # Deployed copy from shared-mastercopies
?   ??? 404.html         # Error page
?
??? README.md            # This file
??? CHANGELOG.md         # Version history and maintenance log
```

---

## Shared Code Architecture

### Master-Copy Approach

To reduce duplication while maintaining Azure Blob Storage compatibility (no-build deployment), we use a master-copy pattern:

**1. DEVELOP:** Edit files in `shared-mastercopies/`
   - `base-grid.css` - Common styles for all apps
   - `base-grid.js` - Shared AG Grid framework

**2. COPY:** Duplicate to each app folder
   - `shared-mastercopies/base-grid.css` ? `membership/base-grid.css`
   - `shared-mastercopies/base-grid.css` ? `olympics/base-grid.css`
   - `shared-mastercopies/base-grid.js` ? `membership/base-grid.js`
   - `shared-mastercopies/base-grid.js` ? `olympics/base-grid.js`

**3. DEPLOY:** Azure serves each app's complete folder independently

#### Benefits
- ? Single source of truth for common code
- ? ~75% reduction in app-specific JavaScript (220 lines ? 50 lines)
- ? No build tools required
- ? Each app folder is self-contained for deployment
- ? Bug fixes propagate to all apps via copy step

#### Tradeoffs
- ?? Must manually copy shared files after editing master copies
- ?? File duplication in repository (acceptable for 2-3 small apps)

---

### Shared Framework Usage

Each app's `index.js` uses `ZsunGridFramework.GridManager`:

```javascript
// App-specific configuration only
const gridManager = new ZsunGridFramework.GridManager({
    appName: 'ZSUN Membership',
    dataUrl: DATA_URL,
    fallbackData: FALLBACK_DATA,
    baseColumnDefs: BASE_COLUMN_DEFS,
    rowHeight: 25,
    headerHeight: 32,
    defaultColWidth: 90,
    sortable: true,
    resizable: true,
    filterable: true,
    minWidth: 40
});

gridManager.initialize();
```

All boilerplate (clipboard, error handling, data loading) is in `base-grid.js`.

---

### HTML References (Required in each app)

```html
<!-- CSS: App-specific first, then shared base -->
<link rel="stylesheet" href="./index.css">
<link rel="stylesheet" href="./base-grid.css">

<!-- JS: Load shared framework before app config -->
<script src="https://cdn.jsdelivr.net/npm/ag-grid-community@29.3.4/dist/ag-grid-community.min.js"></script>
<script src="./base-grid.js"></script>
<script src="./index.js"></script>
```

---

## Workflow: Updating Shared Code

### Step 1: Edit Master Copies

Make changes in `shared-mastercopies/` folder:
- `base-grid.css` - for styling changes affecting all apps
- `base-grid.js` - for framework logic affecting all apps

### Step 2: Copy to App Folders

Manually copy updated files to each app:

**Windows Command Prompt:**
```cmd
cd C:\Users\johng\source\repos\Zwift-Solution-2025\JghTable

copy shared-mastercopies\base-grid.css membership\base-grid.css /Y
copy shared-mastercopies\base-grid.css olympics\base-grid.css /Y

copy shared-mastercopies\base-grid.js membership\base-grid.js /Y
copy shared-mastercopies\base-grid.js olympics\base-grid.js /Y
```

**PowerShell:**
```powershell
cd C:\Users\johng\source\repos\Zwift-Solution-2025\JghTable

Copy-Item shared-mastercopies\base-grid.css membership\base-grid.css -Force
Copy-Item shared-mastercopies\base-grid.css olympics\base-grid.css -Force

Copy-Item shared-mastercopies\base-grid.js membership\base-grid.js -Force
Copy-Item shared-mastercopies\base-grid.js olympics\base-grid.js -Force
```

### Step 3: Test Locally

Test each app with `http-server` (see [Testing](#local-development--testing) section below).

### Step 4: Commit Changes

```bash
git add .
git commit -m "Update shared framework: [description]"
git push origin master
```

### Step 5: Deploy to Azure

See [Deployment](#production-deployment) section below.

---

### Automated Copy Script (Optional)

Create `sync-shared-files.ps1` in JghTable folder:

```powershell
# Sync shared master copies to app folders
$apps = @("membership", "olympics")

Write-Host "Syncing shared files..." -ForegroundColor Green

foreach ($app in $apps) {
    Copy-Item shared-mastercopies\base-grid.css $app\base-grid.css -Force
    Copy-Item shared-mastercopies\base-grid.js $app\base-grid.js -Force
    Write-Host "  ? Updated $app" -ForegroundColor Green
}

Write-Host "Sync complete!" -ForegroundColor Green
```

**Run:** `.\sync-shared-files.ps1`

---

## Local Development & Testing

### Prerequisites (One-time setup)

Install Node.js `http-server` globally:

```bash
npm install -g http-server
```

---

### Testing the Membership App

**Step 1: Open Terminal in App Folder**

In VS Code:
- Right-click on `JghTable/membership` folder
- Select "Open in Integrated Terminal"

Or navigate manually:
```bash
cd C:\Users\johng\source\repos\Zwift-Solution-2025\JghTable\membership
```

**Step 2: Launch Local Web Server**

```bash
http-server .
```

Expected output:
```
Starting up http-server, serving .
Available on:
  http://127.0.0.1:8080
Hit CTRL-C to stop the server
```

**Step 3: Open in Browser**

Navigate to: [http://127.0.0.1:8080/index.html](http://127.0.0.1:8080/index.html)

**Step 4: Test the App**

- ? Verify the membership grid loads data
- ? Test the filter input functionality
- ? Test cell copying (Ctrl+C or double-click)
- ? Verify column sorting and resizing
- ? Open browser console (F12) and check for errors
- ? Verify shared framework loaded (check Network tab for `base-grid.js`)

**Step 5: Stop the Server**

Press `CTRL+C` in the terminal

---

### Testing the Olympics App

Same steps, but use the `olympics` folder:

```bash
cd C:\Users\johng\source\repos\Zwift-Solution-2025\JghTable\olympics
http-server .
```

Then open: [http://127.0.0.1:8080/index.html](http://127.0.0.1:8080/index.html)

---

### Alternative: Python HTTP Server

```bash
cd JghTable/membership
python -m http.server 8080
```

Then open: [http://127.0.0.1:8080/index.html](http://127.0.0.1:8080/index.html)

---

## Production Deployment

### Prerequisites (One-time setup)

1. **Install Azure CLI:**  
   [https://learn.microsoft.com/en-us/cli/azure/install-azure-cli](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)

2. **Login to Azure:**
```bash
   az login
```

---

### Deploy Single App - Membership

**Command Prompt (CMD):**
```cmd
az storage blob upload-batch ^
    --account-name customerzsun ^
    --destination "$web/membership" ^
    --source "./membership" ^
    --overwrite
```

**PowerShell:**
```powershell
az storage blob upload-batch `
    --account-name customerzsun `
    --destination '$web/membership' `
    --source './membership' `
    --overwrite
```

> **Note:** PowerShell requires single quotes around `$web`.

---

### Deploy Single App - Olympics

**Command Prompt (CMD):**
```cmd
az storage blob upload-batch ^
    --account-name customerzsun ^
    --destination "$web/olympics" ^
    --source "./olympics" ^
    --overwrite
```

**PowerShell:**
```powershell
az storage blob upload-batch `
    --account-name customerzsun `
    --destination '$web/olympics' `
    --source './olympics' `
    --overwrite
```

---

### Automated Deployment Script

Create `deploy-all.ps1` in JghTable folder:

```powershell
# Deploy all ZSUN web apps to Azure Blob Storage
$account = "customerzsun"
$apps = @("membership", "olympics")

Write-Host "Starting deployment..." -ForegroundColor Green

foreach ($app in $apps) {
    Write-Host "`nDeploying $app..." -ForegroundColor Yellow
    
    az storage blob upload-batch `
        --account-name $account `
        --destination "`$web/$app" `
        --source "./$app" `
        --overwrite
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ? $app deployed" -ForegroundColor Green
    } else {
        Write-Host "  ? $app failed" -ForegroundColor Red
    }
}

Write-Host "`nDeployment complete!" -ForegroundColor Green
```

**Run:**
```powershell
cd C:\Users\johng\source\repos\Zwift-Solution-2025\JghTable
.\deploy-all.ps1
```

**If execution policy error occurs:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Verification

### Production URLs

**Membership App:**  
[https://customerzsun.blob.core.windows.net/$web/membership/index.html](https://customerzsun.blob.core.windows.net/$web/membership/index.html)

**Olympics App:**  
[https://customerzsun.blob.core.windows.net/$web/olympics/index.html](https://customerzsun.blob.core.windows.net/$web/olympics/index.html)

---

### Verify Shared Files Deployed

Check these URLs return 200 OK:

- [https://customerzsun.blob.core.windows.net/$web/membership/base-grid.css](https://customerzsun.blob.core.windows.net/$web/membership/base-grid.css)
- [https://customerzsun.blob.core.windows.net/$web/membership/base-grid.js](https://customerzsun.blob.core.windows.net/$web/membership/base-grid.js)
- [https://customerzsun.blob.core.windows.net/$web/olympics/base-grid.css](https://customerzsun.blob.core.windows.net/$web/olympics/base-grid.css)
- [https://customerzsun.blob.core.windows.net/$web/olympics/base-grid.js](https://customerzsun.blob.core.windows.net/$web/olympics/base-grid.js)

---

### Browser Console Verification

Open F12 console and verify:

1. ? No 404 errors for `base-grid.css` or `base-grid.js`
2. ? Console shows: `"Initializing ZSUN [AppName] Grid..."`
3. ? Console shows: `"AG Grid initialized successfully"`
4. ? Check `window.ZsunGridFramework` exists:

```javascript
// In console type:
window.ZsunGridFramework
// Should return: {GridManager: class GridManager}
```

---

## Data Sources

Both apps fetch JSON data from Azure Blob Storage:

**Membership data:**  
[https://customerzsun.blob.core.windows.net/preprocessed/rider_stats_dto_as_list.json](https://customerzsun.blob.core.windows.net/preprocessed/rider_stats_dto_as_list.json)

**Olympics data:**  
[https://customerzsun.blob.core.windows.net/preprocessed/wtrl-zrl-2025-26-round3race6-leaderboard-club.json](https://customerzsun.blob.core.windows.net/preprocessed/wtrl-zrl-2025-26-round3race6-leaderboard-club.json)

> Data is updated by Python scripts in the Zsun01 project (separate repository).

---

## Common Development Tasks

### Making Changes to an App-Specific File

1. Edit files in `JghTable/[app-name]/`
   - `index.js` (app configuration)
   - `index.css` (app-specific styles)
   - `index.html` (structure)

2. Test locally with `http-server`
3. Commit to Git
4. Deploy to Azure

---

### Making Changes to Shared Framework

1. **Edit master copy:**
   - `shared-mastercopies/base-grid.css` (styling)
   - `shared-mastercopies/base-grid.js` (framework logic)

2. **Copy to all apps** (see [Workflow](#workflow-updating-shared-code) section)

3. **Test BOTH apps locally**

4. **Commit to Git:**
```bash
   git add .
   git commit -m "Update shared framework: [description]"
   git push
```

5. **Deploy BOTH apps to Azure**

---

### Adding a New App

1. **Create folder:** `JghTable/[new-app-name]/`

2. **Copy shared files:**
   - `shared-mastercopies/base-grid.css` ? `[new-app-name]/base-grid.css`
   - `shared-mastercopies/base-grid.js` ? `[new-app-name]/base-grid.js`

3. **Create app-specific files:**
   - `index.html` (include `base-grid.css` and `base-grid.js` references)
   - `index.js` (use `ZsunGridFramework.GridManager`)
   - `index.css` (app-specific styles)
   - `404.html` (error page)

4. **Test locally**

5. **Update deployment scripts** to include new app

6. **Deploy to Azure:**  
   `https://customerzsun.blob.core.windows.net/$web/[new-app-name]/`

---

## Troubleshooting

### Problem: Grid not initializing

**Solution:**
- Check browser console (F12) for errors
- Verify `base-grid.js` loaded: Check Network tab for 200 OK status
- Verify order in HTML: `base-grid.js` must load BEFORE `index.js`
- Check `window.ZsunGridFramework` exists in console

---

### Problem: Styles not applying correctly

**Solution:**
- Verify `base-grid.css` loaded: Check Network tab
- Check CSS order in HTML: `index.css` should load before `base-grid.css`
- Clear browser cache (`Ctrl+Shift+Delete`)
- Hard refresh (`Ctrl+F5`)

---

### Problem: Changes to shared code not reflected in app

**Solution:**
- Verify you copied master files to app folders
- Check file timestamps match
- Re-deploy app to Azure
- Clear browser cache

---

### Problem: "ZsunGridFramework is not defined"

**Solution:**
- Check HTML has: `<script src="./base-grid.js"></script>`
- Verify `base-grid.js` exists in app folder (not just master copy)
- Check script loads before `index.js`
- Inspect Network tab for 404 error

---

### Problem: Deployment succeeded but changes not visible

**Solution:**
- Wait 1-2 minutes for Azure CDN cache
- Clear browser cache or use incognito mode
- Hard refresh: `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)
- Verify file uploaded: Check Azure Portal Storage Browser

---

### Problem: PowerShell execution policy error

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Or run with bypass:
```powershell
powershell -ExecutionPolicy Bypass -File .\deploy-all.ps1
```

---

### Problem: Grid data not loading

**Solution:**
- Check browser console for fetch errors
- Verify data URL in `index.js` is correct
- Test data URL directly in browser
- Check CORS settings on Azure Blob Storage
- Verify JSON file exists and is valid

---

### Problem: Multiple grids appearing

**Solution:**
- Check for duplicate `<script src="./index.js">` tags in HTML
- Clear browser cache completely
- Hard refresh (`Ctrl+Shift+Delete`)

---

## Best Practices

- ? Edit shared code ONLY in `shared-mastercopies/` folder
- ? Always copy master files to apps after editing
- ? Test ALL apps after changing shared framework
- ? Commit master copies and app copies together in same commit
- ? Use descriptive commit messages: `"Update shared framework: [reason]"`
- ? Test locally before deploying to Azure
- ? Keep each app folder self-contained (no dependencies outside folder)
- ? Use relative paths (`./file.css`) for same-folder assets
- ? Document shared framework changes in `CHANGELOG.md`
- ? Deploy all apps when shared framework changes

---

## Technical Details

### Shared Framework Architecture

`base-grid.js` exports a single global object:

```javascript
window.ZsunGridFramework = {
    GridManager: class GridManager { ... }
}
```

**GridManager encapsulates:**
- Column definition processing
- Clipboard operations (Ctrl+C, double-click)
- Error handling with retry UI
- Data loading with fallback
- Filter input binding
- Grid initialization and lifecycle

Apps provide only configuration objects.

---

### CSS Cascade Order

1. AG Grid CSS (from CDN)
2. AG Grid Theme CSS (from CDN)
3. `base-grid.css` (shared styles - loaded in `<head>`)
4. `index.css` (app-specific overrides - loaded in `<head>`)

App-specific styles override shared styles due to cascade order.

---

### Relative Path Resolution

Using `./` prefix ensures paths work in both environments:

```html
<script src="./base-grid.js"></script>
```

**Local:**
```
file:///C:/.../membership/index.html
? ./base-grid.js resolves to same folder
```

**Azure:**
```
https://customerzsun.blob.core.windows.net/$web/membership/
? ./base-grid.js resolves to same folder
```

**Result:** No file editing required for deployment.

---

### Azure Static Website Behavior

Azure Blob Storage `$web` container serves `index.html` automatically:

```
Request: /$web/membership/
Serves:  /$web/membership/index.html
```

Native Azure behavior - no configuration needed.

---

### AG Grid Version

**Current version:** 29.3.4 (loaded from CDN)

If upgrading, update references in all app HTML files:
- `ag-grid.css`
- `ag-theme-alpine.css`
- `ag-grid-community.min.js`

---

### PowerShell vs CMD Syntax

| Feature | PowerShell | CMD |
|---------|------------|-----|
| **Line continuation** | `` ` `` (backtick) | `^` (caret) |
| **Quoting $web** | `'$web/app'` (single quotes) | `"$web/app"` (double quotes) |
| **Variables** | `$variable = "value"` | `set variable=value` |

---

## Related Resources

- **AG Grid Documentation:**  
  [https://www.ag-grid.com/javascript-data-grid/](https://www.ag-grid.com/javascript-data-grid/)

- **Azure Blob Storage Static Websites:**  
  [https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-static-website](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-static-website)

- **Azure CLI Reference:**  
  [https://learn.microsoft.com/en-us/cli/azure/storage/blob](https://learn.microsoft.com/en-us/cli/azure/storage/blob)

- **PowerShell Documentation:**  
  [https://learn.microsoft.com/en-us/powershell/](https://learn.microsoft.com/en-us/powershell/)

- **Project Repository:**  
  [https://github.com/jghughes/Zwift-Solution-2025](https://github.com/jghughes/Zwift-Solution-2025)

---

## Support

For questions or issues:

1. Check browser console (F12) for JavaScript errors
2. Review troubleshooting section above
3. Check `CHANGELOG.md` for recent changes
4. Verify shared files are copied to app folders
5. **Contact:** John Hughes (project maintainer)

---

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and maintenance log.

**Current Version:** 2.0 (Shared Framework Architecture)

---

**End of Document**
