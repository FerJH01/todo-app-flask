import pytest
from app import app as flask_app
from models import db, Todo


@pytest.fixture
def app():
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_todo(app):
    """Creates a single todo in the DB and returns its id."""
    with app.app_context():
        todo = Todo(title="Buy milk")
        db.session.add(todo)
        db.session.commit()
        return todo.id


# ---------------------------------------------------------------------------
# Services layer
# ---------------------------------------------------------------------------

class TestServices:
    def test_get_all_todos_empty(self, app):
        import services
        with app.app_context():
            assert services.get_all_todos() == []

    def test_create_todo(self, app):
        import services
        with app.app_context():
            todo = services.create_todo("Write tests")
            assert todo.id is not None
            assert todo.title == "Write tests"
            assert todo.done is False

    def test_get_all_todos_returns_newest_first(self, app):
        import services
        with app.app_context():
            services.create_todo("First")
            services.create_todo("Second")
            todos = services.get_all_todos()
            assert todos[0].title == "Second"
            assert todos[1].title == "First"

    def test_delete_todo(self, app):
        import services
        with app.app_context():
            todo = services.create_todo("To be deleted")
            todo_id = todo.id
            services.delete_todo(todo_id)
            assert services.get_all_todos() == []

    def test_delete_nonexistent_todo_raises_404(self, app):
        import services
        from werkzeug.exceptions import NotFound
        with app.app_context():
            with pytest.raises(NotFound):
                services.delete_todo(9999)

    def test_toggle_todo_marks_done(self, app):
        import services
        with app.app_context():
            todo = services.create_todo("Toggle me")
            toggled = services.toggle_todo(todo.id)
            assert toggled.done is True

    def test_toggle_todo_marks_undone(self, app):
        import services
        with app.app_context():
            todo = services.create_todo("Toggle me twice")
            services.toggle_todo(todo.id)
            toggled = services.toggle_todo(todo.id)
            assert toggled.done is False

    def test_toggle_nonexistent_todo_raises_404(self, app):
        import services
        from werkzeug.exceptions import NotFound
        with app.app_context():
            with pytest.raises(NotFound):
                services.toggle_todo(9999)


# ---------------------------------------------------------------------------
# Routes / HTTP layer
# ---------------------------------------------------------------------------

class TestIndexRoute:
    def test_get_index_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_index_shows_todo_titles(self, client, sample_todo, app):
        with app.app_context():
            todo = db.session.get(Todo, sample_todo)
            title = todo.title
        response = client.get("/")
        assert title.encode() in response.data


class TestCreateTodoRoute:
    def test_create_todo_returns_todo_list_html(self, client):
        response = client.post("/todos", data={"title": "New task"})
        assert response.status_code == 200
        assert b"New task" in response.data

    def test_create_todo_empty_title_returns_204(self, client):
        response = client.post("/todos", data={"title": "   "})
        assert response.status_code == 204
        assert response.data == b""

    def test_create_todo_missing_title_returns_204(self, client):
        response = client.post("/todos", data={})
        assert response.status_code == 204

    def test_create_todo_persists_in_db(self, client, app):
        client.post("/todos", data={"title": "Persisted task"})
        with app.app_context():
            todos = db.session.execute(db.select(Todo)).scalars().all()
            assert any(t.title == "Persisted task" for t in todos)


class TestDeleteTodoRoute:
    def test_delete_todo_returns_200(self, client, sample_todo):
        response = client.delete(f"/todos/{sample_todo}")
        assert response.status_code == 200

    def test_delete_todo_removes_from_db(self, client, sample_todo, app):
        client.delete(f"/todos/{sample_todo}")
        with app.app_context():
            assert db.session.get(Todo, sample_todo) is None

    def test_delete_todo_response_excludes_deleted_title(self, client, sample_todo, app):
        with app.app_context():
            title = db.session.get(Todo, sample_todo).title
        response = client.delete(f"/todos/{sample_todo}")
        assert title.encode() not in response.data

    def test_delete_nonexistent_todo_returns_404(self, client):
        response = client.delete("/todos/9999")
        assert response.status_code == 404


class TestToggleTodoRoute:
    def test_toggle_todo_returns_200(self, client, sample_todo):
        response = client.patch(f"/todos/{sample_todo}/toggle")
        assert response.status_code == 200

    def test_toggle_todo_changes_done_status(self, client, sample_todo, app):
        client.patch(f"/todos/{sample_todo}/toggle")
        with app.app_context():
            todo = db.session.get(Todo, sample_todo)
            assert todo.done is True

    def test_toggle_todo_twice_restores_status(self, client, sample_todo, app):
        client.patch(f"/todos/{sample_todo}/toggle")
        client.patch(f"/todos/{sample_todo}/toggle")
        with app.app_context():
            todo = db.session.get(Todo, sample_todo)
            assert todo.done is False

    def test_toggle_nonexistent_todo_returns_404(self, client):
        response = client.patch("/todos/9999/toggle")
        assert response.status_code == 404
