import pytest
import json
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from example import app, InMemoryManager


@pytest.mark.parametrize(
    'id, in_memory_data, status_code, expected_response',
    (
        (1, {}, 200, {},),
        (1, {1:  {'number': 1,  'world': 'helo'}}, 200, {'number': 1,  'world': 'helo'},),
        (2, {1:  {'number': 1,  'world': 'helo'}}, 200, {},),
    )
)
def test_retrieve(mocker, id, in_memory_data, status_code, expected_response):
    client = Client(app, BaseResponse)
    mocker.patch.object(app.endpoints['test'].manager, '_data', in_memory_data)
    response = client.get(f'/test/retrieve/{id}')
    assert response.status_code == status_code
    assert json.loads(response.data) == expected_response


def test_create():
    client = Client(app, BaseResponse)
    assert app.endpoints['test'].manager._data == {}
    response = client.post('/test/create', json={'id': 1, 'word': 'helo', 'number': 2})
    assert response.status_code == 201
    assert json.loads(response.data) == {'id': 1, 'key': 1, 'number': 2, 'word': 'helo'}


@pytest.mark.parametrize(
    'id, in_memory_data, expected_response',
    (
        (1, {1:  {'number': 1,  'world': 'helo'}}, {}),
        (2, {1:  {'number': 1,  'world': 'helo'}}, {1:  {'number': 1,  'world': 'helo'}}),
    )
)
def test_delete(mocker, id, in_memory_data, expected_response):
    client = Client(app, BaseResponse)
    mocker.patch.object(app.endpoints['test'].manager, '_data', in_memory_data)
    response = client.delete(f'/test/delete/{id}')
    assert response.status_code == 200
    assert app.endpoints['test'].manager._data == expected_response


