# Code Audit Skill - Quick Start Guide

## ⚡ 3-Minute Setup

### Step 1: Generate Files (1 minute)
```bash
cd /Users/mckenzie/Documents/event2table
python3 run_audit_setup.py
```

### Step 2: Run Tests (1 minute)
```bash
pytest test/unit/backend_tests/skills/test_code_audit.py -v
```

### Step 3: Use the Skill (1 second)
```bash
/code-audit
```

---

## 📁 What You Have

### Created Files (Immediate) ✅
- `run_audit_setup.py` - Setup script (1,100+ lines)
- `test/unit/backend_tests/skills/test_code_audit.py` - Test suite (350+ lines)
- `CODE_AUDIT_COMPLETE.md` - User guide (600+ lines)
- `CODE_AUDIT_IMPLEMENTATION_STATUS.md` - Technical docs (800+ lines)
- `DELIVERABLES.md` - Deliverables summary (500+ lines)

### Generated Files (After Setup) ⏳
- 35+ Python modules
- 3 git hooks
- 3 documentation files
- 20+ __init__.py files

---

## 🎯 What It Does

### Critical Checks
- ✅ Enforces `game_gid` usage (NOT `game_id`)
- ✅ Detects SQL injection vulnerabilities
- ✅ Detects XSS vulnerabilities
- ✅ Validates API contracts
- ✅ Checks TDD compliance

### Quality Checks
- ✅ Measures cyclomatic complexity
- ✅ Detects code duplication
- ✅ Analyzes test coverage

---

## 🔥 Most Important Rule

### game_gid vs game_id

**❌ WRONG**:
```python
# Using game_id for data association
events = fetch_all('SELECT * FROM events WHERE game_id = ?', (game_id,))
```

**✅ CORRECT**:
```python
# Using game_gid for data association
events = fetch_all('SELECT * FROM events WHERE game_gid = ?', (game_gid,))
```

**Why?**
- `game_id` (1, 2, 3) is database auto-increment - ONLY for games table primary key
- `game_gid` (10000147) is business GID - for ALL data associations

---

## 📊 Reports Generated

After running `/code-audit`, you'll find:
```
.claude/skills/code-audit/output/reports/
├── audit_report.md     # Human-readable
├── audit_report.json   # Machine-readable
└── trends/             # Historical data
```

---

## 🪝 Git Hooks (Optional)

Install automated checks:
```bash
# Pre-commit: Quick audit (~1 min)
# Pre-push: Full audit (~3 min)
python3 scripts/setup/setup_code_audit_hooks.py
```

---

## 🆘 Need Help?

### Quick Links
- **User Guide**: `CODE_AUDIT_COMPLETE.md`
- **Technical Docs**: `CODE_AUDIT_IMPLEMENTATION_STATUS.md`
- **Deliverables**: `DELIVERABLES.md`

### Common Issues

**Problem**: Tests fail with ImportError
**Solution**: Files not generated yet - run Step 1

**Problem**: Permission denied on git hooks
**Solution**: Run `chmod +x .claude/skills/code-audit/hooks/*.sh`

**Problem**: IndentationError in game_gid_check.py
**Solution**: Already fixed in setup script (line 519)

---

## ✅ Success Checklist

After setup, you should have:
- [ ] 35+ Python files in `.claude/skills/code-audit/`
- [ ] All tests pass (`pytest` returns 0)
- [ ] `/code-audit` command works
- [ ] Reports generated in `output/reports/`
- [ ] (Optional) Git hooks installed

---

## 🎉 You're Ready!

Run the setup script and start auditing your code!

```bash
python3 run_audit_setup.py
```

**Generated with ❤️ following TDD principles**
