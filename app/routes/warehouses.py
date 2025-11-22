from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models import Warehouse
from app.forms import WarehouseForm

bp = Blueprint('warehouses', __name__, url_prefix='/warehouses')

@bp.route('/')
@login_required
def index():
    warehouses = Warehouse.query.all()
    return render_template('warehouses/index.html', warehouses=warehouses)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = WarehouseForm()
    
    if form.validate_on_submit():
        warehouse = Warehouse(
            name=form.name.data,
            location=form.location.data
        )
        db.session.add(warehouse)
        db.session.commit()
        
        flash(f'Warehouse "{warehouse.name}" created successfully!', 'success')
        return redirect(url_for('warehouses.index'))
    
    return render_template('warehouses/create.html', form=form)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    warehouse = Warehouse.query.get_or_404(id)
    form = WarehouseForm(obj=warehouse)
    
    if form.validate_on_submit():
        warehouse.name = form.name.data
        warehouse.location = form.location.data
        db.session.commit()
        
        flash(f'Warehouse "{warehouse.name}" updated successfully!', 'success')
        return redirect(url_for('warehouses.index'))
    
    return render_template('warehouses/edit.html', form=form, warehouse=warehouse)

@bp.route('/<int:id>/toggle', methods=['POST'])
@login_required
def toggle(id):
    warehouse = Warehouse.query.get_or_404(id)
    warehouse.is_active = not warehouse.is_active
    db.session.commit()
    
    status = 'activated' if warehouse.is_active else 'deactivated'
    flash(f'Warehouse "{warehouse.name}" {status} successfully!', 'success')
    return redirect(url_for('warehouses.index'))
