from flask import Flask, render_template, request
from models import db
import services

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todos.db"

db.init_app(app)


def _list_context():
    return {
        "todos": services.get_active_todos(),
        "completed": services.get_completed_todos(),
    }


@app.get("/")
def index():
    return render_template("index.html", **_list_context())


@app.post("/todos")
def create_todo():
    title = request.form.get("title", "").strip()
    if not title:
        return "", 204
    services.create_todo(title)
    return render_template("partials/todo_list.html", **_list_context())


@app.delete("/todos/<int:todo_id>")
def delete_todo(todo_id):
    services.delete_todo(todo_id)
    return render_template("partials/todo_list.html", **_list_context())


@app.patch("/todos/<int:todo_id>/toggle")
def toggle_todo(todo_id):
    services.toggle_todo(todo_id)
    return render_template("partials/todo_list.html", **_list_context())


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
