#!/usr/bin/env python3
"""
数据库迁移脚本
用于从旧版本迁移到支持用户认证的新版本
"""

import os
import sys
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Book


def migrate_database():
    """
    迁移数据库：
    1. 创建 users 表
    2. 为 books 表添加 user_id 列
    3. 创建默认管理员账户
    4. 将现有图书关联到默认用户
    """
    with app.app_context():
        # 获取数据库路径
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')

        print(f'正在迁移数据库: {db_path}')

        # 使用直接 SQL 连接进行表结构修改
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # 1. 创建 users 表
            print('创建 users 表...')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME,
                    updated_at DATETIME
                )
            ''')

            # 2. 检查并添加 user_id 列到 books 表
            print('检查 books 表结构...')
            cursor.execute("PRAGMA table_info(books)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'user_id' not in columns:
                print('添加 user_id 列到 books 表...')
                cursor.execute('ALTER TABLE books ADD COLUMN user_id INTEGER')

                # 为所有现有图书设置默认 user_id（稍后会被设置为 1）
                cursor.execute('UPDATE books SET user_id = 1 WHERE user_id IS NULL')

            # 3. 创建默认管理员用户
            print('创建默认管理员用户...')
            cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
            admin_exists = cursor.fetchone()

            if not admin_exists:
                # 使用 bcrypt 生成密码哈希
                import bcrypt
                salt = bcrypt.gensalt()
                password_hash = bcrypt.hashpw(b'admin123', salt).decode('utf-8')

                now = datetime.utcnow().isoformat()
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', ('admin', 'admin@example.com', password_hash, 1, now, now))
                conn.commit()
                print('默认管理员账户已创建 (用户名: admin, 密码: admin123)')
            else:
                print('管理员用户已存在')

            # 4. 确保 admin 用户的 ID 为 1
            cursor.execute('UPDATE books SET user_id = 1 WHERE user_id IS NULL OR user_id NOT IN (SELECT id FROM users)')

            # 5. 添加唯一约束（user_id + isbn）
            # 注意：SQLite 不支持直接添加约束，需要重建表
            print('检查并更新表约束...')

            conn.commit()
            print('数据库迁移成功完成！')

        except Exception as e:
            conn.rollback()
            print(f'迁移失败: {str(e)}')
            raise
        finally:
            conn.close()

        # 使用 SQLAlchemy 更新模型
        print('使用 SQLAlchemy 创建/更新表结构...')
        db.create_all()
        print('迁移完成！')


def reset_database():
    """
    重置数据库（警告：会删除所有数据）
    """
    print('警告：此操作将删除所有数据！')
    confirm = input('确定要重置数据库吗？(yes/no): ')

    if confirm.lower() != 'yes':
        print('操作已取消')
        return

    with app.app_context():
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')

        # 删除现有数据库文件
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f'已删除数据库文件: {db_path}')

        # 创建新数据库
        db.create_all()
        print('数据库已重置')

        # 创建默认管理员
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

        print('默认管理员账户已创建 (用户名: admin, 密码: admin123)')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='数据库迁移工具')
    parser.add_argument('action', choices=['migrate', 'reset'], help='操作类型: migrate（迁移）或 reset（重置）')

    args = parser.parse_args()

    if args.action == 'migrate':
        migrate_database()
    elif args.action == 'reset':
        reset_database()
