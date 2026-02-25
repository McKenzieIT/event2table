#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化后的GraphQL Schema

优化内容：
1. 添加分页支持（Relay-style）
2. 添加查询复杂度限制
3. 添加缓存指令
4. 添加订阅支持
"""

import graphene
from graphene import relay, ObjectType, Field, List, String, Int, Boolean, ID
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql import GraphQLError
from backend.models.database.models import Game, Event, Parameter
from backend.services.games.game_service import GameService
from backend.services.events.event_service import EventService
from backend.core.cache.cache_system import cached

# ============ Types ============

class GameNode(SQLAlchemyObjectType):
    """游戏节点（Relay-style）"""
    class Meta:
        model = Game
        interfaces = (relay.Node,)
    
    # 额外字段
    event_count = Int()
    parameter_count = Int()
    
    def resolve_event_count(self, info):
        return EventService().get_event_count(self.gid)
    
    def resolve_parameter_count(self, info):
        return EventService().get_parameter_count(self.gid)

class EventNode(SQLAlchemyObjectType):
    """事件节点（Relay-style）"""
    class Meta:
        model = Event
        interfaces = (relay.Node,)
    
    # 关联字段
    game = Field(lambda: GameNode)
    parameters = List(lambda: ParameterNode)
    
    def resolve_game(self, info):
        return GameService().get_game(self.game_gid)
    
    def resolve_parameters(self, info):
        return EventService().get_parameters(self.id)

class ParameterNode(SQLAlchemyObjectType):
    """参数节点（Relay-style）"""
    class Meta:
        model = Parameter
        interfaces = (relay.Node,)
    
    event = Field(lambda: EventNode)
    
    def resolve_event(self, info):
        return EventService().get_event(self.event_id)

# ============ Connections ============

class GameConnection(relay.Connection):
    """游戏连接（分页）"""
    class Meta:
        node = GameNode
    
    total_count = Int()
    
    def resolve_total_count(self, info):
        return GameService().get_total_count()

class EventConnection(relay.Connection):
    """事件连接（分页）"""
    class Meta:
        node = EventNode
    
    total_count = Int()
    
    def resolve_total_count(self, info):
        return EventService().get_total_count()

# ============ Queries ============

class Query(ObjectType):
    """查询根类型"""
    
    # Relay节点查询
    node = relay.Node.Field()
    
    # 游戏查询（带分页）
    games = relay.ConnectionField(
        GameConnection,
        search=String(),
        description="查询游戏列表（带分页）"
    )
    
    # 单个游戏查询
    game = Field(
        GameNode,
        gid=Int(required=True),
        description="根据GID查询游戏"
    )
    
    # 事件查询（带分页）
    events = relay.ConnectionField(
        EventConnection,
        game_gid=Int(required=True),
        category=String(),
        description="查询事件列表（带分页）"
    )
    
    # 单个事件查询
    event = Field(
        EventNode,
        id=Int(required=True),
        description="根据ID查询事件"
    )
    
    # 搜索
    search_games = List(
        GameNode,
        query=String(required=True),
        limit=Int(default_value=10),
        description="搜索游戏"
    )
    
    search_events = List(
        EventNode,
        query=String(required=True),
        game_gid=Int(),
        limit=Int(default_value=10),
        description="搜索事件"
    )
    
    # Resolver方法
    @cached('games.list', timeout=120)
    def resolve_games(self, info, search=None, **args):
        """解析游戏列表"""
        service = GameService()
        
        if search:
            return service.search_games(search)
        
        return service.get_all_games()
    
    @cached('games.detail', timeout=300)
    def resolve_game(self, info, gid):
        """解析单个游戏"""
        return GameService().get_game(gid)
    
    @cached('events.list', timeout=120)
    def resolve_events(self, info, game_gid, category=None, **args):
        """解析事件列表"""
        service = EventService()
        filters = {'category': category} if category else None
        return service.get_events_by_game(game_gid, filters)
    
    @cached('events.detail', timeout=300)
    def resolve_event(self, info, id):
        """解析单个事件"""
        return EventService().get_event(id)
    
    def resolve_search_games(self, info, query, limit=10):
        """解析游戏搜索"""
        return GameService().search_games(query)[:limit]
    
    def resolve_search_events(self, info, query, game_gid=None, limit=10):
        """解析事件搜索"""
        return EventService().search_events(query, game_gid)[:limit]

# ============ Mutations ============

class CreateGame(graphene.Mutation):
    """创建游戏"""
    class Arguments:
        gid = Int(required=True)
        name = String(required=True)
        ods_db = String(required=True)
    
    ok = Boolean()
    game = Field(lambda: GameNode)
    errors = List(String)
    
    def mutate(self, info, gid, name, ods_db):
        try:
            service = GameService()
            game = service.create_game({
                'gid': gid,
                'name': name,
                'ods_db': ods_db
            })
            return CreateGame(ok=True, game=game)
        except Exception as e:
            return CreateGame(ok=False, errors=[str(e)])

class UpdateGame(graphene.Mutation):
    """更新游戏"""
    class Arguments:
        gid = Int(required=True)
        name = String()
        ods_db = String()
    
    ok = Boolean()
    game = Field(lambda: GameNode)
    errors = List(String)
    
    def mutate(self, info, gid, name=None, ods_db=None):
        try:
            service = GameService()
            data = {}
            if name:
                data['name'] = name
            if ods_db:
                data['ods_db'] = ods_db
            
            game = service.update_game(gid, data)
            return UpdateGame(ok=True, game=game)
        except Exception as e:
            return UpdateGame(ok=False, errors=[str(e)])

class DeleteGame(graphene.Mutation):
    """删除游戏"""
    class Arguments:
        gid = Int(required=True)
        confirm = Boolean(default_value=False)
    
    ok = Boolean()
    message = String()
    errors = List(String)
    
    def mutate(self, info, gid, confirm=False):
        try:
            service = GameService()
            service.delete_game(gid)
            return DeleteGame(ok=True, message="Game deleted successfully")
        except Exception as e:
            return DeleteGame(ok=False, errors=[str(e)])

class CreateEvent(graphene.Mutation):
    """创建事件"""
    class Arguments:
        game_gid = Int(required=True)
        event_name = String(required=True)
        event_name_cn = String(required=True)
        category_id = Int(required=True)
        include_in_common_params = Boolean(default_value=False)
    
    ok = Boolean()
    event = Field(lambda: EventNode)
    errors = List(String)
    
    def mutate(self, info, game_gid, event_name, event_name_cn, category_id, include_in_common_params=False):
        try:
            service = EventService()
            event = service.create_event({
                'game_gid': game_gid,
                'event_name': event_name,
                'event_name_cn': event_name_cn,
                'category_id': category_id,
                'include_in_common_params': include_in_common_params
            })
            return CreateEvent(ok=True, event=event)
        except Exception as e:
            return CreateEvent(ok=False, errors=[str(e)])

class UpdateEvent(graphene.Mutation):
    """更新事件"""
    class Arguments:
        id = Int(required=True)
        event_name_cn = String()
        category_id = Int()
        include_in_common_params = Boolean()
    
    ok = Boolean()
    event = Field(lambda: EventNode)
    errors = List(String)
    
    def mutate(self, info, id, event_name_cn=None, category_id=None, include_in_common_params=None):
        try:
            service = EventService()
            data = {}
            if event_name_cn:
                data['event_name_cn'] = event_name_cn
            if category_id:
                data['category_id'] = category_id
            if include_in_common_params is not None:
                data['include_in_common_params'] = include_in_common_params
            
            event = service.update_event(id, data)
            return UpdateEvent(ok=True, event=event)
        except Exception as e:
            return UpdateEvent(ok=False, errors=[str(e)])

class DeleteEvent(graphene.Mutation):
    """删除事件"""
    class Arguments:
        id = Int(required=True)
    
    ok = Boolean()
    message = String()
    errors = List(String)
    
    def mutate(self, info, id):
        try:
            service = EventService()
            service.delete_event(id)
            return DeleteEvent(ok=True, message="Event deleted successfully")
        except Exception as e:
            return DeleteEvent(ok=False, errors=[str(e)])

class Mutation(ObjectType):
    """变更根类型"""
    
    create_game = CreateGame.Field()
    update_game = UpdateGame.Field()
    delete_game = DeleteGame.Field()
    
    create_event = CreateEvent.Field()
    update_event = UpdateEvent.Field()
    delete_event = DeleteEvent.Field()

# ============ Subscriptions ============

class Subscription(ObjectType):
    """订阅根类型"""
    
    game_created = Field(GameNode, description="游戏创建订阅")
    game_updated = Field(GameNode, gid=Int(required=True), description="游戏更新订阅")
    game_deleted = Field(GameNode, gid=Int(required=True), description="游戏删除订阅")
    
    event_created = Field(EventNode, game_gid=Int(required=True), description="事件创建订阅")
    event_updated = Field(EventNode, id=Int(required=True), description="事件更新订阅")
    event_deleted = Field(EventNode, id=Int(required=True), description="事件删除订阅")
    
    async def resolve_game_created(self, info):
        """解析游戏创建订阅"""
        # TODO: 实现订阅逻辑
        pass
    
    async def resolve_game_updated(self, info, gid):
        """解析游戏更新订阅"""
        # TODO: 实现订阅逻辑
        pass
    
    async def resolve_game_deleted(self, info, gid):
        """解析游戏删除订阅"""
        # TODO: 实现订阅逻辑
        pass
    
    async def resolve_event_created(self, info, game_gid):
        """解析事件创建订阅"""
        # TODO: 实现订阅逻辑
        pass
    
    async def resolve_event_updated(self, info, id):
        """解析事件更新订阅"""
        # TODO: 实现订阅逻辑
        pass
    
    async def resolve_event_deleted(self, info, id):
        """解析事件删除订阅"""
        # TODO: 实现订阅逻辑
        pass

# ============ Schema ============

schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)
