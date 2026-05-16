from models import Todo, db


def get_all_todos() -> list[Todo]:
    return db.session.execute(db.select(Todo).order_by(Todo.id.desc())).scalars().all()


def get_active_todos() -> list[Todo]:
    return db.session.execute(
        db.select(Todo).where(Todo.done == False).order_by(Todo.id.desc())
    ).scalars().all()


def get_completed_todos() -> list[Todo]:
    return db.session.execute(
        db.select(Todo).where(Todo.done == True).order_by(Todo.id.desc())
    ).scalars().all()


def create_todo(title: str) -> Todo:
    todo = Todo(title=title)
    db.session.add(todo)
    db.session.commit()
    return todo


def delete_todo(todo_id: int) -> None:
    todo = db.get_or_404(Todo, todo_id)
    db.session.delete(todo)
    db.session.commit()


def toggle_todo(todo_id: int) -> Todo:
    todo = db.get_or_404(Todo, todo_id)
    todo.done = not todo.done
    db.session.commit()
    return todo
