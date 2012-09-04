from setuptools import setup, Command
import subprocess


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        errno = subprocess.call(['py.test'])
        raise SystemExit(errno)

setup(
    name='Flask-Uploads',
    version='0.1.0',
    url='http://github.com/FelixLoether/flask-uploads',
    author='Oskari Hiltunen',
    author_email='flask-uploads@loethr.net',
    description='A Flask extension to help you add file uploading '
                'functionality to your site.',
    long_description=open('README.rst').read(),
    packages=['flask_uploads'],
    platforms='any',
    cmdclass={'test': PyTest},
    classifiers=[
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
    ]
)
