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

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///../database/books.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db = SQLAlchemy(app)


# 数据模型
class Book(db.Model):
    """图书模型"""
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    publisher = db.Column(db.String(100))
    publish_date = db.Column(db.Date)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


# API 路由

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({'status': 'ok', 'service': 'book-management-api'})


@app.route('/api/books', methods=['GET'])
def get_books():
    """获取图书列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = Book.query
    
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
def get_book(book_id):
    """获取单本图书详情"""
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())


@app.route('/api/books', methods=['POST'])
def create_book():
    """创建图书"""
    data = request.get_json()
    
    book = Book(
        title=data.get('title'),
        author=data.get('author'),
        isbn=data.get('isbn'),
        publisher=data.get('publisher'),
        category=data.get('category'),
        description=data.get('description'),
        price=data.get('price'),
        stock=data.get('stock', 0)
    )
    
    if data.get('publish_date'):
        book.publish_date = datetime.strptime(data['publish_date'], '%Y-%m-%d').date()
    
    db.session.add(book)
    db.session.commit()
    
    return jsonify(book.to_dict()), 201


@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """更新图书"""
    book = Book.query.get_or_404(book_id)
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
def delete_book(book_id):
    """删除图书"""
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    
    return jsonify({'message': 'Book deleted successfully'})


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取图书分类列表"""
    categories = db.session.query(Book.category).distinct().all()
    return jsonify([c[0] for c in categories if c[0]])


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计数据"""
    total_books = Book.query.count()
    total_stock = db.session.query(db.func.sum(Book.stock)).scalar() or 0
    categories = db.session.query(Book.category).distinct().count()
    
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
    sample_books = [
        Book(title='Python编程：从入门到实践', author='Eric Matthes', 
             isbn='978-7-115-42802-8', publisher='人民邮电出版社',
             category='编程', price=89.00, stock=100),
        Book(title='深入理解计算机系统', author='Randal E. Bryant',
             isbn='978-7-111-54493-7', publisher='机械工业出版社',
             category='计算机', price=139.00, stock=50),
        Book(title='算法导论', author='Thomas H. Cormen',
             isbn='978-7-111-40701-0', publisher='机械工业出版社',
             category='算法', price=128.00, stock=80),
    ]
    
    for book in sample_books:
        existing = Book.query.filter_by(isbn=book.isbn).first()
        if not existing:
            db.session.add(book)
    
    db.session.commit()
    print('Sample data inserted.')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
