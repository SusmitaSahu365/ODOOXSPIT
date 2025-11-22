from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    full_name = db.Column(db.String(100))
    role = db.Column(db.String(50), default='warehouse_staff')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    products = db.relationship('Product', backref='category', lazy='dynamic')

class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    location = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    stock_movements = db.relationship('StockMovement', backref='warehouse', lazy='dynamic')

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(100), unique=True, nullable=False, index=True)
    barcode = db.Column(db.String(100), unique=True, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    unit_of_measure = db.Column(db.String(50), default='pcs')
    minimum_stock = db.Column(db.Float, default=0)
    ideal_stock = db.Column(db.Float, default=0)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    stock_movements = db.relationship('StockMovement', backref='product', lazy='dynamic')
    receipt_lines = db.relationship('ReceiptLine', backref='product', lazy='dynamic')
    delivery_lines = db.relationship('DeliveryLine', backref='product', lazy='dynamic')
    transfer_lines = db.relationship('TransferLine', backref='product', lazy='dynamic')
    adjustment_lines = db.relationship('AdjustmentLine', backref='product', lazy='dynamic')
    
    def get_current_stock(self, warehouse_id=None):
        query = self.stock_movements
        if warehouse_id:
            query = query.filter_by(warehouse_id=warehouse_id)
        return query.with_entities(func.sum(StockMovement.quantity)).scalar() or 0
    
    def get_average_daily_usage(self, days=30):
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        total_outgoing = db.session.query(func.sum(StockMovement.quantity)).filter(
            StockMovement.product_id == self.id,
            StockMovement.quantity < 0,
            StockMovement.created_at >= cutoff_date
        ).scalar() or 0
        
        return abs(total_outgoing) / days if days > 0 else 0
    
    def get_days_left(self, warehouse_id=None):
        current_stock = self.get_current_stock(warehouse_id)
        avg_daily_usage = self.get_average_daily_usage()
        
        if avg_daily_usage > 0:
            return current_stock / avg_daily_usage
        return float('inf')
    
    def get_reorder_quantity(self):
        current_stock = self.get_current_stock()
        if current_stock < self.minimum_stock:
            return max(0, self.ideal_stock - current_stock)
        return 0

class Receipt(db.Model):
    __tablename__ = 'receipts'
    
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(100), unique=True, nullable=False)
    supplier_name = db.Column(db.String(200), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    status = db.Column(db.String(50), default='draft')
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    validated_at = db.Column(db.DateTime)
    
    lines = db.relationship('ReceiptLine', backref='receipt', lazy='dynamic', cascade='all, delete-orphan')
    warehouse = db.relationship('Warehouse', backref='receipts')
    creator = db.relationship('User', backref='receipts')

class ReceiptLine(db.Model):
    __tablename__ = 'receipt_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    receipt_id = db.Column(db.Integer, db.ForeignKey('receipts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_price = db.Column(db.Float, default=0)

class Delivery(db.Model):
    __tablename__ = 'deliveries'
    
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(100), unique=True, nullable=False)
    customer_name = db.Column(db.String(200), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    status = db.Column(db.String(50), default='draft')
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    validated_at = db.Column(db.DateTime)
    
    lines = db.relationship('DeliveryLine', backref='delivery', lazy='dynamic', cascade='all, delete-orphan')
    warehouse = db.relationship('Warehouse', backref='deliveries')
    creator = db.relationship('User', backref='deliveries')

class DeliveryLine(db.Model):
    __tablename__ = 'delivery_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey('deliveries.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)

class Transfer(db.Model):
    __tablename__ = 'transfers'
    
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(100), unique=True, nullable=False)
    source_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    dest_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    status = db.Column(db.String(50), default='draft')
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    validated_at = db.Column(db.DateTime)
    
    lines = db.relationship('TransferLine', backref='transfer', lazy='dynamic', cascade='all, delete-orphan')
    source_warehouse = db.relationship('Warehouse', foreign_keys=[source_warehouse_id], backref='outgoing_transfers')
    dest_warehouse = db.relationship('Warehouse', foreign_keys=[dest_warehouse_id], backref='incoming_transfers')
    creator = db.relationship('User', backref='transfers')

class TransferLine(db.Model):
    __tablename__ = 'transfer_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    transfer_id = db.Column(db.Integer, db.ForeignKey('transfers.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)

class Adjustment(db.Model):
    __tablename__ = 'adjustments'
    
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(100), unique=True, nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    reason = db.Column(db.String(200))
    status = db.Column(db.String(50), default='draft')
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    validated_at = db.Column(db.DateTime)
    
    lines = db.relationship('AdjustmentLine', backref='adjustment', lazy='dynamic', cascade='all, delete-orphan')
    warehouse = db.relationship('Warehouse', backref='adjustments')
    creator = db.relationship('User', backref='adjustments')

class AdjustmentLine(db.Model):
    __tablename__ = 'adjustment_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    adjustment_id = db.Column(db.Integer, db.ForeignKey('adjustments.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    old_quantity = db.Column(db.Float, nullable=False)
    new_quantity = db.Column(db.Float, nullable=False)
    
    @property
    def difference(self):
        return self.new_quantity - self.old_quantity

class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    operation_type = db.Column(db.String(50), nullable=False)
    reference = db.Column(db.String(100))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    creator = db.relationship('User', backref='stock_movements')

class Operation(db.Model):
    __tablename__ = 'operations'
    
    id = db.Column(db.Integer, primary_key=True)
    operation_type = db.Column(db.String(50), nullable=False)
    reference = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    quantity = db.Column(db.Float)
    product_name = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    creator = db.relationship('User', backref='operations')
