#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加载预置HQL模板数据

从JSON文件加载预置模板并插入数据库
"""

import json
import logging
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.core.database.database import get_db_connection
from backend.core.utils import execute_write

logger = logging.getLogger(__name__)


def load_preset_templates():
    """加载预置模板到数据库"""
    
    # 读取预置模板文件
    preset_file = project_root / "backend" / "data" / "presets" / "hql_templates.json"
    
    if not preset_file.exists():
        logger.error(f"Preset templates file not found: {preset_file}")
        return False
    
    try:
        with open(preset_file, 'r', encoding='utf-8') as f:
            preset_data = json.load(f)
        
        templates = preset_data.get('templates', [])
        
        if not templates:
            logger.warning("No templates found in preset file")
            return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        loaded_count = 0
        skipped_count = 0
        
        for template in templates:
            try:
                # 检查模板是否已存在
                cursor.execute(
                    "SELECT id FROM hql_templates WHERE name = ?",
                    (template['name'],)
                )
                
                if cursor.fetchone():
                    logger.info(f"Template '{template['name']}' already exists, skipping")
                    skipped_count += 1
                    continue
                
                # 插入模板
                import json as json_module
                
                query = """
                    INSERT INTO hql_templates (
                        name, display_name, category, subcategory,
                        hql_content, variables, description, tags,
                        is_featured, is_system, is_active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                params = (
                    template['name'],
                    template['display_name'],
                    template['category'],
                    template.get('subcategory'),
                    template['hql_content'],
                    json_module.dumps(template.get('variables', {}), ensure_ascii=False),
                    template.get('description'),
                    json_module.dumps(template.get('tags', []), ensure_ascii=False),
                    1 if template.get('is_featured', False) else 0,
                    1 if template.get('is_system', False) else 0,
                    1
                )
                
                cursor.execute(query, params)
                loaded_count += 1
                logger.info(f"Loaded template: {template['name']}")
                
            except Exception as e:
                logger.error(f"Failed to load template '{template['name']}': {e}")
                continue
        
        conn.commit()
        conn.close()
        
        logger.info(f"Successfully loaded {loaded_count} templates, skipped {skipped_count}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load preset templates: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    success = load_preset_templates()
    sys.exit(0 if success else 1)
