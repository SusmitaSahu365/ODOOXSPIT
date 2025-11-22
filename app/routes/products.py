from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Product, Category, Warehouse, StockMovement
from app.forms import ProductForm, CategoryForm
from sqlalchemy import desc

bp = Blueprint('products', __name__, url_prefix='/products')

@bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '')
    
    query = Product.query.filter_by(is_active=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(
            (Product.name.ilike(f'%{search}%')) | 
            (Product.sku.ilike(f'%{search}%')) |
            (Product.barcode.ilike(f'%{search}%'))
        )
    
    products = query.order_by(desc(Product.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    categories = Category.query.all()
    
    product_data = []
    for product in products.items:
        current_stock = product.get_current_stock()
        days_left = product.get_days_left()
        reorder_qty = product.get_reorder_quantity()
        
        product_data.append({
            'product': product,
            'current_stock': current_stock,
            'days_left': days_left if days_left != float('inf') else None,
            'needs_reorder': current_stock < product.minimum_stock,
            'reorder_qty': reorder_qty
        })
    
    return render_template('products/index.html', 
                         products=products,
                         product_data=product_data,
                         categories=categories)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ProductForm()
    
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            sku=form.sku.data,
            barcode=form.barcode.data,
            category_id=form.category_id.data,
            unit_of_measure=form.unit_of_measure.data,
            minimum_stock=form.minimum_stock.data,
            ideal_stock=form.ideal_stock.data,
            description=form.description.data
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash(f'Product "{product.name}" created successfully!', 'success')
        return redirect(url_for('products.detail', id=product.id))
    
    return render_template('products/create.html', form=form)

@bp.route('/<int:id>')
@login_required
def detail(id):
    product = Product.query.get_or_404(id)
    
    current_stock = product.get_current_stock()
    days_left = product.get_days_left()
    avg_usage = product.get_average_daily_usage()
    reorder_qty = product.get_reorder_quantity()
    
    recent_movements = StockMovement.query.filter_by(product_id=id).order_by(
        desc(StockMovement.created_at)
    ).limit(20).all()
    
    warehouses = Warehouse.query.filter_by(is_active=True).all()
    warehouse_stock = []
    for warehouse in warehouses:
        stock = product.get_current_stock(warehouse.id)
        warehouse_stock.append({
            'warehouse': warehouse,
            'stock': stock
        })
    
    return render_template('products/detail.html',
                         product=product,
                         current_stock=current_stock,
                         days_left=days_left if days_left != float('inf') else None,
                         avg_usage=round(avg_usage, 2),
                         reorder_qty=reorder_qty,
                         recent_movements=recent_movements,
                         warehouse_stock=warehouse_stock)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.sku = form.sku.data
        product.barcode = form.barcode.data
        product.category_id = form.category_id.data
        product.unit_of_measure = form.unit_of_measure.data
        product.minimum_stock = form.minimum_stock.data
        product.ideal_stock = form.ideal_stock.data
        product.description = form.description.data
        
        db.session.commit()
        
        flash(f'Product "{product.name}" updated successfully!', 'success')
        return redirect(url_for('products.detail', id=product.id))
    
    return render_template('products/edit.html', form=form, product=product)

@bp.route('/search-barcode')
@login_required
def search_barcode():
    barcode = request.args.get('barcode', '')
    
    if not barcode:
        return jsonify({'error': 'No barcode provided'}), 400
    
    product = Product.query.filter_by(barcode=barcode, is_active=True).first()
    
    if product:
        return jsonify({
            'success': True,
            'product': {
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'barcode': product.barcode,
                'current_stock': product.get_current_stock(),
                'unit': product.unit_of_measure
            }
        })
    else:
        return jsonify({'success': False, 'error': 'Product not found'}), 404

@bp.route('/categories')
@login_required
def categories():
    categories = Category.query.all()
    return render_template('products/categories.html', categories=categories)

@bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    form = CategoryForm()
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(category)
        db.session.commit()
        
        flash(f'Category "{category.name}" created successfully!', 'success')
        return redirect(url_for('products.categories'))
    
    return render_template('products/create_category.html', form=form)
