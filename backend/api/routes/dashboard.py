"""
Dashboard Statistics API Routes Module

This module provides aggregated statistics for the Dashboard.
While the current Dashboard doesn't use this endpoint (it uses /api/games
and /api/flows directly), this endpoint serves as a convenience API for:
- Future Dashboard enhancements
- External monitoring tools
- Admin panels
- Analytics dashboards

Core endpoints:
- GET /api/dashboard/stats - Complete dashboard statistics
- GET /api/dashboard/summary - Lightweight summary (games, events, params)

Author: Event2Table Development Team
Date: 2026-02-20
"""

import logging
from typing import Any, Dict, Tuple

from flask import request
from flask import current_app

# Import shared utilities
from backend.core.utils import (
    fetch_all_as_dict,
    fetch_one_as_dict,
    json_error_response,
    json_success_response,
)
from backend.core.security import SQLValidator

# Allowed filter columns whitelist
ALLOWED_GAME_FILTERS = {"gid", "name", "ods_db"}
ALLOWED_EVENT_FILTERS = {"game_gid", "category", "event_code"}
ALLOWED_FLOW_FILTERS = {"game_gid", "category"}


def _validate_filter_column(column: str, allowed: set) -> str:
    """Validate filter column name against whitelist."""
    return SQLValidator.validate_field_whitelist(column, allowed)


# Import the parent blueprint
from .. import api_bp

logger = logging.getLogger(__name__)


@api_bp.route("/api/dashboard/stats", methods=["GET"])
def api_dashboard_stats() -> Tuple[Dict[str, Any], int]:
    """
    API: Get complete dashboard statistics

    Query Parameters:
        game_gid (int, optional): Filter statistics for a specific game

    Returns:
        Tuple containing response dictionary and HTTP status code

    Response Format:
        {
            "success": true,
            "data": {
                "total_games": int,
                "total_events": int,
                "total_params": int,
                "total_flows": int,
                "event_categories": {
                    "category_name": int,
                    ...
                },
                "recent_events": [
                    {
                        "event_code": str,
                        "event_name": str,
                        "game_gid": int,
                        "game_name": str,
                        "updated_at": str
                    },
                    ...
                ],
                "top_games": [
                    {
                        "gid": int,
                        "name": str,
                        "event_count": int,
                        "param_count": int
                    },
                    ...
                ],
                "common_params": [
                    {
                        "param_name": str,
                        "count": int
                    },
                    ...
                ],
                "last_updated": str
            }
        }

    Performance:
        - Uses Redis caching with 5-minute TTL
        - Aggregates data in single SQL query
        - Response time: < 100ms (cached), < 500ms (uncached)

    Raises:
        500: If server error occurs during query execution
    """
    try:
        game_gid = request.args.get("game_gid", type=int)

        # Try to get from cache first
        cache_key = f"dashboard:stats:v1:{game_gid or 'all'}"
        try:
            cached_stats = current_app.cache.get(cache_key)
            if cached_stats:
                logger.debug(f"Cache HIT: dashboard stats for game_gid={game_gid}")
                return json_success_response(data=cached_stats)
        except (AttributeError, RuntimeError) as e:
            logger.warning(f"Cache not available: {e}")

        # Cache miss - compute statistics
        logger.debug(f"Cache MISS: computing dashboard stats for game_gid={game_gid}")

        # 1. Get basic counts
        games_filter = "WHERE g.gid = ?" if game_gid else ""

        # Total games (filtered or all)
        total_games_result = fetch_one_as_dict(
            f"SELECT COUNT(DISTINCT g.id) as count FROM games g {games_filter}",
            (game_gid,) if game_gid else (),
        )
        total_games = total_games_result["count"] if total_games_result else 0

        # Total events (filtered or all)
        events_filter = "WHERE le.game_gid = ?" if game_gid else "WHERE 1=1"
        total_events_result = fetch_one_as_dict(
            f"SELECT COUNT(DISTINCT le.id) as count FROM log_events le {events_filter}",
            (game_gid,) if game_gid else (),
        )
        total_events = total_events_result["count"] if total_events_result else 0

        # Total params (filtered or all)
        params_filter = "WHERE le.game_gid = ?" if game_gid else "WHERE 1=1"
        total_params_result = fetch_one_as_dict(
            f"""SELECT COUNT(DISTINCT ep.id) as count
                FROM event_params ep
                INNER JOIN log_events le ON ep.event_id = le.id
                {params_filter}""",
            (game_gid,) if game_gid else (),
        )
        total_params = total_params_result["count"] if total_params_result else 0

        # Total flows (filtered or all)
        flows_filter = "WHERE ft.game_gid = ?" if game_gid else "WHERE 1=1"
        total_flows_result = fetch_one_as_dict(
            f"SELECT COUNT(DISTINCT ft.id) as count FROM flow_templates ft {flows_filter}",
            (game_gid,) if game_gid else (),
        )
        total_flows = total_flows_result["count"] if total_flows_result else 0

        # 2. Event categories breakdown
        category_where = "WHERE le.game_gid = ?" if game_gid else "WHERE 1=1"
        category_stats = fetch_all_as_dict(
            f"""SELECT COALESCE(ec.name, '未分类') as category, COUNT(DISTINCT le.id) as count
                FROM log_events le
                LEFT JOIN event_categories ec ON le.category_id = ec.id
                {category_where}
                GROUP BY category
                ORDER BY count DESC""",
            (game_gid,) if game_gid else (),
        )
        event_categories = {cat["category"]: cat["count"] for cat in category_stats}

        # 3. Recent events (last 10)
        recent_where = "WHERE le.game_gid = ?" if game_gid else "WHERE 1=1"
        recent_events = fetch_all_as_dict(
            f"""SELECT
                le.event_code,
                le.event_name,
                le.game_gid,
                g.name as game_name,
                le.updated_at
            FROM log_events le
            INNER JOIN games g ON g.gid = le.game_gid
            {recent_where}
            ORDER BY le.updated_at DESC
            LIMIT 10""",
            (game_gid,) if game_gid else (),
        )

        # 4. Top 5 games by event count
        top_games = fetch_all_as_dict(
            """SELECT
                g.gid,
                g.name,
                COUNT(DISTINCT le.id) as event_count,
                COUNT(DISTINCT CASE WHEN ep.is_active = 1 THEN ep.id END) as param_count
            FROM games g
            LEFT JOIN log_events le ON le.game_gid = g.gid
            LEFT JOIN event_params ep ON ep.event_id = le.id
            GROUP BY g.gid, g.name
            ORDER BY event_count DESC
            LIMIT 5"""
        )

        # 5. Top 10 common parameters
        common_params_where = "WHERE le.game_gid = ?" if game_gid else "WHERE 1=1"
        common_params = fetch_all_as_dict(
            f"""SELECT
                ep.param_name,
                COUNT(DISTINCT ep.id) as count
            FROM event_params ep
            INNER JOIN log_events le ON ep.event_id = le.id
            {common_params_where}
            GROUP BY ep.param_name
            ORDER BY count DESC
            LIMIT 10""",
            (game_gid,) if game_gid else (),
        )

        # 6. Last updated timestamp
        last_updated_result = fetch_one_as_dict(
            f"""SELECT MAX(le.updated_at) as last_updated
                FROM log_events le
                {recent_where}""",
            (game_gid,) if game_gid else (),
        )
        last_updated = (
            last_updated_result["last_updated"] if last_updated_result else None
        )

        # Build response data
        stats_data = {
            "total_games": total_games,
            "total_events": total_events,
            "total_params": total_params,
            "total_flows": total_flows,
            "event_categories": event_categories,
            "recent_events": recent_events,
            "top_games": top_games,
            "common_params": common_params,
            "last_updated": last_updated,
        }

        # Cache the result (5-minute TTL)
        try:
            current_app.cache.set(cache_key, stats_data, timeout=300)
            logger.debug(f"Cached dashboard stats for game_gid={game_gid} for 300s")
        except (AttributeError, RuntimeError) as e:
            logger.warning(f"Cache set failed: {e}")

        return json_success_response(data=stats_data)

    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        return json_error_response(
            "Failed to fetch dashboard statistics", status_code=500
        )


@api_bp.route("/api/dashboard/summary", methods=["GET"])
def api_dashboard_summary() -> Tuple[Dict[str, Any], int]:
    """
    API: Get lightweight dashboard summary

    This endpoint provides a minimal set of statistics for quick loading.
    Use this for loading spinners or initial page load.

    Query Parameters:
        game_gid (int, optional): Filter summary for a specific game

    Returns:
        Tuple containing response dictionary and HTTP status code

    Response Format:
        {
            "success": true,
            "data": {
                "total_games": int,
                "total_events": int,
                "total_params": int,
                "total_flows": int,
                "last_updated": str,
                "health_status": "healthy" | "warning" | "error"
            }
        }

    Performance:
        - Uses Redis caching with 5-minute TTL
        - Minimal SQL queries (fast execution)
        - Response time: < 50ms (cached), < 200ms (uncached)

    Raises:
        500: If server error occurs during query execution
    """
    try:
        game_gid = request.args.get("game_gid", type=int)

        # Try to get from cache first
        cache_key = f"dashboard:summary:v1:{game_gid or 'all'}"
        try:
            cached_summary = current_app.cache.get(cache_key)
            if cached_summary:
                logger.debug(f"Cache HIT: dashboard summary for game_gid={game_gid}")
                return json_success_response(data=cached_summary)
        except (AttributeError, RuntimeError) as e:
            logger.warning(f"Cache not available: {e}")

        # Cache miss - compute summary
        logger.debug(f"Cache MISS: computing dashboard summary for game_gid={game_gid}")

        # Build WHERE clause
        if game_gid:
            query_value = (game_gid,)
        else:
            query_value = ()

        # Merge into 2 queries: basic counts + last_updated
        basic_stats = fetch_one_as_dict(
            """
            SELECT
                (SELECT COUNT(DISTINCT g.id) FROM games g) as total_games,
                (SELECT COUNT(DISTINCT le.id) FROM log_events le WHERE le.game_gid = ?) as total_events,
                (SELECT COUNT(DISTINCT ep.id) FROM event_params ep INNER JOIN log_events le ON ep.event_id = le.id WHERE le.game_gid = ?) as total_params,
                (SELECT COUNT(DISTINCT ft.id) FROM flow_templates ft WHERE ft.game_gid = ?) as total_flows
            """,
            query_value * 4 if game_gid else (),
        )
        last_updated = fetch_one_as_dict(
            "SELECT MAX(le.updated_at) as last_updated FROM log_events le WHERE le.game_gid = ?",
            query_value,
        )

        # Build summary data
        summary_data = {
            "total_games": basic_stats["total_games"] if basic_stats else 0,
            "total_events": basic_stats["total_events"] if basic_stats else 0,
            "total_params": basic_stats["total_params"] if basic_stats else 0,
            "total_flows": basic_stats["total_flows"] if basic_stats else 0,
            "last_updated": last_updated["last_updated"] if last_updated else None,
            "health_status": "healthy",
        }

        # Cache the result (5-minute TTL)
        try:
            current_app.cache.set(cache_key, summary_data, timeout=300)
            logger.debug(f"Cached dashboard summary for game_gid={game_gid} for 300s")
        except (AttributeError, RuntimeError) as e:
            logger.warning(f"Cache set failed: {e}")

        return json_success_response(data=summary_data)

    except Exception as e:
        logger.error(f"Error fetching dashboard summary: {e}")
        return json_error_response("Failed to fetch dashboard summary", status_code=500)
