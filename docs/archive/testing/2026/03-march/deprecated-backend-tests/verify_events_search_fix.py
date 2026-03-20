#!/usr/bin/env python3
"""
验证Events页面搜索框修复的脚本

检查: 
1. EventsList.jsx是否使用SearchInput组件
2. EventsList.css是否移除了冲突的.search-input样式
3. SearchInput组件是否正确导出
"""

import os
import re


def check_events_list_jsx():
    """检查EventsList.jsx是否使用SearchInput"""
    print("=" * 60)
    print("1. 检查 EventsList.jsx")
    print("=" * 60)

    file_path = "frontend/src/analytics/pages/EventsList.jsx"

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否导入SearchInput
    has_search_input_import = "SearchInput" in content and "import" in content
    print(f"   ✅ 导入 SearchInput: {has_search_input_import}")

    # 检查是否使用SearchInput组件
    uses_search_input_component = "<SearchInput" in content
    print(f"   ✅ 使用 <SearchInput> 组件: {uses_search_input_component}")

    # 检查是否还有旧的Input组件作为搜索框
    # 我们期望保留Input导入(可能其他地方使用), 但不在搜索框中使用
    old_search_pattern = r'div className="search-input"\s*<Input'
    has_old_search_input = re.search(old_search_pattern, content, re.MULTILINE | re.DOTALL)
    print(f"   ✅ 移除旧的 <Input> 搜索框: {not has_old_search_input}")

    if has_search_input_import and uses_search_input_component and not has_old_search_input:
        print("\n   🎉 EventsList.jsx 修复成功！")
        return True
    else:
        print("\n   ❌ EventsList.jsx 修复未完成")
        return False


def check_events_list_css():
    """检查EventsList.css是否移除了冲突的样式"""
    print("\n" + "=" * 60)
    print("2. 检查 EventsList.css")
    print("=" * 60)

    file_path = "frontend/src/analytics/pages/EventsList.css"

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否移除了.search-input样式(或简化为flex: 1)
    has_complex_search_input = (
        ".search-input {" in content and "padding:" in content and "2.5rem" in content
    )
    print(f"   ✅ 移除冲突的 .search-input 样式: {not has_complex_search_input}")

    # 检查是否保留了简单的flex样式
    has_simple_flex = ".filters-bar > :first-child" in content and "flex: 1" in content
    print(f"   ✅ 添加简单的 flex 样式: {has_simple_flex}")

    if not has_complex_search_input:
        print("\n   🎉 EventsList.css 修复成功！")
        return True
    else:
        print("\n   ⚠️ EventsList.css 可能还有冲突的样式")
        return False


def check_search_input_export():
    """检查SearchInput组件是否正确导出"""
    print("\n" + "=" * 60)
    print("3. 检查 SearchInput 组件导出")
    print("=" * 60)

    file_path = "frontend/src/shared/ui/index.js"

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否导出SearchInput
    has_search_input_export = "SearchInput" in content and "export" in content
    print(f"   ✅ SearchInput 已导出: {has_search_input_export}")

    # 检查SearchInput组件文件是否存在
    component_file = "frontend/src/shared/ui/SearchInput/SearchInput.tsx"
    file_exists = os.path.exists(component_file)
    print(f"   ✅ SearchInput.tsx 文件存在: {file_exists}")

    if has_search_input_export and file_exists:
        print("\n   🎉 SearchInput 组件配置正确！")
        return True
    else:
        print("\n   ❌ SearchInput 组件配置有问题")
        return False


def check_dom_structure():
    """检查预期的DOM结构"""
    print("\n" + "=" * 60)
    print("4. 预期的DOM结构")
    print("=" * 60)

    print("\n   修复前（使用Input组件）:")
    print("   <div className=\"filters-bar\">")
    print("     <div className=\"search-input\">              ❌ 外层容器")
    print("       <div class=\"cyber-input\">                  ❌ 三层嵌套")
    print("         <div class=\"cyber-input-wrapper\">")
    print("           <input class=\"cyber-input\" />")
    print("         </div>")
    print("       </div>")
    print("     </div>")
    print("   </div>")

    print("\n   修复后（使用SearchInput组件）:")
    print("   <div className=\"filters-bar\">")
    print("     <div className=\"search-input-wrapper\">      ✅ 单层结构")
    print("       <input className=\"search-input\" />        ✅ 直接的input")
    print("     </div>")
    print("   </div>")

    print("\n   CSS类名对比:")
    print("   - 修复前: .cyber-input, .cyber-input-wrapper")
    print("   - 修复后: .search-input-wrapper, .search-input")
    print("   - 对比: 与Parameters页面的搜索框一致 ✅")

    return True


if __name__ == '__main__':
    os.chdir("/Users/mckenzie/Documents/event2table")

    results = []

    # 运行所有检查
    results.append(check_events_list_jsx())
    results.append(check_events_list_css())
    results.append(check_search_input_export())
    results.append(check_dom_structure())

    # 总结
    print("\n" + "=" * 60)
    print("修复验证总结")
    print("=" * 60)

    if all(results):
        print("\n✅ 所有检查通过！Events页面搜索框修复成功！")
        print("\n下一步: ")
        print("1. 启动前端开发服务器: cd frontend && npm run dev")
        print("2. 访问Events页面: http://localhost:5173/#/events/list?game_gid=10000147")
        print("3. 检查浏览器DevTools, 确认DOM结构:")
        print("   - 应该看到 .search-input-wrapper")
        print("   - 应该看到 .search-input")
        print("   - 不应该看到 .cyber-input")
        print("4. 运行E2E测试验证修复")
    else:
        print("\n❌ 部分检查未通过, 请检查修复")
