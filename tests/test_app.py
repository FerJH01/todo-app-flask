import pytest
import sqlalchemy as sa
from sqlalchemy.pool import StaticPool
from app import app as flask_app
from models import db, Todo


@pytest.fixture
def app():
    flask_app.config["TESTING"] = True

    # Dispose any existing engine and replace it with a fresh in-memory one.
    # This bypasses init_app (which can't be re-called after first request) while
    # still ensuring proper isolation between tests.
    if flask_app in db._app_engines:
        for engine in db._app_engines[flask_app].values():
            engine.dispose()

    db._app_engines[flask_app] = {
        None: sa.create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    }

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_todo(app):
    """Creates a single active todo in the DB and returns its id."""
    todo = Todo(title="Buy milk")
    db.session.add(todo)
    db.session.commit()
    return todo.id


@pytest.fixture
def sample_done_todo(app):
    """Creates a single completed todo in the DB and returns its id."""
    todo = Todo(title="Buy eggs", done=True)
    db.session.add(todo)
    db.session.commit()
    return todo.id


# ---------------------------------------------------------------------------
# Services layer
# ---------------------------------------------------------------------------

class TestServices:
    def test_get_all_todos_empty(self, app):
        import services
        assert services.get_all_todos() == []

    def test_create_todo(self, app):
        import services
        todo = services.create_todo("Write tests")
        assert todo.id is not None
        assert todo.title == "Write tests"
        assert todo.done is False

    def test_get_all_todos_returns_newest_first(self, app):
        import services
        services.create_todo("First")
        services.create_todo("Second")
        todos = services.get_all_todos()
        assert todos[0].title == "Second"
        assert todos[1].title == "First"

    def test_delete_todo(self, app):
        import services
        todo = services.create_todo("To be deleted")
        todo_id = todo.id
        services.delete_todo(todo_id)
        assert services.get_all_todos() == []

    def test_delete_nonexistent_todo_raises_404(self, app):
        import services
        from werkzeug.exceptions import NotFound
        with pytest.raises(NotFound):
            services.delete_todo(9999)

    def test_toggle_todo_marks_done(self, app):
        import services
        todo = services.create_todo("Toggle me")
        toggled = services.toggle_todo(todo.id)
        assert toggled.done is True

    def test_toggle_todo_marks_undone(self, app):
        import services
        todo = services.create_todo("Toggle me twice")
        services.toggle_todo(todo.id)
        toggled = services.toggle_todo(todo.id)
        assert toggled.done is False

    def test_toggle_nonexistent_todo_raises_404(self, app):
        import services
        from werkzeug.exceptions import NotFound
        with pytest.raises(NotFound):
            services.toggle_todo(9999)

    def test_get_active_todos_empty(self, app):
        import services
        assert services.get_active_todos() == []

    def test_get_active_todos_returns_only_undone(self, app):
        import services
        active = services.create_todo("Active task")
        done = services.create_todo("Done task")
        services.toggle_todo(done.id)
        result = services.get_active_todos()
        assert len(result) == 1
        assert result[0].id == active.id

    def test_get_active_todos_returns_newest_first(self, app):
        import services
        services.create_todo("First active")
        services.create_todo("Second active")
        result = services.get_active_todos()
        assert result[0].title == "Second active"
        assert result[1].title == "First active"

    def test_get_completed_todos_empty(self, app):
        import services
        assert services.get_completed_todos() == []

    def test_get_completed_todos_returns_only_done(self, app):
        import services
        services.create_todo("Active task")
        done = services.create_todo("Done task")
        services.toggle_todo(done.id)
        result = services.get_completed_todos()
        assert len(result) == 1
        assert result[0].id == done.id

    def test_get_completed_todos_returns_newest_first(self, app):
        import services
        t1 = services.create_todo("First done")
        t2 = services.create_todo("Second done")
        services.toggle_todo(t1.id)
        services.toggle_todo(t2.id)
        result = services.get_completed_todos()
        assert result[0].title == "Second done"
        assert result[1].title == "First done"


# ---------------------------------------------------------------------------
# Routes / HTTP layer
# ---------------------------------------------------------------------------

class TestIndexRoute:
    def test_get_index_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_index_shows_todo_titles(self, client, sample_todo, app):
        todo = db.session.get(Todo, sample_todo)
        title = todo.title
        response = client.get("/")
        assert title.encode() in response.data

    def test_index_empty_active_shows_no_tasks_message(self, client):
        response = client.get("/")
        assert b"NO TASKS YET" in response.data

    def test_index_shows_completed_todo_title(self, client, sample_done_todo, app):
        todo = db.session.get(Todo, sample_done_todo)
        title = todo.title
        response = client.get("/")
        assert title.encode() in response.data

    def test_index_empty_completed_shows_no_completed_message(self, client):
        response = client.get("/")
        assert b"NO COMPLETED TASKS" in response.data


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
        db.session.expire_all()
        todos = db.session.execute(db.select(Todo)).scalars().all()
        assert any(t.title == "Persisted task" for t in todos)

    def test_create_todo_response_includes_completed_list_oob(self, client):
        response = client.post("/todos", data={"title": "Check OOB"})
        assert b"completed-list" in response.data


class TestDeleteTodoRoute:
    def test_delete_todo_returns_200(self, client, sample_todo):
        response = client.delete(f"/todos/{sample_todo}")
        assert response.status_code == 200

    def test_delete_todo_removes_from_db(self, client, sample_todo, app):
        client.delete(f"/todos/{sample_todo}")
        db.session.expire_all()
        assert db.session.get(Todo, sample_todo) is None

    def test_delete_todo_response_excludes_deleted_title(self, client, sample_todo, app):
        title = db.session.get(Todo, sample_todo).title
        response = client.delete(f"/todos/{sample_todo}")
        assert title.encode() not in response.data

    def test_delete_nonexistent_todo_returns_404(self, client):
        response = client.delete("/todos/9999")
        assert response.status_code == 404

    def test_delete_completed_todo_returns_200(self, client, sample_done_todo):
        response = client.delete(f"/todos/{sample_done_todo}")
        assert response.status_code == 200

    def test_delete_completed_todo_removes_from_db(self, client, sample_done_todo, app):
        client.delete(f"/todos/{sample_done_todo}")
        db.session.expire_all()
        assert db.session.get(Todo, sample_done_todo) is None


class TestToggleTodoRoute:
    def test_toggle_todo_returns_200(self, client, sample_todo):
        response = client.patch(f"/todos/{sample_todo}/toggle")
        assert response.status_code == 200

    def test_toggle_todo_changes_done_status(self, client, sample_todo, app):
        client.patch(f"/todos/{sample_todo}/toggle")
        db.session.expire_all()
        todo = db.session.get(Todo, sample_todo)
        assert todo.done is True

    def test_toggle_todo_twice_restores_status(self, client, sample_todo, app):
        client.patch(f"/todos/{sample_todo}/toggle")
        client.patch(f"/todos/{sample_todo}/toggle")
        db.session.expire_all()
        todo = db.session.get(Todo, sample_todo)
        assert todo.done is False

    def test_toggle_nonexistent_todo_returns_404(self, client):
        response = client.patch("/todos/9999/toggle")
        assert response.status_code == 404

    def test_toggle_response_includes_completed_list_oob(self, client, sample_todo):
        response = client.patch(f"/todos/{sample_todo}/toggle")
        assert b"completed-list" in response.data

    def test_toggle_active_todo_appears_in_completed_section(self, client, sample_todo, app):
        title = db.session.get(Todo, sample_todo).title
        response = client.patch(f"/todos/{sample_todo}/toggle")
        # The OOB completed-list should contain the title after toggling
        assert title.encode() in response.data
