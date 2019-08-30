import pytest
from mocker.models import Mock, SINGLE, SEQUENCE, CYCLE


pytestmark = pytest.mark.django_db


def test_single_string_response():
    mock = Mock.objects.create(host='some.any', route='/', method='GET', responses='resp 1', response_type=SINGLE)
    expected_resp = {'body': 'resp 1', 'return_code': 200, 'headers': {'Content-Type': 'text/html; charset=utf-8'}}

    assert mock.get_response() == expected_resp
    assert mock.get_response() == expected_resp


def test_single_dict_response():
    mock = Mock.objects.create(host='some.any', route='/', method='POST', response_type=SINGLE,
                               responses={'body': 42, 'return_code': 204})
    expected_resp = {'body': 42, 'return_code': 204, 'headers': {'Content-Type': 'text/html; charset=utf-8'}}

    assert mock.get_response() == expected_resp
    assert mock.get_response() == expected_resp


@pytest.mark.parametrize(
    'response_type,responses,expected_resp', [
        (
            SEQUENCE, [{'body': 42, 'return_code': 204}],
            {'body': 42, 'return_code': 204, 'headers': {'Content-Type': 'text/html; charset=utf-8'}}
        ),
        (
            CYCLE, [{'body': 42, 'return_code': 204}],
            {'body': 42, 'return_code': 204, 'headers': {'Content-Type': 'text/html; charset=utf-8'}}
        ),
        (
            SEQUENCE, [42],
            {'body': 42, 'return_code': 200, 'headers': {'Content-Type': 'text/html; charset=utf-8'}}
        ),
        (
            CYCLE, [42],
            {'body': 42, 'return_code': 200, 'headers': {'Content-Type': 'text/html; charset=utf-8'}}
        ),
    ]
)
def test_array_with_single_response(response_type, responses, expected_resp):
    mock = Mock.objects.create(host='some.any', route='/', method='POST',
                               response_type=response_type, responses=responses)
    assert mock.get_response() == expected_resp
    assert mock.get_response() == expected_resp


def test_sequence_response():
    mock = Mock.objects.create(host='some.any', route='/', method='POST', response_type=SEQUENCE,
                               responses=[42, 'hello', {'return_code': 204, 'body': 'created'}])

    expected_resp_1 = {'body': 42, 'return_code': 200, 'headers': {'Content-Type': 'text/html; charset=utf-8'}}
    expected_resp_2 = {'body': 'hello', 'return_code': 200, 'headers': {'Content-Type': 'text/html; charset=utf-8'}}
    expected_resp_3 = {'body': 'created', 'return_code': 204, 'headers': {'Content-Type': 'text/html; charset=utf-8'}}

    assert mock.get_response() == expected_resp_1
    assert mock.get_response() == expected_resp_2
    assert mock.get_response() == expected_resp_3
    assert mock.get_response() == expected_resp_3


def test_cycle_response():
    mock = Mock.objects.create(host='some.any', route='/', method='POST', response_type=CYCLE,
                               responses=[42, 'hello', {'return_code': 204, 'body': 'created'}])

    expected_resp_1 = {'body': 42, 'return_code': 200, 'headers': {'Content-Type': 'text/html; charset=utf-8'}}
    expected_resp_2 = {'body': 'hello', 'return_code': 200, 'headers': {'Content-Type': 'text/html; charset=utf-8'}}
    expected_resp_3 = {'body': 'created', 'return_code': 204, 'headers': {'Content-Type': 'text/html; charset=utf-8'}}

    assert mock.get_response() == expected_resp_1
    assert mock.get_response() == expected_resp_2
    assert mock.get_response() == expected_resp_3

    assert mock.get_response() == expected_resp_1
    assert mock.get_response() == expected_resp_2
    assert mock.get_response() == expected_resp_3

    assert mock.get_response() == expected_resp_1
    assert mock.get_response() == expected_resp_2
    assert mock.get_response() == expected_resp_3
