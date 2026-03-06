#!/usr/bin/env python3
"""
JWT 认证工具模块
提供 token 生成、验证和用户认证装饰器
"""

import jwt
from functools import wraps
from flask import request, jsonify, current_app
from datetime import datetime, timedelta


def get_user_model():
    """延迟导入 User 模型以避免循环导入"""
    from app import User
    return User


def generate_token(user_id, expires_in=24):
    """
    生成 JWT token

    Args:
        user_id: 用户 ID
        expires_in: 过期时间（小时），默认 24 小时

    Returns:
        str: JWT token
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=expires_in),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')


def decode_token(token):
    """
    解码 JWT token

    Args:
        token: JWT token 字符串

    Returns:
        dict: 解码后的 payload

    Raises:
        jwt.ExpiredSignatureError: token 已过期
        jwt.InvalidTokenError: 无效的 token
    """
    return jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])


def get_user_id_from_token():
    """
    从请求头中提取用户 ID

    Returns:
        int: 用户 ID，如果未找到或无效则返回 None
    """
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return None

    token = auth_header.split(' ')[1]

    try:
        payload = decode_token(token)
        return payload.get('user_id')
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def token_required(f):
    """
    路由保护装饰器
    验证请求是否包含有效的 JWT token

    用法:
        @app.route('/api/protected')
        @token_required
        def protected_route():
            user_id = get_user_id_from_token()
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_user_id_from_token()

        if user_id is None:
            return jsonify({'error': 'Unauthorized - Invalid or missing token'}), 401

        # 验证用户是否存在
        User = get_user_model()
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return jsonify({'error': 'Unauthorized - User not found or inactive'}), 401

        # 将 user_id 添加到 request 对象中，供路由函数使用
        request.current_user_id = user_id

        return f(*args, **kwargs)

    return decorated_function


def optional_token(f):
    """
    可选的 token 验证装饰器
    如果提供了有效的 token 则验证，否则不验证

    用法:
        @app.route('/api/optional')
        @optional_token
        def optional_route():
            user_id = get_user_id_from_token()
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_user_id_from_token()

        if user_id is not None:
            User = get_user_model()
            user = User.query.get(user_id)
            if user and user.is_active:
                request.current_user_id = user_id
            else:
                request.current_user_id = None
        else:
            request.current_user_id = None

        return f(*args, **kwargs)

    return decorated_function
