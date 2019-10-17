import pytest
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from mocker.models import Mock, CYCLE, SINGLE


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

    mock = Mock.objects.get(name='from_test_42')
    assert mock.route == '/42'
    assert mock.method == 'GET'
    assert mock.response_type == CYCLE
    assert mock.responses == [42, 'Hi', {'body': 'secret', 'return_code': 201}]


def test_api_create_mock_negative(api_client):
    resp = api_client.post(
        reverse('mock-list'),
        {
            'name': 'from_test_42', 'response_type': CYCLE,
            'responses': [42, 'Hi', {'body': 'secret', 'return_code': 201}]
        },
        format='json'
    )
    assert resp.status_code == 400


def test_api_create_overlapped_mock(api_client):
    Mock.objects.create(route='/', method='GET', responses='resp 1')
    resp = api_client.post(reverse('mock-list'), {'route': '/', 'method': 'GET', 'responses': 42}, format='json')
    assert resp.status_code == 409


@pytest.mark.parametrize(
    'ttl,expired', [
        (120, False),
        (0, True),
    ]
)
def test_api_delete_mock(api_client, ttl, expired):
    mock = Mock.objects.create(name='for_delete', route='/', method='GET', responses='resp 1', ttl=ttl)
    resp = api_client.delete(reverse('mock-detail', kwargs={'pk': mock.pk}))
    assert resp.status_code == 200
    assert Mock.objects.filter(name='for_delete').first() is None
    assert resp.json()['is_expired'] is expired


def test_api_create_mocks(api_client):
    resp = api_client.post(
        reverse('mock-list'),
        [
            {
                'name': 'from_test_42_1', 'route': '/42_1', 'method': 'GET', 'response_type': CYCLE,
                'responses': [42, 'Hi', {'body': 'secret', 'return_code': 201}]
            },
            {
                'name': 'from_test_42_2', 'route': '/42_2', 'method': 'GET', 'responses': 42,
            },
        ],
        format='json'
    )
    assert resp.status_code == 201

    mock = Mock.objects.get(name='from_test_42_1')
    assert mock.route == '/42_1'
    assert mock.method == 'GET'
    assert mock.response_type == CYCLE
    assert mock.responses == [42, 'Hi', {'body': 'secret', 'return_code': 201}]

    mock = Mock.objects.get(name='from_test_42_2')
    assert mock.route == '/42_2'
    assert mock.method == 'GET'
    assert mock.response_type == SINGLE
    assert mock.responses == 42


def test_api_rollbacks_create_overlapped_mocks(api_client):
    Mock.objects.create(name='for_rollback', route='/', method='GET', responses='first')
    resp = api_client.post(
        reverse('mock-list'),
        [
            {
                'name': 'from_test_42_1', 'route': '/42_1', 'method': 'GET', 'response_type': CYCLE,
                'responses': [42, 'Hi', {'body': 'secret', 'return_code': 201}]
            },
            {
                'name': 'from_test_42_2', 'route': '/', 'method': 'GET', 'responses': 42,  # dup by route
            },
        ],
        format='json'
    )
    assert resp.status_code == 409

    assert Mock.objects.filter(name='from_test_42_1').first() is None
    assert Mock.objects.filter(name='from_test_42_2').first() is None


def test_api_create_mocks_negative(api_client):
    resp = api_client.post(
        reverse('mock-list'),
        [
            {
                'name': 'from_test_42_1', 'route': '/42_1', 'method': 'GET', 'response_type': CYCLE,
                'responses': [42, 'Hi', {'body': 'secret', 'return_code': 201}]
            },
            {
                'name': 'from_test_42_2', 'method': 'GET', 'responses': 42,  # missed 'route' -> bad request
            },
        ],
        format='json'
    )
    assert resp.status_code == 400

    assert Mock.objects.filter(name='from_test_42_1').first() is None
    assert Mock.objects.filter(name='from_test_42_2').first() is None
