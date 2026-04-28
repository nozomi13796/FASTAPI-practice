import os
import pytest
from model.user import User
from errors import Missing, Duplicate

os.environ['CRYPTID_SQLITE_DB'] = ':memory:'
from data import user

@pytest.fixture
def sample() -> User:
    return User(name='nonnon', hash='abc')

def test_create(sample):
    resp = user.create(sample)
    assert resp == sample

def test_create_deplicate(sample):
    with pytest.raises(Duplicate):
        _ = user.create(sample)

def test_get_one(sample):
    resp = user.get_one(sample.name)
    assert resp == sample

def test_get_one_missing():
    with pytest.raises(Missing):
        _ = user.get_one('boxturtle')

def test_modify(sample):
    sample.hash = 'newhash'
    resp = user.modify(sample.name, sample)
    assert resp == sample

def test_modify_missing():
    thing: User = User(name='ahhaha', hash='hahahash')
    with pytest.raises(Missing):
        _ = user.modify(thing.name, thing)

def test_delete(sample):
    resp = user.delete(sample.name)
    assert resp is None

def test_delete_missing(sample):
    with pytest.raises(Missing):
        _ = user.delete(sample.name)
