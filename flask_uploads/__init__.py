import os
from StringIO import StringIO
import sqlalchemy
import flask.ext.sqlalchemy

_db = None
_resizer = None
_Storage = None


class Upload(flask.ext.sqlalchemy.Model):
    """
    The database model class based on some preset fields and the
    ``resizer`` argument passed to :func:`init`. Each of the resizer's sizes
    add a :attr:`{size}_name` and a :attr:`{size}_url` field to the model.

    .. attribute:: id

        Auto-incrementing integer field. Primary key.

    .. attribute:: name

        Unicode string field of length 255. The name of the original upload.

    .. attribute:: url

        Unicode string field of length 255. Absolute URL to the original
        upload.

    .. attribute:: {size}_name

        Unicode string field of length 255. The name of the image resized to
        {size}. None if the upload was not an image file.

    .. attribute:: {size}_url

        Unicode string field of length 255. Absolute URL to the image resized
        to {size}. None if the upload was not an image file.
    """
    __tablename__ = 'upload'

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        autoincrement=True,
        primary_key=True
    )
    name = sqlalchemy.Column(sqlalchemy.Unicode(255), nullable=False)
    url = sqlalchemy.Column(sqlalchemy.Unicode(255), nullable=False)


def save_file(name, data):
    """Saves data as a new upload with name ``name``. Used by :func:`save`.

    :param name:
        The name to use when saving the upload.
    :param data:
        The original upload data.
    """
    storage = _Storage()
    name = storage.save(name, data)
    url = storage.url(name)
    _db.session.add(Upload(name=name, url=url))
    _db.session.commit()


def save_images(name, data, images):
    """Saves data as a new upload with the given images. Used by :func:`save`.

    :param name:
        The name to use when saving the upload.
    :param data:
        The original upload data.
    :param images:
        A dictionary containing the names and datas of the images, as returned
        by ``Resizer.resize_image``.
    """
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
    """Saves data to a new file. If data is an image and resizer was provided
    for :func:`init`, the image will be resized to all of the resizer's sizes.

    :param data:
        The data to save. Should have a :meth:`read` method and, if ``name``
        was not provided, a :attr:`filename` attribute.
    :param name:
        The name to use when saving the data. Defaults to ``data.filename``.
    """
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
        print 'save %s' % name
        return save_file(name, data)


def delete(upload):
    """Deletes the uploaded file.

    :param upload:
        An instance of :class:`Upload`.
    """
    storage = _Storage()
    storage.delete(upload.name)
    if _resizer:
        for size in _resizer.sizes.iterkeys():
            if getattr(upload, size + '_name'):
                storage.delete(getattr(upload, size + '_name'))
    _db.session.delete(upload)
    _db.session.commit()


def init(db, Storage, resizer=None):
    """Initializes the extension.

    :param db:
        The Flask-SQLAlchemy object to use.
    :type db:
        a Flask-SQLAlchemy object
    :param Storage:
        The Flask-Storage class to use.
    :type Storage:
        a Flask-Storage storage class
    :param resizer:
        The Resizer object to use for resizing images. If not present, images
        will not be resized.
    :type resizer:
        a Resizer object
    """
    global _db, _resizer, _Storage
    _db = db
    _resizer = resizer
    _Storage = Storage

    if resizer:
        for size in resizer.sizes.iterkeys():
            setattr(Upload, size + '_name', db.Column(db.Unicode(255)))
            setattr(Upload, size + '_url', db.Column(db.Unicode(255)))
