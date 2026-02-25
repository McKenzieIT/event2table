"""领域异常模块"""
from .domain_exceptions import (
    DomainException,
    InvalidGameGID,
    EventAlreadyExists,
    CannotDeleteGameWithEvents,
    InvalidEventName,
    ParameterAlreadyExists,
    GameNotFound,
    EventNotFound,
)

__all__ = [
    'DomainException',
    'InvalidGameGID',
    'EventAlreadyExists',
    'CannotDeleteGameWithEvents',
    'InvalidEventName',
    'ParameterAlreadyExists',
    'GameNotFound',
    'EventNotFound',
]
