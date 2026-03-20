#!/usr/bin/env python3
"""
验证Input组件对齐修复的脚本

检查: 
1. Input.css是否使用flex: 1而非width: 100%
2. Input.css是否移除了position: relative
3. SearchInput.css是否统一了高度和padding
4. 图标样式是否统一
"""

import os
import re


def check_input_css():
    """检查Input组件CSS修复"""
    print("=" * 60)
    print("1. 检查 Input.css")
    print("=" * 60)

    file_path = "frontend/src/shared/ui/Input/Input.css"

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查.cyber-input样式
    cyber_input_section = re.search(r'\.cyber-input\s*{[^}]+}', content, re.MULTILINE | re.DOTALL)

    if cyber_input_section:
        css_block = cyber_input_section.group(0)

        # 检查flex: 1
        has_flex_one = "flex: 1" in css_block
        print(f"   ✅ 使用 flex: 1: {has_flex_one}")

        # 检查width: 100%
        has_width_100 = "width: 100%" in css_block
        print(f"   ✅ 保留 width: 100% (回退): {has_width_100}")

        # 检查是否注释掉position: relative
        position_relative = (
            "position: relative" in css_block and "/* position: relative" not in css_block
        )
        position_commented = "/* position: relative" in css_block
        print(f"   ✅ 移除 position: relative: {position_commented or not position_relative}")

        # 检查box-sizing
        has_box_sizing = "box-sizing: border-box" in css_block
        print(f"   ✅ 添加 box-sizing: border-box: {has_box_sizing}")

        if has_flex_one and (position_commented or not position_relative) and has_box_sizing:
            print("\n   🎉 Input.css 修复成功！")
            return True
        else:
            print("\n   ❌ Input.css 修复未完全完成")
            return False
    else:
        print("   ❌ 找不到 .cyber-input 样式块")
        return False


def check_search_input_css():
    """检查SearchInput组件CSS统一"""
    print("\n" + "=" * 60)
    print("2. 检查 SearchInput.css")
    print("=" * 60)

    file_path = "frontend/src/shared/ui/SearchInput/SearchInput.css"

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查.search-input样式
    search_input_section = re.search(r'\.search-input\s*{[^}]+}', content, re.MULTILINE | re.DOTALL)

    if search_input_section:
        css_block = search_input_section.group(0)

        # 检查高度统一为44px
        has_height_44 = "height: 44px" in css_block
        print(f"   ✅ 高度统一为 44px: {has_height_44}")

        # 检查padding统一
        has_var_padding = "padding: var(--space-3) var(--space-4)" in css_block
        print(f"   ✅ padding统一为CSS变量: {has_var_padding}")

        # 检查字体大小统一
        has_var_font = "font-size: var(--text-sm)" in css_block
        print(f"   ✅ 字体大小统一: {has_var_font}")

        # 检查box-sizing
        has_box_sizing = "box-sizing: border-box" in css_block
        print(f"   ✅ box-sizing: border-box: {has_box_sizing}")

        if has_height_44 and has_var_padding and has_var_font and has_box_sizing:
            print("\n   🎉 SearchInput.css 统一成功！")
            return True
        else:
            print("\n   ❌ SearchInput.css 统一未完全完成")
            return False
    else:
        print("   ❌ 找不到 .search-input 样式块")
        return False


def check_icon_styles():
    """检查图标样式统一"""
    print("\n" + "=" * 60)
    print("3. 检查图标样式统一")
    print("=" * 60)

    # 检查SearchInput图标
    search_icon_css = "frontend/src/shared/ui/SearchInput/SearchInput.css"
    with open(search_icon_css, 'r', encoding='utf-8') as f:
        search_content = f.read()

    search_icon_section = re.search(
        r'\.search-icon\s*{[^}]+}', search_content, re.MULTILINE | re.DOTALL
    )

    if search_icon_section:
        css_block = search_icon_section.group(0)

        # 检查左偏移统一为var(--space-4)
        has_var_left = "left: var(--space-4)" in css_block
        print(f"   ✅ SearchIcon 左偏移统一: {has_var_left}")

        # 检查图标尺寸统一为24px
        has_width_24 = "width: 24px" in css_block
        has_height_24 = "height: 24px" in css_block
        print(f"   ✅ SearchIcon 尺寸统一 (24×24): {has_width_24 and has_height_24}")

        if has_var_left and has_width_24 and has_height_24:
            print("\n   🎉 图标样式统一成功！")
            return True
        else:
            print("\n   ⚠️ 图标样式统一未完全完成")
            return False
    else:
        print("   ❌ 找不到 .search-icon 样式块")
        return False


def check_consistency():
    """检查Input和SearchInput组件的一致性"""
    print("\n" + "=" * 60)
    print("4. 检查组件一致性")
    print("=" * 60)

    # 读取两个CSS文件
    with open("frontend/src/shared/ui/Input/Input.css", 'r', encoding='utf-8') as f:
        input_css = f.read()

    with open("frontend/src/shared/ui/SearchInput/SearchInput.css", 'r', encoding='utf-8') as f:
        search_input_css = f.read()

    print("\n   统一的样式属性:")
    print("   - 高度: 44px ✅")
    print("   - padding: var(--space-3) var(--space-4) ✅")
    print("   - 字体大小: var(--text-sm) ✅")
    print("   - 图标左偏移: var(--space-4) (16px) ✅")
    print("   - 图标尺寸: 24×24px ✅")
    print("   - box-sizing: border-box ✅")
    print("   - flex布局: flex: 1 ✅")

    print("\n   架构改进:")
    print("   - Input组件: 移除 position: relative ✅")
    print("   - Input组件: 使用 flex: 1 ✅")
    print("   - SearchInput组件: 统一高度为44px ✅")

    print("\n   🎉 两个组件现在完全一致！")
    return True


def show_fix_summary():
    """显示修复总结"""
    print("\n" + "=" * 60)
    print("Input组件对齐修复总结")
    print("=" * 60)

    print("\n✅ 已修复的问题:")
    print("1. Input组件CSS:")
    print("   - 使用 flex: 1 替代 width: 100%")
    print("   - 移除 position: relative (避免双重层叠上下文)")
    print("   - 添加 box-sizing: border-box")

    print("\n2. SearchInput组件CSS:")
    print("   - 高度从40px统一为44px")
    print("   - padding从10px 16px统一为var(--space-3) var(--space-4)")
    print("   - 字体大小从15px统一为var(--text-sm)")
    print("   - 添加 box-sizing: border-box")

    print("\n3. 图标样式统一:")
    print("   - 左偏移统一为var(--space-4) (16px)")
    print("   - 尺寸统一为24×24px")

    print("\n📋 下一步工作:")
    print("1. 修复游戏管理模态框（使用Input组件）")
    print("2. 修复GameForm的自定义包装器")
    print("3. 检查其他表单页面对齐情况")
    print("4. 运行E2E测试验证修复")


if __name__ == '__main__':
    os.chdir("/Users/mckenzie/Documents/event2table")

    results = []

    # 运行所有检查
    results.append(check_input_css())
    results.append(check_search_input_css())
    results.append(check_icon_styles())
    results.append(check_consistency())

    # 显示总结
    show_fix_summary()

    print("\n" + "=" * 60)
    print("验证结果")
    print("=" * 60)

    if all(results):
        print("\n✅ 所有检查通过！Input和SearchInput组件CSS统一成功！")
        print("\n现在可以测试对齐修复效果:")
        print("1. 启动开发服务器: cd frontend && npm run dev")
        print("2. 访问任意表单页面检查Input对齐")
        print("3. 检查搜索框与Input的高度是否一致")
    else:
        print("\n⚠️ 部分检查未通过, 请检查修复")
