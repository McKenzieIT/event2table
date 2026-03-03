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

### 4. V2 Architecture Analysis 🆕
**File**: [HQL_V2_INDEPENDENCE_ANALYSIS.md](./HQL_V2_INDEPENDENCE_ANALYSIS.md)

**For**: Architects and developers understanding V2 architecture

**Contents**:
- V2 vs V1 feature comparison
- Adapter pattern design
- Project dependency analysis
- Independence evaluation
- Migration strategy

**Read this if**: You want to understand V2 architecture decisions and the adapter pattern.

---

### 5. V2 Migration Roadmap 🆕
**File**: [HQL_V2_MIGRATION_ROADMAP.md](./HQL_V2_MIGRATION_ROADMAP.md)

**For**: Developers planning V2 migration

**Contents**:
- Migration phases
- Adapter pattern implementation
- API compatibility strategy
- Testing and validation
- Rollback plan

**Read this if**: You're involved in V1 to V2 migration.

---

### 6. DML Generator Quick Reference 🆕
**File**: [dml-generator-quick-reference.md](./dml-generator-quick-reference.md)

**For**: Developers using DML generation features

**Contents**:
- INSERT OVERWRITE generation
- DDL statement generation
- Canvas HQL composition
- Code examples
- Best practices

**Read this if**: You need to generate INSERT OVERWRITE or CREATE TABLE statements.

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
- **V2 Generator**: `backend/services/hql/core/generator.py`
- **DML Generator**: `backend/services/hql/core/dml_generator.py` 🆕
- **DDL Generator**: `backend/services/hql/core/ddl_generator.py` 🆕
- **V1→V2 Transformer**: `backend/services/hql/adapters/v1_to_v2_transformer.py` 🆕
- **V2→V1 Transformer**: `backend/services/hql/adapters/v2_to_v1_transformer.py` 🆕
- **Models**: `backend/services/hql/models/event.py`
- **Builders**: `backend/services/hql/builders/`

### API Endpoints
- **V2 API**: `backend/api/routes/hql_preview_v2.py`
- **V1 Adapter API**: `backend/api/routes/v1_adapter.py` 🆕

### Frontend Components
- **Canvas**: `frontend/src/features/canvas/`
- **Event Builder**: `frontend/src/event-builder/`

---

## Version History

### v2.1 (2026-02-18) 🆕
- Added V1/V2 API adapter pattern
- Added DML/DDL generators
- Added V2 architecture analysis documentation
- Added migration roadmap
- Event node builder fixes (6 issues)

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

**Last Updated**: 2026-02-18
**Status**: ✅ Production Ready
**Version**: 2.1
