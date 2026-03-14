
[1m======================================================================[0m
[1m🚀 API Contract Test Suite[0m
[1m======================================================================[0m

[1m🧪 Test 1: GraphQL Enum Consistency[0m
[94mℹ️  Checking FieldTypeEnum consistency...[0m
[92m✅ FieldTypeEnum: Frontend and backend types match perfectly[0m
[94mℹ️  Checking FilterModeEnum consistency...[0m
[92m✅ FilterModeEnum: Frontend and backend modes match perfectly[0m
[94mℹ️  Checking enum hyphen/underscore consistency...[0m
[92m✅ Enum 'non-common' uses hyphen consistently (GraphQL-compliant)[0m
[92m✅ GraphQL Enum Consistency: PASSED[0m

[1m🧪 Test 2: Backend API Endpoints Existence[0m
[94mℹ️  Checking GraphQL schema...[0m
[92m✅ GraphQL schema file found: schema_parameter_management.py[0m
[92m✅ GraphQL Mutation: batch_add_fields_to_canvas[0m
[94mℹ️  Checking GraphQL mutations...[0m
[92m✅ GraphQL mutations directory found[0m
[92m✅ Mutation file: field_builder_mutations.py[0m
[92m✅ Mutation file: event_mutations.py[0m
[92m✅ Mutation file: parameter_mutations.py[0m
[92m✅ Backend API Endpoints: PASSED[0m

[1m🧪 Test 3: Parameter Naming Convention (game_gid)[0m
[94mℹ️  Scanning frontend TypeScript files for parameter usage...[0m
[94mℹ️  Found 17 game_gid references[0m
[94mℹ️  Found 17 game_id references[0m
[92m✅ Frontend uses game_gid parameter correctly[0m
[93m⚠️  Found 17 game_id references (may be legitimate)[0m
[94mℹ️    Reviewing game_id usage context...[0m
[94mℹ️    All game_id uses appear legitimate (database operations)[0m
[92m✅ Parameter Naming Convention: PASSED[0m

[1m🧪 Test 4: GraphQL Mutation Parameter Types[0m
[94mℹ️  Checking batchAddFieldsToCanvas mutation...[0m
[92m✅ Mutation batchAddFieldsToCanvas found in schema[0m
[92m✅   Backend parameter event_id: Int[0m
[92m✅   Backend parameter field_type: FieldTypeEnum[0m
[94mℹ️  Checking frontend mutation call...[0m
[92m✅ Frontend mutation definition found[0m
[92m✅   Frontend uses parameter: $eventId[0m
[92m✅   Frontend uses parameter: $fieldType[0m
[92m✅ Mutation Parameter Types: PASSED[0m

[1m🧪 Test 5: Type Import Consistency[0m
[94mℹ️  Checking type imports in frontend components...[0m
[92m✅ FieldSelectionModal: FieldOptionType type defined[0m
[92m✅   FieldOptionType includes: all[0m
[92m✅   FieldOptionType includes: params[0m
[92m✅   FieldOptionType includes: non-common[0m
[92m✅   FieldOptionType includes: common[0m
[92m✅   FieldOptionType includes: base[0m
[92m✅ Type Import Consistency: PASSED[0m

[1m======================================================================[0m
[1m📊 Test Summary[0m
[1m======================================================================[0m

Total Tests: 5
[92m✅ Passed: 5[0m
[91m❌ Failed: 0[0m

[1m======================================================================[0m
[92m[1m✅ ALL TESTS PASSED[0m
[92mAPI contract is consistent![0m
[1m======================================================================[0m

