#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HQL Generation Module
Handles all HQL generation operations
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, session
from .manager import hql_manager
from backend.core.utils import fetch_all_as_dict, fetch_one_as_dict

hql_bp = Blueprint('hql_generator', __name__)


@hql_bp.route('/generate', methods=['GET', 'POST'])
def generate_hql():
    """Generate HQL scripts and save to database"""
    game_gid = request.args.get('game_gid', type=int)
    mode = request.args.get('mode', 'classic')  # classic or field_builder

    # Check if there are any games in database
    from backend.core.utils import fetch_one_as_dict
    result = fetch_one_as_dict('SELECT COUNT(*) as count FROM games')
    games_exist = result['count'] > 0 if result else False

    if not games_exist:
        flash('请先创建游戏', 'error')
        return redirect(url_for('games.list_games'))

    # Get events for selected game
    if game_gid:
        events = fetch_all_as_dict('''
            SELECT le.*,
                g.gid, g.name as game_name, g.ods_db,
                ec.name as category_name,
                (SELECT COUNT(*) FROM event_params ep WHERE ep.event_id = le.id AND ep.is_active = 1) as param_count
            FROM log_events le
            LEFT JOIN games g ON le.game_gid = g.gid
            LEFT JOIN event_categories ec ON le.category_id = ec.id
            WHERE le.game_gid = ?
            ORDER BY le.event_name
        ''', (game_gid,))
    else:
        events = fetch_all_as_dict('''
            SELECT le.*,
                g.gid, g.name as game_name, g.ods_db,
                ec.name as category_name,
                (SELECT COUNT(*) FROM event_params ep WHERE ep.event_id = le.id AND ep.is_active = 1) as param_count
            FROM log_events le
            LEFT JOIN games g ON le.game_gid = g.gid
            LEFT JOIN event_categories ec ON le.category_id = ec.id
            ORDER BY le.event_name
        ''')

    # Query join configurations
    join_configs = fetch_all_as_dict('''
        SELECT jc.*
        FROM join_configs jc
        ORDER BY jc.created_at DESC
    ''')

    # Get current game info
    current_game = fetch_one_as_dict('SELECT * FROM games WHERE gid = ?', (game_gid,)) if game_gid else None

    # Save game_gid to session for persistence
    if game_gid:
        session['current_game_gid'] = game_gid

    if request.method == 'POST':
        selected_events = request.form.getlist('selected_events')

        if not selected_events:
            flash('请至少选择一个日志事件', 'error')
            return render_template('generate.html',
                                    events=events,
                                    join_configs=join_configs,
                                    selected_game_gid=game_gid,
                                    current_game=current_game,
                                    mode=mode)

        # Generate HQL for each selected event
        total_generated = 0
        for event_id in selected_events:
            results = hql_manager.generate_all_for_event(event_id)
            if results:
                total_generated += len(results)

        if total_generated > 0:
            flash(f'成功生成并保存 {total_generated} 个HQL语句到数据库', 'success')
        else:
            flash('生成HQL失败', 'error')

        return redirect(url_for('hql_generator.hql_results'))

    # Render field builder template if mode is field_builder
    if mode == 'field_builder':
        return render_template('field_builder.html',
                              events=events,
                              selected_game_gid=game_gid,
                              current_game=current_game)

    return render_template('generate.html',
                          events=events,
                          join_configs=join_configs,
                          selected_game_gid=game_gid,
                          current_game=current_game,
                          mode=mode)


@hql_bp.route('/hql-results')
def hql_results():
    """显示HQL生成结果 - 自动加载当前游戏的HQL"""
    from backend.core.database import get_db_connection
    conn = get_db_connection()

    # 获取当前游戏GID
    game_gid = request.args.get('game_gid', type=int)
    if not game_gid and 'current_game_gid' in session:
        game_gid = session['current_game_gid']

    if not game_gid:
        conn.close()
        flash('请先选择游戏', 'error')
        return redirect(url_for('index'))

    # 按游戏过滤
    hql_statements = conn.execute('''
        SELECT hs.*, le.event_name, le.event_name_cn, g.name as game_name
        FROM hql_statements hs
        JOIN log_events le ON hs.event_id = le.id
        JOIN games g ON le.game_gid = g.gid
        WHERE le.game_gid = ?
        ORDER BY hs.created_at DESC
    ''', (game_gid,)).fetchall()

    # 获取游戏信息
    current_game = conn.execute('SELECT gid, name FROM games WHERE gid = ?', (game_gid,)).fetchone()

    conn.close()

    return render_template('hql_results.html',
                          hql_statements=hql_statements,
                          current_game=current_game,
                          selected_game_gid=game_gid)


@hql_bp.route('/api/hql/<int:id>')
def api_get_hql(id):
    """API: Get HQL content by ID"""
    hql_content = hql_manager.get_hql_content(id)

    if hql_content:
        return jsonify({'success': True, 'data': hql_content})
    else:
        return jsonify({'success': False, 'error': 'HQL not found'}), 404


@hql_bp.route('/api/hql/<int:id>/deactivate', methods=['POST'])
def api_deactivate_hql(id):
    """API: Deactivate an HQL statement"""
    hql_manager.deactivate_hql(id)
    return jsonify({'success': True, 'message': 'HQL已停用'})


@hql_bp.route('/api/hql/<int:id>/activate', methods=['POST'])
def api_activate_hql(id):
    """API: Activate an HQL statement"""
    from backend.core.database import get_db_connection
    conn = get_db_connection()

    # Get current HQL
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, hql_version FROM hql_statements
        WHERE id = ?
        ORDER BY hql_version DESC
        LIMIT 1
    ''', (id,))
    current = cursor.fetchone()

    if current and current['hql_version'] > 1:
        # Update to new version
        cursor.execute('''
            UPDATE hql_statements
            SET is_active = 0, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (id,))
        conn.commit()
        return jsonify({'success': True, 'message': 'HQL已激活'})

    return jsonify({'success': True, 'message': 'HQL已是最新版本，无需激活'}), 400


@hql_bp.route('/hql/manage')
def hql_manage():
    """HQL管理主页 - 自动加载当前游戏的HQL"""
    from backend.core.database import get_db_connection
    conn = get_db_connection()

    # 获取当前游戏GID（优先使用URL参数，否则使用session/cookie中的游戏ID）
    game_gid = request.args.get('game_gid', type=int)

    # 如果没有指定game_gid，尝试从session获取（需要前端设置）
    if not game_gid and 'current_game_gid' in session:
        game_gid = session['current_game_gid']

    hql_type = request.args.get('hql_type')
    show_edited_only = request.args.get('edited_only', 'false').lower() == 'true'

    # 如果没有游戏GID，重定向到游戏选择页面
    if not game_gid:
        conn.close()
        flash('请先选择游戏', 'error')
        return redirect(url_for('index'))

    # 构建查询 - 自动按当前游戏筛选
    query = '''
        SELECT hs.*, le.event_name, le.event_name_cn, g.name as game_name, g.gid
        FROM hql_statements hs
        JOIN log_events le ON hs.event_id = le.id
        JOIN games g ON le.game_gid = g.gid
        WHERE le.game_gid = ?
    '''
    params = [game_gid]

    if hql_type:
        query += ' AND hs.hql_type = ?'
        params.append(hql_type)

    if show_edited_only:
        query += ' AND hs.is_user_edited = 1'

    query += ' ORDER BY hs.updated_at DESC'

    hql_list = conn.execute(query, params).fetchall()

    # 获取当前游戏信息
    current_game = conn.execute('SELECT gid, name FROM games WHERE gid = ?', (game_gid,)).fetchone()

    conn.close()

    return render_template('hql_manage.html',
                          hql_list=hql_list,
                          current_game=current_game,
                          selected_game_gid=game_gid,
                          selected_type=hql_type,
                          edited_only=show_edited_only)


@hql_bp.route('/hql/<int:id>/edit', methods=['GET', 'POST'])
def edit_hql(id):
    """编辑HQL内容"""
    from backend.core.database import get_db_connection

    conn = get_db_connection()
    hql_data = conn.execute('''
        SELECT hs.*, le.event_name, le.event_name_cn, g.name as game_name
        FROM hql_statements hs
        JOIN log_events le ON hs.event_id = le.id
        JOIN games g ON le.game_gid = g.gid
        WHERE hs.id = ?
    ''', (id,)).fetchone()

    if not hql_data:
        flash('HQL语句不存在', 'error')
        return redirect(url_for('hql_generator.hql_manage'))

    if request.method == 'POST':
        new_content = request.form.get('hql_content')
        edit_notes = request.form.get('edit_notes', '')

        if not new_content:
            flash('HQL内容不能为空', 'error')
        else:
            # 更新HQL
            success = hql_manager.update_hql_content(id, new_content, edit_notes)

            if success:
                flash('HQL已更新', 'success')
                return redirect(url_for('hql_generator.hql_manage'))
            else:
                flash('更新失败', 'error')

    conn.close()
    return render_template('hql_edit.html', hql=dict(hql_data))


@hql_bp.route('/api/hql/<int:id>/update', methods=['PUT'])
def api_update_hql(id):
    """API: 更新HQL内容"""
    data = request.get_json()
    new_content = data.get('hql_content')
    edit_notes = data.get('edit_notes', '')

    if not new_content:
        return jsonify({'success': False, 'error': 'Content is required'}), 400

    success = hql_manager.update_hql_content(id, new_content, edit_notes)

    if success:
        return jsonify({'success': True, 'message': 'HQL已更新'})
    else:
        return jsonify({'success': False, 'error': 'Update failed'}), 500


@hql_bp.route('/api/hql/<int:id>/copy', methods=['POST'])
def api_copy_hql(id):
    """API: 复制HQL到剪贴板/下载"""
    hql_data = hql_manager.get_hql_content(id)

    if not hql_data:
        return jsonify({'success': False, 'error': 'HQL not found'}), 404

    return jsonify({
        'success': True,
        'data': {
            'hql_content': hql_data['hql_content'],
            'hql_type': hql_data['hql_type'],
            'event_name': hql_data.get('event_name')
        }
    })


@hql_bp.route('/api/hql/<int:id>/diff', methods=['GET'])
def api_hql_diff(id):
    """API: 获取HQL对比信息"""
    diff_data = hql_manager.compare_hql_versions(id)

    if not diff_data:
        return jsonify({'success': False, 'error': 'HQL not found'}), 404

    return jsonify({'success': True, 'data': diff_data})


@hql_bp.route('/api/hql/<int:id>', methods=['DELETE'])
def api_delete_hql(id):
    """API: 删除HQL语句"""
    from logger import get_logger
    logger = get_logger(__name__)
    try:
        hql_manager.delete_hql(id)
        return jsonify({'success': True, 'message': 'HQL已删除'})
    except Exception as e:
        logger.error(f"删除HQL失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@hql_bp.route('/field_builder')
def field_builder():
    """字段构建器页面 - Node System Phase 2"""
    game_gid = request.args.get('game_gid', type=int) or session.get('current_game_gid')

    # Check if there are any games in database
    result = fetch_one_as_dict('SELECT COUNT(*) as count FROM games')
    games_exist = result['count'] > 0 if result else False

    if not games_exist:
        flash('请先创建游戏', 'error')
        return redirect(url_for('games.list_games'))

    # Get events for selected game
    if game_gid:
        events = fetch_all_as_dict('''
            SELECT le.*,
                   g.gid, g.name as game_name, g.ods_db,
                   ec.name as category_name,
                   (SELECT COUNT(*) FROM event_params ep WHERE ep.event_id = le.id AND ep.is_active = 1) as param_count
            FROM log_events le
            LEFT JOIN games g ON le.game_gid = g.gid
            LEFT JOIN event_categories ec ON le.category_id = ec.id
            WHERE le.game_gid = ?
            ORDER BY le.event_name
        ''', (game_gid,))
    else:
        events = fetch_all_as_dict('''
            SELECT le.*,
                   g.gid, g.name as game_name, g.ods_db,
                   ec.name as category_name,
                   (SELECT COUNT(*) FROM event_params ep WHERE ep.event_id = le.id AND ep.is_active = 1) as param_count
            FROM log_events le
            LEFT JOIN games g ON le.game_gid = g.gid
            LEFT JOIN event_categories ec ON le.category_id = ec.id
            ORDER BY le.event_name
        ''')

    # Get current game info
    current_game = fetch_one_as_dict('SELECT * FROM games WHERE gid = ?', (game_gid,)) if game_gid else None

    # Save game_gid to session for persistence
    if game_gid:
        session['current_game_gid'] = game_gid

    return render_template('field_builder.html',
                          events=events,
                          selected_game_gid=game_gid,
                          current_game=current_game)


@hql_bp.route('/flow_builder')
def flow_builder():
    """节点连接器页面 - Node System Phase 2"""
    game_gid = request.args.get('game_gid', type=int) or session.get('current_game_gid')

    # Check if there are any games in database
    result = fetch_one_as_dict('SELECT COUNT(*) as count FROM games')
    games_exist = result['count'] > 0 if result else False

    if not games_exist:
        flash('请先创建游戏', 'error')
        return redirect(url_for('games.list_games'))

    # Get current game info
    current_game = fetch_one_as_dict('SELECT * FROM games WHERE gid = ?', (game_gid,)) if game_gid else None

    # Save game_gid to session for persistence
    if game_gid:
        session['current_game_gid'] = game_gid

    return render_template('flow_builder.html',
                          selected_game_gid=game_gid,
                          current_game=current_game)


@hql_bp.route('/canvas')
def canvas():
    """节点式画布页面 - Node System Phase 3"""
    game_gid = request.args.get('game_gid', type=int) or session.get('current_game_gid')

    # Check if there are any games in database
    result = fetch_one_as_dict('SELECT COUNT(*) as count FROM games')
    games_exist = result['count'] > 0 if result else False

    if not games_exist:
        flash('请先创建游戏', 'error')
        return redirect(url_for('games.list_games'))

    if not game_gid:
        flash('请先选择游戏', 'error')
        return redirect(url_for('games.list_games'))

    # Get current game info
    current_game = fetch_one_as_dict('SELECT * FROM games WHERE gid = ?', (game_gid,))

    if not current_game:
        flash('游戏不存在', 'error')
        return redirect(url_for('games.list_games'))

    # Save game_gid to session for persistence
    session['current_game_gid'] = game_gid

    return render_template('node_canvas.html',
                          selected_game_gid=game_gid,
                          current_game=current_game)
