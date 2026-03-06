#!/usr/bin/env python3
"""
图书管理系统后端 API
使用 Flask + SQLAlchemy
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import bcrypt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///../database/books.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')

CORS(app)
db = SQLAlchemy(app)

# Import auth utilities after app is created
from auth import generate_token, decode_token, get_user_id_from_token, token_required


# 数据模型
class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系：一个用户可以有多本图书
    books = db.relationship('Book', backref='user', lazy=True)

    def set_password(self, password):
        """设置密码（使用 bcrypt 加密）"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self):
        """序列化为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Book(db.Model):
    """图书模型"""
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20))
    publisher = db.Column(db.String(100))
    publish_date = db.Column(db.Date)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    stock = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 复合索引：用户 + ISBN 确保同一用户下 ISBN 唯一
    __table_args__ = (
        db.UniqueConstraint('user_id', 'isbn', name='uq_user_isbn'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'publisher': self.publisher,
            'publish_date': self.publish_date.isoformat() if self.publish_date else None,
            'category': self.category,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# API 路由

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'service': 'book-management-api'})


# 认证相关端点

@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()

    # 验证必填字段
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email and password are required'}), 400

    # 检查用户名是否已存在
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409

    # 检查邮箱是否已存在
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409

    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    # 生成 token
    token = generate_token(user.id)

    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict(),
        'token': token
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400

    # 查找用户
    user = User.query.filter_by(username=data['username']).first()

    # 验证密码
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401

    # 检查账户是否激活
    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 403

    # 生成 token
    token = generate_token(user.id)

    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'token': token
    }), 200


@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user():
    """获取当前用户信息"""
    user_id = request.current_user_id
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(user.to_dict()), 200


@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout():
    """用户登出（客户端删除 token）"""
    return jsonify({'message': 'Logout successful'}), 200


@app.route('/api/books', methods=['GET'])
@token_required
def get_books():
    """获取图书列表"""
    user_id = request.current_user_id
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')

    query = Book.query.filter_by(user_id=user_id)

    if search:
        query = query.filter(
            db.or_(
                Book.title.contains(search),
                Book.author.contains(search),
                Book.isbn.contains(search)
            )
        )

    if category:
        query = query.filter(Book.category == category)

    pagination = query.order_by(Book.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'items': [book.to_dict() for book in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page,
        'per_page': per_page
    })


@app.route('/api/books/<int:book_id>', methods=['GET'])
@token_required
def get_book(book_id):
    """获取单本图书详情"""
    user_id = request.current_user_id
    book = Book.query.filter_by(id=book_id, user_id=user_id).first_or_404()
    return jsonify(book.to_dict())


@app.route('/api/books', methods=['POST'])
@token_required
def create_book():
    """创建图书"""
    user_id = request.current_user_id
    data = request.get_json()

    book = Book(
        title=data.get('title'),
        author=data.get('author'),
        isbn=data.get('isbn'),
        publisher=data.get('publisher'),
        category=data.get('category'),
        description=data.get('description'),
        price=data.get('price'),
        stock=data.get('stock', 0),
        user_id=user_id
    )

    if data.get('publish_date'):
        book.publish_date = datetime.strptime(data['publish_date'], '%Y-%m-%d').date()

    db.session.add(book)
    db.session.commit()

    return jsonify(book.to_dict()), 201


@app.route('/api/books/<int:book_id>', methods=['PUT'])
@token_required
def update_book(book_id):
    """更新图书"""
    user_id = request.current_user_id
    book = Book.query.filter_by(id=book_id, user_id=user_id).first_or_404()
    data = request.get_json()

    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.isbn = data.get('isbn', book.isbn)
    book.publisher = data.get('publisher', book.publisher)
    book.category = data.get('category', book.category)
    book.description = data.get('description', book.description)
    book.price = data.get('price', book.price)
    book.stock = data.get('stock', book.stock)

    if data.get('publish_date'):
        book.publish_date = datetime.strptime(data['publish_date'], '%Y-%m-%d').date()

    db.session.commit()

    return jsonify(book.to_dict())


@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@token_required
def delete_book(book_id):
    """删除图书"""
    user_id = request.current_user_id
    book = Book.query.filter_by(id=book_id, user_id=user_id).first_or_404()
    db.session.delete(book)
    db.session.commit()

    return jsonify({'message': 'Book deleted successfully'})


@app.route('/api/categories', methods=['GET'])
@token_required
def get_categories():
    """获取图书分类列表"""
    user_id = request.current_user_id
    categories = db.session.query(Book.category).filter_by(user_id=user_id).distinct().all()
    return jsonify([c[0] for c in categories if c[0]])


@app.route('/api/stats', methods=['GET'])
@token_required
def get_stats():
    """获取统计数据"""
    user_id = request.current_user_id
    total_books = Book.query.filter_by(user_id=user_id).count()
    total_stock = db.session.query(db.func.sum(Book.stock)).filter_by(user_id=user_id).scalar() or 0
    categories = db.session.query(Book.category).filter_by(user_id=user_id).distinct().count()

    return jsonify({
        'total_books': total_books,
        'total_stock': total_stock,
        'categories': categories
    })


# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


# 初始化数据库
@app.cli.command('init-db')
def init_db():
    """初始化数据库"""
    db.create_all()
    print('Database initialized.')


# 插入示例数据
@app.cli.command('seed')
def seed_data():
    """插入示例数据"""
    # 创建默认管理员用户
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.flush()
        print('Default admin user created (username: admin, password: admin123)')
    else:
        print('Admin user already exists')

    # 获取 admin 用户 ID
    admin_user = User.query.filter_by(username='admin').first()

    sample_books = [
        Book(title='Python编程：从入门到实践', author='Eric Matthes',
             isbn='978-7-115-42802-8', publisher='人民邮电出版社',
             category='编程', price=89.00, stock=100, user_id=admin_user.id),
        Book(title='深入理解计算机系统', author='Randal E. Bryant',
             isbn='978-7-111-54493-7', publisher='机械工业出版社',
             category='计算机', price=139.00, stock=50, user_id=admin_user.id),
        Book(title='算法导论', author='Thomas H. Cormen',
             isbn='978-7-111-40701-0', publisher='机械工业出版社',
             category='算法', price=128.00, stock=80, user_id=admin_user.id),
    ]

    for book in sample_books:
        existing = Book.query.filter_by(user_id=admin_user.id, isbn=book.isbn).first()
        if not existing:
            db.session.add(book)

    db.session.commit()
    print('Sample data inserted.')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
