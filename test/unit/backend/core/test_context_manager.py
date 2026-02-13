"""
Context Manager 模块测试

测试智能上下文管理系统：
- Observation分类逻辑
- Markdown生成
- MCP工具集成
- 端到端工作流

TDD Phase: Red - 先写测试，看测试失败
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch


# ============================================================================
# Test Class 1: Categorization Logic (9 tests)
# ============================================================================

class TestCategorizeObservations:
    """测试observation分类逻辑"""

    def test_categorize_backend_observation(self):
        """Backend文件路径应归类为'backend'"""
        from backend.core.context_manager import categorize_observation

        observation = {
            'files_modified': ['dwd_generator/backend/services/hql_v2/core/cache.py'],
            'files_read': []
        }
        category = categorize_observation(observation)
        assert category == 'backend'

    def test_categorize_frontend_observation(self):
        """Frontend文件路径应归类为'frontend'"""
        from backend.core.context_manager import categorize_observation

        observation = {
            'files_modified': ['dwd_generator/frontend/src/components/Header.jsx'],
            'files_read': []
        }
        category = categorize_observation(observation)
        assert category == 'frontend'

    def test_categorize_testing_observation(self):
        """测试文件路径应归类为'testing'"""
        from backend.core.context_manager import categorize_observation

        observation = {
            'files_modified': ['dwd_generator/backend/tests/test_crypto.py'],
            'files_read': []
        }
        category = categorize_observation(observation)
        assert category == 'testing'

    def test_categorize_docs_observation(self):
        """文档文件路径应归类为'docs'"""
        from backend.core.context_manager import categorize_observation

        observation = {
            'files_modified': ['docs/development/CLAUDE.md'],
            'files_read': []
        }
        category = categorize_observation(observation)
        assert category == 'docs'

    def test_categorize_general_observation(self):
        """无文件的observation应归类为'general'"""
        from backend.core.context_manager import categorize_observation

        observation = {
            'files_modified': [],
            'files_read': []
        }
        category = categorize_observation(observation)
        assert category == 'general'

    def test_categorize_mixed_files_backend_dominant(self):
        """混合文件应按多数归类（backend主导）"""
        from backend.core.context_manager import categorize_observation

        observation = {
            'files_modified': [
                'dwd_generator/backend/services/cache.py',
                'dwd_generator/backend/services/api.py',
                'dwd_generator/frontend/src/utils.js'
            ],
            'files_read': []
        }
        category = categorize_observation(observation)
        assert category == 'backend'

    def test_categorize_considers_both_modified_and_read(self):
        """应同时考虑files_modified和files_read"""
        from backend.core.context_manager import categorize_observation

        observation = {
            'files_modified': [],
            'files_read': ['dwd_generator/backend/core/common.py']
        }
        category = categorize_observation(observation)
        assert category == 'backend'

    def test_categorize_handles_missing_fields_gracefully(self):
        """缺少字段时应默认为general"""
        from backend.core.context_manager import categorize_observation

        observation = {'title': 'Some observation'}
        category = categorize_observation(observation)
        assert category == 'general'


# ============================================================================
# Test Class 2: Markdown Generation (6 tests)
# ============================================================================

class TestMarkdownGeneration:
    """测试markdown上下文文件生成"""

    def test_generate_backend_context_file_structure(self):
        """生成的markdown应有正确结构"""
        from backend.core.context_manager import generate_context_markdown

        observations = [{
            'id': '5600',
            'type': 'feature',
            'title': 'FieldRecommender implementation',
            'created_at': '2026-02-09 23:30',
            'created_at_epoch': 1739121000000,
            'files_modified': ['dwd_generator/backend/services/field_recommender.py'],
            'narrative': 'Implemented complete FieldRecommender service',
            'facts': ['100% pass rate']
        }]

        markdown = generate_context_markdown('backend', observations, days=7)

        assert '# Backend Context' in markdown
        assert '## Summary' in markdown
        assert '## Recent Activity' in markdown
        assert '## Details' in markdown

    def test_markdown_includes_observation_summary_table(self):
        """Markdown应包含observation汇总表"""
        from backend.core.context_manager import generate_context_markdown

        observations = [{
            'id': '5600',
            'type': 'feature',
            'title': 'Feature title',
            'created_at': '2026-02-09 23:30',
            'files_modified': ['backend/service.py']
        }]

        markdown = generate_context_markdown('backend', observations, days=7)

        assert '| ID |' in markdown
        assert '| Time |' in markdown
        assert '| Type |' in markdown
        assert '| #5600 |' in markdown

    def test_markdown_sorts_observations_by_time_descending(self):
        """Observations应按时间降序排列（最新的在前）"""
        from backend.core.context_manager import generate_context_markdown

        observations = [
            {
                'id': '100',
                'created_at_epoch': 1000,
                'title': 'Old',
                'type': 'feature',
                'created_at': '2026-02-09 10:00',
                'files_modified': []
            },
            {
                'id': '200',
                'created_at_epoch': 2000,
                'title': 'New',
                'type': 'bugfix',
                'created_at': '2026-02-09 12:00',
                'files_modified': []
            }
        ]

        markdown = generate_context_markdown('backend', observations, days=7)

        new_pos = markdown.index('| #200 |')
        old_pos = markdown.index('| #100 |')
        assert new_pos < old_pos

    def test_markdown_includes_type_emoji_mapping(self):
        """Observation类型应映射为emoji图标"""
        from backend.core.context_manager import generate_context_markdown

        observations = [
            {
                'id': '1',
                'type': 'bugfix',
                'title': 'Bug fix',
                'created_at': '2026-02-09 12:00',
                'files_modified': []
            },
            {
                'id': '2',
                'type': 'feature',
                'title': 'New feature',
                'created_at': '2026-02-09 12:00',
                'files_modified': []
            }
        ]

        markdown = generate_context_markdown('backend', observations, days=7)

        assert '🔴' in markdown
        assert '🟣' in markdown

    def test_markdown_limits_file_list_in_summary(self):
        """汇总表应限制文件列表以避免溢出"""
        from backend.core.context_manager import generate_context_markdown

        observations = [{
            'id': '1',
            'type': 'feature',
            'title': 'Many files',
            'created_at': '2026-02-09 12:00',
            'files_modified': [f'backend/file{i}.py' for i in range(10)]
        }]

        markdown = generate_context_markdown('backend', observations, days=7)

        # Should show file count limit indicator (e.g., "+8 more")
        assert '+8 more' in markdown or '+ more' in markdown

    def test_markdown_includes_metadata_header(self):
        """生成的markdown应包含元数据"""
        from backend.core.context_manager import generate_context_markdown

        observations = [{
            'id': '1',
            'type': 'feature',
            'title': 'Test',
            'created_at': '2026-02-09 12:00',
            'files_modified': []
        }]

        markdown = generate_context_markdown('backend', observations, days=7)

        assert '> Generated:' in markdown
        assert '> Time range: Last 7 days' in markdown
        assert '> Total observations: 1' in markdown


# ============================================================================
# Test Class 3: MCP Integration (3 tests)
# ============================================================================

class TestMCPIntegration:
    """测试MCP工具集成"""

    def test_fetch_recent_observations_calls_search(self):
        """应调用MCP search获取observation索引"""
        from backend.core.context_manager import fetch_recent_observations

        mock_search = Mock(return_value=[
            {'id': 5600, 'type': 'feature', 'title': 'Test obs 1'},
            {'id': 5590, 'type': 'bugfix', 'title': 'Test obs 2'}
        ])

        results = fetch_recent_observations(days=7, mcp_search=mock_search)

        assert len(results) == 2
        assert results[0]['id'] == 5600
        mock_search.assert_called_once()

    def test_fetch_observation_details_by_ids(self):
        """应获取指定ID的observation完整详情"""
        from backend.core.context_manager import fetch_observation_details

        mock_get = Mock(return_value=[
            {
                'id': 5600,
                'type': 'feature',
                'title': 'FieldRecommender',
                'narrative': 'Implementation complete'
            }
        ])

        details = fetch_observation_details(ids=[5600], mcp_get_observations=mock_get)

        assert len(details) == 1
        assert details[0]['title'] == 'FieldRecommender'
        mock_get.assert_called_once_with([5600])

    def test_context_manager_full_workflow(self):
        """完整工作流：search → categorize → generate"""
        from backend.core.context_manager import ContextManager

        mock_search = Mock(return_value=[
            {'id': 5600, 'type': 'feature', 'files_modified': ['backend/service.py']},
            {'id': 5590, 'type': 'bugfix', 'files_modified': ['frontend/test.js']}
        ])

        manager = ContextManager(mcp_search=mock_search)
        result = manager.update_context(days=7)

        assert 'total_observations' in result
        assert 'categories_generated' in result
        assert result['total_observations'] == 2
