/**
 * Event2Table Form Validation Test Script
 * 表单验证测试脚本
 */

const API_BASE = 'http://127.0.0.1:5001/api/graphql';

// Test data
const TEST_GID = 99999992;
const EXISTING_GID = 10000147;

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function separator() {
  log('\n' + '='.repeat(80), 'blue');
}

// GraphQL query helper
async function graphqlQuery(query, variables = {}) {
  const response = await fetch(API_BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, variables })
  });
  return response.json();
}

// Test 1: Add Game Form Validation
async function testAddGameForm() {
  separator();
  log('🎮 TEST 1: Add Game Form Validation', 'magenta');
  separator();

  // Test 1.1: Empty GID (should fail at frontend, but let's test backend)
  log('\n1.1 Testing empty GID...', 'blue');
  try {
    const result = await graphqlQuery(`
      mutation {
        createGame(gid: 0, name: "Test", odsDb: "ieu_ods") {
          ok
          errors
          game { gid name }
        }
      }
    `);
    if (result.errors) {
      log('✅ PASS: Backend rejected empty GID', 'green');
      log(`   Error: ${result.errors[0].message}`, 'yellow');
    } else {
      log('❌ FAIL: Backend accepted empty GID', 'red');
    }
  } catch (error) {
    log(`❌ ERROR: ${error.message}`, 'red');
  }

  // Test 1.2: Non-numeric GID (should fail)
  log('\n1.2 Testing non-numeric GID...', 'blue');
  try {
    const result = await graphqlQuery(`
      mutation {
        createGame(gid: "abc", name: "Test", odsDb: "ieu_ods") {
          ok
          errors
          game { gid name }
        }
      }
    `);
    if (result.errors) {
      log('✅ PASS: Backend rejected non-numeric GID', 'green');
      log(`   Error: ${result.errors[0].message}`, 'yellow');
    } else {
      log('❌ FAIL: Backend accepted non-numeric GID', 'red');
    }
  } catch (error) {
    log(`❌ ERROR: ${error.message}`, 'red');
  }

  // Test 1.3: Duplicate GID (should fail)
  log('\n1.3 Testing duplicate GID...', 'blue');
  try {
    const result = await graphqlQuery(`
      mutation {
        createGame(gid: ${EXISTING_GID}, name: "Duplicate Test", odsDb: "ieu_ods") {
          ok
          errors
          game { gid name }
        }
      }
    `);
    if (result.errors || !result.data?.createGame?.ok) {
      log('✅ PASS: Backend rejected duplicate GID', 'green');
      log(`   Error: ${result.errors?.[0]?.message || result.data?.createGame?.errors?.[0]}`, 'yellow');
    } else {
      log('❌ FAIL: Backend accepted duplicate GID', 'red');
    }
  } catch (error) {
    log(`❌ ERROR: ${error.message}`, 'red');
  }

  // Test 1.4: Successful creation
  log('\n1.4 Testing successful game creation...', 'blue');
  try {
    const result = await graphqlQuery(`
      mutation {
        createGame(gid: ${TEST_GID}, name: "E2E Validation Test Game", odsDb: "ieu_ods") {
          ok
          errors
          game { gid name odsDb }
        }
      }
    `);
    if (result.data?.createGame?.ok) {
      log('✅ PASS: Game created successfully', 'green');
      log(`   Game GID: ${result.data.createGame.game.gid}`, 'yellow');
      log(`   Game Name: ${result.data.createGame.game.name}`, 'yellow');

      // Clean up - delete the test game
      log('\n🧹 Cleaning up test game...', 'blue');
      await graphqlQuery(`
        mutation {
          deleteGame(gid: ${TEST_GID}) {
            ok
          }
        }
      `);
      log('✅ Test game deleted', 'green');
    } else {
      log('❌ FAIL: Game creation failed', 'red');
      log(`   Error: ${result.data?.createGame?.errors?.[0] || 'Unknown error'}`, 'yellow');
    }
  } catch (error) {
    log(`❌ ERROR: ${error.message}`, 'red');
  }
}

// Test 2: Create Event Form Validation
async function testCreateEventForm() {
  separator();
  log('📝 TEST 2: Create Event Form Validation', 'magenta');
  separator();

  // Test 2.1: Empty event name (should fail)
  log('\n2.1 Testing empty event name...', 'blue');
  try {
    const result = await graphqlQuery(`
      mutation {
        createEvent(
          gameGid: ${TEST_GID}
          eventName: ""
          eventNameCn: "测试事件"
          tableName: "ieu_ods.ods_10000147_all_view"
        ) {
          ok
          errors
          event { eventName }
        }
      }
    `);
    if (result.errors || !result.data?.createEvent?.ok) {
      log('✅ PASS: Backend rejected empty event name', 'green');
      log(`   Error: ${result.errors?.[0]?.message || result.data?.createEvent?.errors?.[0]}`, 'yellow');
    } else {
      log('❌ FAIL: Backend accepted empty event name', 'red');
    }
  } catch (error) {
    log(`❌ ERROR: ${error.message}`, 'red');
  }

  // Test 2.2: Invalid table name format (should fail)
  log('\n2.2 Testing invalid table name format...', 'blue');
  try {
    const result = await graphqlQuery(`
      mutation {
        createEvent(
          gameGid: ${TEST_GID}
          eventName: "test_event"
          eventNameCn: "测试事件"
          tableName: "invalid_table_name"
        ) {
          ok
          errors
          event { eventName }
        }
      }
    `);
    if (result.errors || !result.data?.createEvent?.ok) {
      log('✅ PASS: Backend rejected invalid table name', 'green');
      log(`   Error: ${result.errors?.[0]?.message || result.data?.createEvent?.errors?.[0]}`, 'yellow');
    } else {
      log('❌ FAIL: Backend accepted invalid table name', 'red');
    }
  } catch (error) {
    log(`❌ ERROR: ${error.message}`, 'red');
  }

  // Test 2.3: Missing game context (should fail)
  log('\n2.3 Testing missing game context...', 'blue');
  try {
    const result = await graphqlQuery(`
      mutation {
        createEvent(
          eventName: "test_event"
          eventNameCn: "测试事件"
          tableName: "ieu_ods.ods_10000147_all_view"
        ) {
          ok
          errors
          event { eventName }
        }
      }
    `);
    if (result.errors) {
      log('✅ PASS: Backend requires game context', 'green');
      log(`   Error: ${result.errors[0].message}`, 'yellow');
    } else {
      log('❌ FAIL: Backend did not require game context', 'red');
    }
  } catch (error) {
    log(`❌ ERROR: ${error.message}`, 'red');
  }
}

// Test 3: Add Parameter Form Validation
async function testAddParameterForm() {
  separator();
  log('⚙️ TEST 3: Add Parameter Form Validation', 'magenta');
  separator();

  // Test 3.1: Empty parameter name (should fail)
  log('\n3.1 Testing empty parameter name...', 'blue');
  try {
    const result = await graphqlQuery(`
      mutation {
        createEventParam(
          gameGid: ${TEST_GID}
          eventName: "login"
          paramName: ""
          paramNameCn: "测试参数"
          type: base
        ) {
          ok
          errors
          param { paramName }
        }
      }
    `);
    if (result.errors || !result.data?.createEventParam?.ok) {
      log('✅ PASS: Backend rejected empty parameter name', 'green');
      log(`   Error: ${result.errors?.[0]?.message || result.data?.createEventParam?.errors?.[0]}`, 'yellow');
    } else {
      log('❌ FAIL: Backend accepted empty parameter name', 'red');
    }
  } catch (error) {
    log(`❌ ERROR: ${error.message}`, 'red');
  }

  // Test 3.2: Parameter name with spaces (should fail)
  log('\n3.2 Testing parameter name with spaces...', 'blue');
  try {
    const result = await graphqlQuery(`
      mutation {
        createEventParam(
          gameGid: ${TEST_GID}
          eventName: "login"
          paramName: "invalid param name"
          paramNameCn: "测试参数"
          type: base
        ) {
          ok
          errors
          param { paramName }
        }
      }
    `);
    if (result.errors || !result.data?.createEventParam?.ok) {
      log('✅ PASS: Backend rejected parameter name with spaces', 'green');
      log(`   Error: ${result.errors?.[0]?.message || result.data?.createEventParam?.errors?.[0]}`, 'yellow');
    } else {
      log('❌ FAIL: Backend accepted parameter name with spaces', 'red');
    }
  } catch (error) {
    log(`❌ ERROR: ${error.message}`, 'red');
  }

  // Test 3.3: Invalid parameter type (should fail)
  log('\n3.3 Testing invalid parameter type...', 'blue');
  try {
    const result = await graphqlQuery(`
      mutation {
        createEventParam(
          gameGid: ${TEST_GID}
          eventName: "login"
          paramName: "test_param"
          paramNameCn: "测试参数"
          type: "invalid_type"
        ) {
          ok
          errors
          param { paramName }
        }
      }
    `);
    if (result.errors) {
      log('✅ PASS: Backend rejected invalid parameter type', 'green');
      log(`   Error: ${result.errors[0].message}`, 'yellow');
    } else {
      log('❌ FAIL: Backend accepted invalid parameter type', 'red');
    }
  } catch (error) {
    log(`❌ ERROR: ${error.message}`, 'red');
  }

  // Test 3.4: Successful parameter creation
  log('\n3.4 Testing successful parameter creation...', 'blue');
  try {
    const result = await graphqlQuery(`
      mutation {
        createEventParam(
          gameGid: ${EXISTING_GID}
          eventName: "login"
          paramName: "test_validation_param"
          paramNameCn: "验证测试参数"
          type: base
        ) {
          ok
          errors
          param { paramName paramNameCn type }
        }
      }
    `);
    if (result.data?.createEventParam?.ok) {
      log('✅ PASS: Parameter created successfully', 'green');
      log(`   Parameter Name: ${result.data.createEventParam.param.paramName}`, 'yellow');
      log(`   Type: ${result.data.createEventParam.param.type}`, 'yellow');

      // Clean up - delete the test parameter
      log('\n🧹 Cleaning up test parameter...', 'blue');
      await graphqlQuery(`
        mutation {
          deleteEventParam(
            gameGid: ${EXISTING_GID}
            eventName: "login"
            paramName: "test_validation_param"
          ) {
            ok
          }
        }
      `);
      log('✅ Test parameter deleted', 'green');
    } else {
      log('❌ FAIL: Parameter creation failed', 'red');
      log(`   Error: ${result.data?.createEventParam?.errors?.[0] || 'Unknown error'}`, 'yellow');
    }
  } catch (error) {
    log(`❌ ERROR: ${error.message}`, 'red');
  }
}

// Main test runner
async function runAllTests() {
  log('\n🧪 Event2Table Form Validation Test Suite', 'magenta');
  log('Testing GraphQL API validation rules', 'blue');
  log('Start Time: ' + new Date().toISOString(), 'blue');

  try {
    await testAddGameForm();
    await testCreateEventForm();
    await testAddParameterForm();

    separator();
    log('\n✅ All tests completed!', 'green');
    separator();
  } catch (error) {
    log('\n❌ Test suite failed!', 'red');
    log(`Error: ${error.message}`, 'red');
  }
}

// Run tests
runAllTests();
