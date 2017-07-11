.. You should enable this project on travis-ci.org and coveralls.io to make
   these badges work. The necessary Travis and Coverage config files have been
   generated for you.

.. image:: https://travis-ci.org/surel89/ckanext-localimp.svg?branch=master
    :target: https://travis-ci.org/surel89/ckanext-localimp

.. image:: https://coveralls.io/repos/surel89/ckanext-localimp/badge.svg
  :target: https://coveralls.io/r/surel89/ckanext-localimp

.. image:: https://pypip.in/download/ckanext-localimp/badge.svg
    :target: https://pypi.python.org/pypi//ckanext-localimp/
    :alt: Downloads

.. image:: https://pypip.in/version/ckanext-localimp/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-localimp/
    :alt: Latest Version

.. image:: https://pypip.in/py_versions/ckanext-localimp/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-localimp/
    :alt: Supported Python versions

.. image:: https://pypip.in/status/ckanext-localimp/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-localimp/
    :alt: Development Status

.. image:: https://pypip.in/license/ckanext-localimp/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-localimp/
    :alt: License

=============
ckanext-localimp
=============

This extension enables users to import data from a home directory into ckan
without the use of http uploads.

**resource_create**
   Instead of the old parameter upload (FieldStorage (optional) needs multipart/form-data)
   there are now to possibilities, where the user can choose one:

   -upload_remote: Upload your file as FieldStorage (original ckan functionality)
   -upload_local: Filepath relative to your home directory


------------
Requirements
------------

The application server needs access to the users home directories. Therefore it
is best that the user of the application server is in all usergroups. We use
LDAP (PosixAccount) with the extension
.. _ckanext-ldap: https://github.com/NaturalHistoryMuseum/ckanext-ldap
and provide an extra input server with chrooted sftp and ftps access for the users.

Serving big files via your application server (uwsgi, gunicorn, ...) is
not a good idea, due to cache issues and blocking of workers. Therefore, we use
the possibility of X-Accel-Redirect for nginx with a reverse proxy to uwsgi.
This is implemented in the extension
.. _ckanext-iauth: https://github.com/ccca-dc/ckanext-iauth/blob/master/ckanext/iauth/controllers/package_override.py

------------
Installation
------------

To install ckanext-localimp:

1. Setup ckan with nginx + uwsgi 

2. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

3. Install the ckanext-localimp Python package into your virtual environment::

     python setup.py install

4. Add ``localimp`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

5. Restart CKAN. For example if you've deployed CKAN with uwsgi (emperor) on Ubuntu::

     sudo service uwsgi-emperor restart


---------------
Config Settings
---------------

Document any optional config settings here. For example::

    # The minimum number of hours to wait before re-checking a resource
    # (optional, default: 24).
    ckanext.localimp.some_setting = some_default_value


------------------------
Development Installation
------------------------

To install ckanext-localimp for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/surel89/ckanext-localimp.git
    cd ckanext-localimp
    python setup.py develop
    pip install -r dev-requirements.txt


-----------------
Running the Tests
-----------------

To run the tests, do::

    nosetests --nologcapture --with-pylons=test.ini

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.localimp --cover-inclusive --cover-erase --cover-tests


---------------------------------
Registering ckanext-localimp on PyPI
---------------------------------

ckanext-localimp should be availabe on PyPI as
https://pypi.python.org/pypi/ckanext-localimp. If that link doesn't work, then
you can register the project on PyPI for the first time by following these
steps:

1. Create a source distribution of the project::

     python setup.py sdist

2. Register the project::

     python setup.py register

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the first release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.1 then do::

       git tag 0.0.1
       git push --tags


----------------------------------------
Releasing a New Version of ckanext-localimp
----------------------------------------

ckanext-localimp is availabe on PyPI as https://pypi.python.org/pypi/ckanext-localimp.
To publish a new version to PyPI follow these steps:

1. Update the version number in the ``setup.py`` file.
   See `PEP 440 <http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers>`_
   for how to choose version numbers.

2. Create a source distribution of the new version::

     python setup.py sdist

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the new release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.2 then do::

       git tag 0.0.2
       git push --tags
