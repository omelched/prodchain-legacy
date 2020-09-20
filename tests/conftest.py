import pytest

from node import application


def test_adequacy():
    assert (1, 2, 3) == (1, 2, 3)


@pytest.fixture
def app():
    yield application


@pytest.fixture
def client(app):
    return app.test_client()
