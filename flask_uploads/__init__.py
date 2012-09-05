import os
from StringIO import StringIO
from .helpers import Proxy


Upload = Proxy(None)
_db = None
_resizer = None
_Storage = None


def save_file(name, data):
    storage = _Storage()
    name = storage.save(name, data)
    url = storage.url(name)
    _db.session.add(Upload(name=name, url=url))
    _db.session.commit()


def save_images(name, data, images):
    storage = _Storage()
    name = storage.save(name, data).decode('utf-8')
    url = storage.url(name).decode('utf-8')
    upload = Upload(name=name, url=url)

    for size, image in images.iteritems():
        imageio = StringIO()
        image.save(imageio, format=image.ext)
        n = storage.save(
            '%s_%s.%s' % (
                os.path.splitext(name)[0],
                size,
                image.ext
            ),
            imageio
        ).decode('utf-8')
        url = storage.url(n).decode('utf-8')
        setattr(upload, u'%s_name' % size, n)
        setattr(upload, u'%s_url' % size, url)

    _db.session.add(upload)
    _db.session.commit()


def save(data, name=None):
    if name is None:
        name = data.filename
    data = data.read()
    datafile = StringIO(data)
    if _resizer:
        try:
            images = _resizer.resize_image(datafile)
        except IOError:
            # Not an image.
            return save_file(name, data)
        save_images(name, data, images)
    else:
        return save_file(name, data)


def delete(upload):
    storage = _Storage()
    storage.delete(upload.name)
    if _resizer:
        for size in _resizer.sizes.iterkeys():
            if getattr(upload, size + '_name'):
                storage.delete(getattr(upload, size + '_name'))
    _db.session.delete(upload)
    _db.session.commit()


def init(db, Storage, resizer=None):
    if 'upload' in db.metadata.tables:
        return  # Already initialized.

    global _db, _resizer, _Storage
    _db = db
    _resizer = resizer
    _Storage = Storage

    class _Upload(db.Model):
        __tablename__ = 'upload'

        id = db.Column(db.Integer, autoincrement=True, primary_key=True)
        name = db.Column(db.Unicode(255), nullable=False)
        url = db.Column(db.Unicode(255), nullable=False)

    Upload.set_obj(_Upload)

    if resizer:
        for size in resizer.sizes.iterkeys():
            setattr(Upload, size + '_name', db.Column(db.Unicode(255)))
            setattr(Upload, size + '_url', db.Column(db.Unicode(255)))
