from datetime import datetime
from printaiapp import db, login_manager
from sqlalchemy import Column, Integer, ForeignKey
from flask_login import UserMixin
from printaiapp import bcrypt
from sqlalchemy import func
import uuid


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=True)
    last_name = db.Column(db.String(20), nullable=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    ip_address = db.Column(db.String(20), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)


    def get_id(self):
        return (self.user_id)

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
        
    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

class Products(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(1000), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    unique_id = db.Column(db.String(36), nullable=False, unique=True, default=str(uuid.uuid4()))
    __table_args__ = (db.Index('idx_unique_id', 'unique_id'),)

    @classmethod
    def create_from_variant(cls, variant, product_id):
        unique_id = str(uuid.uuid4())
        return cls(
            product_id=product_id,
            product_name=variant['name'],
            quantity=1,
            price=variant['price'],
            unique_id=unique_id
        )

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.TIMESTAMP, nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    product_unique_id = db.Column(db.String(36), db.ForeignKey('products.unique_id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    mockup_url = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    variant_id = db.Column(db.Integer, nullable=False)
    product = db.relationship('Products', primaryjoin="and_(Cart.product_id==Products.product_id, Cart.product_unique_id==Products.unique_id)")

class Checkout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    total_price = db.Column(db.Integer, db.ForeignKey('cart.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Image_gen(db.Model):
    __tablename__ = 'images'
    image_id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(512), nullable=False)
    prompt = db.Column(db.String(256), nullable=False)
    seed = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    creator = db.relationship('User', backref=db.backref('images', lazy=True))