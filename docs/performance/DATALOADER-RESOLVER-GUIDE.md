# DataLoader Resolver Integration Guide

This guide shows how to update GraphQL resolvers to use DataLoader for optimal performance.

## Why Use DataLoader?

Without DataLoader:
```python
# N+1 query problem
def resolve_games(self, info, limit=10):
    games = fetch_all_as_dict("SELECT * FROM games LIMIT ?", (limit,))

    # For each game, fetch events (N queries)
    for game in games:
        game['events'] = fetch_all_as_dict(
            "SELECT * FROM events WHERE game_gid = ?",
            (game['gid'],)
        )

    return games
# Total queries: 1 + N (where N = number of games)
```

With DataLoader:
```python
# Batch loading
def resolve_games(self, info, limit=10):
    from backend.gql_api.middleware.dataloader_context import get_dataloader

    games = fetch_all_as_dict("SELECT * FROM games LIMIT ?", (limit,))

    # Batch load all events in single query
    event_loader = get_dataloader(info, 'event')
    game_gids = [g['gid'] for g in games]
    events_by_game = event_loader.load_many(game_gids).get()

    # Associate events with games
    for i, game in enumerate(games):
        game['events'] = events_by_game[i]

    return games
# Total queries: 2 (1 for games + 1 batch for all events)
```

## Step-by-Step Migration

### 1. Simple Query - No Relations

**Before**:
```python
# backend/gql_api/queries/game_queries.py
def resolve_game(self, info, gid):
    from backend.core.utils import fetch_one_as_dict

    return fetch_one_as_dict(
        "SELECT * FROM games WHERE gid = ?",
        (gid,)
    )
```

**After**:
```python
def resolve_game(self, info, gid):
    from backend.gql_api.middleware.dataloader_context import get_dataloader

    loader = get_dataloader(info, 'game')
    return loader.load(gid).get()
```

### 2. List Query - No Relations

**Before**:
```python
def resolve_games(self, info, limit=10, offset=0):
    from backend.core.utils import fetch_all_as_dict

    return fetch_all_as_dict(
        "SELECT * FROM games LIMIT ? OFFSET ?",
        (limit, offset)
    )
```

**After**:
```python
def resolve_games(self, info, limit=10, offset=0):
    from backend.gql_api.middleware.dataloader_context import get_dataloader
    import json

    loader = get_dataloader(info, 'games_by_filter')
    filter_key = json.dumps({'limit': limit, 'offset': offset})
    return loader.load(filter_key).get()
```

### 3. Nested Query - One-to-Many

**Before** (N+1 problem):
```python
def resolve_game_with_events(self, info, gid):
    from backend.core.utils import fetch_one_as_dict, fetch_all_as_dict

    game = fetch_one_as_dict(
        "SELECT * FROM games WHERE gid = ?",
        (gid,)
    )

    # N+1 query: loads events separately
    game['events'] = fetch_all_as_dict(
        "SELECT * FROM log_events WHERE game_gid = ?",
        (gid,)
    )

    return game
```

**After** (batched):
```python
def resolve_game(self, info, gid):
    from backend.gql_api.middleware.dataloader_context import get_dataloader

    # Load game
    game_loader = get_dataloader(info, 'game')
    game = game_loader.load(gid).get()

    return game

def resolve_events(game, info):
    """Called automatically by GraphQL when events field is queried"""
    from backend.gql_api.middleware.dataloader_context import get_dataloader

    event_loader = get_dataloader(info, 'event')
    return event_loader.load(game['gid']).get()
```

### 4. Multiple Nested Levels

**Before** (N+1^2 problem):
```python
def resolve_game_with_all(self, info, gid):
    from backend.core.utils import fetch_one_as_dict, fetch_all_as_dict

    game = fetch_one_as_dict(
        "SELECT * FROM games WHERE gid = ?",
        (gid,)
    )

    # Load events
    events = fetch_all_as_dict(
        "SELECT * FROM log_events WHERE game_gid = ?",
        (gid,)
    )

    # For each event, load parameters (N^2 queries!)
    for event in events:
        event['parameters'] = fetch_all_as_dict(
            "SELECT * FROM event_params WHERE event_id = ?",
            (event['id'],)
        )

    game['events'] = events
    return game
```

**After** (fully batched):
```python
def resolve_game(self, info, gid):
    """Load game"""
    from backend.gql_api.middleware.dataloader_context import get_dataloader

    loader = get_dataloader(info, 'game')
    return loader.load(gid).get()

def resolve_events(game, info):
    """Load events for game (batched)"""
    from backend.gql_api.middleware.dataloader_context import get_dataloader

    loader = get_dataloader(info, 'event')
    return loader.load(game['gid']).get()

def resolve_parameters(event, info):
    """Load parameters for event (batched)"""
    from backend.gql_api.middleware.dataloader_context import get_dataloader

    loader = get_dataloader(info, 'parameter')
    return loader.load(event['id']).get()
```

## Complete Example: Game Queries

Here's a complete migration example for the game queries:

```python
# backend/gql_api/queries/game_queries.py

from graphene import Field, Int, List, ObjectType, String
from backend.gql_api.types.game_type import GameType
from backend.gql_api.middleware.dataloader_context import get_dataloader


class GameQueries(ObjectType):
    """Game queries with DataLoader"""

    game = Field(GameType, gid=Int(required=True), description="Get game by GID")
    games = List(GameType, limit=Int(default_value=10), offset=Int(default_value=0))

    def resolve_game(self, info, gid):
        """
        Get single game by GID.

        Uses DataLoader for efficient batch loading when multiple games
        are requested in the same query.
        """
        try:
            loader = get_dataloader(info, 'game')
            game = loader.load(gid).get()

            if not game:
                raise ValueError(f"Game not found: gid={gid}")

            return game

        except Exception as e:
            logger.error(f"Error loading game {gid}: {e}")
            raise

    def resolve_games(self, info, limit=10, offset=0):
        """
        Get list of games with pagination.

        Uses GamesByFilterLoader for caching filtered queries.
        """
        try:
            import json

            loader = get_dataloader(info, 'games_by_filter')
            filter_key = json.dumps({'limit': limit, 'offset': offset})
            games = loader.load(filter_key).get()

            return games or []

        except Exception as e:
            logger.error(f"Error loading games: {e}")
            return []

    def resolve_search_games(self, info, query):
        """Search games by name"""
        # For search queries, we might need custom loading
        # because the query is dynamic
        from backend.core.utils import fetch_all_as_dict

        pattern = f"%{query}%"
        return fetch_all_as_dict(
            "SELECT * FROM games WHERE name LIKE ?",
            (pattern,)
        )
```

## Testing DataLoader Integration

### Unit Test Example

```python
# test/graphql/test_game_queries.py
import pytest
from unittest.mock import patch, MagicMock
from backend.gql_api.queries.game_queries import GameQueries

@pytest.mark.describe("Game Queries with DataLoader")
class TestGameQueries:
    """Test game queries using DataLoader"""

    @pytest.fixture
    def queries(self):
        return GameQueries()

    @pytest.fixture
    def mock_context(self):
        """Mock GraphQL context with DataLoaders"""
        from promise.dataloader import DataLoader
        from unittest.mock import MagicMock

        context = MagicMock()

        # Mock game loader
        game_loader = MagicMock()
        game_loader.load.return_value.get.return_value = {
            'gid': 10000147,
            'name': 'Test Game'
        }

        context.dataloaders = {
            'game': game_loader,
            'event': MagicMock(),
            'parameter': MagicMock()
        }

        return context

    @pytest.mark.it("should use DataLoader to load game")
    def test_resolve_game_uses_loader(self, queries, mock_context):
        """Test that resolve_game uses DataLoader"""
        # Create mock info
        info = MagicMock()
        info.context = mock_context

        # Resolve
        result = queries.resolve_game(info, gid=10000147)

        # Verify DataLoader was called
        mock_context.dataloaders['game'].load.assert_called_once_with(10000147)

        # Verify result
        assert result['gid'] == 10000147
        assert result['name'] == 'Test Game'
```

## Performance Comparison

### Query: Get 10 games with their events and parameters

**Without DataLoader**:
```
Operation: games { events { parameters } }

Query Count:
- 1 query for games
- 10 queries for events (1 per game)
- 50 queries for parameters (avg 5 per event)
Total: 61 queries
Time: ~500ms
```

**With DataLoader**:
```
Operation: games { events { parameters } }

Query Count:
- 1 query for games
- 1 query for all events (batched)
- 1 query for all parameters (batched)
Total: 3 queries
Time: ~50ms

Improvement: 95% reduction in queries, 10x faster
```

## Common Pitfalls

### 1. Not Using the Context

❌ **Wrong**: Creating new loader instance
```python
def resolve_game(self, info, gid):
    from backend.gql_api.dataloaders.game_loader import GameLoader
    loader = GameLoader()  # Wrong! Breaks batching
    return loader.load(gid).get()
```

✅ **Correct**: Getting loader from context
```python
def resolve_game(self, info, gid):
    from backend.gql_api.middleware.dataloader_context import get_dataloader
    loader = get_dataloader(info, 'game')  # Correct!
    return loader.load(gid).get()
```

### 2. Calling .get() Too Early

❌ **Wrong**: Breaking batching with .get()
```python
def resolve_games(self, info, gids):
    loader = get_dataloader(info, 'game')
    games = []
    for gid in gids:
        game = loader.load(gid).get()  # Wrong! Breaks batching
        games.append(game)
    return games
```

✅ **Correct**: Load all, then get all
```python
def resolve_games(self, info, gids):
    loader = get_dataloader(info, 'game')
    promises = [loader.load(gid) for gid in gids]
    from promise import Promise
    games = Promise.all(promises).get()  # Correct! Batches all
    return games
```

### 3. Forgetting Error Handling

❌ **Wrong**: No error handling
```python
def resolve_game(self, info, gid):
    loader = get_dataloader(info, 'game')
    return loader.load(gid).get()  # What if it fails?
```

✅ **Correct**: Proper error handling
```python
def resolve_game(self, info, gid):
    try:
        loader = get_dataloader(info, 'game')
        game = loader.load(gid).get()

        if not game:
            raise ValueError(f"Game not found: gid={gid}")

        return game

    except Exception as e:
        logger.error(f"Error loading game {gid}: {e}")
        raise
```

## Checklist

Before deploying DataLoader integration:

- [ ] All resolvers updated to use loaders from context
- [ ] DataLoader context middleware added to GraphQL route
- [ ] Unit tests updated to mock loaders
- [ ] Integration tests verify query reduction
- [ ] Performance benchmarks show 5-10x improvement
- [ ] Error handling covers loader failures
- [ ] Documentation updated for team

## Resources

- [Facebook DataLoader Documentation](https://github.com/facebook/dataloader)
- [GraphQL Best Practices](https://graphql.org/learn/best-practices/)
- [Project Performance Guide](/docs/performance/)
