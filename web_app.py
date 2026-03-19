#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event2Table - Data Warehouse HQL Generator
Main application file that registers all modules
"""

from pathlib import Path
import os
from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_caching import Cache
from flask_cors import CORS
from backend.core.database import init_db, migrate_db, get_db_connection, create_indexes
from backend.core.config import get_db_path, FlaskConfig, CacheConfig, BASE_DIR, OUTPUT_DIR
from backend.core.logging import get_logger
from backend.core.utils import fetch_all_as_dict, fetch_one_as_dict
from backend.core.cache.cache_system import cache_result
from backend.core.cache.cache_warmer import cache_warmer
from backend.core.startup.app_initializer import initialize_app
from backend.api.middleware.deprecation import init_deprecation_middleware

# Initialize logger early
logger = get_logger(__name__)

# API Blueprints - from backend/api
from backend.api import api_bp
from backend.api.routes.hql_preview_v2 import hql_preview_v2_bp  # V2 HQL Preview API
from backend.api.routes.v1_adapter import v1_adapter_bp  # V1-to-V2 Adapter API (2026-02-17)
from backend.api.routes.health import health_bp  # Health check endpoint (2026-03-01)

# GraphQL API
from backend.gql_api.schema import schema
from flask_graphql import GraphQLView

# Service Blueprints - from backend/services (standardized package imports)
# NOTE: games_bp routes are now in api_bp (backend.api.routes.games)
# Old games_bp from backend.services.games has conflicting routes - DO NOT USE
# NOTE: events_bp routes are now in api_bp (backend.api.routes.events)
# Old events_bp from backend.services.events has been removed (2026-03-19)
from backend.services.parameters import common_params_bp, parameter_aliases_bp
from backend.services.canvas import canvas_bp
from backend.services.cache_monitor import cache_monitor_bp
from backend.services.event_node_builder import event_node_builder_bp  # Event Node Builder API

# Optional blueprints (may not exist in all deployments)
try:
    from backend.services.categories import categories_bp
except ImportError:
    categories_bp = None
    logger.warning("categories_bp not found - categories module not available")

try:
    from backend.services.async_tasks import async_task_bp
except ImportError:
    async_task_bp = None
    logger.warning("async_task_bp not found - async_tasks module not available")

# flows_bp removed 2026-03-19 - migrated to backend/api/routes/flows.py

try:
    from backend.services.hql import hql_bp
except ImportError:
    hql_bp = None
    logger.warning("hql_bp not found - hql module not available")

try:
    from backend.services.bulk_operations import bulk_bp
except ImportError:
    bulk_bp = None
    logger.warning("bulk_bp not found - bulk_operations module not available")

try:
    from backend.services.react_shell import react_bp
except ImportError:
    react_bp = None
    logger.warning("react_bp not found - react_shell module not available")

try:
    from backend.services.sql_optimizer import sql_optimizer_bp
except ImportError:
    sql_optimizer_bp = None
    logger.warning("sql_optimizer_bp not found - sql_optimizer module not available")

# All modules now migrated to backend/services!

# Security (if exists)
try:
    from backend.core.security import add_security_headers, init_csrf_protection
except ImportError:
    def add_security_headers(response): return response
    def init_csrf_protection(app): pass


app = Flask(__name__,
            template_folder=FlaskConfig.TEMPLATE_FOLDER,
            static_folder=FlaskConfig.STATIC_FOLDER)

# 环境配置
DEBUG_MODE = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

if DEBUG_MODE:
    # 开发模式：禁用所有缓存，快速迭代
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    logger.info("🔧 开发模式：已禁用所有缓存")
else:
    # 生产模式：使用哈希文件名 + 长期缓存
    # JS/CSS 文件带有内容哈希（如 index-DSrejIbn.js）
    # 当文件变化时哈希自动变化，浏览器自动请求新文件
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1年缓存
    logger.info("✅ 生产模式：已启用静态资源长期缓存")

app.secret_key = FlaskConfig.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = FlaskConfig.MAX_CONTENT_LENGTH

# Security configuration
app.config['SESSION_COOKIE_SECURE'] = FlaskConfig.SESSION_COOKIE_SECURE
app.config['SESSION_COOKIE_HTTPONLY'] = FlaskConfig.SESSION_COOKIE_HTTPONLY
app.config['SESSION_COOKIE_SAMESITE'] = FlaskConfig.SESSION_COOKIE_SAMESITE
app.config['PERMANENT_SESSION_LIFETIME'] = FlaskConfig.PERMANENT_SESSION_LIFETIME

# Cache configuration
app.config['CACHE_TYPE'] = CacheConfig.CACHE_TYPE
app.config['CACHE_REDIS_URL'] = CacheConfig.CACHE_REDIS_URL
app.config['CACHE_KEY_PREFIX'] = CacheConfig.CACHE_KEY_PREFIX
app.config['CACHE_DEFAULT_TIMEOUT'] = CacheConfig.CACHE_DEFAULT_TIMEOUT

# Initialize cache
cache = Cache()
cache.init_app(app)

# Attach cache to app for access via current_app.cache
app.cache = cache

# CORS configuration - Allow frontend-originated requests
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    },
    r"/api/graphql": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
logger.info("✅ CORS已启用: 允许来自 localhost:5173 的请求")

# Check cache status and log
try:
    # Test cache connection
    cache.set('health_check', 'ok', timeout=10)
    result = cache.get('health_check')
    if result == 'ok':
        logger.info("✅ Redis缓存已成功连接并激活")
    else:
        logger.warning("⚠️ Redis缓存连接异常")
except Exception as e:
    logger.error(f"❌ Redis缓存初始化失败: {e}")
    logger.warning("⚠️ 应用将在无缓存模式下运行")

# Register security middleware
try:
    init_csrf_protection(app)
except Exception as e:
    logger.warning(f"CSRF protection initialization failed: {e}")

app.after_request(add_security_headers)

# Register V1 API deprecation middleware
try:
    init_deprecation_middleware(app)
except Exception as e:
    logger.warning(f"V1 API deprecation middleware initialization failed: {e}")

# 缓存控制 - 开发模式禁用 HTML 缓存
@app.after_request
def add_cache_headers(response):
    """Disable HTML caching to ensure updates take effect immediately.
    JS/CSS files use content-hash filenames for long-term caching."""
    if 'text/html' in response.content_type:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# 上下文处理器 - 为模板提供全局变量 🆕
@app.context_processor
def inject_template_vars():
    """
    为模板提供全局变量：
    - config.ENV: 当前环境（development/production）
    - vite_dev_url: Vite开发服务器URL
    """
    # 检测是否为开发环境
    is_dev = (
        os.environ.get('FLASK_ENV') == 'development' or
        DEBUG_MODE
    )

    env = 'development' if is_dev else 'production'

    # Vite开发服务器URL（仅在开发模式下使用）
    vite_dev_url = os.environ.get('VITE_DEV_URL', 'http://localhost:5173')

    return {
        'config': type('Config', (), {'ENV': env})(),
        'vite_dev_url': vite_dev_url
    }

# Serve frontend static files (React app)
FRONTEND_DIST_DIR = BASE_DIR / 'frontend' / 'dist'

@app.route('/frontend/dist/<path:filename>')
def serve_frontend_dist(filename):
    """Serve React app static files from frontend/dist/"""
    logger.debug(f"[Frontend Static] Serving dist file: {filename}")
    try:
        return send_from_directory(str(FRONTEND_DIST_DIR), filename)
    except FileNotFoundError:
        logger.error(f"[Frontend Static] Dist file not found: {filename}")
        raise

@app.route('/frontend/src/<path:filename>')
def serve_frontend_src(filename):
    """Serve React app source files (for dev mode)"""
    frontend_src_dir = BASE_DIR / 'frontend' / 'src'
    logger.debug(f"[Frontend Static] Serving src file: {filename}")
    try:
        return send_from_directory(str(frontend_src_dir), filename)
    except FileNotFoundError:
        logger.error(f"[Frontend Static] Src file not found: {filename}")
        raise

# Root route - serve React SPA
@app.route('/')
def index():
    """Serve React Single Page Application"""
    try:
        return send_from_directory(str(FRONTEND_DIST_DIR), 'index.html')
    except FileNotFoundError:
        return """
        <h1>Event2Table API</h1>
        <p>Frontend not built. Please run:</p>
        <pre>cd frontend && npm run build</pre>
        <h2>Available API Endpoints:</h2>
        <ul>
            <li><a href="/api/games">GET /api/games</a></li>
            <li><a href="/api/events">GET /api/events</a></li>
            <li><a href="/api/parameters/all">GET /api/parameters/all</a></li>
            <li><a href="/api/categories">GET /api/categories</a></li>
            <li><a href="/hql-preview-v2/api/status">GET /hql-preview-v2/api/status</a></li>
        </ul>
        """, 200

# Initialize database (always call init_db first to ensure schema exists)
db_initialized = False
if not Path(get_db_path()).exists():
    db_initialized = True
    logger.info(f"Creating new database at {get_db_path()}")

# Always call init_db() to ensure all tables exist (CREATE TABLE IF NOT EXISTS is safe)
init_db()
if db_initialized:
    logger.info("Database initialized successfully")
else:
    logger.info(f"Using existing database at {get_db_path()}")

# Run database migrations (for both new and existing databases)
try:
    migrate_db()
    logger.info("Database migrations completed successfully")
except Exception as e:
    logger.error(f"Database migration failed: {e}")
    raise

# Create indexes for performance optimization
try:
    create_indexes()
    if db_initialized:
        logger.info("Database indexes created successfully")
    else:
        logger.info("Database indexes verified/updated")
except Exception as e:
    logger.warning(f"Could not create database indexes: {e}")

# Register all blueprints
# Note: Register API blueprints first, then React shell as catch-all
app.register_blueprint(health_bp)  # Health check endpoint (/api/health) - 2026-03-01
app.register_blueprint(api_bp)  # API endpoints (/api/*)
app.register_blueprint(hql_preview_v2_bp)  # HQL Preview V2 API (/hql-preview-v2/*)
app.register_blueprint(v1_adapter_bp)  # V1-to-V2 Adapter API (/api/v1-adapter/*) (2026-02-17)
app.register_blueprint(event_node_builder_bp)  # Event Node Builder API (/event_node_builder/*)

# Register GraphQL API endpoint
app.add_url_rule('/api/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True), methods=['GET', 'POST'])
logger.info("✅ GraphQL API registered at /api/graphql with GraphiQL IDE")
if bulk_bp:
    app.register_blueprint(bulk_bp)  # Bulk operations
app.register_blueprint(cache_monitor_bp)  # Cache monitoring (/admin/cache/*)
app.register_blueprint(canvas_bp)  # Canvas pages and API (/canvas/*, /api/canvas/*)
# event_nodes_bp removed 2026-03-01 (replaced by GraphQL + event_node_builder_bp)
app.register_blueprint(parameter_aliases_bp)  # Parameter aliases
if async_task_bp:
    app.register_blueprint(async_task_bp)  # Async tasks
if sql_optimizer_bp:
    app.register_blueprint(sql_optimizer_bp)  # SQL optimizer
# flows_bp removed 2026-03-19 - migrated to backend/api/routes/flows.py
if hql_bp:
    app.register_blueprint(hql_bp)  # HQL management

app.register_blueprint(common_params_bp)

# Register React shell LAST as catch-all for all frontend routes
if react_bp:
    app.register_blueprint(react_bp)


# Global JSON error handlers for API endpoints
API_ROUTE_PREFIXES = ('/api/', '/canvas/', '/hql-preview-v2/')


def _is_api_request():
    return request.path.startswith(API_ROUTE_PREFIXES)


@app.errorhandler(400)
def bad_request_error(error):
    """Handle 400 Bad Request errors with JSON response for API routes"""
    if _is_api_request():
        return jsonify({
            'success': False,
            'error': 'Bad Request',
            'message': str(error),
            'timestamp': None
        }), 400
    return error  # Let default error handler deal with non-API routes


@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 Not Found errors with JSON response for API routes, or serve SPA for frontend routes"""
    if _is_api_request():
        from datetime import datetime
        return jsonify({
            'success': False,
            'error': 'Resource not found',
            'message': 'The requested resource was not found',
            'timestamp': datetime.now().isoformat()
        }), 404

    # For frontend routes (React SPA), serve index.html
    # This enables client-side routing (React Router)
    try:
        return send_from_directory(str(FRONTEND_DIST_DIR), 'index.html')
    except FileNotFoundError:
        # Frontend not built, return default error page
        return render_template('errors/404.html'), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    """Handle 405 Method Not Allowed errors with JSON response for API routes"""
    if _is_api_request():
        return jsonify({
            'success': False,
            'error': 'Method Not Allowed',
            'message': 'The method is not allowed for the requested URL',
            'timestamp': None
        }), 405
    return error  # Let default error handler deal with non-API routes


@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 Internal Server Error with JSON response for API routes"""
    if _is_api_request():
        return jsonify({
            'success': False,
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'timestamp': None
        }), 500
    return error  # Let default error handler deal with non-API routes

# Cache warming on startup (after all blueprints registered)
# Use app.app_context() to ensure cache utilities can access current_app
try:
    with app.app_context():
        # 使用新的应用初始化器
        initialize_app(app)
        logger.info("✅ 应用初始化器已启动")
except Exception as e:
    logger.warning(f"⚠️ 应用初始化失败: {e}")
    logger.info("应用将在无初始化模式下运行")
    # 降级到旧的缓存预热方式
    try:
        with app.app_context():
            cache_warmer.warmup_on_startup(warm_all_events=False)
            cache_warmer.start_periodic_warmup(interval_hours=1)
    except Exception as e2:
        logger.warning(f"⚠️ 缓存预热失败: {e2}")
        logger.info("应用将在无预热缓存模式下运行")


# Cached functions for database queries
@cache_result('games:all_with_counts', timeout=CacheConfig.CACHE_TIMEOUT_GAMES)
def get_games_with_counts():
    """Get games list with event and parameter counts (cached)"""
    return fetch_all_as_dict('''
        SELECT g.*,
               (SELECT COUNT(*) FROM log_events WHERE game_id = g.id) as event_count,
               (SELECT COUNT(*) FROM event_params ep
                 JOIN log_events e ON ep.event_id = e.id
                 WHERE e.game_id = g.id AND ep.is_active = 1) as param_count
        FROM games g
        ORDER BY g.id
    ''')




if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("Event2Table application started")
    logger.info("=" * 80)
    logger.info(f"Database: {get_db_path()}")
    logger.info(f"Output Directory: {OUTPUT_DIR}")
    logger.info(f"Templates Directory: {FlaskConfig.TEMPLATE_FOLDER}")
    logger.info(f"Base Directory: {BASE_DIR}")
    logger.info(f"Debug Mode: {FlaskConfig.DEBUG}")
    logger.info("")
    logger.info("Starting web server...")
    logger.info(f"Access the application at: http://{FlaskConfig.HOST}:{FlaskConfig.PORT}")
    logger.info("=" * 80)

    logger.info("=" * 80)

    app.run(debug=FlaskConfig.DEBUG,
            host=FlaskConfig.HOST,
            port=FlaskConfig.PORT,
            use_reloader=False)
