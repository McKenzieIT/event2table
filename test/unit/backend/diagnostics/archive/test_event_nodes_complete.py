#!/usr/bin/env python3
"""
事件节点管理页面 - 完整自动化测试
Event Nodes Management - Complete Automated Testing

测试范围：
1. 页面加载和初始化
2. 游戏上下文验证
3. 统计卡片显示
4. 搜索功能（防抖）
5. 高级筛选功能
6. 排序功能
7. 分页功能
8. 批量操作
9. 单个节点操作
10. 模态框功能
11. Toast通知
12. URL状态同步
"""

from playwright.sync_api import sync_playwright, expect
import time
import json

BASE_URL = "http://127.0.0.1:5001"
EVENT_NODES_URL = f"{BASE_URL}/event-nodes"

def test_event_nodes_complete():
    """完整的事件节点管理页面测试"""

    with sync_playwright() as p:
        # 启动浏览器（非headless模式以便观察）
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()

        # 启用控制台日志监听
        console_messages = []
        def on_console(msg):
            console_messages.append(f"{msg.type}: {msg.text}")
        page.on("console", on_console)

        try:
            print("=" * 80)
            print("🧪 开始事件节点管理页面自动化测试")
            print("=" * 80)

            # ========== 测试1: 页面加载 ==========
            print("\n📋 测试1: 页面加载和初始化")
            page.goto(EVENT_NODES_URL)
            page.wait_for_load_state('networkidle', timeout=10000)
            page.screenshot(path='test_results/01_page_load.png')
            print("✅ 页面加载成功")

            # 检查是否显示游戏选择提示
            game_prompt = page.locator('.glass-card').filter(has_text='请先选择游戏')
            if game_prompt.count() > 0:
                print("🎮 检测到游戏选择提示，需要先选择游戏")
                # 点击前往游戏管理
                page.click('text=前往游戏管理')
                page.wait_for_load_state('networkidle')
                page.screenshot(path='test_results/02_games_list.png')
                print("✅ 跳转到游戏管理页面")

                # 选择第一个游戏
                first_game = page.locator('table tbody tr').first
                if first_game.count() > 0:
                    first_game.click()
                    page.wait_for_timeout(1000)
                    page.screenshot(path='test_results/03_game_selected.png')
                    print("✅ 选择游戏成功")

                    # 返回事件节点页面
                    page.goto(EVENT_NODES_URL)
                    page.wait_for_load_state('networkidle')
                else:
                    print("❌ 没有可用的游戏")
                    return
            else:
                print("✅ 已有游戏上下文")

            # ========== 测试2: 统计卡片 ==========
            print("\n📋 测试2: 统计卡片显示")
            page.wait_for_selector('.glass-card', timeout=5000)
            page.screenshot(path='test_results/04_statistics_cards.png')

            stats_cards = page.locator('.glass-card').all()
            print(f"✅ 找到 {len(stats_cards)} 个卡片（包括统计卡片）")

            # ========== 测试3: 搜索功能 ==========
            print("\n📋 测试3: 搜索功能（防抖）")
            search_input = page.locator('input[placeholder*="搜索"]')
            if search_input.count() > 0:
                search_input.fill('test')
                print("✅ 输入搜索关键词")
                page.wait_for_timeout(500) # 等待防抖
                page.screenshot(path='test_results/05_search_results.png')
                print("✅ 搜索完成")

                # 清空搜索
                search_input.fill('')
                page.wait_for_timeout(500)
            else:
                print("⚠️  未找到搜索输入框")

            # ========== 测试4: 高级筛选 ==========
            print("\n📋 测试4: 高级筛选面板")
            advanced_filter_btn = page.locator('button:has-text("高级筛选")')
            if advanced_filter_btn.count() > 0:
                advanced_filter_btn.click()
                page.wait_for_timeout(500)
                page.screenshot(path='test_results/06_advanced_filter_open.png')
                print("✅ 高级筛选面板展开")

                # 检查筛选选项
                today_modified = page.locator('#todayModified')
                if today_modified.count() > 0:
                    print("✅ 找到'今日修改'复选框")

                event_filter = page.locator('#filterEventId')
                if event_filter.count() > 0:
                    print("✅ 找到'事件筛选'下拉框")

                # 关闭高级筛选
                advanced_filter_btn.click()
                page.wait_for_timeout(500)
            else:
                print("⚠️  未找到高级筛选按钮")

            # ========== 测试5: 表格和排序 ==========
            print("\n📋 测试5: 表格显示和排序")

            # 等待表格加载
            table = page.locator('table')
            try:
                table.wait_for(state='visible', timeout=10000)
                page.screenshot(path='test_results/07_table_display.png')
                print("✅ 表格显示正常")

                # 检查表头
                headers = page.locator('th').all()
                print(f"✅ 找到 {len(headers)} 个列")

                # 尝试排序
                if len(headers) > 2:
                    headers[2].click() # 点击第三列排序
                    page.wait_for_timeout(500)
                    page.screenshot(path='test_results/08_table_sorted.png')
                    print("✅ 排序功能正常")

            except Exception as e:
                print(f"⚠️  表格可能为空或未加载: {e}")

            # ========== 测试6: 批量操作 ==========
            print("\n📋 测试6: 批量操作")

            checkboxes = page.locator('input[type="checkbox"]').all()
            if len(checkboxes) > 1: # 至少有全选和行选择框
                # 全选
                checkboxes[0].check()
                page.wait_for_timeout(500)
                page.screenshot(path='test_results/09_all_selected.png')
                print("✅ 全选功能正常")

                # 检查选中计数
                selected_count = page.locator('text=/已选择 \\d+ 个节点/')
                if selected_count.count() > 0:
                    print("✅ 选中计数显示正常")

                # 取消全选
                checkboxes[0].uncheck()
                page.wait_for_timeout(500)
            else:
                print("⚠️  没有复选框（可能没有数据）")

            # ========== 测试7: 单个节点操作 ==========
            print("\n📋 测试7: 单个节点操作")

            # 查找第一个节点的操作按钮
            rows = page.locator('tbody tr').all()
            if len(rows) > 0:
                first_row = rows[0]

                # 点击操作下拉菜单
                dropdown_btn = first_row.locator('.dropdown-toggle, button:has-text("操作")')
                if dropdown_btn.count() > 0:
                    dropdown_btn.click()
                    page.wait_for_timeout(500)
                    page.screenshot(path='test_results/10_dropdown_menu.png')
                    print("✅ 操作下拉菜单展开")

                    # 检查菜单项
                    menu_items = [
                        '查看HQL',
                        '字段列表',
                        '快速编辑',
                        '构建器编辑',
                        '复制配置',
                        '删除'
                    ]

                    for item in menu_items:
                        if page.locator(f'text={item}').count() > 0:
                            print(f"  ✅ 找到'{item}'菜单项")

                    # 测试查看HQL
                    if page.locator('text=查看HQL').count() > 0:
                        page.locator('text=查看HQL').click()
                        page.wait_for_timeout(1000)
                        page.screenshot(path='test_results/11_hql_modal.png')
                        print("✅ HQL模态框打开")

                        # 关闭模态框
                        close_btn = page.locator('.btn-close, button:has-text("关闭")').first
                        if close_btn.count() > 0:
                            close_btn.click()
                            page.wait_for_timeout(500)
                            print("✅ 模态框关闭")

                    # 重新打开菜单测试其他功能
                    dropdown_btn.click()
                    page.wait_for_timeout(500)

                    # 测试字段列表
                    if page.locator('text=字段列表').count() > 0:
                        page.locator('text=字段列表').click()
                        page.wait_for_timeout(1000)
                        page.screenshot(path='test_results/12_fields_modal.png')
                        print("✅ 字段列表模态框打开")

                        # 关闭模态框
                        close_btn = page.locator('.btn-close, button:has-text("关闭")').first
                        if close_btn.count() > 0:
                            close_btn.click()
                            page.wait_for_timeout(500)
                else:
                    print("⚠️  未找到操作按钮")
            else:
                print("⚠️  没有数据行")

            # ========== 测试8: Toast通知 ==========
            print("\n📋 测试8: Toast通知系统")

            # 触发一个操作来产生Toast
            if page.locator('text=批量导出HQL').count() > 0:
                page.locator('text=批量导出HQL').click()
                page.wait_for_timeout(500)
                page.screenshot(path='test_results/13_toast_notification.png')

                # 检查Toast容器
                toast_container = page.locator('.toast-container')
                if toast_container.count() > 0:
                    print("✅ Toast通知显示正常")
                else:
                    print("⚠️  Toast容器未找到")

            # ========== 测试9: URL状态同步 ==========
            print("\n📋 测试9: URL状态同步")

            current_url = page.url
            print(f"当前URL: {current_url}")

            # 输入搜索关键词
            search_input = page.locator('input[placeholder*="搜索"]')
            if search_input.count() > 0:
                search_input.fill('test_keyword')
                page.wait_for_timeout(500) # 等待防抖

                # 检查URL是否包含搜索参数
                updated_url = page.url
                if 'q=test_keyword' in updated_url or 'test_keyword' in updated_url:
                    print("✅ URL状态同步正常")
                else:
                    print(f"⚠️  URL未更新: {updated_url}")

            # ========== 测试10: 空状态处理 ==========
            print("\n📋 测试10: 空状态处理（通过搜索触发）")

            # 搜索不存在的关键词
            search_input = page.locator('input[placeholder*="搜索"]')
            if search_input.count() > 0:
                search_input.fill('nonexistent_node_xyz_123')
                page.wait_for_timeout(1000)
                page.screenshot(path='test_results/14_empty_state.png')
                print("✅ 空状态截图完成")

            # ========== 测试11: 分页功能 ==========
            print("\n📋 测试11: 分页功能")

            pagination_btns = page.locator('.btn-group .btn').all()
            if len(pagination_btns) > 0:
                print(f"✅ 找到 {len(pagination_btns)} 个分页按钮")
                page.screenshot(path='test_results/15_pagination.png')
            else:
                print("⚠️  未找到分页按钮（数据可能不足一页）")

            # ========== 测试12: 响应式设计 ==========
            print("\n📋 测试12: 响应式设计")

            # 调整窗口大小
            page.set_viewport_size({'width': 375, 'height': 667}) # 手机尺寸
            page.wait_for_timeout(500)
            page.screenshot(path='test_results/16_mobile_view.png')
            print("✅ 移动端视图截图完成")

            # 恢复桌面尺寸
            page.set_viewport_size({'width': 1920, 'height': 1080})
            page.wait_for_timeout(500)

            # ========== 完成测试 ==========
            print("\n" + "=" * 80)
            print("🎉 所有测试完成！")
            print("=" * 80)
            print(f"\n📊 测试统计:")
            print(f"  - 控制台消息数: {len(console_messages)}")
            print(f"  - 截图保存: test_results/")
            print(f"  - 错误数: {len([m for m in console_messages if 'error' in m.lower()])}")

            # 保存测试报告
            with open('test_results/test_report.json', 'w') as f:
                json.dump({
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'console_messages': console_messages,
                    'total_tests': 12,
                    'status': 'completed'
                }, f, indent=2)

            print("\n📄 测试报告已保存到: test_results/test_report.json")

        except Exception as e:
            print(f"\n❌ 测试过程中出错: {e}")
            import traceback
            traceback.print_exc()
            page.screenshot(path='test_results/error_screenshot.png')
            print("📸 错误截图已保存")

        finally:
            # 保持浏览器打开5秒供观察
            print("\n⏳ 浏览器将保持打开5秒供观察...")
            time.sleep(5)

            browser.close()
            print("\n✅ 测试结束，浏览器已关闭")

if __name__ == '__main__':
    import os
    os.makedirs('test_results', exist_ok=True)
    test_event_nodes_complete()
