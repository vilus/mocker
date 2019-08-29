import pytest
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from mocker.models import Mock, CYCLE


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


def test_api_create_mock(api_client):
    resp = api_client.post(
        reverse('mock-list'),
        {
            'name': 'from_test_42', 'route': '/42', 'method': 'GET', 'response_type': CYCLE,
            'responses': [42, 'Hi', {'body': 'secret', 'return_code': 201}]
        },
        format='json'
    )
    assert resp.status_code == 201

    # TODO: refactor hardcode
    mock = Mock.objects.get(name='from_test_42')
    assert mock.route == '/42'
    assert mock.method == 'GET'
    assert mock.response_type == CYCLE
    assert mock.responses == [42, 'Hi', {'body': 'secret', 'return_code': 201}]


# TODO: add more tests, MORE!!!!1
