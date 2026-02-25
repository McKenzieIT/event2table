"""领域异常定义"""


class DomainException(Exception):
    """领域异常基类"""
    pass


class InvalidGameGID(DomainException):
    """无效的游戏GID"""
    pass


class EventAlreadyExists(DomainException):
    """事件已存在"""
    pass


class CannotDeleteGameWithEvents(DomainException):
    """无法删除有事件的游戏"""
    pass


class InvalidEventName(DomainException):
    """无效的事件名称"""
    pass


class ParameterAlreadyExists(DomainException):
    """参数已存在"""
    pass


class GameNotFound(DomainException):
    """游戏不存在"""
    pass


class EventNotFound(DomainException):
    """事件不存在"""
    pass
