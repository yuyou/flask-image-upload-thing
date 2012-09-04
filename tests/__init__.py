from flexmock import flexmock
from flask.ext.storage import MockStorage
from flask_uploads import init

created_objects = []
added_objects = []
deleted_objects = []
committed_objects = []


class MockModel(object):
    def __init__(self, **kw):
        created_objects.append(self)
        for key, val in kw.iteritems():
            setattr(self, key, val)

db_mock = flexmock(
    Column=lambda *a, **kw: ('column', a, kw),
    Integer=('integer', [], {}),
    Unicode=lambda *a, **kw: ('unicode', a, kw),
    Model=MockModel,
    session=flexmock(
        add=added_objects.append,
        commit=lambda: committed_objects.extend(
            added_objects + deleted_objects
        ),
        delete=deleted_objects.append,
    ),
)


class TestCase(object):
    def setup_method(self, method, resizer=None):
        init(db_mock, MockStorage, resizer)
        self.db = db_mock
        self.Storage = MockStorage
        self.resizer = resizer
