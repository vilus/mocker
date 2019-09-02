import pytest

from mocker.models import Mock, RESPONSE_DEFAULT, ANY


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'route,method,responses,expected', [
        (
            '/42', 'GET', 42,
            {'content': b'42', 'status_code': 200, 'Content-Type': RESPONSE_DEFAULT['headers']['Content-Type']}
        ),
        (
            '/', 'POST',
            {'body': '{"status":"created"}', 'return_code': 201, 'headers': {'Content-Type': 'application/json'}},
            {'content': b'{"status":"created"}', 'status_code': 201, 'Content-Type': 'application/json'}
        ),
        (
            '/42', 'HEAD',
            {'body': 'it should not be returned cause 204', 'return_code': 204},
            {'content': b'', 'status_code': 204, 'Content-Type': RESPONSE_DEFAULT['headers']['Content-Type']},
        ),
    ]
)
def test_http_response(client, route, method, responses, expected):
    Mock.objects.create(route=route, method=method, responses=responses)

    resp = getattr(client, method.lower())(route)

    assert resp.content == expected['content']
    assert resp.status_code == expected['status_code']
    assert resp.get('Content-Type') == expected['Content-Type']


def test_http_response_404(client):
    Mock.objects.create(route='/42', method='POST', responses=42)

    resp = client.get('/42')

    assert resp.status_code == 404


@pytest.mark.parametrize(
    'method,route', [
        ('get', '/'),
        ('post', '/42'),
        ('put', '/qwerty'),
    ]
)
def test_http_response_by_any(client, method, route):
    Mock.objects.create(route=ANY, method=ANY, responses=42)

    resp = getattr(client, method)(route)

    assert resp.content == b'42'
