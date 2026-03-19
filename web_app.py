#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Event2Table - Data Warehouse HQL Generator

Entry point that delegates to the application factory.
"""

from backend.app_factory import create_app
from backend.core.config import FlaskConfig, OUTPUT_DIR, BASE_DIR
from backend.core.logging import get_logger

logger = get_logger(__name__)

app = create_app()

if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("Event2Table application started")
    logger.info("=" * 80)
    logger.info(f"Database: {FlaskConfig.TEMPLATE_FOLDER}")
    logger.info(f"Output Directory: {OUTPUT_DIR}")
    logger.info(f"Base Directory: {BASE_DIR}")
    logger.info(f"Debug Mode: {FlaskConfig.DEBUG}")
    logger.info("")
    logger.info("Starting web server...")
    logger.info(f"Access the application at: http://{FlaskConfig.HOST}:{FlaskConfig.PORT}")
    logger.info("=" * 80)

    app.run(
        debug=FlaskConfig.DEBUG,
        host=FlaskConfig.HOST,
        port=FlaskConfig.PORT,
        use_reloader=False,
    )
