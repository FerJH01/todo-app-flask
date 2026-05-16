from flask import Flask, render_template, request
from models import db
import services

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todos.db"

db.init_app(app)


@app.get("/")
def index():
    return render_template("index.html", todos=services.get_all_todos())


@app.post("/todos")
def create_todo():
    title = request.form.get("title", "").strip()
    if not title:
        return "", 204
    services.create_todo(title)
    return render_template("partials/todo_list.html", todos=services.get_all_todos())


@app.delete("/todos/<int:todo_id>")
def delete_todo(todo_id):
    services.delete_todo(todo_id)
    return render_template("partials/todo_list.html", todos=services.get_all_todos())


@app.patch("/todos/<int:todo_id>/toggle")
def toggle_todo(todo_id):
    services.toggle_todo(todo_id)
    return render_template("partials/todo_list.html", todos=services.get_all_todos())


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
