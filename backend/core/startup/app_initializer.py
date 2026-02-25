"""
应用启动初始化器

自动化启动缓存预热、性能监控、事件处理器等
"""

import logging
from flask import Flask
from backend.core.cache.cache_warmer import CacheWarmer
from backend.core.cache.statistics import CacheStatistics
# NOTE: DDD event system removed in architecture migration (2026-02-25)
# Event handlers are now managed directly in Service layer with CacheInvalidator
# from backend.infrastructure.events.event_handlers import register_event_handlers, unregister_event_handlers

logger = logging.getLogger(__name__)


class AppInitializer:
    """
    应用启动初始化器
    
    职责:
    - 自动启动缓存预热
    - 自动启动性能监控
    - 注册事件处理器
    - 健康检查
    """
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.cache_warmer = CacheWarmer()
        self.cache_stats = CacheStatistics()
        self._initialized = False
    
    def init_app(self, app: Flask):
        """
        初始化Flask应用
        
        Args:
            app: Flask应用实例
        """
        self.app = app
        self._initialize()
    
    def _initialize(self):
        """执行初始化流程"""
        if self._initialized:
            logger.warning("应用已初始化,跳过重复初始化")
            return
        
        logger.info("=" * 60)
        logger.info("开始应用初始化...")
        logger.info("=" * 60)
        
        try:
            # 1. 注册事件处理器
            # NOTE: DDD event system removed (2026-02-25)
            # Event handlers are now managed directly in Service layer
            # self._register_event_handlers()

            # 2. 启动缓存预热
            self._start_cache_warming()
            
            # 3. 启动性能监控
            self._start_performance_monitoring()
            
            # 4. 注册关闭钩子
            self._register_shutdown_hooks()
            
            # 5. 健康检查
            self._health_check()
            
            self._initialized = True
            logger.info("=" * 60)
            logger.info("应用初始化完成!")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"应用初始化失败: {e}", exc_info=True)
            raise
    
    def _register_event_handlers(self):
        """注册领域事件处理器"""
        # NOTE: DDD event system removed (2026-02-25)
        # Event handlers are now managed directly in Service layer
        logger.info("步骤1: 跳过DDD事件处理器注册(已迁移到Service层)...")

    def _start_cache_warming(self):
        """启动缓存预热"""
        logger.info("步骤1: 启动缓存预热...")
        try:
            # 预热游戏数据
            logger.info("  - 预热游戏数据...")
            self.cache_warmer.warmup_games()
            
            # 预热事件数据
            logger.info("  - 预热事件数据...")
            self.cache_warmer.warmup_events()
            
            # 预热参数数据
            logger.info("  - 预热参数数据...")
            self.cache_warmer.warmup_parameters()
            
            logger.info("✓ 缓存预热完成")
        except Exception as e:
            logger.warning(f"✗ 缓存预热失败(非致命错误): {e}")
            # 缓存预热失败不影响应用启动
    
    def _start_performance_monitoring(self):
        """启动性能监控"""
        logger.info("步骤2: 启动性能监控...")
        try:
            # 启动缓存统计
            self.cache_stats.start_monitoring()
            
            logger.info("✓ 性能监控启动成功")
        except Exception as e:
            logger.warning(f"✗ 性能监控启动失败(非致命错误): {e}")
            # 性能监控失败不影响应用启动
    
    def _register_shutdown_hooks(self):
        """注册关闭钩子"""
        logger.info("步骤3: 注册关闭钩子...")
        try:
            import atexit
            atexit.register(self._shutdown)
            logger.info("✓ 关闭钩子注册成功")
        except Exception as e:
            logger.error(f"✗ 关闭钩子注册失败: {e}")
            raise
    
    def _health_check(self):
        """健康检查"""
        logger.info("步骤4: 执行健康检查...")
        try:
            # 检查缓存系统
            cache_health = self._check_cache_health()
            
            # 检查数据库连接
            db_health = self._check_database_health()
            
            # 检查Redis连接
            redis_health = self._check_redis_health()
            
            if cache_health and db_health and redis_health:
                logger.info("✓ 健康检查通过")
            else:
                logger.warning("⚠ 健康检查发现问题,但应用仍可运行")
                
        except Exception as e:
            logger.warning(f"✗ 健康检查失败(非致命错误): {e}")
    
    def _check_cache_health(self) -> bool:
        """检查缓存系统健康状态"""
        try:
            from backend.core.cache.cache_system import HierarchicalCache
            cache = HierarchicalCache()
            stats = cache.get_stats()
            
            logger.info(f"  - 缓存系统: L1大小={stats.get('l1_size', 0)}, L2连接={stats.get('l2_connected', False)}")
            return True
        except Exception as e:
            logger.warning(f"  - 缓存系统检查失败: {e}")
            return False
    
    def _check_database_health(self) -> bool:
        """检查数据库健康状态"""
        try:
            from backend.core.database import db
            # 执行简单查询
            db.session.execute('SELECT 1')
            logger.info("  - 数据库: 连接正常")
            return True
        except Exception as e:
            logger.warning(f"  - 数据库检查失败: {e}")
            return False
    
    def _check_redis_health(self) -> bool:
        """检查Redis健康状态"""
        try:
            import redis
            from backend.config import Config
            
            client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB
            )
            client.ping()
            logger.info("  - Redis: 连接正常")
            return True
        except Exception as e:
            logger.warning(f"  - Redis检查失败: {e}")
            return False
    
    def _shutdown(self):
        """应用关闭时的清理工作"""
        logger.info("=" * 60)
        logger.info("开始应用关闭清理...")
        logger.info("=" * 60)
        
        try:
            # 1. 注销事件处理器
            # NOTE: DDD event system removed (2026-02-25)
            logger.info("步骤1: 跳过DDD事件处理器注销(已迁移到Service层)...")

            # 2. 停止性能监控
            logger.info("步骤2: 停止性能监控...")
            self.cache_stats.stop_monitoring()
            logger.info("✓ 性能监控已停止")
            
            # 3. 保存缓存统计
            logger.info("步骤3: 保存缓存统计...")
            self.cache_stats.save_snapshot()
            logger.info("✓ 缓存统计已保存")
            
            logger.info("=" * 60)
            logger.info("应用关闭清理完成!")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"应用关闭清理失败: {e}", exc_info=True)


# 全局初始化器实例
app_initializer = AppInitializer()


def initialize_app(app: Flask):
    """
    初始化Flask应用
    
    Args:
        app: Flask应用实例
    """
    app_initializer.init_app(app)
