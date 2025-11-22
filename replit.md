# StockMaster - Inventory Management System

## Overview
StockMaster is a comprehensive modular Inventory Management System (IMS) built with Flask, TailwindCSS, and Alpine.js. It digitizes and streamlines all stock-related operations within a business, replacing manual registers and Excel sheets with a centralized, real-time application.

## Technology Stack
- **Backend**: Flask 3.0.0 with SQLAlchemy ORM
- **Frontend**: TailwindCSS 3.x + Alpine.js 3.x
- **Database**: SQLite (for offline functionality)
- **Authentication**: Flask-Login with custom authentication
- **Barcode Scanning**: html5-qrcode library

## Project Structure
```
/app
  /__init__.py           - Flask app factory
  /models.py             - SQLAlchemy database models
  /forms.py              - WTForms form definitions
  /routes/               - Blueprint routes
    /auth.py             - Authentication routes
    /dashboard.py        - Dashboard routes
    /products.py         - Product management routes
    /operations.py       - Operations routes (receipts, deliveries, transfers, adjustments)
    /warehouses.py       - Warehouse management routes
    /profile.py          - User profile routes
  /templates/            - Jinja2 HTML templates
    /base.html           - Base template with sidebar navigation
    /auth/               - Login and signup pages
    /dashboard/          - Dashboard with KPIs
    /products/           - Product management pages
    /operations/         - Operations pages
    /warehouses/         - Warehouse management pages
    /profile/            - User profile page
/config.py               - Application configuration
/main.py                 - Application entry point
/requirements.txt        - Python dependencies
```

## Core Features

### 1. Authentication & User Management
- User signup and login
- Role-based access (Inventory Manager, Warehouse Staff)
- Session management with Flask-Login

### 2. Dashboard
- **KPIs**: Total Products, Low Stock Items, Pending Receipts/Deliveries, Pending Transfers
- **Recent Operations Timeline**: Displays all operations sorted by latest first
- **Quick Actions Widget**: Shortcuts to Add Product, Create Receipt, Create Delivery, Internal Transfer, and Adjustment
- **Smart Low-Stock Predictor**: Shows items with days left < 7 based on average daily usage

### 3. Product Management
- Create/Edit products with SKU, barcode, category, unit of measure
- Set minimum and ideal stock levels
- View current stock by warehouse
- Track stock movements and history
- **Barcode Scanner**: Camera-based product search using html5-qrcode
- **Reorder Recommendation System**: Alerts when stock < minimum, displays recommended reorder quantity

### 4. Operations

#### Receipts (Incoming Stock)
- Create receipts from suppliers
- Add products with quantities
- Validate to automatically increase stock levels
- Track receipt status (Draft, Done)

#### Delivery Orders (Outgoing Stock)
- Create deliveries to customers
- Stock validation before delivery
- Validate to automatically decrease stock levels

#### Internal Transfers
- Move stock between warehouses/locations
- Dual-entry system (outgoing from source, incoming to destination)
- Full logging of all movements

#### Inventory Adjustments
- Fix mismatches between recorded stock and physical count
- Automatic calculation of differences
- Reason tracking for adjustments

### 5. Warehouse Management
- Create and manage multiple warehouses
- Track location information
- View stock levels per warehouse
- Active/inactive status management

### 6. Move History
- Complete stock ledger showing all stock movements
- Filterable by operation type, product, warehouse
- Timestamped entries with references

## Unique Features

### 1. Smart Low-Stock Predictor (Days Left)
- Tracks outgoing quantity per product per day
- Calculates average daily usage over 30 days
- Formula: Days Left = Current Stock ÷ Avg Daily Usage
- Highlights items with < 7 days remaining on dashboard

### 2. Recent Operations Timeline
- Logs all operations: Receipts, Deliveries, Transfers, Adjustments
- Displays on dashboard sorted by latest first
- Includes icon, quantity, and timestamp for each entry

### 3. Quick Actions Widget
- Dashboard card with shortcuts to:
  - Add Product
  - Create Receipt
  - Create Delivery
  - Internal Transfer
  - Adjustment

### 4. Barcode Scanner for Product Search
- Uses html5-qrcode library
- Opens camera to scan barcodes
- Auto-navigates to product detail page
- Supports standard barcode formats

### 5. Reorder Recommendation System
- Formula: reorder_qty = ideal_stock - current_stock
- Alerts when current_stock < minimum_stock
- Displays recommended reorder quantity on product detail page

## Database Schema

### Core Models
- **User**: Authentication and user management
- **Product**: Product information, SKU, barcode, stock levels
- **Category**: Product categorization
- **Warehouse**: Storage location management
- **Receipt**: Incoming stock tracking
- **Delivery**: Outgoing stock tracking
- **Transfer**: Internal stock movements
- **Adjustment**: Stock discrepancy corrections
- **StockMovement**: Ledger of all stock changes
- **Operation**: Timeline of all operations

## Getting Started

### Initial Setup
1. Database is automatically created on first run
2. Default warehouse and categories are created via `flask init-db`
3. Access the application at the provided URL
4. Sign up for a new account to get started

### First Steps
1. Create warehouses (Settings > Warehouses)
2. Add product categories (Products > Categories)
3. Add products with minimum/ideal stock levels
4. Start creating operations (Receipts, Deliveries, etc.)

## Development Guidelines

### For Multiple Developers
- **Modular Structure**: Each feature has its own route blueprint and templates
- **Clear Separation**: Models, routes, forms, and templates are separated
- **RESTful Routes**: Consistent URL patterns across all modules
- **Template Inheritance**: Base template with reusable components
- **Form Validation**: WTForms for consistent form handling
- **Database Migrations**: Use Flask-SQLAlchemy for schema changes

### Code Conventions
- Follow Flask blueprints pattern for modularity
- Use SQLAlchemy ORM for all database operations
- TailwindCSS utility classes for styling
- Alpine.js for interactive components
- Jinja2 templates with proper inheritance

## Recent Changes
- 2025-11-22: Initial project setup with all core features
- 2025-11-22: Implemented all 5 unique features (Smart Predictor, Timeline, Quick Actions, Barcode Scanner, Reorder System)
- 2025-11-22: Created comprehensive UI with TailwindCSS and Alpine.js
- 2025-11-22: Switched from PostgreSQL to SQLite for offline functionality and portability

## Future Enhancements
- Gmail integration for automated email notifications (low stock alerts, delivery confirmations)
- GitHub integration for version control and collaborative development workflows
- PDF export for receipts, deliveries, and inventory reports
- Advanced analytics dashboard with charts for stock trends and usage patterns
- Role-based access control (Inventory Manager vs Warehouse Staff permissions)
- Batch operations for bulk product imports/exports via CSV

## User Preferences
- Stack: Flask + TailwindCSS + Alpine.js
- Focus on modular design for multi-developer collaboration
- Professional UI with modern design
- Real-time stock tracking and alerts
