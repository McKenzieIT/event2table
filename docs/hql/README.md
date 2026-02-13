# HQL Generator Documentation

This directory contains comprehensive documentation for the HQL Generator in the event2table project.

## Documentation Files

### 1. Quick Reference
**File**: [HQL_GENERATOR_QUICK_REFERENCE.md](./HQL_GENERATOR_QUICK_REFERENCE.md)

**For**: Developers who need quick answers

**Contents**:
- TL;DR overview
- Quick start example
- Output format summary
- Three modes (single/join/union)
- Field types reference
- Common use cases
- Troubleshooting tips

**Read this if**: You just want to know how to use the generator quickly.

---

### 2. Complete Documentation
**File**: [HQL_GENERATOR_OUTPUT_FORMAT.md](./HQL_GENERATOR_OUTPUT_FORMAT.md)

**For**: Developers implementing features with the HQL Generator

**Contents**:
- Detailed output format specification
- All modes with examples
- Field type reference
- Event model documentation
- Integration examples (Flask, Canvas)
- Best practices
- Testing guide
- Troubleshooting
- Version history

**Read this if**: You need to implement a feature that uses the HQL Generator.

---

### 3. Investigation Report
**File**: [HQL_GENERATOR_INVESTIGATION_REPORT.md](./HQL_GENERATOR_INVESTIGATION_REPORT.md)

**For**: Developers investigating issues or understanding the design

**Contents**:
- Executive summary
- Investigation findings
- Issues and resolutions
- Code changes made
- Verification results
- Recommendations
- Backwards compatibility notes
- Future enhancements

**Read this if**: You want to understand why the generator works the way it does, or if you're investigating a bug.

---

## Key Concepts

### What is the HQL Generator?

The HQL Generator is a **core SELECT statement generator** that produces reusable HQL queries for data extraction and transformation.

**Key Characteristics**:
- Framework-independent
- Produces SELECT statements (not CREATE VIEW)
- Supports single/join/union modes
- Fully tested and documented

### What Does It Produce?

**Output**: SELECT queries
```sql
SELECT
  `role_id`,
  get_json_object(params, '$.zoneId') AS `zone_id`
FROM ieu_ods.ods_10000147_all_view
WHERE
  ds = '${ds}'
```

**Not**: CREATE VIEW, CREATE TABLE, INSERT OVERWRITE

### Why This Design?

The generator produces **reusable SELECT queries** that can be:
- Used directly in ad-hoc queries
- Wrapped in CREATE VIEW statements
- Used in INSERT OVERWRITE operations
- Embedded in stored procedures

This provides maximum flexibility for different use cases.

---

## Quick Links

### For New Users
1. Start with [Quick Reference](./HQL_GENERATOR_QUICK_REFERENCE.md)
2. Read [Complete Documentation](./HQL_GENERATOR_OUTPUT_FORMAT.md) for details
3. Run [Test Suite](../../test_hql_generator_verification.py) to verify

### For Feature Implementation
1. Read [Complete Documentation](./HQL_GENERATOR_OUTPUT_FORMAT.md)
2. Review integration examples
3. Follow best practices

### For Issue Investigation
1. Read [Investigation Report](./HQL_GENERATOR_INVESTIGATION_REPORT.md)
2. Check [Troubleshooting](./HQL_GENERATOR_OUTPUT_FORMAT.md#troubleshooting)
3. Run [Test Suite](../../test_hql_generator_verification.py)

### For Code Review
1. Review [Investigation Report](./HQL_GENERATOR_INVESTIGATION_REPORT.md#code-changes)
2. Check [Backwards Compatibility](./HQL_GENERATOR_INVESTIGATION_REPORT.md#backwards-compatibility)
3. Verify [Test Results](./HQL_GENERATOR_INVESTIGATION_REPORT.md#verification-results)

---

## Related Files

### Source Code
- **Generator**: `/Users/mckenzie/Documents/event2table/backend/services/hql/core/generator.py`
- **Models**: `/Users/mckenzie/Documents/event2table/backend/services/hql/models/event.py`
- **Builders**: `/Users/mckenzie/Documents/event2table/backend/services/hql/builders/`

### Tests
- **Verification Suite**: `/Users/mckenzie/Documents/event2table/test_hql_generator_verification.py`
- **Functional Tests**: `/Users/mckenzie/Documents/event2table/manual_functional_test.py`

### Integration
- **Flask API**: `/Users/mckenzie/Documents/event2table/backend/api/routes/hql_preview_v2.py`
- **Canvas Component**: `/Users/mckenzie/Documents/event2table/frontend/src/features/canvas/`

---

## Version History

### v2.0 (2025-02-10)
- Added `alias` field to Event model
- Fixed JOIN/UNION mode support
- Complete documentation created
- All tests passing (5/5)

### v1.0
- Initial release
- Basic HQL generation
- Single/join/union modes

---

## Support

### Questions?
- Check [Quick Reference](./HQL_GENERATOR_QUICK_REFERENCE.md) for quick answers
- See [Complete Documentation](./HQL_GENERATOR_OUTPUT_FORMAT.md) for details
- Review [Investigation Report](./HQL_GENERATOR_INVESTIGATION_REPORT.md) for design rationale

### Issues?
- Check [Troubleshooting](./HQL_GENERATOR_OUTPUT_FORMAT.md#troubleshooting)
- Run [Test Suite](../../test_hql_generator_verification.py)
- Review [Investigation Findings](./HQL_GENERATOR_INVESTIGATION_REPORT.md#issues-and-resolutions)

### Contributions?
- Follow [Best Practices](./HQL_GENERATOR_OUTPUT_FORMAT.md#best-practices)
- Review [Future Enhancements](./HQL_GENERATOR_INVESTIGATION_REPORT.md#future-enhancements)
- Ensure [Backwards Compatibility](./HQL_GENERATOR_INVESTIGATION_REPORT.md#backwards-compatibility)

---

**Last Updated**: 2025-02-10
**Status**: ✅ Production Ready
**Version**: 2.0
