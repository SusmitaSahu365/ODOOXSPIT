from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, FloatField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models import User, Category, Warehouse

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), EqualTo('password', message='Passwords must match')])

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=200)])
    sku = StringField('SKU/Code', validators=[DataRequired(), Length(max=100)])
    barcode = StringField('Barcode', validators=[Optional(), Length(max=100)])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    unit_of_measure = StringField('Unit of Measure', validators=[DataRequired(), Length(max=50)])
    minimum_stock = FloatField('Minimum Stock', validators=[DataRequired()], default=0)
    ideal_stock = FloatField('Ideal Stock', validators=[DataRequired()], default=0)
    description = TextAreaField('Description', validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [('', 'Select Category')] + [(c.id, c.name) for c in Category.query.all()]

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])

class WarehouseForm(FlaskForm):
    name = StringField('Warehouse Name', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location', validators=[Optional(), Length(max=200)])

class ReceiptForm(FlaskForm):
    reference = StringField('Reference', validators=[DataRequired(), Length(max=100)])
    supplier_name = StringField('Supplier Name', validators=[DataRequired(), Length(max=200)])
    warehouse_id = SelectField('Warehouse', coerce=int, validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(ReceiptForm, self).__init__(*args, **kwargs)
        self.warehouse_id.choices = [(w.id, w.name) for w in Warehouse.query.filter_by(is_active=True).all()]

class DeliveryForm(FlaskForm):
    reference = StringField('Reference', validators=[DataRequired(), Length(max=100)])
    customer_name = StringField('Customer Name', validators=[DataRequired(), Length(max=200)])
    warehouse_id = SelectField('Warehouse', coerce=int, validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(DeliveryForm, self).__init__(*args, **kwargs)
        self.warehouse_id.choices = [(w.id, w.name) for w in Warehouse.query.filter_by(is_active=True).all()]

class TransferForm(FlaskForm):
    reference = StringField('Reference', validators=[DataRequired(), Length(max=100)])
    source_warehouse_id = SelectField('Source Warehouse', coerce=int, validators=[DataRequired()])
    dest_warehouse_id = SelectField('Destination Warehouse', coerce=int, validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(TransferForm, self).__init__(*args, **kwargs)
        warehouses = Warehouse.query.filter_by(is_active=True).all()
        self.source_warehouse_id.choices = [(w.id, w.name) for w in warehouses]
        self.dest_warehouse_id.choices = [(w.id, w.name) for w in warehouses]

class AdjustmentForm(FlaskForm):
    reference = StringField('Reference', validators=[DataRequired(), Length(max=100)])
    warehouse_id = SelectField('Warehouse', coerce=int, validators=[DataRequired()])
    reason = StringField('Reason', validators=[Optional(), Length(max=200)])
    notes = TextAreaField('Notes', validators=[Optional()])
    
    def __init__(self, *args, **kwargs):
        super(AdjustmentForm, self).__init__(*args, **kwargs)
        self.warehouse_id.choices = [(w.id, w.name) for w in Warehouse.query.filter_by(is_active=True).all()]
