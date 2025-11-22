from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import (Receipt, ReceiptLine, Delivery, DeliveryLine, 
                       Transfer, TransferLine, Adjustment, AdjustmentLine,
                       Product, Warehouse, StockMovement, Operation)
from app.forms import ReceiptForm, DeliveryForm, TransferForm, AdjustmentForm
from datetime import datetime
from sqlalchemy import desc

bp = Blueprint('operations', __name__, url_prefix='/operations')

@bp.route('/receipts')
@login_required
def receipts():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Receipt.query
    if status:
        query = query.filter_by(status=status)
    
    receipts = query.order_by(desc(Receipt.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('operations/receipts.html', receipts=receipts)

@bp.route('/receipts/create', methods=['GET', 'POST'])
@login_required
def create_receipt():
    form = ReceiptForm()
    
    if form.validate_on_submit():
        receipt = Receipt(
            reference=form.reference.data,
            supplier_name=form.supplier_name.data,
            warehouse_id=form.warehouse_id.data,
            notes=form.notes.data,
            status='draft',
            created_by=current_user.id
        )
        db.session.add(receipt)
        db.session.commit()
        
        flash(f'Receipt "{receipt.reference}" created successfully!', 'success')
        return redirect(url_for('operations.edit_receipt', id=receipt.id))
    
    return render_template('operations/create_receipt.html', form=form)

@bp.route('/receipts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_receipt(id):
    receipt = Receipt.query.get_or_404(id)
    products = Product.query.filter_by(is_active=True).all()
    
    return render_template('operations/edit_receipt.html', receipt=receipt, products=products)

@bp.route('/receipts/<int:id>/add-line', methods=['POST'])
@login_required
def add_receipt_line(id):
    receipt = Receipt.query.get_or_404(id)
    
    if receipt.status != 'draft':
        return jsonify({'error': 'Can only edit draft receipts'}), 400
    
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity', 0)
    unit_price = request.json.get('unit_price', 0)
    
    line = ReceiptLine(
        receipt_id=receipt.id,
        product_id=product_id,
        quantity=quantity,
        unit_price=unit_price
    )
    db.session.add(line)
    db.session.commit()
    
    return jsonify({'success': True, 'line_id': line.id})

@bp.route('/receipts/<int:id>/validate', methods=['POST'])
@login_required
def validate_receipt(id):
    receipt = Receipt.query.get_or_404(id)
    
    if receipt.status != 'draft':
        return jsonify({'error': 'Receipt already validated'}), 400
    
    for line in receipt.lines:
        movement = StockMovement(
            product_id=line.product_id,
            warehouse_id=receipt.warehouse_id,
            quantity=line.quantity,
            operation_type='receipt',
            reference=receipt.reference,
            notes=f'Receipt from {receipt.supplier_name}',
            created_by=current_user.id
        )
        db.session.add(movement)
        
        operation = Operation(
            operation_type='receipt',
            reference=receipt.reference,
            description=f'Receipt from {receipt.supplier_name}',
            quantity=line.quantity,
            product_name=line.product.name,
            created_by=current_user.id
        )
        db.session.add(operation)
    
    receipt.status = 'done'
    receipt.validated_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Receipt "{receipt.reference}" validated successfully!', 'success')
    return jsonify({'success': True})

@bp.route('/deliveries')
@login_required
def deliveries():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Delivery.query
    if status:
        query = query.filter_by(status=status)
    
    deliveries = query.order_by(desc(Delivery.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('operations/deliveries.html', deliveries=deliveries)

@bp.route('/deliveries/create', methods=['GET', 'POST'])
@login_required
def create_delivery():
    form = DeliveryForm()
    
    if form.validate_on_submit():
        delivery = Delivery(
            reference=form.reference.data,
            customer_name=form.customer_name.data,
            warehouse_id=form.warehouse_id.data,
            notes=form.notes.data,
            status='draft',
            created_by=current_user.id
        )
        db.session.add(delivery)
        db.session.commit()
        
        flash(f'Delivery "{delivery.reference}" created successfully!', 'success')
        return redirect(url_for('operations.edit_delivery', id=delivery.id))
    
    return render_template('operations/create_delivery.html', form=form)

@bp.route('/deliveries/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_delivery(id):
    delivery = Delivery.query.get_or_404(id)
    products = Product.query.filter_by(is_active=True).all()
    
    return render_template('operations/edit_delivery.html', delivery=delivery, products=products)

@bp.route('/deliveries/<int:id>/add-line', methods=['POST'])
@login_required
def add_delivery_line(id):
    delivery = Delivery.query.get_or_404(id)
    
    if delivery.status != 'draft':
        return jsonify({'error': 'Can only edit draft deliveries'}), 400
    
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity', 0)
    
    product = Product.query.get(product_id)
    current_stock = product.get_current_stock(delivery.warehouse_id)
    
    if current_stock < quantity:
        return jsonify({'error': f'Insufficient stock. Available: {current_stock}'}), 400
    
    line = DeliveryLine(
        delivery_id=delivery.id,
        product_id=product_id,
        quantity=quantity
    )
    db.session.add(line)
    db.session.commit()
    
    return jsonify({'success': True, 'line_id': line.id})

@bp.route('/deliveries/<int:id>/validate', methods=['POST'])
@login_required
def validate_delivery(id):
    delivery = Delivery.query.get_or_404(id)
    
    if delivery.status != 'draft':
        return jsonify({'error': 'Delivery already validated'}), 400
    
    for line in delivery.lines:
        movement = StockMovement(
            product_id=line.product_id,
            warehouse_id=delivery.warehouse_id,
            quantity=-line.quantity,
            operation_type='delivery',
            reference=delivery.reference,
            notes=f'Delivery to {delivery.customer_name}',
            created_by=current_user.id
        )
        db.session.add(movement)
        
        operation = Operation(
            operation_type='delivery',
            reference=delivery.reference,
            description=f'Delivery to {delivery.customer_name}',
            quantity=line.quantity,
            product_name=line.product.name,
            created_by=current_user.id
        )
        db.session.add(operation)
    
    delivery.status = 'done'
    delivery.validated_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Delivery "{delivery.reference}" validated successfully!', 'success')
    return jsonify({'success': True})

@bp.route('/transfers')
@login_required
def transfers():
    page = request.args.get('page', 1, type=int)
    transfers = Transfer.query.order_by(desc(Transfer.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('operations/transfers.html', transfers=transfers)

@bp.route('/transfers/create', methods=['GET', 'POST'])
@login_required
def create_transfer():
    form = TransferForm()
    
    if form.validate_on_submit():
        if form.source_warehouse_id.data == form.dest_warehouse_id.data:
            flash('Source and destination warehouses must be different.', 'error')
        else:
            transfer = Transfer(
                reference=form.reference.data,
                source_warehouse_id=form.source_warehouse_id.data,
                dest_warehouse_id=form.dest_warehouse_id.data,
                notes=form.notes.data,
                status='draft',
                created_by=current_user.id
            )
            db.session.add(transfer)
            db.session.commit()
            
            flash(f'Transfer "{transfer.reference}" created successfully!', 'success')
            return redirect(url_for('operations.edit_transfer', id=transfer.id))
    
    return render_template('operations/create_transfer.html', form=form)

@bp.route('/transfers/<int:id>/edit')
@login_required
def edit_transfer(id):
    transfer = Transfer.query.get_or_404(id)
    products = Product.query.filter_by(is_active=True).all()
    
    return render_template('operations/edit_transfer.html', transfer=transfer, products=products)

@bp.route('/transfers/<int:id>/add-line', methods=['POST'])
@login_required
def add_transfer_line(id):
    transfer = Transfer.query.get_or_404(id)
    
    if transfer.status != 'draft':
        return jsonify({'error': 'Can only edit draft transfers'}), 400
    
    product_id = request.json.get('product_id')
    quantity = request.json.get('quantity', 0)
    
    line = TransferLine(
        transfer_id=transfer.id,
        product_id=product_id,
        quantity=quantity
    )
    db.session.add(line)
    db.session.commit()
    
    return jsonify({'success': True, 'line_id': line.id})

@bp.route('/transfers/<int:id>/validate', methods=['POST'])
@login_required
def validate_transfer(id):
    transfer = Transfer.query.get_or_404(id)
    
    if transfer.status != 'draft':
        return jsonify({'error': 'Transfer already validated'}), 400
    
    for line in transfer.lines:
        outgoing = StockMovement(
            product_id=line.product_id,
            warehouse_id=transfer.source_warehouse_id,
            quantity=-line.quantity,
            operation_type='transfer_out',
            reference=transfer.reference,
            notes=f'Transfer to {transfer.dest_warehouse.name}',
            created_by=current_user.id
        )
        db.session.add(outgoing)
        
        incoming = StockMovement(
            product_id=line.product_id,
            warehouse_id=transfer.dest_warehouse_id,
            quantity=line.quantity,
            operation_type='transfer_in',
            reference=transfer.reference,
            notes=f'Transfer from {transfer.source_warehouse.name}',
            created_by=current_user.id
        )
        db.session.add(incoming)
        
        operation = Operation(
            operation_type='transfer',
            reference=transfer.reference,
            description=f'Transfer: {transfer.source_warehouse.name} → {transfer.dest_warehouse.name}',
            quantity=line.quantity,
            product_name=line.product.name,
            created_by=current_user.id
        )
        db.session.add(operation)
    
    transfer.status = 'done'
    transfer.validated_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Transfer "{transfer.reference}" validated successfully!', 'success')
    return jsonify({'success': True})

@bp.route('/adjustments')
@login_required
def adjustments():
    page = request.args.get('page', 1, type=int)
    adjustments = Adjustment.query.order_by(desc(Adjustment.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('operations/adjustments.html', adjustments=adjustments)

@bp.route('/adjustments/create', methods=['GET', 'POST'])
@login_required
def create_adjustment():
    form = AdjustmentForm()
    
    if form.validate_on_submit():
        adjustment = Adjustment(
            reference=form.reference.data,
            warehouse_id=form.warehouse_id.data,
            reason=form.reason.data,
            notes=form.notes.data,
            status='draft',
            created_by=current_user.id
        )
        db.session.add(adjustment)
        db.session.commit()
        
        flash(f'Adjustment "{adjustment.reference}" created successfully!', 'success')
        return redirect(url_for('operations.edit_adjustment', id=adjustment.id))
    
    return render_template('operations/create_adjustment.html', form=form)

@bp.route('/adjustments/<int:id>/edit')
@login_required
def edit_adjustment(id):
    adjustment = Adjustment.query.get_or_404(id)
    products = Product.query.filter_by(is_active=True).all()
    
    return render_template('operations/edit_adjustment.html', adjustment=adjustment, products=products)

@bp.route('/adjustments/<int:id>/add-line', methods=['POST'])
@login_required
def add_adjustment_line(id):
    adjustment = Adjustment.query.get_or_404(id)
    
    if adjustment.status != 'draft':
        return jsonify({'error': 'Can only edit draft adjustments'}), 400
    
    product_id = request.json.get('product_id')
    new_quantity = request.json.get('new_quantity', 0)
    
    product = Product.query.get(product_id)
    old_quantity = product.get_current_stock(adjustment.warehouse_id)
    
    line = AdjustmentLine(
        adjustment_id=adjustment.id,
        product_id=product_id,
        old_quantity=old_quantity,
        new_quantity=new_quantity
    )
    db.session.add(line)
    db.session.commit()
    
    return jsonify({'success': True, 'line_id': line.id, 'old_quantity': old_quantity})

@bp.route('/adjustments/<int:id>/validate', methods=['POST'])
@login_required
def validate_adjustment(id):
    adjustment = Adjustment.query.get_or_404(id)
    
    if adjustment.status != 'draft':
        return jsonify({'error': 'Adjustment already validated'}), 400
    
    for line in adjustment.lines:
        difference = line.difference
        
        if difference != 0:
            movement = StockMovement(
                product_id=line.product_id,
                warehouse_id=adjustment.warehouse_id,
                quantity=difference,
                operation_type='adjustment',
                reference=adjustment.reference,
                notes=f'Adjustment: {adjustment.reason}',
                created_by=current_user.id
            )
            db.session.add(movement)
            
            operation = Operation(
                operation_type='adjustment',
                reference=adjustment.reference,
                description=f'Adjustment: {adjustment.reason}',
                quantity=abs(difference),
                product_name=line.product.name,
                created_by=current_user.id
            )
            db.session.add(operation)
    
    adjustment.status = 'done'
    adjustment.validated_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Adjustment "{adjustment.reference}" validated successfully!', 'success')
    return jsonify({'success': True})

@bp.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    movements = StockMovement.query.order_by(desc(StockMovement.created_at)).paginate(
        page=page, per_page=50, error_out=False
    )
    
    return render_template('operations/history.html', movements=movements)
