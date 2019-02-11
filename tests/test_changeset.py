from pyjen.changeset import Changeset
import pytest

        
def test_get_scm_type():
    data = dict()
    data['kind'] = "svn"
    data['items'] = []
    cs = Changeset(data)

    assert cs.scm_type == "svn"


def test_has_no_changes():
    data = dict()
    data['kind'] = "svn"
    data['items'] = []
    cs = Changeset(data)

    assert cs.has_changes == False


def test_has_changes():
    data = dict()
    data['kind'] = "svn"
    data['items'] = {"message": "Hello World"}
    cs = Changeset(data)

    assert cs.has_changes == True


def test_affected_items():
    expected_message = "Here is the commit log"

    data = dict()
    data['kind'] = "svn"
    data['items'] = [{"msg": expected_message}]
    cs = Changeset(data)
    actual_items = cs.affected_items

    assert len(actual_items) == 1
    assert actual_items[0].message == expected_message


def test_actual_items_empty():
    data = dict()
    data['kind'] = "svn"
    data['items'] = []
    cs = Changeset(data)
    actual_items = cs.affected_items

    assert actual_items is not None
    assert len(actual_items) == 0


def test_authors():
    expected_url = "http://localhost:8080/user/jdoe/"

    data = dict()
    data['kind'] = "svn"
    data['items'] = [{"author": {"absoluteUrl": expected_url, "fullName": "John Doe"}}]
    cs = Changeset(data)
    actual_items = cs.affected_items

    assert len(actual_items) == 1
    assert actual_items[0].author.url == expected_url
    
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
