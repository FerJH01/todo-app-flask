# ✅ To-Do App — Flask + HTMX

A lightweight, full-stack To-Do application built with **Python Flask**, **SQLAlchemy ORM**, and an **HTMX** frontend. Tasks can be added, completed, and deleted without any page reloads.

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3 + Flask |
| ORM | Flask-SQLAlchemy (SQLite) |
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

- ➕ **Add tasks** — type a task and press *Add*
- ✅ **Toggle complete** — click the circle button to mark done/undone
- 🗑️ **Delete tasks** — hover a task and click the trash icon
- ⚡ **No page reloads** — all interactions are handled by HTMX

---

## 🗄️ Database

SQLite is used by default. The database file (`todos.db`) is created automatically inside the `instance/` folder on first run. No setup required.

---

## 📄 License

MIT
