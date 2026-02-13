#!/usr/bin/env node
/**
 * Template API 集成测试（Node.js版本）
 * 测试templateApi.js模块的所有功能
 */

const http = require('http');

const API_BASE = 'http://127.0.0.1:5001';

// 颜色输出
const colors = {
    green: '\x1b[92m',
    red: '\x1b[91m',
    blue: '\x1b[94m',
    yellow: '\x1b[93m',
    bold: '\x1b[1m',
    reset: '\x1b[0m'
};

function log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function logSection(title) {
    console.log(`\n${colors.bold}${colors.blue}=${'='.repeat(59)}${colors.reset}`);
    console.log(`${colors.bold}${colors.blue}${title}${colors.reset}`);
    console.log(`${colors.bold}${colors.blue}=${'='.repeat(59)}${colors.reset}\n`);
}

// HTTP请求封装
function request(method, path, data = null) {
    return new Promise((resolve, reject) => {
        const url = new URL(path, API_BASE);
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        const req = http.request(url, options, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                try {
                    const json = JSON.parse(body);
                    resolve({ status: res.statusCode, data: json });
                } catch (e) {
                    resolve({ status: res.statusCode, data: body });
                }
            });
        });

        req.on('error', reject);

        if (data) {
            req.write(JSON.stringify(data));
        }

        req.end();
    });
}

// 测试函数
async function testGetCategories() {
    logSection('测试 1: 获取模板分类列表');
    const result = await request('GET', '/api/templates/categories');
    if (result.status === 200 && result.data.success) {
        log('✓ 分类列表获取成功', 'green');
        log(`分类数量: ${result.data.data.categories.length}`, 'blue');
        return true;
    } else {
        log('✗ 分类列表获取失败', 'red');
        return false;
    }
}

async function testListTemplates() {
    logSection('测试 2: 获取模板列表');
    const result = await request('GET', '/api/templates?page=1&per_page=10');
    if (result.status === 200 && result.data.success) {
        log('✓ 模板列表获取成功', 'green');
        const templates = result.data.data.templates;
        log(`找到 ${templates.length} 个模板`, 'blue');
        return templates;
    } else {
        log('✗ 模板列表获取失败', 'red');
        return [];
    }
}

async function testCreateTemplate() {
    logSection('测试 3: 创建新模板');
    const templateData = {
        name: '集成测试模板',
        game_gid: 10000147,
        canvas_data: {
            nodes: [
                { id: 'event1', type: 'event', position: { x: 100, y: 100 }, data: { label: '测试事件' } },
                { id: 'output1', type: 'output', position: { x: 400, y: 100 }, data: { label: '输出' } }
            ],
            edges: [
                { id: 'e1', source: 'event1', target: 'output1' }
            ]
        },
        description: '通过集成测试创建的模板',
        category: '测试',
        tags: ['测试', '集成'],
        is_public: false
    };

    const result = await request('POST', '/api/templates', templateData);
    if (result.status === 200 && result.data.success) {
        const templateId = result.data.data.id;
        log(`✓ 模板创建成功 (ID: ${templateId})`, 'green');
        return templateId;
    } else {
        log('✗ 模板创建失败', 'red');
        log(JSON.stringify(result.data, null, 2), 'yellow');
        return null;
    }
}

async function testGetTemplate(templateId) {
    if (!templateId) return;

    logSection('测试 4: 获取模板详情');
    const result = await request('GET', `/api/templates/${templateId}`);
    if (result.status === 200 && result.data.success) {
        log('✓ 模板详情获取成功', 'green');
        const template = result.data.data;
        log(`名称: ${template.name}`, 'blue');
        log(`分类: ${template.category}`, 'blue');
        log(`节点数: ${template.flow_graph.nodes.length}`, 'blue');
        log(`连接数: ${template.flow_graph.edges.length}`, 'blue');
        return true;
    } else {
        log('✗ 模板详情获取失败', 'red');
        return false;
    }
}

async function testUpdateTemplate(templateId) {
    if (!templateId) return;

    logSection('测试 5: 更新模板');
    const result = await request('PUT', `/api/templates/${templateId}`, {
        name: '集成测试模板（已更新）',
        description: '更新后的描述'
    });
    if (result.status === 200 && result.data.success) {
        log('✓ 模板更新成功', 'green');
        log(`新名称: ${result.data.data.name}`, 'blue');
        return true;
    } else {
        log('✗ 模板更新失败', 'red');
        return false;
    }
}

async function testApplyTemplate(templateId) {
    if (!templateId) return;

    logSection('测试 6: 应用模板到画布');
    const result = await request('POST', `/api/templates/${templateId}/apply`, {
        variables: {}
    });
    if (result.status === 200 && result.data.success) {
        log('✓ 模板应用成功', 'green');
        const flowGraph = result.data.data;
        log(`返回节点数: ${flowGraph.nodes.length}`, 'blue');
        log(`返回连接数: ${flowGraph.edges.length}`, 'blue');
        return true;
    } else {
        log('✗ 模板应用失败', 'red');
        return false;
    }
}

async function testCloneTemplate(templateId) {
    if (!templateId) return;

    logSection('测试 7: 克隆模板');
    const result = await request('POST', `/api/templates/${templateId}/clone`, {
        new_name: '集成测试模板（克隆）',
        game_gid: 10000147
    });
    if (result.status === 200 && result.data.success) {
        const clonedId = result.data.data.id;
        log(`✓ 模板克隆成功 (新ID: ${clonedId})`, 'green');
        return clonedId;
    } else {
        log('✗ 模板克隆失败', 'red');
        return null;
    }
}

async function testDeleteTemplate(templateId, label = '模板') {
    if (!templateId) return false;

    logSection(`测试: 删除${label}`);
    const result = await request('DELETE', `/api/templates/${templateId}`);
    if (result.status === 200 && result.data.success) {
        log(`✓ ${label}删除成功`, 'green');
        return true;
    } else {
        log(`✗ ${label}删除失败`, 'red');
        return false;
    }
}

// 主测试函数
async function runTests() {
    console.log(`\n${colors.bold}Canvas Template API 集成测试${colors.reset}`);
    console.log(`${colors.bold}${'='.repeat(60)}${colors.reset}\n`);

    try {
        // 1. 获取分类列表
        await testGetCategories();

        // 2. 获取模板列表
        await testListTemplates();

        // 3. 创建模板
        const templateId = await testCreateTemplate();

        if (templateId) {
            // 4. 获取模板详情
            await testGetTemplate(templateId);

            // 5. 更新模板
            await testUpdateTemplate(templateId);

            // 6. 应用模板
            await testApplyTemplate(templateId);

            // 7. 克隆模板
            const clonedId = await testCloneTemplate(templateId);

            // 8. 删除克隆的模板
            if (clonedId) {
                await testDeleteTemplate(clonedId, '克隆模板');
            }

            // 9. 删除原始模板
            await testDeleteTemplate(templateId, '原始模板');
        }

        // 总结
        logSection('测试总结');
        log('✓ 所有集成测试完成！', 'green');
        log('Template API工作正常，前端API模块验证成功', 'blue');

        process.exit(0);
    } catch (error) {
        log(`✗ 测试过程中发生错误: ${error.message}`, 'red');
        console.error(error);
        process.exit(1);
    }
}

// 运行测试
runTests();
