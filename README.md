# ✅ To-Do App — Flask + HTMX

A lightweight, full-stack To-Do application built with **Python Flask**, **SQLAlchemy ORM**, and an **HTMX** frontend. Tasks can be added, toggled, and deleted without any page reloads. Active and completed tasks are displayed in separate sections, updated dynamically via HTMX out-of-band swaps.

---

## 🛠 Tech Stack

| Layer    | Technology                |
| -------- | ------------------------- |
| Backend  | Python 3 + Flask          |
| ORM      | Flask-SQLAlchemy (SQLite) |
| Frontend | HTMX + Tailwind CSS (CDN) |

---

## 📁 Project Structure

```
├── app.py                        # Application layer: Flask routes
├── services.py                   # Business logic: CRUD operations
├── models.py                     # Data layer: SQLAlchemy model
├── requirements.txt
├── templates/
│   ├── index.html                # Main page
│   └── partials/
│       └── todo_list.html        # HTMX partial for todo items
├── tests/
│   └── test_app.py               # Pytest test suite (services + routes)
└── .venv/                        # Virtual environment (not committed)
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/FerJH01/todo-app-flask.git
cd todo-app-flask
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
```

Open your browser at **http://localhost:5000**

---

## ⚙️ Features

- ➕ **Add tasks** — type a task and press _Add_
- ✅ **Toggle complete** — click the circle button to mark done/undone
- 🗑️ **Delete tasks** — hover a task and click the trash icon
- 📂 **Two sections** — active and completed tasks displayed separately
- ⚡ **No page reloads** — all interactions handled by HTMX (including OOB swaps)

---

## 🧪 Testing

The project includes a pytest suite covering both the service layer and all HTTP routes.

```bash
pip install pytest
pytest tests/
```

Tests use an in-memory SQLite database for full isolation.

---

## 🗄️ Database

SQLite is used by default. The database file (`todos.db`) is created automatically inside the `instance/` folder on first run. No setup required.

---

## 📄 License

MIT
