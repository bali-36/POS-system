# Retail Point of Sale (POS) & Inventory Management System

A production-ready, full-stack Point of Sale (POS) and inventory management application designed for modern retail environments. This system integrates a clean user interface with robust backend operations to track, log, and analyze sales and product stocks.

Developed as a course project for the **Database Systems Course**.

---

## 📌 Project Overview & Purpose

In retail operations, the accuracy of transactional data and real-world tracking of inventory are critical. Standard file systems fail to guarantee the concurrency control, data integrity, and ACID properties required for financial transactions. 

This project solves these challenges by implementing a desktop/tablet-friendly Point of Sale (POS) system. It features:
1. **Interactive POS Terminal:** Real-time search, barcode scanning simulation, cart operations, dynamic discount and tax calculations, and secure checkout.
2. **Automated Inventory Tracking & Logs:** Every transaction automatically updates stock counts and creates immutable log records tracking previous vs. new stock values.
3. **Loyalty Points System:** Tracks customer purchases and automatically awards loyalty points based on checkout subtotals.
4. **Interactive Dashboard Analytics:** Uses analytical aggregates to render sales charts, categorize revenue, track low-stock items, and list top-performing products.

---

## 🛠️ Technology Stack & Directory Structure

```
POS system/
├── app/                       # React Frontend (SPA)
│   ├── src/
│   │   ├── components/        # Layout & Shared UI Components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── pages/             # Dashboard, POS, Products, Customers, Orders, etc.
│   │   ├── services/          # API connector (Axios setup)
│   │   ├── types/             # TypeScript interfaces matching DB tables
│   │   └── App.tsx            # Routes configurations
│   ├── package.json
│   └── vite.config.ts
│
└── pos-system/
    └── backend/               # Flask REST API
        ├── database.py        # Database creation, seeding, & SQL logic
        ├── app.py             # Flask controllers & routing
        ├── pos_database.db    # SQLite binary database file
        └── static/            # Pre-compiled React frontend static assets
```

*   **Frontend:** React 19, TypeScript, Vite 7, Tailwind CSS, shadcn/ui component library, Axios, Lucide Icons, Recharts (analytics graphs).
*   **Backend:** Python 3, Flask 3.0, Flask-CORS 4.0.
*   **Database:** SQLite 3 (Standard SQL).

---

## 🚀 Setup & Installation

### Prerequisites
*   Python 3.8 or higher installed.
*   Node.js 18+ installed (if you want to modify or compile the frontend).

### 1. Backend Setup & Run
Open a terminal in the project directory:

```bash
# Navigate to the backend directory
cd pos-system/backend

# (Optional) Create a Python virtual environment
python -m venv .venv
# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install required Python packages
pip install -r requirements.txt

# Run the Flask app (this will automatically initialize and seed the DB)
python app.py
```
*The Flask server will start at `http://127.0.0.1:5000`.*

### 2. Frontend Development Setup (Optional)
If you wish to modify the React frontend:

```bash
# Navigate to the frontend app directory
cd app

# Install Node dependencies
npm install

# Run the frontend dev server
npm run dev
```
*The Vite development server runs at `http://localhost:3000`.*

If you make modifications and want to build the frontend, run:
```bash
# Compile and package files
npm run build
```
Copy all files from the compiled `app/dist` directory into the backend's static directory: `pos-system/backend/static`. The Flask server will serve the new build automatically.

---

## 🔒 Demo Accounts

The database seed function initializes the system with default accounts:

| Username | Password | Role | Description |
| :--- | :--- | :--- | :--- |
| **admin** | `admin123` | Administrator | Access to Dashboard stats, Product/Customer CRUD, Settings. |
| **cashier** | `cashier123` | Cashier | POS terminal checkout, transaction history, inventory views. |

---

## 🎓 Academic Concepts Covered
This project is a practical showcase of the following database design competencies:
*   **Logical Database Design:** Creation of normalized (3NF) relational tables mapping entities, key constraints, defaults, and data types.
*   **Referential Integrity:** Active foreign keys, auto-increment primary keys, unique constraints, and cascading rules.
*   **ACID Compliance:** Transaction blocks containing rollback error controls protecting complex inventory deductions and receipt mappings.
*   **Data Aggregation & Reporting:** Analytical joining, grouping, filtering, and datetime formatting for retail reporting metrics.
