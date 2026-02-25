"""
GraphQL Schema

Main GraphQL schema definition for Event2Table API.
"""

import graphene
from graphene import ObjectType, Field, List, Int, String, Boolean
import logging

from backend.gql_api.types.game_type import GameType
from backend.gql_api.types.event_type import EventType
from backend.gql_api.types.parameter_type import ParameterType
from backend.gql_api.types.category_type import CategoryType
from backend.gql_api.types.dashboard_type import DashboardStatsType, GameStatsType
from backend.gql_api.types.template_type import TemplateType
from backend.gql_api.types.node_type import NodeType, FlowType
from backend.gql_api.types.event_parameter_type import EventParameterExtendedType, ParamVersionType, ParamConfigType, ValidationRuleType
from backend.gql_api.types.join_config_type import JoinConfigType
from backend.gql_api.queries.game_queries import GameQueries
from backend.gql_api.queries.event_queries import EventQueries
from backend.gql_api.queries.category_queries import CategoryQueries
from backend.gql_api.queries.parameter_queries import ParameterQueries
from backend.gql_api.queries.dashboard_queries import DashboardQueries
from backend.gql_api.queries.template_queries import TemplateQueries
from backend.gql_api.queries.node_queries import NodeQueries, FlowQueries
from backend.gql_api.queries.event_parameter_queries import EventParameterQueries
from backend.gql_api.queries.join_config_queries import JoinConfigQueries
from backend.gql_api.mutations.game_mutations import GameMutations
from backend.gql_api.mutations.event_mutations import EventMutations
from backend.gql_api.mutations.parameter_mutations import ParameterMutations
from backend.gql_api.mutations.category_mutations import CategoryMutations
from backend.gql_api.mutations.template_mutations import TemplateMutations
from backend.gql_api.mutations.node_mutations import NodeMutations, FlowMutations
from backend.gql_api.mutations.event_parameter_mutations import EventParameterMutations
from backend.gql_api.mutations.join_config_mutations import JoinConfigMutations
from backend.gql_api.mutations.hql_mutations import HQLMutations

# Parameter Management Schema imports
from backend.gql_api.schema_parameter_management import (
    ParameterManagementQueries,
    ParameterManagementMutations,
    ParameterTypeEnum,
    ParameterFilterModeEnum,
    FieldTypeEnum
)

logger = logging.getLogger(__name__)


class Query(
    ParameterManagementQueries,
    GameQueries,
    EventQueries,
    EventParameterQueries,
    CategoryQueries,
    DashboardQueries,
    FlowQueries,
    NodeQueries,
    TemplateQueries,
    JoinConfigQueries
):
    """
    GraphQL Query Root Type

    Provides all query operations for the API.
    """

    # Game queries
    game = Field(
        GameType,
        gid=Int(required=True),
        description="根据GID查询单个游戏"
    )

    games = List(
        GameType,
        limit=Int(default_value=10),
        offset=Int(default_value=0),
        description="查询游戏列表（支持分页）"
    )

    search_games = List(
        GameType,
        query=String(required=True),
        description="搜索游戏"
    )

    # Event queries
    event = Field(
        EventType,
        id=Int(required=True),
        description="根据ID查询单个事件"
    )

    events = List(
        EventType,
        game_gid=Int(required=True),
        category=String(),
        limit=Int(default_value=50),
        offset=Int(default_value=0),
        description="查询游戏的事件列表（支持过滤和分页）"
    )

    search_events = List(
        EventType,
        query=String(required=True),
        game_gid=Int(),
        description="搜索事件"
    )

    # Category queries
    category = Field(
        CategoryType,
        id=Int(required=True),
        description="根据ID查询单个分类"
    )

    categories = List(
        CategoryType,
        limit=Int(default_value=50),
        offset=Int(default_value=0),
        description="查询分类列表（支持分页）"
    )

    search_categories = List(
        CategoryType,
        query=String(required=True),
        description="搜索分类"
    )

    # Parameter queries
    parameter = Field(
        ParameterType,
        id=Int(required=True),
        description="根据ID查询单个参数"
    )

    parameters = List(
        ParameterType,
        event_id=Int(required=True),
        activeOnly=Boolean(default_value=True),
        description="查询事件的参数列表"
    )

    search_parameters = List(
        ParameterType,
        query=String(required=True),
        event_id=Int(),
        description="搜索参数"
    )

    # Dashboard queries
    dashboard_stats = Field(
        DashboardStatsType,
        description="获取仪表盘统计数据"
    )

    game_stats = Field(
        GameStatsType,
        game_gid=Int(required=True),
        description="获取指定游戏的统计数据"
    )

    all_game_stats = List(
        GameStatsType,
        limit=Int(default_value=20),
        description="获取所有游戏的统计数据"
    )

    # Template queries
    template = Field(
        TemplateType,
        id=Int(required=True),
        description="根据ID查询单个模板"
    )

    templates = List(
        TemplateType,
        game_gid=Int(),
        category=String(),
        search=String(),
        limit=Int(default_value=20),
        offset=Int(default_value=0),
        description="查询模板列表"
    )

    search_templates = List(
        TemplateType,
        query=String(required=True),
        game_gid=Int(),
        description="搜索模板"
    )

    # Node queries
    node = Field(
        NodeType,
        id=Int(required=True),
        description="根据ID查询单个节点"
    )

    nodes = List(
        NodeType,
        game_gid=Int(),
        node_type=String(),
        limit=Int(default_value=50),
        offset=Int(default_value=0),
        description="查询节点列表"
    )

    # Flow queries
    flow = Field(
        FlowType,
        id=Int(required=True),
        description="根据ID查询单个流程"
    )

    flows = List(
        FlowType,
        game_gid=Int(),
        flow_type=String(),
        limit=Int(default_value=50),
        offset=Int(default_value=0),
        description="查询流程列表"
    )

    # Event Parameter extended queries
    event_parameter_extended = Field(
        EventParameterExtendedType,
        id=Int(required=True),
        description="查询扩展事件参数"
    )

    param_history = List(
        ParamVersionType,
        param_id=Int(required=True),
        limit=Int(default_value=10),
        description="查询参数版本历史"
    )

    param_config = Field(
        ParamConfigType,
        param_id=Int(required=True),
        description="查询参数配置"
    )

    validation_rules = List(
        ValidationRuleType,
        param_id=Int(required=True),
        description="查询参数验证规则"
    )

    # Join Config queries
    join_config = Field(
        JoinConfigType,
        id=Int(required=True),
        description="根据ID查询单个Join配置"
    )

    join_configs = List(
        JoinConfigType,
        game_id=Int(),
        join_type=String(),
        limit=Int(default_value=50),
        offset=Int(default_value=0),
        description="查询Join配置列表"
    )

    # Resolvers
    def resolve_game(self, info, gid):
        """Resolve single game"""
        return GameQueries.resolve_game(self, info, gid)

    def resolve_games(self, info, limit, offset):
        """Resolve game list"""
        return GameQueries.resolve_games(self, info, limit, offset)

    def resolve_search_games(self, info, query):
        """Resolve game search"""
        return GameQueries.resolve_search_games(self, info, query)

    def resolve_event(self, info, id):
        """Resolve single event"""
        return EventQueries.resolve_event(self, info, id)

    def resolve_events(self, info, game_gid, category=None, limit=50, offset=0):
        """Resolve event list"""
        return EventQueries.resolve_events(self, info, game_gid, category, limit, offset)

    def resolve_search_events(self, info, query, game_gid=None):
        """Resolve event search"""
        return EventQueries.resolve_search_events(self, info, query, game_gid)

    def resolve_category(self, info, id):
        """Resolve single category"""
        return CategoryQueries.resolve_category(self, info, id)

    def resolve_categories(self, info, limit, offset):
        """Resolve category list"""
        return CategoryQueries.resolve_categories(self, info, limit, offset)

    def resolve_search_categories(self, info, query):
        """Resolve category search"""
        return CategoryQueries.resolve_search_categories(self, info, query)

    def resolve_parameter(self, info, id):
        """Resolve single parameter"""
        return ParameterQueries.resolve_parameter(self, info, id)

    def resolve_parameters(self, info, event_id, activeOnly=True):
        """Resolve parameter list"""
        return ParameterQueries.resolve_parameters(self, info, event_id, activeOnly)

    def resolve_search_parameters(self, info, query, event_id=None):
        """Resolve parameter search"""
        return ParameterQueries.resolve_search_parameters(self, info, query, event_id)

    def resolve_dashboard_stats(self, info):
        """Resolve dashboard statistics"""
        return DashboardQueries.resolve_dashboard_stats(self, info)

    def resolve_game_stats(self, info, game_gid):
        """Resolve game statistics"""
        return DashboardQueries.resolve_game_stats(self, info, game_gid)

    def resolve_all_game_stats(self, info, limit=20):
        """Resolve all game statistics"""
        return DashboardQueries.resolve_all_game_stats(self, info, limit)

    def resolve_template(self, info, id):
        """Resolve single template"""
        return TemplateQueries.resolve_template(self, info, id)

    def resolve_templates(self, info, game_gid=None, category=None, search=None, limit=20, offset=0):
        """Resolve templates list"""
        return TemplateQueries.resolve_templates(self, info, game_gid, category, search, limit, offset)

    def resolve_search_templates(self, info, query, game_gid=None):
        """Resolve template search"""
        return TemplateQueries.resolve_search_templates(self, info, query, game_gid)

    def resolve_node(self, info, id):
        """Resolve single node"""
        return NodeQueries.resolve_node(self, info, id)

    def resolve_nodes(self, info, game_gid=None, node_type=None, limit=50, offset=0):
        """Resolve nodes list"""
        return NodeQueries.resolve_nodes(self, info, game_gid, node_type, limit, offset)

    def resolve_flow(self, info, id):
        """Resolve single flow"""
        return FlowQueries.resolve_flow(self, info, id)

    def resolve_flows(self, info, game_gid=None, flow_type=None, limit=50, offset=0):
        """Resolve flows list"""
        return FlowQueries.resolve_flows(self, info, game_gid, flow_type, limit, offset)

    def resolve_event_parameter_extended(self, info, id):
        """Resolve extended event parameter"""
        return EventParameterQueries.resolve_event_parameter_extended(self, info, id)

    def resolve_param_history(self, info, param_id, limit=10):
        """Resolve parameter history"""
        return EventParameterQueries.resolve_param_history(self, info, param_id, limit)

    def resolve_param_config(self, info, param_id):
        """Resolve parameter config"""
        return EventParameterQueries.resolve_param_config(self, info, param_id)

    def resolve_validation_rules(self, info, param_id):
        """Resolve validation rules"""
        return EventParameterQueries.resolve_validation_rules(self, info, param_id)

    def resolve_join_config(self, info, id):
        """Resolve single join config"""
        return JoinConfigQueries.resolve_join_config(self, info, id)

    def resolve_join_configs(self, info, game_id=None, join_type=None, limit=50, offset=0):
        """Resolve join configs list"""
        return JoinConfigQueries.resolve_join_configs(self, info, game_id, join_type, limit, offset)

    # ========================================================================
    # Parameter Management Query Resolvers
    # ========================================================================

    def resolve_parameters_management(self, info, game_gid, mode='all', event_id=None):
        """Resolve parameters management query"""
        from backend.gql_api.resolvers.parameter_resolvers import resolve_parameters_management
        return resolve_parameters_management(info, game_gid, mode, event_id)

    def resolve_common_parameters(self, info, game_gid, threshold=0.5):
        """Resolve common parameters query"""
        from backend.gql_api.resolvers.parameter_resolvers import resolve_common_parameters
        return resolve_common_parameters(info, game_gid, threshold)

    def resolve_parameter_changes(self, info, game_gid, parameter_id=None, limit=50):
        """Resolve parameter changes query"""
        from backend.gql_api.resolvers.parameter_resolvers import resolve_parameter_changes
        return resolve_parameter_changes(info, game_gid, parameter_id, limit)

    def resolve_event_fields(self, info, event_id, field_type='all'):
        """Resolve event fields query"""
        from backend.gql_api.resolvers.parameter_resolvers import resolve_event_fields
        return resolve_event_fields(info, event_id, field_type)


class Mutation(
    ParameterManagementMutations,
    GameMutations,
    EventMutations,
    ParameterMutations,
    CategoryMutations,
    TemplateMutations,
    NodeMutations,
    FlowMutations,
    EventParameterMutations,
    JoinConfigMutations,
    HQLMutations
):
    """
    GraphQL Mutation Root Type

    Provides all mutation operations for the API.
    """

    # Game mutations
    create_game = GameMutations.CreateGame.Field()
    update_game = GameMutations.UpdateGame.Field()
    delete_game = GameMutations.DeleteGame.Field()

    # Event mutations
    create_event = EventMutations.CreateEvent.Field()
    update_event = EventMutations.UpdateEvent.Field()
    delete_event = EventMutations.DeleteEvent.Field()

    # Parameter mutations
    create_parameter = ParameterMutations.CreateParameter.Field()
    update_parameter = ParameterMutations.UpdateParameter.Field()
    delete_parameter = ParameterMutations.DeleteParameter.Field()

    # Category mutations
    create_category = CategoryMutations.CreateCategory.Field()
    update_category = CategoryMutations.UpdateCategory.Field()
    delete_category = CategoryMutations.DeleteCategory.Field()

    # Template mutations
    create_template = TemplateMutations.CreateTemplate.Field()
    update_template = TemplateMutations.UpdateTemplate.Field()
    delete_template = TemplateMutations.DeleteTemplate.Field()

    # Node mutations
    create_node = NodeMutations.CreateNode.Field()
    update_node = NodeMutations.UpdateNode.Field()
    delete_node = NodeMutations.DeleteNode.Field()

    # Flow mutations
    create_flow = FlowMutations.CreateFlow.Field()
    update_flow = FlowMutations.UpdateFlow.Field()
    delete_flow = FlowMutations.DeleteFlow.Field()

    # Event Parameter extended mutations
    update_event_parameter = EventParameterMutations.UpdateEventParameter.Field()
    delete_event_parameter = EventParameterMutations.DeleteEventParameter.Field()
    set_param_config = EventParameterMutations.SetParamConfig.Field()
    rollback_event_parameter = EventParameterMutations.RollbackEventParameter.Field()
    create_validation_rule = EventParameterMutations.CreateValidationRule.Field()

    # Join Config mutations
    create_join_config = JoinConfigMutations.create_join_config
    update_join_config = JoinConfigMutations.update_join_config
    delete_join_config = JoinConfigMutations.delete_join_config
    
    # HQL mutations
    generate_hql = HQLMutations.GenerateHQL.Field()
    save_hql_template = HQLMutations.SaveHQLTemplate.Field()
    delete_hql_template = HQLMutations.DeleteHQLTemplate.Field()

    # Parameter Management mutations
    change_parameter_type = ParameterManagementMutations.change_parameter_type
    auto_sync_common_parameters = ParameterManagementMutations.auto_sync_common_parameters
    batch_add_fields_to_canvas = ParameterManagementMutations.batch_add_fields_to_canvas


# Create the schema
schema = graphene.Schema(query=Query, mutation=Mutation)
