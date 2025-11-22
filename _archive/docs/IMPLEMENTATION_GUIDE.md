# Implementation Guide for LMU Telemetry Logger

This folder contains all planning and specification documents for implementing the LMU Telemetry Logger.

---

## 📄 Document Overview

### 1. **TELEMETRY_LOGGER_PLAN.md** (High-Level Roadmap)
**Purpose**: Big picture overview of the project
**Audience**: Everyone (developers, project managers, stakeholders)
**Contains**:
- Project overview and goals
- Architecture and components
- Cross-platform development strategy
- Phase-by-phase plan
- Timeline (4-6 days)
- Technology stack
- Resources and links

**When to read**: Start here to understand what we're building and why

---

### 2. **TECHNICAL_SPEC.md** (Detailed Implementation Guide)
**Purpose**: Detailed specifications for implementation
**Audience**: Developers building the application
**Contains**:
- Component specifications (classes, methods, parameters)
- Complete data schemas (telemetry dict, CSV format)
- API contracts and interfaces
- Configuration file schema
- Error handling specifications
- Performance requirements
- Testing requirements
- Phase acceptance criteria

**When to read**: When you're ready to write code and need exact specifications

---

### 3. **GITHUB_ISSUES.md** (Task Breakdown)
**Purpose**: Ready-to-use GitHub issues for project tracking
**Audience**: Project managers, developers
**Contains**:
- 13 detailed issues (one per major task)
- Task checklists for each issue
- Acceptance criteria per issue
- Time estimates
- Labels for organization

**When to read**: When setting up project tracking in GitHub

---

### 4. **example.csv** (Reference Output)
**Purpose**: Example of expected CSV output format
**Audience**: Developers implementing CSV formatter
**Contains**:
- Actual telemetry data from LMU
- All 6 sections of CSV format
- Field formatting examples

**When to read**: When implementing CSV formatter (Phase 3)

---

## 🚀 Getting Started

### For Project Managers

1. **Read**: `TELEMETRY_LOGGER_PLAN.md` (30 minutes)
   - Understand scope and timeline
   - Review technology decisions

2. **Create GitHub Issues**: Use `GITHUB_ISSUES.md`
   - Copy each issue into GitHub
   - Set up GitHub Project board
   - Assign issues to developers

3. **Track Progress**: Use phase acceptance criteria
   - From `TECHNICAL_SPEC.md`
   - Mark phases complete when criteria met

### For Developers

1. **Read**: `TELEMETRY_LOGGER_PLAN.md` (30 minutes)
   - Understand overall architecture
   - Review cross-platform strategy

2. **Deep Dive**: `TECHNICAL_SPEC.md` (1-2 hours)
   - Study component specifications
   - Review data schemas
   - Understand acceptance criteria

3. **Start Coding**:
   - Follow phases in order (1 → 7)
   - Reference `TECHNICAL_SPEC.md` for details
   - Use `example.csv` for CSV formatter
   - Check acceptance criteria before moving to next phase

4. **Track Work**: GitHub issues
   - Pick issue from backlog
   - Follow task checklist
   - Meet acceptance criteria
   - Close issue when done

---

## 📋 Development Workflow

### Phase 1-4: macOS Development (Days 1-4)

```bash
# Day 1: Setup
git clone <repo>
cd lmu-telemetry-logger
python -m venv venv
source venv/bin/activate  # macOS
pip install -r requirements.txt

# Follow Phase 1 from TECHNICAL_SPEC.md
# Build mock telemetry system
# Reference GITHUB_ISSUES.md #1

# Day 2-4: Core development
# Follow TECHNICAL_SPEC.md phases 2-5
# All development happens on macOS with mocks
# Reference GITHUB_ISSUES.md #2-7
```

### Phase 5-6: Windows Testing (Days 5-6)

```bash
# Day 5: Windows setup and live testing
# On Windows machine:
git clone <repo>
cd lmu-telemetry-logger
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements-windows.txt

# Enable LMU plugin
# Follow Phase 7 from TECHNICAL_SPEC.md
# Reference GITHUB_ISSUES.md #9-10

# Day 6: Build and release
# Follow PyInstaller build steps
# Reference GITHUB_ISSUES.md #11-13
```

---

## ✅ Quality Checklist

Before moving to next phase, verify:

- [ ] All tasks in GitHub issue completed
- [ ] Acceptance criteria met (from TECHNICAL_SPEC.md)
- [ ] Unit tests written and passing
- [ ] Code reviewed (if team)
- [ ] Performance targets met (if applicable)
- [ ] Documentation updated

---

## 📊 Progress Tracking

### Recommended GitHub Project Setup

**Columns**:
1. 📋 Backlog - All issues
2. 🏗️ In Progress - Currently working on
3. 👀 Review - Code review needed
4. ✅ Done - Meets acceptance criteria

**Labels**:
- `phase-1` through `phase-7` - Phase tracking
- `setup`, `core`, `formatter`, `ui`, `testing`, `windows`, `packaging` - Component
- `bug`, `enhancement`, `documentation` - Type
- `cross-platform` or `windows-only` - Platform

---

## 🎯 Success Criteria

**Project is complete when**:

From `TECHNICAL_SPEC.md`:
1. ✅ All 13 GitHub issues closed
2. ✅ All phase acceptance criteria met
3. ✅ Unit test coverage ≥ 80%
4. ✅ All integration tests pass
5. ✅ Live testing on Windows (3+ sessions)
6. ✅ Performance requirements met
7. ✅ .exe builds and runs on clean Windows
8. ✅ Documentation complete
9. ✅ GitHub release published
10. ✅ Zero critical bugs

---

## 🔧 Key Implementation Notes

### Cross-Platform Development

**On macOS (Days 1-4)**:
- Use `MockTelemetryReader`
- Test with Chrome/VS Code for process detection
- System tray appears in menu bar
- All code and tests work without Windows

**On Windows (Days 5-6)**:
- Switch to `RealTelemetryReader`
- Test with actual LMU game
- Build .exe with PyInstaller
- System tray appears in taskbar

### Data Flow

```
LMU Game
  ↓
rF2SharedMemoryMapPlugin (already installed)
  ↓
pyRfactor2SharedMemory (Windows) / MockTelemetryReader (macOS)
  ↓
TelemetryReader (our abstraction)
  ↓
SessionManager (detects laps, buffers samples)
  ↓
CSVFormatter (formats to CSV)
  ↓
FileManager (writes to disk)
```

### Critical Files

**Reference constantly**:
- `TECHNICAL_SPEC.md` - Component specs and data schemas
- `example.csv` - CSV format reference

**Update as you go**:
- `README.md` - User-facing documentation
- Unit tests - Maintain 80%+ coverage

---

## 📞 Questions?

**Architecture questions**: See `TELEMETRY_LOGGER_PLAN.md`
**Implementation details**: See `TECHNICAL_SPEC.md`
**Task breakdown**: See `GITHUB_ISSUES.md`
**CSV format**: See `example.csv`

**Not covered?**: Create GitHub issue with question label

---

## 🎉 Milestones

- **Milestone 1**: Phase 1-2 complete (macOS setup + core logger)
- **Milestone 2**: Phase 3-4 complete (CSV formatter + file management)
- **Milestone 3**: Phase 5 complete (System tray UI working on macOS)
- **Milestone 4**: Phase 6 complete (All tests passing)
- **Milestone 5**: Phase 7.1-7.2 complete (Windows integration + live testing)
- **Milestone 6**: v1.0 Release (Build, package, document, release)

---

## 📈 Estimated Timeline

Based on `TELEMETRY_LOGGER_PLAN.md`:

| Days | Platform | Work |
|------|----------|------|
| 1 | macOS | Setup, mock system, research |
| 2 | macOS | Core logger, session manager |
| 3 | macOS | CSV formatter |
| 4 | macOS | File manager, system tray UI |
| 5 | Windows | Setup, integration, live testing |
| 6 | Windows | Build .exe, documentation, release |

**Total**: 4-6 working days (48-57 hours)

---

**Good luck building! 🚀**
