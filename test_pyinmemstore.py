import pytest
import time
from pyinmemstore import PyInMemStore

@pytest.fixture
def store():
    return PyInMemStore()

def test_set_get(store):
    store.set('key', 'value')
    assert store.get('key') == 'value'

def test_get_invalid_key(store):
    assert store.get('invalid_key') is None

def test_delete_invalid_key(store):
    store.delete('invalid_key')  # Make sure no exception is raised
    assert True

def test_expire_and_ttl(store):
    store.set('key', 'value')
    store.expire('key', 10)

    initial_ttl = store.ttl('key')
    assert initial_ttl == 10

    time.sleep(5)

    ttl_after_5_seconds = store.ttl('key')
    assert ttl_after_5_seconds > 3 and ttl_after_5_seconds < 5

def test_invalid_expiry(store):
    store.set('key', 'value')
    store.expire('key', -10)

    assert store.get('key') == 'value'  # Key should still exist
    assert store.ttl('key') == -1 or store.ttl('key') == 0  # TTL should be -1 or 0 for keys with negative expiry time

def test_invalid_ttl(store):
    assert store.ttl('nonexistent_key') == -2  # TTL should be -2 for nonexistent keys
