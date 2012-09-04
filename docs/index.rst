.. Flask-Uploads documentation master file, created by
   sphinx-quickstart on Mon Sep  3 13:33:23 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Flask-Upload
============

Flask-Upload is a Flask extension to help you add file uploading functionality
to your site. Here's a small example on utilizing Flask-Upload::

    import os.path
    from flask import Flask, redirect, request, render_template, url_for
    from flask.ext.sqlalchemy import SQLAlchemy
    from flask.ext.storage import get_default_storage_class
    from flask.ext.uploads import delete, init, save, Upload

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    app.config['DEFAULT_FILE_STORAGE'] = 'filesystem'
    app.config['UPLOADS_FOLDER'] = os.path.realpath('.') + '/static/'
    app.config['FILE_SYSTEM_STORAGE_FILE_VIEW'] = 'static'
    init(SQLAlchemy(app), get_default_storage_class(app))


    @app.route('/')
    def index():
        """List the uploads."""
        uploads = Upload.query.all()
        return render_template('list.html', uploads=uploads)


    @app.route('/upload', methods=['GET', 'POST'])
    def upload():
        """Upload a new file."""
        if request.method == 'POST':
            save(request.files['upload'])
            return redirect(url_for('index'))
        return render_template('upload.html')


    @app.route('/delete/<int:id>', methods=['POST'])
    def remove(id):
        """Delete an uploaded file."""
        upload = Upload.query.get_or_404(id)
        delete(upload)
        return redirect(url_for('index'))

    if __name__ == '__main__':
        app.run()

.. toctree::
   :maxdepth: 2


Installation
------------

::

    pip install -e git://github.com/FelixLoether/flask-uploads#egg=Flask-Uploads


API Reference
-------------

.. automodule:: flask_uploads
.. class:: Upload

    The database model class generated based on some preset fields and the
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

.. autofunction:: init
.. autofunction:: save
.. autofunction:: delete
.. autofunction:: save_images
.. autofunction:: save_file
