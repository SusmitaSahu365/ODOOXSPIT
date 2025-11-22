from app import create_app, db
from app.models import User, Product, Category, Warehouse

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Product': Product,
        'Category': Category,
        'Warehouse': Warehouse
    }

@app.cli.command()
def init_db():
    db.create_all()
    print('Database initialized.')
    
    if not Warehouse.query.first():
        main_warehouse = Warehouse(name='Main Warehouse', location='Main Location')
        db.session.add(main_warehouse)
        db.session.commit()
        print('Default warehouse created.')
    
    if not Category.query.first():
        categories = [
            Category(name='Electronics', description='Electronic items'),
            Category(name='Hardware', description='Hardware tools and materials'),
            Category(name='Office Supplies', description='Office and stationery items')
        ]
        db.session.add_all(categories)
        db.session.commit()
        print('Default categories created.')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
