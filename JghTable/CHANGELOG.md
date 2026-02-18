# ZSUN Club Web Apps - Changelog

All notable changes to the ZSUN web applications will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2.0.0] - 2026-02-18

### Added - Shared Framework Architecture
- Created `shared-mastercopies/` folder for master-copy pattern
- Added `base-grid.js` - shared AG Grid framework (~230 lines)
  - `ZsunGridFramework.GridManager` class for grid lifecycle management
  - Centralized clipboard operations (Ctrl+C, double-click to copy)
  - Unified error handling with retry UI
  - Shared data loading logic with fallback support
  - Common utility functions (escapeHtml, generateColumnDefs)
- Added `base-grid.css` - shared Excel-style AG Grid layouts
  - Calibri 11pt font (15px) matching Excel
  - Copyable cell focus styles
  - Error overlay styling
  - Responsive and print media queries
- Created sync-shared-files.ps1 for automated copying

### Changed - Code Architecture
- Refactored `membership/index.js` from 270 lines ? 50 lines (81% reduction)
- Refactored `olympics/index.js` from 250 lines ? 50 lines (80% reduction)
- App files now contain only configuration, not boilerplate logic
- Updated HTML files to load base-grid.js before index.js

### Deployment Architecture
- Master-copy approach: develop in shared-mastercopies/, copy to apps
- Maintains Azure Blob Storage compatibility (no build tools required)
- Each app folder remains self-contained for independent deployment

### Benefits
- Single source of truth for common code
- Bug fixes propagate to all apps via copy step
- ~75% reduction in app-specific JavaScript
- Easier maintenance and testing

---

## [1.0.0] - 2026-02-17

### Added - Initial Release
- Created `membership/` app for rider statistics
  - AG Grid displaying cycling power data
  - Columns: name, flag, zFTP, 60min power, racing score, categories
  - Quick filter search
  - Excel-style Calibri font
- Created `olympics/` app for ZRL race results
  - AG Grid displaying race leaderboard
  - Columns: name, flag, position, time, route, gender, league, division, team
  - Quick filter search
- Implemented copyable cell functionality
  - Double-click to copy cell value
  - Ctrl+C (Cmd+C) keyboard shortcut
  - Focus styling for active cells
- Error handling with user-friendly overlays
  - HTTP error code translation (401, 403, 404, 500)
  - Retry button functionality
  - Fallback data display on error
- Responsive design with media queries
- Print-friendly styling

### Documentation
- Created comprehensive README.txt
  - Local development instructions (http-server)
  - Azure deployment commands (PowerShell and CMD)
  - Troubleshooting guide
  - Technical architecture details
- Created DEPLOYMENT-README.txt (later merged into README.txt)
- Added 404.html error pages for both apps

### Infrastructure
- Azure Blob Storage static website hosting
  - Account: customerzsun
  - Container: $web
  - URLs: /$web/membership/ and /$web/olympics/
- Data sources in separate 'preprocessed' container
  - rider_stats_dto_as_list.json (membership data)
  - wtrl-zrl-2025-26-round3race6-leaderboard-club.json (olympics data)

### Refactoring
- Externalized CSS from inline styles to index.css files
- Renamed olympics_init.js to index.js for consistency
- Removed complex log viewer (simplified error handling)
- Reduced JavaScript code by ~40% through cleanup

---

## Technical Architecture Notes

### File Structure Evolution

**Version 1.0:**