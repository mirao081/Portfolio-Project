# Store Management System

A modular Django-based store management system with three main apps:
- **users**: Handles user registration, login, approval, and roles (manager, supervisor, salesperson).
- **inventory**: Manages products, stock, and inventory operations.
- **pos**: Handles sales, sales dashboards, supervisor dashboards, and sales reporting.

---

## Features

- **User Registration & Approval:**  
  Users register and must be approved by a manager before logging in.
- **Role-Based Access:**  
  - **Manager:** Full permissions, can approve users, manage staff.
  - **Supervisor:** Can view sales performance, manage products, and see stock.
  - **Salesperson:** Can log sales, scan barcodes, and process returns.
- **Inventory Management:**  
  Add, list, and manage products and stock.
- **Sales Management:**  
  Create sales, add multiple products per sale, view sales dashboards.
- **Supervisor Dashboard:**  
  View all salespersons’ performance, total sales, returns, and manage products.
- **Modern UI:**  
  Clean, responsive templates for all major workflows.

---

## Setup Instructions

### 1. **Clone the Repository**
```bash
git clone <your-repo-url>
cd <your-project-directory>
```

### 2. **Create and Activate a Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Apply Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. **Create a Superuser**
```bash
python manage.py createsuperuser
```

### 6. **Run the Development Server**
```bash
python manage.py runserver
```

### 7. **Access the Application**
- Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) for the user portal.
- Visit [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) for the Django admin panel.

---

## App Structure

```
store_manager/
    users/         # User registration, login, approval, roles
    inventory/     # Product and stock management
    pos/           # Sales, dashboards, reporting
    templates/
    static/
    manage.py
    requirements.txt
```

---

## Key URLs

- `/register/` — User registration
- `/login/` — User login
- `/pos/sales/` — Sales dashboard (salesperson)
- `/pos/supervisor-dashboard/` — Supervisor dashboard
- `/inventory/add-product/` — Add product (supervisor/manager)
- `/inventory/products/` — Product list

---

## Notes

- **User Approval:**  
  New users must be approved by a manager (via admin or dashboard) before they can log in.
- **Role-Based Redirects:**  
  After login, users are redirected to dashboards based on their role.
- **Barcode Sales:**  
  Salespersons can enter or scan product barcodes to add products to a sale.

---

## License

MIT License

---

