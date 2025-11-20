# Bug: Terminal Window Opens on Application Launch

**Status**: ✅ **RESOLVED** (2025-11-20)

## Summary
When the application is launched via the `.exe`, a terminal/console window opens alongside the system tray icon. This is unwanted for most users but helpful for debugging.

## Original Behavior
- Running `LMU_Telemetry_Logger.exe` opens a console window
- Console shows debug output (INFO, ERROR messages)
- Window remains open until application exits
- Users see console output by default

## Desired Behavior
- Application should run silently in system tray without console window (default)
- Console output should be optional for debugging purposes
- Add a "Show Terminal Window" option in system tray menu or settings dialog

## Root Cause
The PyInstaller build script (`build.bat`) does not include the `--noconsole` flag:

```batch
pyinstaller --onedir ^
    --name "LMU_Telemetry_Logger" ^
    --icon=NONE ^
    --add-data "src;src" ^
    --hidden-import psutil ^
    --hidden-import datetime ^
    --hidden-import pystray ^
    --hidden-import PIL ^
    --collect-all src ^
    tray_app.py
```

## Proposed Solution

### Option 1: Build Two Executables
Build two versions:
- `LMU_Telemetry_Logger.exe` - no console (default for users)
- `LMU_Telemetry_Logger_Debug.exe` - with console (for debugging)

Modify `build.bat`:
```batch
# Production build (no console)
pyinstaller --onedir --noconsole ^
    --name "LMU_Telemetry_Logger" ^
    ...

# Debug build (with console)
pyinstaller --onedir ^
    --name "LMU_Telemetry_Logger_Debug" ^
    ...
```

### Option 2: Single Executable with Runtime Toggle
Build without console, but add menu option to:
- Write logs to a file (always enabled)
- "Open Log File" menu item in system tray
- Optional: "Show Logs in Notepad" to view real-time logs

### Option 3: Settings Dialog Option
Add a checkbox in Settings UI:
- ☐ Show debug console window (requires restart)
- Save preference to `config.json`
- Launcher script checks setting and launches appropriate exe variant

## Recommendation
**Option 2** is most user-friendly:
1. Build with `--noconsole` flag
2. Log all output to `telemetry_logger.log` in app directory
3. Add "Open Log File" menu item to system tray
4. Keeps single executable, reduces distribution complexity

## Files to Modify
- `build.bat` - Add `--noconsole` flag
- `tray_app.py` - Add logging to file
- `src/tray_ui.py` - Add "Open Log File" menu item

## Solution Implemented

Implemented **Option 2** (recommended solution):

### Changes Made

1. **build.bat** - Added `--noconsole` flag to PyInstaller
   - Line 18: `pyinstaller --onedir --noconsole ^`
   - Prevents console window from appearing when running .exe

2. **tray_app.py** - Added file logging system
   - New `setup_logging()` function configures Python logging module
   - Logs written to `telemetry_logger.log` in application directory
   - Format: `YYYY-MM-DD HH:MM:SS [LEVEL] message`
   - Replaced all `print()` statements with `logger.info()` / `logger.error()` calls
   - Console output only shown when running as script (development mode)
   - When running as .exe, output only goes to log file

3. **src/tray_ui.py** - Added "Open Log File" menu item
   - New menu item after "Open Output Folder"
   - `on_open_log_file()` handler opens log in default text editor
   - Cross-platform support: Windows (startfile), macOS (open), Linux (xdg-open)
   - Silently handles case where log file doesn't exist yet

### Benefits
- ✅ No console window for end users
- ✅ All debug output captured in log file
- ✅ Easy access to logs via system tray menu
- ✅ Single executable (no separate debug build needed)
- ✅ Developers still see console output when running as script

## Testing
- [x] Added `--noconsole` flag to build script
- [x] Implemented file logging system
- [x] Added "Open Log File" menu item
- [x] Code compiles without syntax errors
- [ ] Build with `--noconsole` flag (requires Windows)
- [ ] Launch exe, verify no console appears (requires Windows)
- [ ] Verify logs are written to file (requires Windows)
- [ ] Test "Open Log File" menu item opens log in default text editor (requires Windows)
- [ ] Verify all debug output is captured in log file (requires Windows)

## Priority
**Medium** - Cosmetic issue but affects user experience. Most users don't need console output.

## Related Files (Modified)
- `/home/user/eztel-writer/build.bat:18` - PyInstaller command (added --noconsole flag)
- `/home/user/eztel-writer/tray_app.py:40-76` - Logging setup (new setup_logging() function)
- `/home/user/eztel-writer/tray_app.py` - Replaced all print() with logger calls
- `/home/user/eztel-writer/src/tray_ui.py:86` - Added "Open Log File" menu item
- `/home/user/eztel-writer/src/tray_ui.py:176-206` - Added on_open_log_file() handler
