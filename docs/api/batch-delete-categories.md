# Batch Delete Categories - Quick Reference

## Endpoint
```
POST /api/categories/batch-delete
```

## Request Format
```json
{
  "category_ids": [1, 2, 3, 4, 5]
}
```

## Response Format
```json
{
  "success": true,
  "message": "Successfully deleted 4 out of 5 categories (1 failed)",
  "data": {
    "deleted_count": 4,
    "failed_ids": [3],
    "failed_reasons": {
      "3": "Category has 5 associated events"
    }
  }
}
```

## Common Scenarios

### 1. Delete All Successfully
```json
Request:  {"category_ids": [1, 2, 3]}
Response: {
  "deleted_count": 3,
  "failed_ids": [],
  "message": "Successfully deleted all 3 categories"
}
```

### 2. Foreign Key Constraint
```json
Request:  {"category_ids": [10]}
Response: {
  "deleted_count": 0,
  "failed_ids": [10],
  "failed_reasons": {"10": "Category has 5 associated events"},
  "message": "Failed to delete any categories (1 errors)"
}
```

### 3. Mixed Results
```json
Request:  {"category_ids": [1, 2, 10, 999]}
Response: {
  "deleted_count": 2,
  "failed_ids": [10, 999],
  "failed_reasons": {
    "10": "Category has 3 associated events",
    "999": "Category not found"
  },
  "message": "Successfully deleted 2 out of 4 categories (2 failed)"
}
```

## Error Codes

| Status | Error | Solution |
|--------|-------|----------|
| 400 | category_ids is required | Include category_ids in request |
| 400 | Too many IDs: 101 > 100 | Limit to 100 IDs per request |
| 400 | All category IDs must be positive integers | Ensure all IDs are > 0 |
| 500 | Failed to delete categories | Server error, check logs |

## Constraints

- ✅ Maximum 100 categories per request
- ✅ All IDs must be positive integers
- ✅ Categories with events cannot be deleted
- ✅ Deleted categories cannot be recovered

## Tips

1. **Check failed_ids**: Always check this array for partial failures
2. **Read failed_reasons**: Contains detailed error messages for each failure
3. **Handle foreign keys**: Delete associated events before deleting categories
4. **Use transactions**: Each batch is atomic (all or nothing per category)
