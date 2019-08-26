import pytest
from mocker.models import DupError, Mock, ANY, TTL


pytestmark = pytest.mark.django_db


def create_mocks(ttl=TTL):
    Mock.objects.create(host='some.any', route='/', method='GET', responses='resp 1', ttl=ttl)
    Mock.objects.create(host='www.some.any', route='/', method='GET', responses='resp 2', ttl=ttl)
    Mock.objects.create(host='www.some.any', route='/1', method='GET', responses='resp 3', ttl=ttl)
    Mock.objects.create(host='www.some.any', route='/1', method='POST', responses='resp 4', ttl=ttl)
    Mock.objects.create(host=ANY, route='/qwerty', method='GET', responses='resp 5', ttl=ttl)
    Mock.objects.create(host=ANY, route=ANY, method='HEAD', responses='resp 6', ttl=ttl)


def test_match_mock():
    create_mocks()

    assert Mock.objects.get_by(host='some.any', route='/', method='GET').responses == 'resp 1'
    assert Mock.objects.get_by(host='www.some.any', route='/1', method='GET').responses == 'resp 3'
    assert Mock.objects.get_by(host='hi.ho', route='/qwerty', method='GET').responses == 'resp 5'
    assert Mock.objects.get_by(host='co.ol', route='/42', method='HEAD').responses == 'resp 6'


def test_not_match_mock():
    create_mocks()

    assert Mock.objects.get_by(host='some.any', route='/', method='PUT') is None
    assert Mock.objects.get_by(host='some.any', route='/2', method='GET') is None
    assert Mock.objects.get_by(host='co.ol', route='/qwerty', method='POST') is None
    assert Mock.objects.get_by(host='co.ol', route='/42', method='GET') is None


def test_not_match_expired_mock():
    create_mocks(ttl=0)

    assert Mock.objects.get_by(host='some.any', route='/', method='GET') is None
    assert Mock.objects.get_by(host='www.some.any', route='/1', method='GET') is None
    assert Mock.objects.get_by(host='hi.ho', route='/qwerty', method='GET') is None
    assert Mock.objects.get_by(host='co.ol', route='/42', method='HEAD') is None


def test_match_by_all_any():
    Mock.objects.create(host=ANY, route=ANY, method=ANY, responses='all any')
    assert Mock.objects.get_by(host='co.ol', route='/42', method='PATCH').responses == 'all any'
    assert Mock.objects.get_by(host='lh', route='/', method='GET').responses == 'all any'


def test_match_similar_mock():
    Mock.objects.create(host='qwer.ty', route='/qwerty', method='GET', responses='resp 42')
    Mock.objects.create(host='qwer.ty', route='/42', method=ANY, responses='resp 42')
    Mock.objects.create(host='qwer.ty', route=ANY, method=ANY, responses='resp 42')

    assert Mock.objects.get_by(host='qwer.ty', route='/qwerty', method='GET').responses == 'resp 42'
    assert Mock.objects.get_by(host='qwer.ty', route='/42', method='PUT').responses == 'resp 42'
    assert Mock.objects.get_by(host='qwer.ty', route='/42', method='CONNECT').responses == 'resp 42'


def test_match_similar_with_different_responses_mock():
    Mock.objects.create(host='qwer.ty', route='/qwerty', method='GET', responses='resp 42')
    Mock.objects.create(host='qwer.ty', route='/42', method=ANY, responses='resp 42')
    Mock.objects.create(host='qwer.ty', route=ANY, method=ANY, responses='resp 42')

    Mock(name='wrong_mock_1', ttl=TTL, host='qwer.ty', route='/qwerty', method='GET', responses='wrong 1').save()
    with pytest.raises(DupError) as exc_info:
        Mock.objects.get_by(host='qwer.ty', route='/qwerty', method='GET')
    assert 'wrong_mock_1' in str(exc_info.value)  # TODO: tmp hardcode

    Mock(name='wrong_mock_2', ttl=TTL, host='qwer.ty', route=ANY, method='PUT', responses='wrong 2').save()
    with pytest.raises(DupError) as exc_info:
        Mock.objects.get_by(host='qwer.ty', route='/hi', method='PUT')
    assert 'wrong_mock_2' in str(exc_info.value)  # TODO: tmp hardcode
