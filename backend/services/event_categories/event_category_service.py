"""
Event Category Service

Business logic layer for event category operations.
Follows Entity-Repository-Service pattern.

Version: 1.0.0
"""

from typing import List, Optional, Dict
import logging

from backend.models.entities_category import EventCategoryEntity
from backend.models.repositories.category_repository import CategoryRepository
from backend.core.cache.decorators import cached, cache_invalidate
from backend.core.cache.cache_system import CacheInvalidator

logger = logging.getLogger(__name__)


class EventCategoryService:
    """
    Event category business service.

    This service handles all business logic for event category operations,
    including CRUD, game-scoped queries, statistics, and batch operations.
    """

    def __init__(self):
        """Initialize service with required repositories and utilities."""
        self.category_repo = CategoryRepository()
        self.event_repo = CategoryRepository()
        self.cache_invalidator = CacheInvalidator()

    # ================================================================
    # Basic CRUD Operations
    # ================================================================

    @cached(ttl=3600, key_prefix="event_categories")
    def get_by_id(self, category_id: int) -> Optional[EventCategoryEntity]:
        """
        Get category by ID.

        Args:
            category_id: Category ID

        Returns:
            EventCategoryEntity if found, None otherwise

        Example:
            >>> service = EventCategoryService()
            >>> category = service.get_by_id(1)
            >>> print(category.name)
            '充值/付费'
        """
        if not category_id or category_id <= 0:
            raise ValueError("Invalid category ID")

        category_data = self.category_repo.find_by_id(category_id)
        if not category_data:
            return None

        return EventCategoryEntity(**category_data)

    @cached(ttl=3600, key_prefix="event_categories")
    def get_all(self, game_gid: Optional[int] = None) -> List[EventCategoryEntity]:
        """
        Get all categories, optionally filtered by game.

        Args:
            game_gid: Optional game GID filter

        Returns:
            List of EventCategoryEntity objects

        Example:
            >>> service = EventCategoryService()
            >>> categories = service.get_all(game_gid=10000147)
            >>> len(categories)
            5
        """
        if game_gid is not None:
            if game_gid <= 0:
                raise ValueError("Invalid game GID")
            categories_data = self.category_repo.find_by_game_gid(game_gid)
        else:
            categories_data = self.category_repo.find_all()

        return [EventCategoryEntity(**data) for data in categories_data]

    @cache_invalidate
    def create(self, category_data: EventCategoryEntity) -> EventCategoryEntity:
        """
        Create a new event category.

        Args:
            category_data: EventCategoryEntity with category data

        Returns:
            Created EventCategoryEntity with ID

        Raises:
            ValueError: If validation fails

        Example:
            >>> service = EventCategoryService()
            >>> category = service.create(EventCategoryEntity(
            ...     name="test",
            ...     display_name="Test",
            ...     game_gid=10000147
            ... ))
            >>> print(category.id)
            10
        """
        # Validate required fields
        if not category_data.name or not category_data.name.strip():
            raise ValueError("Category name is required")

        if not category_data.game_gid or category_data.game_gid <= 0:
            raise ValueError("Valid game GID is required")

        # Check for duplicate name in the same game
        existing = self.category_repo.find_by_name_and_game(
            category_data.name.strip(),
            category_data.game_gid
        )
        if existing:
            raise ValueError(
                f"Category '{category_data.name}' already exists for game {category_data.game_gid}"
            )

        # Create category
        category_dict = category_data.model_dump(exclude={'id', 'created_at', 'updated_at'})
        category_dict['name'] = category_dict['name'].strip()

        category_id = self.category_repo.create(category_dict)

        # Fetch and return the created category
        created_data = self.category_repo.find_by_id(category_id)
        if not created_data:
            raise RuntimeError("Failed to retrieve created category")

        logger.info(f"Created event category: {category_id} - {category_data.name}")
        return EventCategoryEntity(**created_data)

    @cache_invalidate
    def update(self, category_id: int, updates: dict) -> EventCategoryEntity:
        """
        Update an event category.

        Args:
            category_id: Category ID
            updates: Dictionary of fields to update

        Returns:
            Updated EventCategoryEntity

        Raises:
            ValueError: If validation fails or category not found

        Example:
            >>> service = EventCategoryService()
            >>> category = service.update(1, {"display_name": "New Name"})
            >>> print(category.display_name)
            'New Name'
        """
        if not category_id or category_id <= 0:
            raise ValueError("Invalid category ID")

        if not updates:
            raise ValueError("No updates provided")

        # Verify category exists
        existing = self.category_repo.find_by_id(category_id)
        if not existing:
            raise ValueError(f"Category {category_id} not found")

        # Validate name uniqueness if updating name
        if 'name' in updates:
            new_name = updates['name'].strip()
            if not new_name:
                raise ValueError("Category name cannot be empty")

            # Check for duplicate (excluding current category)
            duplicate = self.category_repo.find_by_name_and_game(
                new_name,
                existing['game_gid']
            )
            if duplicate and duplicate['id'] != category_id:
                raise ValueError(
                    f"Category '{new_name}' already exists for game {existing['game_gid']}"
                )

            updates['name'] = new_name

        # Perform update
        self.category_repo.update(category_id, updates)

        # Fetch and return updated category
        updated_data = self.category_repo.find_by_id(category_id)
        if not updated_data:
            raise RuntimeError("Failed to retrieve updated category")

        logger.info(f"Updated event category: {category_id}")
        return EventCategoryEntity(**updated_data)

    @cache_invalidate
    def delete(self, category_id: int) -> bool:
        """
        Delete an event category.

        Args:
            category_id: Category ID

        Returns:
            True if deleted, False otherwise

        Raises:
            ValueError: If category has associated events

        Example:
            >>> service = EventCategoryService()
            >>> success = service.delete(10)
            >>> print(success)
            True
        """
        if not category_id or category_id <= 0:
            raise ValueError("Invalid category ID")

        # Verify category exists
        existing = self.category_repo.find_by_id(category_id)
        if not existing:
            raise ValueError(f"Category {category_id} not found")

        # Check for associated events
        event_count = self.category_repo.count_events(category_id)
        if event_count > 0:
            raise ValueError(
                f"Cannot delete category with {event_count} associated events. "
                "Please reassign or delete events first."
            )

        # Delete category
        success = self.category_repo.delete(category_id)

        if success:
            logger.info(f"Deleted event category: {category_id}")

        return success

    # ================================================================
    # Game-scoped Operations
    # ================================================================

    @cached(ttl=3600, key_prefix="event_categories")
    def get_by_game_gid(self, game_gid: int) -> List[EventCategoryEntity]:
        """
        Get all categories for a specific game.

        Args:
            game_gid: Game GID

        Returns:
            List of EventCategoryEntity objects

        Example:
            >>> service = EventCategoryService()
            >>> categories = service.get_by_game_gid(10000147)
            >>> len(categories)
            5
        """
        if not game_gid or game_gid <= 0:
            raise ValueError("Invalid game GID")

        categories_data = self.category_repo.find_by_game_gid(game_gid)
        return [EventCategoryEntity(**data) for data in categories_data]

    @cached(ttl=1800, key_prefix="event_categories")
    def get_active_by_game_gid(self, game_gid: int) -> List[EventCategoryEntity]:
        """
        Get active categories for a specific game.

        Args:
            game_gid: Game GID

        Returns:
            List of active EventCategoryEntity objects

        Example:
            >>> service = EventCategoryService()
            >>> categories = service.get_active_by_game_gid(10000147)
            >>> all(c.is_active for c in categories)
            True
        """
        if not game_gid or game_gid <= 0:
            raise ValueError("Invalid game GID")

        categories_data = self.category_repo.find_active_by_game_gid(game_gid)
        return [EventCategoryEntity(**data) for data in categories_data]

    # ================================================================
    # Statistics Operations
    # ================================================================

    @cached(ttl=1800, key_prefix="event_categories")
    def get_category_stats(self, game_gid: Optional[int] = None) -> Dict[str, int]:
        """
        Get category statistics.

        Args:
            game_gid: Optional game GID filter

        Returns:
            Dictionary with statistics:
            - total: Total number of categories
            - active: Number of active categories
            - with_events: Number of categories with associated events

        Example:
            >>> service = EventCategoryService()
            >>> stats = service.get_category_stats(game_gid=10000147)
            >>> print(stats)
            {'total': 5, 'active': 4, 'with_events': 3}
        """
        if game_gid is not None and game_gid <= 0:
            raise ValueError("Invalid game GID")

        stats = self.category_repo.get_stats(game_gid)
        return stats

    @cached(ttl=1800, key_prefix="event_categories")
    def get_event_counts(self, game_gid: Optional[int] = None) -> Dict[int, int]:
        """
        Get event counts per category.

        Args:
            game_gid: Optional game GID filter

        Returns:
            Dictionary mapping category_id to event count

        Example:
            >>> service = EventCategoryService()
            >>> counts = service.get_event_counts(game_gid=10000147)
            >>> print(counts)
            {1: 150, 2: 75, 3: 30}
        """
        if game_gid is not None and game_gid <= 0:
            raise ValueError("Invalid game GID")

        counts = self.category_repo.get_event_counts(game_gid)
        return counts

    # ================================================================
    # Batch Operations
    # ================================================================

    @cache_invalidate
    def batch_delete(self, category_ids: List[int]) -> int:
        """
        Delete multiple categories.

        Args:
            category_ids: List of category IDs

        Returns:
            Number of categories deleted

        Raises:
            ValueError: If any category has associated events

        Example:
            >>> service = EventCategoryService()
            >>> count = service.batch_delete([10, 11, 12])
            >>> print(count)
            3
        """
        if not category_ids:
            raise ValueError("No category IDs provided")

        # Validate all IDs
        valid_ids = [cid for cid in category_ids if cid and cid > 0]
        if not valid_ids:
            raise ValueError("No valid category IDs provided")

        # Check for associated events
        for category_id in valid_ids:
            event_count = self.category_repo.count_events(category_id)
            if event_count > 0:
                existing = self.category_repo.find_by_id(category_id)
                category_name = existing['name'] if existing else f"ID {category_id}"
                raise ValueError(
                    f"Cannot delete category '{category_name}' with {event_count} "
                    "associated events"
                )

        # Perform batch delete
        deleted_count = 0
        for category_id in valid_ids:
            if self.category_repo.delete(category_id):
                deleted_count += 1

        logger.info(f"Batch deleted {deleted_count} event categories")
        return deleted_count

    @cache_invalidate
    def batch_update(self, category_ids: List[int], updates: dict) -> int:
        """
        Update multiple categories with the same values.

        Args:
            category_ids: List of category IDs
            updates: Dictionary of fields to update

        Returns:
            Number of categories updated

        Raises:
            ValueError: If validation fails

        Example:
            >>> service = EventCategoryService()
            >>> count = service.batch_update([1, 2, 3], {"is_active": False})
            >>> print(count)
            3
        """
        if not category_ids:
            raise ValueError("No category IDs provided")

        if not updates:
            raise ValueError("No updates provided")

        # Validate all IDs
        valid_ids = [cid for cid in category_ids if cid and cid > 0]
        if not valid_ids:
            raise ValueError("No valid category IDs provided")

        # Validate updates
        if 'name' in updates:
            new_name = updates['name'].strip()
            if not new_name:
                raise ValueError("Category name cannot be empty")

            # Check for duplicate name for each category
            for category_id in valid_ids:
                existing = self.category_repo.find_by_id(category_id)
                if not existing:
                    continue

                duplicate = self.category_repo.find_by_name_and_game(
                    new_name,
                    existing['game_gid']
                )
                if duplicate and duplicate['id'] not in valid_ids:
                    raise ValueError(
                        f"Category '{new_name}' already exists for game {existing['game_gid']}"
                    )

            updates['name'] = new_name

        # Perform batch update
        updated_count = 0
        for category_id in valid_ids:
            try:
                self.category_repo.update(category_id, updates)
                updated_count += 1
            except Exception as e:
                logger.warning(f"Failed to update category {category_id}: {e}")

        logger.info(f"Batch updated {updated_count} event categories")
        return updated_count
