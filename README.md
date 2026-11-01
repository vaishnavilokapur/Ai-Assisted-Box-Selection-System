# PackWise – AI-Assisted Smart Box Selection System

## 1. Project Overview
PackWise is a Django-based web application developed to simplify shipping box selection for ecommerce orders. It evaluates product dimensions, quantities, and weight to recommend a suitable shipping box based on physical fit, weight capacity, and packaging cost.

## 2. Problem Statement
Selecting the correct shipping box for an order can be challenging when an order contains multiple products with different dimensions and weights. Manual selection often results in using oversized boxes that waste packaging material and increase shipping costs, or undersized boxes that risk product damage. PackWise addresses this problem by checking product placement and recommending a suitable available box.

## 3. Technologies Used
- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite
- **Development Tools:** Antigravity, Git

## 4. Key Features
- Product creation and management.
- Shipping box creation and management.
- Order creation with multiple products and quantities.
- Product rotation and dimensional fit checking.
- 3D packing validation to check boundaries and overlapping.
- Total order weight calculation.
- Box weight capacity validation.
- Automatic recommendation of the smallest suitable box.
- Box cost comparison when box volumes are equal.
- Clear results when no suitable box is available.

## 5. How the Recommendation Works
The recommendation service in `orders/services.py` follows these steps:

1. **Retrieve Order Details:** Fetch all selected products, dimensions, weights, and quantities for the order.
2. **Calculate Total Weight and Volume:** Compute the combined weight and volume of all items using Decimal arithmetic.
3. **Check Weight Capacity:** Discard candidate boxes whose maximum weight capacity is less than the total order weight.
4. **Simulate 3D Placement:** Test physical placement of items inside candidate boxes. This includes checking all six orthogonal product rotations (length, width, height permutations), verifying that items remain within box boundaries, and ensuring items do not overlap in 3D coordinate space.
5. **Select Best Box:** Recommend the smallest suitable box by volume. If two suitable boxes have identical volume, the box with the lower packaging cost is selected.

> **Note:** The current implementation uses a 3D packing heuristic based on corner-point placement and orientation testing. It is not a guaranteed mathematically optimal bin-packing solver, and no external AI or machine learning models are used.

## 6. Project Structure

```text
box_selection_system/
│
├── manage.py                   # Django management script
├── requirements.txt            # Project dependencies
├── db.sqlite3                  # SQLite database
├── README.md                   # Project documentation
│
├── config/                     # Core Project Configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py             # Settings, installed apps, static/template configs
│   ├── urls.py                 # Root URL routing
│   └── wsgi.py
│
├── products/                   # Products Application
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py                # Admin registration
│   ├── apps.py
│   ├── forms.py                # ProductForm with validation
│   ├── models.py               # Product model (dimensions & weight)
│   ├── tests.py                # Automated tests for products
│   ├── urls.py                 # Product URL patterns
│   └── views.py                # Product CRUD views
│
├── boxes/                      # Boxes Application
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py                # Admin registration
│   ├── apps.py
│   ├── forms.py                # BoxForm with validation
│   ├── models.py               # Box model (dimensions, max weight, cost)
│   ├── tests.py                # Automated tests for boxes
│   ├── urls.py                 # Box URL patterns
│   └── views.py                # Box CRUD views
│
├── orders/                     # Orders & Recommendation Application
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py                # Admin registration
│   ├── apps.py
│   ├── forms.py                # OrderCreateForm
│   ├── models.py               # Order and OrderItem models
│   ├── services.py             # Recommendation engine and 3D packing heuristic
│   ├── tests.py                # Automated tests for orders and recommendation logic
│   ├── urls.py                 # Order URL patterns and dashboard routing
│   └── views.py                # Order creation, recommendation result, and list views
│
├── static/                     # Static Assets
│   ├── css/
│   │   └── style.css           # Application styling
│   └── js/
│       └── main.js             # Dynamic product row management in order form
│
└── templates/                  # HTML Templates
    ├── base.html               # Base layout with navigation
    ├── home.html               # Dashboard homepage
    ├── products/
    │   ├── product_list.html
    │   ├── product_form.html
    │   └── product_confirm_delete.html
    ├── boxes/
    │   ├── box_list.html
    │   ├── box_form.html
    │   └── box_confirm_delete.html
    └── orders/
        ├── order_form.html
        ├── order_list.html
        └── recommendation_result.html
```

## 7. Installation and Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd box_selection_system
```

### 2. Create and Activate a Virtual Environment

**On Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply Database Migrations
```bash
python manage.py migrate
```

### 5. Start the Development Server
```bash
python manage.py runserver
```

Once running, access the application in your browser at `http://127.0.0.1:8000/`.

## 8. Running Tests
The project contains 32 automated tests across the `products`, `boxes`, and `orders` applications. These tests verify model validation, view responses, form handling, product rotations, weight limits, non-overlapping constraints, and cost tie-breakers.

Run the test suite using:
```bash
python manage.py test
```

Expected output:
```text
Found 32 test(s).
Creating test database for alias 'default'...
................................
----------------------------------------------------------------------
Ran 32 tests in 0.165s

OK
Destroying test database for alias 'default'...
```

## 9. Application Workflow
1. **Add Products:** Navigate to the Products page and add items with their dimensions (length, width, height in cm) and weight (kg).
2. **Add Shipping Boxes:** Navigate to the Boxes page and register available boxes with internal dimensions, maximum weight capacity, and unit packaging cost.
3. **Create an Order:** Go to the New Order page, enter an order number, and select products with their respective quantities.
4. **View Recommendation:** Submit the order to view the recommended shipping box, dimensions, cost, and order summary. If no box fits, the page displays the reason why.
