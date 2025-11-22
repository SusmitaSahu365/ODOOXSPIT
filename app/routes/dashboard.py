from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import Product, Receipt, Delivery, Transfer, Operation, Warehouse
from app import db
from sqlalchemy import func, desc
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@bp.route('/dashboard')
@login_required
def index():
    total_products = Product.query.filter_by(is_active=True).count()
    
    low_stock_items = []
    for product in Product.query.filter_by(is_active=True).all():
        current_stock = product.get_current_stock()
        if current_stock <= product.minimum_stock:
            low_stock_items.append(product)
    
    pending_receipts = Receipt.query.filter(Receipt.status.in_(['draft', 'waiting'])).count()
    pending_deliveries = Delivery.query.filter(Delivery.status.in_(['draft', 'waiting'])).count()
    pending_transfers = Transfer.query.filter(Transfer.status.in_(['draft', 'waiting'])).count()
    
    recent_operations = Operation.query.order_by(desc(Operation.created_at)).limit(10).all()
    
    low_stock_predictor = []
    for product in Product.query.filter_by(is_active=True).all():
        days_left = product.get_days_left()
        if days_left < 7 and days_left != float('inf'):
            low_stock_predictor.append({
                'product': product,
                'days_left': round(days_left, 1),
                'current_stock': product.get_current_stock()
            })
    
    low_stock_predictor.sort(key=lambda x: x['days_left'])
    
    stats = {
        'total_products': total_products,
        'low_stock_count': len(low_stock_items),
        'pending_receipts': pending_receipts,
        'pending_deliveries': pending_deliveries,
        'pending_transfers': pending_transfers
    }
    
    return render_template('dashboard/index.html', 
                         stats=stats, 
                         recent_operations=recent_operations,
                         low_stock_predictor=low_stock_predictor[:5])
