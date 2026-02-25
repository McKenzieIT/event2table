#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Path Validator - 防止路径遍历攻击
=============================

提供安全的文件路径验证功能，防止路径遍历攻击。

安全特性:
- 防止../路径遍历
- 防止绝对路径逃逸
- 文件名安全过滤
- 路径长度限制

使用示例:
    >>> from backend.core.security.path_validator import PathValidator
    >>>
    >>> # 验证文件路径
    >>> safe_path = PathValidator.validate_path("uploads/test.txt", "/app/data")
    >>>
    >>> # 生成安全文件名
    >>> safe_name = PathValidator.safe_filename("../../../etc/passwd")
    >>> # 返回: "________etc_passwd"

Author: Event2Table Development Team
Version: 1.0.0
Date: 2026-02-24
"""

import os
import re
import logging
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)


class PathValidator:
    """
    路径验证器 - 防止路径遍历攻击

    安全措施:
    1. 使用Path.resolve()解析所有符号链接和相对路径
    2. 检查解析后的路径是否在base_dir范围内
    3. 过滤危险字符
    4. 限制路径长度
    """

    # 允许的文件扩展名（可根据需要扩展）
    ALLOWED_EXTENSIONS = {
        '.txt', '.log', '.json', '.csv', '.xlsx', '.xls',
        '.db', '.sqlite', '.sql', '.hql', '.py', '.md',
        '.pem', '.key', '.crt', '.pkl'  # 注意：.pkl文件需要额外验证
    }

    # 危险文件名黑名单
    BLACKLISTED_NAMES = {
        'CON', 'PRN', 'AUX', 'NUL',  # Windows保留名
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
        '.htaccess', '.env', '.git',  # 敏感配置文件
        'etc', 'proc', 'sys'  # Unix系统目录
    }

    # 最大路径长度（防止缓冲区溢出）
    MAX_PATH_LENGTH = 4096

    # 最大文件名长度
    MAX_FILENAME_LENGTH = 255

    @staticmethod
    def validate_path(file_path: str, base_dir: str) -> str:
        """
        验证文件路径是否在base_dir范围内

        Args:
            file_path: 用户提供的文件路径（相对或绝对）
            base_dir: 允许的根目录

        Returns:
            安全的绝对路径

        Raises:
            ValueError: 路径遍历攻击检测或路径无效

        Example:
            >>> PathValidator.validate_path("uploads/test.txt", "/app/data")
            '/app/data/uploads/test.txt'

            >>> PathValidator.validate_path("../../../etc/passwd", "/app/data")
            ValueError: Path traversal detected
        """
        # 检查路径长度
        if len(file_path) > PathValidator.MAX_PATH_LENGTH:
            raise ValueError(
                f"Path too long: {len(file_path)} > {PathValidator.MAX_PATH_LENGTH}"
            )

        # 转换为绝对路径并解析所有符号链接和相对路径
        try:
            base = Path(base_dir).resolve()
            path = (base / file_path).resolve()
        except (OSError, RuntimeError) as e:
            logger.error(f"Invalid path: {e}")
            raise ValueError(f"Invalid path: {e}")

        # 检查路径是否在base_dir下
        try:
            path.relative_to(base)
        except ValueError:
            logger.error(
                f"Path traversal detected: {file_path} "
                f"(resolved to {path}, outside base {base})"
            )
            raise ValueError(
                f"Path traversal detected: {file_path} is outside {base_dir}"
            )

        # 验证路径中的每个组件
        try:
            PathValidator._validate_path_components(path)
        except ValueError as e:
            logger.error(f"Invalid path component: {e}")
            raise

        logger.debug(f"Path validated: {path}")
        return str(path)

    @staticmethod
    def _validate_path_components(path: Path) -> None:
        """
        验证路径中的每个组件

        Args:
            path: 要验证的路径

        Raises:
            ValueError: 包含非法组件
        """
        for part in path.parts:
            # 检查黑名单
            if part in PathValidator.BLACKLISTED_NAMES:
                raise ValueError(f"Blacklisted path component: {part}")

            # 检查危险字符（Windows）
            if re.search(r'[<>:"|?*]', part):
                raise ValueError(f"Invalid characters in path component: {part}")

    @staticmethod
    def safe_filename(filename: str, max_length: Optional[int] = None) -> str:
        """
        生成安全的文件名

        Args:
            filename: 原始文件名
            max_length: 最大长度（默认MAX_FILENAME_LENGTH）

        Returns:
            安全的文件名

        Example:
            >>> PathValidator.safe_filename("../../../etc/passwd")
            '________etc_passwd'

            >>> PathValidator.safe_filename("test file.txt")
            'test_file.txt'
        """
        if max_length is None:
            max_length = PathValidator.MAX_FILENAME_LENGTH

        # 移除路径分隔符和危险字符
        safe = re.sub(r'[\\/.]', '_', filename)  # 路径分隔符
        safe = re.sub(r'[<>:"|?*\x00-\x1f]', '_', safe)  # 危险字符
        safe = re.sub(r'\s+', '_', safe)  # 空格

        # 移除前导和尾随的下划线
        safe = safe.strip('_')

        # 如果为空，生成默认名称
        if not safe:
            safe = "unnamed_file"

        # 限制长度
        if len(safe) > max_length:
            # 保留扩展名
            name, ext = os.path.splitext(safe)
            safe = name[:max_length - len(ext)] + ext

        logger.debug(f"Safe filename generated: {filename} -> {safe}")
        return safe

    @staticmethod
    def validate_extension(filename: str, allowed: Optional[set] = None) -> bool:
        """
        验证文件扩展名是否在允许列表中

        Args:
            filename: 文件名
            allowed: 允许的扩展名集合（默认使用ALLOWED_EXTENSIONS）

        Returns:
            True if extension is allowed, False otherwise
        """
        if allowed is None:
            allowed = PathValidator.ALLOWED_EXTENSIONS

        ext = os.path.splitext(filename)[1].lower()

        if ext not in allowed:
            logger.warning(f"File extension not allowed: {ext}")
            return False

        return True

    @staticmethod
    def safe_join(base_dir: str, *paths: str) -> str:
        """
        安全地连接路径组件（防止路径遍历）

        Args:
            base_dir: 基础目录
            *paths: 路径组件

        Returns:
            安全的连接后的路径

        Raises:
            ValueError: 路径遍历攻击检测
        """
        if not paths:
            return base_dir

        # 连接所有路径
        joined = os.path.join(base_dir, *paths)

        # 验证最终路径
        return PathValidator.validate_path(joined, base_dir)

    @staticmethod
    def normalize_path(path: str) -> str:
        """
        标准化路径（解析.和..）

        Args:
            path: 原始路径

        Returns:
            标准化后的路径
        """
        try:
            # 使用Path.normalize()或resolve()
            normalized = os.path.normpath(path)
            return normalized
        except Exception as e:
            logger.error(f"Failed to normalize path: {e}")
            raise ValueError(f"Invalid path: {path}")


# 快捷函数
def validate_path(file_path: str, base_dir: str) -> str:
    """快捷函数：验证文件路径"""
    return PathValidator.validate_path(file_path, base_dir)


def safe_filename(filename: str, max_length: Optional[int] = None) -> str:
    """快捷函数：生成安全文件名"""
    return PathValidator.safe_filename(filename, max_length)


def safe_join(base_dir: str, *paths: str) -> str:
    """快捷函数：安全连接路径"""
    return PathValidator.safe_join(base_dir, *paths)


logger.info("✅ PathValidator模块已加载 (1.0.0)")
