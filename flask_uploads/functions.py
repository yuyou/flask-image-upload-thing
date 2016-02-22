import os
from functools import wraps
from StringIO import StringIO
import extensions as ext
from .models import Upload


def require_storage(f):
    @wraps(f)
    def wrapper(*args, **kw):
        if not ext.storage:
            ext.storage = ext.Storage()
        return f(*args, **kw)
    return wrapper


@require_storage
def save_file(name, data, folder_name=None):
    storage = ext.storage
    if folder_name is not None:
        _old_folder = ext.storage.folder_name
        if _old_folder != folder_name:
            #TODO: hacky patch to create a new Storage
            storage = ext.Storage(folder_name=folder_name)
    f = storage.save(name, data)
    name = f.name.decode('utf-8')
    url = f.url.decode('utf-8')
    up = Upload(name=name, url=url)
    ext.db.session.add(up)
    ext.db.session.commit()
    return up

@require_storage
def save_images(name, data, images, folder_name=None):
    storage = ext.storage
    if folder_name is not None:
        _old_folder = ext.storage.folder_name
        if _old_folder != folder_name:
            #TODO: hacky patch to create a new Storage
            storage = ext.Storage(folder_name=folder_name)

    f = storage.save(name, data)
    name = f.name.decode('utf-8')
    url = f.url.decode('utf-8')
    upload = Upload(name=name, url=url)

    for size, image in images.iteritems():
        imageio = StringIO()
        image.save(imageio, format=image.ext)
        f = storage.save(
            '%s_%s.%s' % (
                os.path.splitext(name)[0],
                size,
                image.ext
            ),
            imageio
        )
        setattr(upload, u'%s_name' % size, f.name.decode('utf-8'))
        setattr(upload, u'%s_url' % size, f.url.decode('utf-8'))

    ext.db.session.add(upload)
    ext.db.session.commit()
    return upload

def save(data, name=None, folder_name=None):
    if name is None:
        name = data.filename
    data = data.read()
    datafile = StringIO(data)
    if ext.resizer:
        try:
            images = ext.resizer.resize_image(datafile)
        except IOError:
            # Not an image.
            return save_file(name, data, folder_name=folder_name)
        return save_images(name, data, images, folder_name=folder_name)
    else:
        return save_file(name, data, folder_name=folder_name)


@require_storage
def delete(upload):
    ext.storage.delete(upload.name)
    if ext.resizer:
        for size in ext.resizer.sizes.iterkeys():
            if getattr(upload, size + '_name'):
                ext.storage.delete(getattr(upload, size + '_name'))
    ext.db.session.delete(upload)
    ext.db.session.commit()
