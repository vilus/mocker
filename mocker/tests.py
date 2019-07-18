import pytest

pytestmark = pytest.mark.django_db


def test_create_first_mock():
    assert False


class TestMockModel:
    def test_create_first_mock(self):
        assert False
