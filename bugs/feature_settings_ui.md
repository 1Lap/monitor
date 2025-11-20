# Feature: Settings/Configuration UI

**Status**: ✅ IMPLEMENTED
**Priority**: Low-Medium
**Category**: User Interface
**Related Phase**: Phase 5 (System Tray UI & User Controls)
**Implemented**: 2025-11-20

---

## Description

Add a graphical settings dialog to configure the telemetry logger without editing code or config files.

**Current**: Configuration requires editing code in `example_app.py` or config files
**Desired**: Simple GUI dialog for configuring common settings

## User Story

As a user, I want a settings dialog so that:
- I can change the output directory without editing code
- I can enable/disable opponent tracking
- I can configure auto-start behavior
- I can customize file naming format
- I don't need to be a programmer to configure the app

## Requirements

### Must Have

1. **Output Directory Selection**
   - File browser to select output directory
   - Default: `./telemetry_output`
   - User preference: `~/Documents/eztel/my_laps/` or custom path
   - Validate directory exists or can be created

2. **Basic Settings**
   - Enable/disable opponent tracking (checkbox)
   - Enable/disable AI opponent tracking (checkbox)
   - Target process name (text input, for advanced users)
   - Poll interval (Hz) - dropdown: 50, 100, 200 Hz

3. **Save/Cancel Buttons**
   - "Save" - write settings to config file and apply
   - "Cancel" - discard changes and close dialog
   - "Restore Defaults" - reset to default values

4. **Settings Persistence**
   - Save settings to `config.json` file
   - Load settings on app startup
   - Apply settings to TelemetryLoop and FileManager

### Nice to Have

1. **File Naming Format**
   - Template editor for filename format
   - Preview of generated filename
   - Variables: `{date}`, `{time}`, `{track}`, `{car}`, `{driver}`, `{lap}`, `{lap_time}`

2. **Auto-Start with Windows**
   - Checkbox: "Start with Windows"
   - Add/remove registry entry or startup shortcut

3. **Logging Options**
   - Minimum lap time filter (seconds) - to skip out-laps
   - Minimum samples per lap - quality filter
   - Auto-delete old laps (checkbox + days threshold)

4. **UI Theme**
   - Light/Dark mode (if supported by UI library)

5. **Validation**
   - Real-time validation of input fields
   - Show error messages for invalid values
   - Disable "Save" button if validation fails

## Current Implementation Status

### Already Implemented (Backend)

✅ **FileManager supports custom output directory**:
```python
file_manager = FileManager({'output_dir': './custom/path'})
```

✅ **TelemetryLoop supports configuration**:
```python
telemetry_loop = TelemetryLoop({
    'target_process': 'Le Mans Ultimate',
    'poll_interval': 0.01,  # 100Hz
    'track_opponents': True,
    'track_opponent_ai': False,
})
```

✅ **FileManager supports custom filename format**:
```python
file_manager = FileManager({
    'filename_format': '{session_id}_{track}_{driver}_lap{lap}.csv'
})
```

### Missing (Frontend)

❌ **No GUI for editing these settings**
❌ **No settings persistence (config.json)**
❌ **No settings validation UI**
❌ **No settings loading on startup**

## Technical Implementation

### UI Library Options

**Option 1: tkinter** (Recommended)
- ✅ Built into Python (no extra dependencies)
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Simple for basic dialogs
- ❌ Looks dated on modern Windows

**Option 2: PyQt5/PySide6**
- ✅ Modern, native-looking UI
- ✅ Excellent theming support
- ❌ Large dependency (~50MB)
- ❌ License complexity (LGPL for PySide6)

**Option 3: wxPython**
- ✅ Native look and feel
- ✅ Good documentation
- ❌ Large dependency
- ❌ Less popular than PyQt

**Recommendation**: Start with **tkinter** for MVP, consider PyQt5 later if needed.

### Architecture

```python
# New file: src/settings_ui.py

import tkinter as tk
from tkinter import filedialog, messagebox
import json
from pathlib import Path

class SettingsDialog:
    """Settings dialog for telemetry logger configuration"""

    DEFAULT_CONFIG = {
        'output_dir': './telemetry_output',
        'target_process': 'Le Mans Ultimate',
        'poll_interval': 0.01,  # 100Hz
        'track_opponents': True,
        'track_opponent_ai': False,
        'filename_format': '{date}_{time}_{track}_{car}_{driver}_lap{lap}_t{lap_time}s.csv',
        'min_lap_time': 30.0,
        'min_samples': 10,
    }

    def __init__(self, parent=None, config_file='config.json'):
        self.config_file = Path(config_file)
        self.config = self.load_config()
        self.root = tk.Tk() if parent is None else tk.Toplevel(parent)
        self.root.title("Telemetry Logger Settings")
        self._build_ui()

    def _build_ui(self):
        """Build settings dialog UI"""
        # Output directory section
        # Opponent tracking section
        # Advanced settings section
        # Save/Cancel buttons

    def load_config(self):
        """Load settings from config.json"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return {**self.DEFAULT_CONFIG, **json.load(f)}
        return self.DEFAULT_CONFIG.copy()

    def save_config(self):
        """Save settings to config.json"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def on_browse_output_dir(self):
        """Open file browser for output directory"""
        dir_path = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.config['output_dir']
        )
        if dir_path:
            self.config['output_dir'] = dir_path
            # Update UI label

    def on_save(self):
        """Save settings and close dialog"""
        # Validate inputs
        # Save to config.json
        # Close dialog
        # Return True (settings changed)

    def on_cancel(self):
        """Close dialog without saving"""
        # Close dialog
        # Return False (no changes)

    def on_restore_defaults(self):
        """Restore default settings"""
        # Reset config to defaults
        # Update UI fields
```

### Integration with Main App

```python
# In example_app.py or tray_app.py

class TelemetryApp:
    def __init__(self):
        # Load config from file
        self.config = self.load_config()

        # Initialize components with config
        self.file_manager = FileManager({
            'output_dir': self.config['output_dir'],
            'filename_format': self.config.get('filename_format')
        })

        self.telemetry_loop = TelemetryLoop({
            'target_process': self.config['target_process'],
            'poll_interval': self.config['poll_interval'],
            'track_opponents': self.config['track_opponents'],
            'track_opponent_ai': self.config['track_opponent_ai'],
            # ... callbacks ...
        })

    def load_config(self):
        """Load configuration from config.json"""
        from src.settings_ui import SettingsDialog
        return SettingsDialog.load_config_static('config.json')

    def show_settings(self):
        """Show settings dialog"""
        from src.settings_ui import SettingsDialog
        dialog = SettingsDialog(config_file='config.json')
        if dialog.show():  # Returns True if saved
            # Reload config and restart components
            self.reload_config()
```

### Config File Format (config.json)

```json
{
  "output_dir": "./telemetry_output",
  "target_process": "Le Mans Ultimate",
  "poll_interval": 0.01,
  "track_opponents": true,
  "track_opponent_ai": false,
  "filename_format": "{date}_{time}_{track}_{car}_{driver}_lap{lap}_t{lap_time}s.csv",
  "min_lap_time": 30.0,
  "min_samples": 10,
  "auto_start": false
}
```

## Testing Requirements

### Manual Testing

1. **Open Settings Dialog**:
   - Verify dialog opens without errors
   - Verify all fields populated with current values

2. **Change Output Directory**:
   - Click "Browse" button
   - Select new directory
   - Click "Save"
   - Verify config.json updated
   - Verify new laps saved to new directory

3. **Toggle Opponent Tracking**:
   - Disable opponent tracking
   - Click "Save"
   - Verify opponent laps not saved

4. **Restore Defaults**:
   - Change several settings
   - Click "Restore Defaults"
   - Verify all fields reset to defaults

5. **Cancel**:
   - Change settings
   - Click "Cancel"
   - Verify config.json unchanged

### Automated Testing

```python
# tests/test_settings_ui.py

def test_load_config_creates_default_if_missing():
    """Test config loading when file doesn't exist"""

def test_save_config_writes_json_file():
    """Test config saving"""

def test_validate_output_directory():
    """Test directory validation"""

def test_restore_defaults():
    """Test restoring default values"""
```

## Dependencies

### Required

- **tkinter**: Built into Python (no install needed)
- **json**: Built into Python (no install needed)

### Optional (for better UI)

- **ttkthemes**: Modern tkinter themes
  ```
  pip install ttkthemes
  ```

## Files to Create

- `src/settings_ui.py` - Settings dialog class
- `config.json` - User settings file (created on first save)
- `tests/test_settings_ui.py` - Unit tests for settings dialog

## Files to Modify

- `example_app.py` (or `tray_app.py`) - Load config on startup, add "Settings" menu/button
- `requirements.txt` - Add `ttkthemes` (optional)

## Implementation Steps

1. **Create SettingsDialog class** (3-4 hours)
   - Basic tkinter dialog with fields
   - Load/save config.json
   - Input validation

2. **Add file browser for output directory** (1 hour)
   - tkinter.filedialog.askdirectory()
   - Update label with selected path

3. **Add all settings fields** (2-3 hours)
   - Opponent tracking checkboxes
   - Poll interval dropdown
   - Target process text input
   - Min lap time/samples inputs

4. **Integrate with main app** (2-3 hours)
   - Load config on app startup
   - Add "Settings" menu item (if using system tray)
   - Reload components when settings change

5. **Test and polish** (2-3 hours)
   - Test all fields
   - Add input validation
   - Write unit tests
   - Handle edge cases

## Acceptance Criteria

- [ ] Settings dialog opens without errors
- [ ] All configuration options are editable
- [ ] "Browse" button opens file browser for output directory
- [ ] "Save" button writes config.json and applies settings
- [ ] "Cancel" button discards changes
- [ ] "Restore Defaults" button resets all fields
- [ ] Settings persist across app restarts
- [ ] Invalid inputs are validated and show error messages
- [ ] App loads config.json on startup if it exists
- [ ] All existing functionality still works after changing settings

## Notes

- **Independent of System Tray**: This feature can work standalone (open settings dialog from command-line) or integrated with system tray ("Settings..." menu item)
- **Backward Compatible**: If config.json doesn't exist, use default values
- **Hot Reload** (Future): Could support applying settings without restarting app, but initial implementation can require restart
- **Security**: Validate all user inputs (directory paths, numeric values, etc.)

## Related Issues

- `feature_system_tray.md` - System tray can add "Settings..." menu item
- `feature_auto_update.md` - Settings could include auto-update preferences
- Phase 5 in `CLAUDE.md` - This is one component of Phase 5

---

## Implementation Summary

**Date**: 2025-11-20

### What Was Implemented

✅ **All Must-Have Features**:
- Output directory selection with file browser
- Enable/disable opponent tracking (checkbox)
- Enable/disable AI opponent tracking (checkbox)
- Target process name (text input)
- Poll interval selection (50, 100, 200 Hz radio buttons)
- Save/Cancel/Restore Defaults buttons
- Settings persistence (config.json)

### Files Created

1. **`src/settings_ui.py`** - Settings UI implementation
   - `SettingsConfig` class - Backend configuration management (load/save/validate)
   - `SettingsDialog` class - tkinter GUI dialog
   - `show_settings_dialog()` - Convenience function

2. **`tests/test_settings_ui.py`** - Comprehensive test suite
   - 13 tests covering all configuration logic
   - TDD approach (tests written first)
   - Tests for load, save, validate, defaults, conversions

### Files Modified

1. **`example_app.py`** - Integration with main app
   - Added `--settings` command line flag
   - Added `--config` flag for custom config file path
   - Loads configuration from `config.json` on startup
   - Falls back to defaults if config doesn't exist

### Usage

```bash
# Run with saved settings
python example_app.py

# Open settings dialog first
python example_app.py --settings

# Use custom config file
python example_app.py --config my_config.json
```

### Test Results

All 106 tests pass, including 13 new settings UI tests:
- ✅ Config load/save/validate
- ✅ Default values and merging
- ✅ Hz/interval conversions
- ✅ Directory validation
- ✅ No breaking changes to existing functionality

### Technical Decisions

1. **UI Library**: tkinter (built-in, cross-platform, no extra dependencies)
2. **Architecture**: Separated `SettingsConfig` (backend) from `SettingsDialog` (GUI)
   - Enables testing without GUI
   - Clean separation of concerns
3. **Config Format**: JSON (human-readable, standard format)
4. **Integration**: Command-line flag approach for standalone app
   - Can be integrated with system tray later (future work)

### Known Limitations

- GUI testing not automated (manual testing required on each platform)
- Nice-to-have features not yet implemented:
  - File naming format template editor
  - Auto-start with Windows
  - Logging filters (min lap time, min samples)
  - UI theme selection

### Future Work

- Integrate with system tray menu (when Phase 5 system tray is implemented)
- Add nice-to-have features based on user feedback
- Consider hot-reload (apply settings without restart)
