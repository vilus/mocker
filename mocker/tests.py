import pytest
from mocker.models import Mock, DupError, ANY, CYCLE, SEQUENCE


pytestmark = pytest.mark.django_db


def test_create_unique_mock():
    Mock.objects.create(host='some.any', route='/', method='GET', responses='resp 1')
    Mock.objects.create(host='www.some.any', route='/', method='GET', responses='resp 2')
    Mock.objects.create(host='www.some.any', route='/1', method='GET', responses='resp 3')
    Mock.objects.create(host='www.some.any', route='/1', method='POST', responses='resp 4')
    Mock.objects.create(host=ANY, route='/1', method='PUT', responses='resp 5')
    Mock.objects.create(host=ANY, route=ANY, method='HEAD', responses=['resp 6'])


@pytest.mark.parametrize(
    'first,second', [
        (
            {'host': 'some.any', 'route': '/', 'method': 'GET', 'responses': 'resp'},
            {'host': ANY, 'route': ANY, 'method': ANY, 'responses': 'resp'},
        ),
        (
            {'host': ANY, 'route': ANY, 'method': 'GET', 'responses': 'resp'},
            {'host': ANY, 'route': '/', 'method': ANY, 'responses': 'resp'},
        ),
        (
            {'host': ANY, 'route': ANY, 'method': ANY, 'responses': 'resp'},
            {'host': 'some.any', 'route': '/', 'method': 'GET', 'responses': 'resp'},
        ),
    ]
)
def test_create_similar_mock(first, second):
    Mock.objects.create(**first)
    Mock.objects.create(**second)


@pytest.mark.parametrize(
    'first,dup', [
        pytest.param(
            {'host': 'some.any', 'route': '/', 'method': 'GET', 'responses': 'resp 1'},
            {'host': 'some.any', 'route': '/', 'method': 'GET', 'responses': 'resp 1 for dup'},
            id='dup_by_all'
        ),
        pytest.param(
            {'host': 'some.any', 'route': '/', 'method': 'GET', 'responses': 'resp 1'},
            {'host': ANY, 'route': '/', 'method': 'GET', 'responses': 'resp 1 for dup'},
            id='dup_by_host_any_second'
        ),
        pytest.param(
            {'host': ANY, 'route': '/', 'method': 'GET', 'responses': 'resp 1'},
            {'host': 'some.any', 'route': '/', 'method': 'GET', 'responses': 'resp 1 for dup'},
            id='dup_by_host_any_first'
        ),
        pytest.param(
            {'host': 'some.any', 'route': '/', 'method': 'GET', 'responses': 'resp 1'},
            {'host': 'some.any', 'route': ANY, 'method': 'GET', 'responses': 'resp 1 for dup'},
            id='dup_by_any_route_second'
        ),
        pytest.param(
            {'host': 'some.any', 'route': ANY, 'method': 'GET', 'responses': 'resp 1'},
            {'host': 'some.any', 'route': '/', 'method': 'GET', 'responses': 'resp 1 for dup'},
            id='dup_by_any_route_first'
        ),
        pytest.param(
            {'host': 'some.any', 'route': '/', 'method': 'GET', 'responses': 'resp 1'},
            {'host': 'some.any', 'route': '/', 'method': ANY, 'responses': 'resp 1 for dup'},
            id='dup_by_any_method_second'
        ),
        pytest.param(
            {'host': 'some.any', 'route': '/', 'method': ANY, 'responses': 'resp 1'},
            {'host': 'some.any', 'route': '/', 'method': 'GET', 'responses': 'resp 1 for dup'},
            id='dup_by_any_method_first'
        ),
        pytest.param(
            {'host': 'some.any', 'route': '/', 'method': 'GET', 'responses': 'resp 1'},
            {'host': ANY, 'route': ANY, 'method': ANY, 'responses': 'resp 1 for dup'},
            id='dup_by_any_all_second'
        ),
        pytest.param(
            {'host': ANY, 'route': ANY, 'method': ANY, 'responses': 'resp 1'},
            {'host': 'some.any', 'route': '/', 'method': 'GET', 'responses': 'resp 1 for dup'},
            id='dup_by_any_all_first'
        ),
        pytest.param(
            {'route': '/', 'method': 'GET', 'responses': ['resp 1', 'resp 2'], 'response_type': SEQUENCE},
            {'route': '/', 'method': 'GET', 'responses': ['resp 1', 'resp 2'], 'response_type': CYCLE},
            id='dup_by_response_type'
        ),
        pytest.param(
            {'host': ANY, 'route': ANY, 'method': ANY, 'responses': 'resp 1', 'is_exclusive': True},
            {'host': ANY, 'route': ANY, 'method': ANY, 'responses': 'resp 1'},
            id='dup_by_exclusive_first'
        ),
        pytest.param(
            {'host': ANY, 'route': ANY, 'method': ANY, 'responses': 'resp 1'},
            {'host': ANY, 'route': ANY, 'method': ANY, 'responses': 'resp 1', 'is_exclusive': True},
            id='dup_by_exclusive_second'
        ),
    ]
)
def test_create_overlapped_mock(first, dup):
    Mock.objects.create(**first)

    with pytest.raises(DupError):
        Mock.objects.create(**dup)


def test_expired_mock():
    m = Mock.objects.create(route=ANY, method=ANY, responses='resp 1', ttl=0)
    assert m.is_expired()


def test_not_expired_mock():
    m = Mock.objects.create(route=ANY, method=ANY, responses='resp 1', ttl=60)
    assert not m.is_expired()


def test_create_dup_over_expired_mock():
    Mock.objects.create(route=ANY, method=ANY, responses='resp 1', ttl=0)
    Mock.objects.create(route=ANY, method=ANY, responses='resp 2')
