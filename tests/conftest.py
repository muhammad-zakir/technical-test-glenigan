import pytest

from application import create_app, database


@pytest.fixture()
def client():
    application = create_app()
    application.config["TESTING"] = True
    with application.app_context():
        with application.test_client() as client:
            yield client
        database.session.remove()
        database.engine.dispose()
