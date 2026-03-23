"""
Application Factory for Event2Table.

Provides create_app() factory function that creates and configures the Flask application.
This enables testing frameworks to create app instances directly.
"""

import os
from pathlib import Path
from flask import Flask, send_from_directory
from flask_caching import Cache
from flask_cors import CORS
from flask_graphql import GraphQLView

from backend.core.config import FlaskConfig, CacheConfig, BASE_DIR
from backend.core.logging import get_logger
from backend.core.error_handlers import register_error_handlers

logger = get_logger(__name__)

FRONTEND_DIST_DIR = BASE_DIR / 'frontend' / 'dist'


def create_app():
    """Create and configure the Flask application.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(
        __name__,
        template_folder=FlaskConfig.TEMPLATE_FOLDER,
        static_folder=FlaskConfig.STATIC_FOLDER,
    )

    _configure_app(app)
    _init_extensions(app)
    _register_blueprints(app)
    _register_graphql(app)
    register_error_handlers(app)
    _register_frontend_routes(app)
    _init_database()
    _warmup_cache(app)

    return app


def _configure_app(app):
    """Apply Flask configuration settings."""
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    if debug_mode:
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
        logger.info("🔧 开发模式：已禁用所有缓存")
    else:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year
        logger.info("✅ 生产模式：已启用静态资源长期缓存")

    app.secret_key = FlaskConfig.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = FlaskConfig.MAX_CONTENT_LENGTH

    # Session security
    app.config['SESSION_COOKIE_SECURE'] = FlaskConfig.SESSION_COOKIE_SECURE
    app.config['SESSION_COOKIE_HTTPONLY'] = FlaskConfig.SESSION_COOKIE_HTTPONLY
    app.config['SESSION_COOKIE_SAMESITE'] = FlaskConfig.SESSION_COOKIE_SAMESITE
    app.config['PERMANENT_SESSION_LIFETIME'] = FlaskConfig.PERMANENT_SESSION_LIFETIME

    # Cache backend
    app.config['CACHE_TYPE'] = CacheConfig.CACHE_TYPE
    app.config['CACHE_REDIS_URL'] = CacheConfig.CACHE_REDIS_URL
    app.config['CACHE_KEY_PREFIX'] = CacheConfig.CACHE_KEY_PREFIX
    app.config['CACHE_DEFAULT_TIMEOUT'] = CacheConfig.CACHE_DEFAULT_TIMEOUT

    # Template context
    @app.context_processor
    def inject_template_vars():
        is_dev = os.environ.get('FLASK_ENV') == 'development' or debug_mode
        return {
            'config': type('Config', (), {'ENV': 'development' if is_dev else 'production'})(),
            'vite_dev_url': os.environ.get('VITE_DEV_URL', 'http://localhost:5173'),
        }

    # Cache headers
    @app.after_request
    def add_cache_headers(response):
        if 'text/html' in response.content_type:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response


def _init_extensions(app):
    """Initialize Flask extensions: cache, CORS, security, deprecation middleware."""
    # Cache
    cache = Cache()
    cache.init_app(app)
    app.cache = cache

    try:
        cache.set('health_check', 'ok', timeout=10)
        if cache.get('health_check') == 'ok':
            logger.info("✅ Redis缓存已成功连接并激活")
        else:
            logger.warning("⚠️ Redis缓存连接异常")
    except Exception as exc:
        logger.error(f"❌ Redis缓存初始化失败: {exc}")
        logger.warning("⚠️ 应用将在无缓存模式下运行")

    # CORS
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
            },
            r"/api/graphql": {
                "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
                "methods": ["GET", "POST", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
            },
        },
    )
    logger.info("✅ CORS已启用: 允许来自 localhost:5173 的请求")

    # Security
    try:
        from backend.core.security import add_security_headers, init_csrf_protection
    except ImportError:

        def add_security_headers(response):
            return response

        def init_csrf_protection(application):
            pass

    try:
        init_csrf_protection(app)
    except Exception as exc:
        logger.warning(f"CSRF protection initialization failed: {exc}")

    app.after_request(add_security_headers)

    # V1 API deprecation middleware
    try:
        from backend.api.middleware.deprecation import init_deprecation_middleware

        init_deprecation_middleware(app)
    except Exception as exc:
        logger.warning(f"V1 API deprecation middleware initialization failed: {exc}")


def _register_blueprints(app):
    """Register all API and service blueprints."""
    from backend.api import api_bp
    from backend.api.routes.hql_preview import hql_preview_bp
    from backend.api.routes.v1_adapter import v1_adapter_bp
    from backend.api.routes.health import health_bp
    from backend.api.routes.bulk_operations import bulk_bp
    from backend.api.routes.cache_monitor import cache_monitor_bp
    from backend.api.routes.canvas import canvas_bp
    from backend.api.routes.event_node_builder import event_node_builder_bp
    from backend.api.routes.common_params import common_params_bp
    from backend.api.routes.parameter_aliases import parameter_aliases_bp

    # Core API blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(hql_preview_bp)
    app.register_blueprint(v1_adapter_bp)

    # Migrated service blueprints (from backend/api/routes/)
    app.register_blueprint(event_node_builder_bp)
    app.register_blueprint(common_params_bp)
    app.register_blueprint(parameter_aliases_bp)
    app.register_blueprint(canvas_bp)
    app.register_blueprint(cache_monitor_bp)
    app.register_blueprint(bulk_bp)

    # Optional blueprints
    _register_optional_blueprint(app, 'backend.services.categories', 'categories_bp')
    _register_optional_blueprint(app, 'backend.services.async_tasks', 'async_task_bp')
    _register_optional_blueprint(app, 'backend.services.hql', 'hql_bp')
    _register_optional_blueprint(app, 'backend.services.sql_optimizer', 'sql_optimizer_bp')

    # React shell (catch-all, must be registered LAST)
    _register_optional_blueprint(app, 'backend.services.react_shell', 'react_bp')


def _register_optional_blueprint(app, module_path, blueprint_name):
    """Safely import and register an optional blueprint."""
    try:
        import importlib

        module = importlib.import_module(module_path)
        blueprint = getattr(module, blueprint_name, None)
        if blueprint:
            app.register_blueprint(blueprint)
    except ImportError:
        logger.warning(f"{blueprint_name} not found in {module_path} - module not available")


def _register_graphql(app):
    """Register the GraphQL API endpoint."""
    from backend.gql_api.schema import schema

    app.add_url_rule(
        '/api/graphql',
        view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True),
        methods=['GET', 'POST'],
    )
    logger.info("✅ GraphQL API registered at /api/graphql with GraphiQL IDE")


def _register_frontend_routes(app):
    """Register routes for serving the React SPA and static files."""

    @app.route('/')
    def index():
        try:
            return send_from_directory(str(FRONTEND_DIST_DIR), 'index.html')
        except FileNotFoundError:
            return (
                """
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
            """,
                200,
            )

    @app.route('/frontend/dist/<path:filename>')
    def serve_frontend_dist(filename):
        logger.debug(f"[Frontend Static] Serving dist file: {filename}")
        try:
            return send_from_directory(str(FRONTEND_DIST_DIR), filename)
        except FileNotFoundError:
            logger.error(f"[Frontend Static] Dist file not found: {filename}")
            raise

    @app.route('/frontend/src/<path:filename>')
    def serve_frontend_src(filename):
        frontend_src_dir = BASE_DIR / 'frontend' / 'src'
        logger.debug(f"[Frontend Static] Serving src file: {filename}")
        try:
            return send_from_directory(str(frontend_src_dir), filename)
        except FileNotFoundError:
            logger.error(f"[Frontend Static] Src file not found: {filename}")
            raise


def _init_database():
    """Initialize database, run migrations, and create indexes."""
    from backend.core.database import init_db, migrate_db, create_indexes
    from backend.core.config import get_db_path

    db_path = get_db_path()
    is_new_database = not Path(db_path).exists()

    if is_new_database:
        logger.info(f"Creating new database at {db_path}")

    init_db()

    if is_new_database:
        logger.info("Database initialized successfully")
    else:
        logger.info(f"Using existing database at {db_path}")

    try:
        migrate_db()
        logger.info("Database migrations completed successfully")
    except Exception as exc:
        logger.error(f"Database migration failed: {exc}")
        raise

    try:
        create_indexes()
        logger.info("Database indexes verified/updated")
    except Exception as exc:
        logger.warning(f"Could not create database indexes: {exc}")


def _warmup_cache(app):
    """Warm up caches on startup."""
    try:
        with app.app_context():
            from backend.core.startup.app_initializer import initialize_app

            initialize_app(app)
            logger.info("✅ 应用初始化器已启动")
    except Exception as exc:
        logger.warning(f"⚠️ 应用初始化失败: {exc}")
        logger.info("应用将在无初始化模式下运行")
        try:
            with app.app_context():
                from backend.core.cache.cache_warmer import cache_warmer

                cache_warmer.warmup_on_startup(warm_all_events=False)
                cache_warmer.start_periodic_warmup(interval_hours=1)
        except Exception as exc2:
            logger.warning(f"⚠️ 缓存预热失败: {exc2}")
            logger.info("应用将在无预热缓存模式下运行")
