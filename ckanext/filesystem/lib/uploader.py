import logging

import ckan.lib.munge as munge
import ckan.model as model

import os
import shutil
import cgi
import pylons
import datetime
import mimetypes
import pathlib2

config = pylons.config
log = logging.getLogger(__name__)

_storage_path = None
_max_resource_size = None
_max_image_size = None

def get_storage_path():
    '''Function to cache storage path'''
    global _storage_path

    # None means it has not been set. False means not in config.
    if _storage_path is None:
        storage_path = config.get('ckan.storage_path')
        ofs_impl = config.get('ofs.impl')
        ofs_storage_dir = config.get('ofs.storage_dir')
        if storage_path:
            _storage_path = storage_path
        elif ofs_impl == 'pairtree' and ofs_storage_dir:
            log.warn('''Please use config option ckan.storage_path instead of
                     ofs.storage_dir''')
            _storage_path = ofs_storage_dir
            return _storage_path
        elif ofs_impl:
            log.critical('''We only support local file storage form version 2.2
                         of ckan please specify ckan.storage_path in your
                         config for your uploads''')
            _storage_path = False
        else:
            log.critical('''Please specify a ckan.storage_path in your config
                         for your uploads''')
            _storage_path = False

    return _storage_path


def get_max_resource_size():
    global _max_resource_size
    if _max_resource_size is None:
        _max_resource_size = int(config.get('ckan.max_resource_size', 10))
    return _max_resource_size


class FileSystemResourceUpload(object):
    def __init__(self, resource):
        path = get_storage_path()
        if not path:
            self.storage_path = None
            return
        self.storage_path = os.path.join(path, 'resources')
        try:
            os.makedirs(self.storage_path)
        except OSError, e:
            # errno 17 is file already exists
            if e.errno != 17:
                raise
        self.filename = None

        url = resource.get('url')
        upload_field = resource.pop('upload', None)
        self.clear = resource.pop('clear_upload', None)

        # upload is FieldStorage
        if isinstance(upload_field, cgi.FieldStorage):
            self.filename = upload_field.filename
            # self.filename = munge.munge_filename(self.filename)
            resource['url'] = munge.munge_filename(self.filename)
            resource['url_type'] = 'upload'
            resource['last_modified'] = datetime.datetime.utcnow()
            self.url_type = resource['url_type']
            self.upload_file = upload_field.file
        # upload is path to local file
        elif isinstance(upload_field, pathlib2.Path):
            self.localpath = str(upload_field.absolute())
            self.filename = upload_field.name
            # self.filename = munge.munge_filename(self.filename)
            resource['url'] = munge.munge_filename(self.filename)
            log.debug('URL: ' + resource['url'])
            resource['url_type'] = 'local'
            self.url_type = resource['url_type']
        elif self.clear:
            resource['url_type'] = ''

    def get_directory(self, id):
        directory = os.path.join(self.storage_path,
                                 id[0:3], id[3:6])
        return directory

    def get_path(self, id):
        directory = self.get_directory(id)
        filepath = os.path.join(directory, id[6:])
        return filepath

    def upload(self, id, max_size=10):
        '''Actually upload the file.

        :returns: ``'file uploaded'`` if a new file was successfully uploaded
            (whether it overwrote a previously uploaded file or not),
            ``'file deleted'`` if an existing uploaded file was deleted,
            or ``None`` if nothing changed
        :rtype: ``string`` or ``None``

        '''
        if not self.storage_path:
            return

        # Get directory and filepath on the system
        # where the file for this resource will be stored
        directory = self.get_directory(id)
        filepath = self.get_path(id)

        # If a filename has been provided (a file is being uploaded)
        # we write it to the filepath (and overwrite it if it already
        # exists). This way the uploaded file will always be stored
        # in the same location
        if self.filename:
            try:
                os.makedirs(directory)
            except OSError, e:
                # errno 17 is file already exists
                if e.errno != 17:
                    raise
            if self.url_type == 'upload':
                tmp_filepath = filepath + '~'
                output_file = open(tmp_filepath, 'wb+')
                self.upload_file.seek(0)
                current_size = 0
                while True:
                    current_size = current_size + 1
                    # MB chunks
                    data = self.upload_file.read(2 ** 20)
                    if not data:
                        break
                    output_file.write(data)
                    if current_size > max_size:
                        os.remove(tmp_filepath)
                        raise logic.ValidationError(
                            {'upload': ['File upload too large']}
                        )
                output_file.close()
                os.rename(tmp_filepath, filepath)
                return
            elif self.url_type == 'local':
                # Move file to ckan file system path
                # FIXME ownership of file and exceptions
                shutil.move(self.localpath,filepath)
                return

        # The resource form only sets self.clear (via the input clear_upload)
        # to True when an uploaded file is not replaced by another uploaded
        # file, only if it is replaced by a link to file.
        # If the uploaded file is replaced by a link, we should remove the
        # previously uploaded file to clean up the file system.
        if self.clear:
            try:
                os.remove(filepath)
            except OSError, e:
                pass
