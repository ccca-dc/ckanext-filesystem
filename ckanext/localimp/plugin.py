import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from logging import getLogger

import ckanext.localimp.lib.uploader

import os
import cgi
import pprint
import pathlib2

log = getLogger(__name__)


class LocalimpPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IUploader)
    plugins.implements(plugins.IResourceController, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'localimp')

    # IUploader
    def get_uploader(self, upload_to, old_filename=None):
        '''Return an uploader object used to upload general files.'''
        return ckanext.localimp.lib.uploader.LocalimpUpload(upload_to, old_filename)
    def get_resource_uploader(self, data_dict):
        '''Return an uploader object used to upload resource files.'''
        return ckanext.localimp.lib.uploader.LocalimpResourceUpload(data_dict)

    # IRoutes
    def before_map(self, map):
        # Local file import
        map.connect('sftp_filelist', '/sftp_filelist',
                    controller='ckanext.localimp.controllers.upload:UploadController',
                    action='show_filelist')
        map.connect('sftp_upload', '/sftp_upload',
                    controller='ckanext.localimp.controllers.upload:UploadController',
                    action='upload_file')
        # Package
#        map.connect('new_resource', '/dataset/new_resource/{id}',
#                    controller='ckanext.localimp.controllers.package_override:PackageContributeOverride',
#                    action='new_resource')

        map.connect('resource_download', '/dataset/{id}/resource/{resource_id}/download/{filename}', controller='ckanext.localimp.controllers.package_override:PackageContributeOverride', action='resource_download')
        #map.connect('resource_edit', '/dataset/{id}/resource_edit/{resource_id}', controller='ckanext.localimp.controllers.package_override:PackageContributeOverride', action='resource_edit')

        return map

    # IResourceController
    def before_create(self, context, data_dict):
        log.debug(pprint.pprint(data_dict))
        # Check form fields (remote file or local path)
        if isinstance(data_dict['upload_remote'],cgi.FieldStorage):
            data_dict['upload'] = data_dict.pop('upload_remote')
            data_dict.pop('upload_local', None)
        elif data_dict['upload_local'] and pathlib2.Path.exists(pathlib2.Path(os.path.join(
                os.path.expanduser('~'+context['user']),data_dict.get('upload_local')))):
            data_dict['upload'] = pathlib2.Path(os.path.join(
                os.path.expanduser('~'+context['user']),data_dict.pop('upload_local')))
            log.debug('local')
            data_dict.pop('upload_remote', None)
        else:
            data_dict.pop('upload_local', None)
            data_dict.pop('upload_remote', None)
        log.debug("After")
        log.debug(pprint.pprint(data_dict))


    def before_update(self, context, orig_data_dict, data_dict):
        log.debug(pprint.pprint(data_dict))
        # Check form fields (remote file or local path)
        if isinstance(data_dict['upload_remote'],cgi.FieldStorage):
            data_dict['upload'] = data_dict.pop('upload_remote')
            data_dict.pop('upload_local', None)
        elif data_dict['upload_local'] and pathlib2.Path.exists(pathlib2.Path(os.path.join(
                os.path.expanduser('~'+context['user']),data_dict.get('upload_local')))):
            data_dict['upload'] = pathlib2.Path(os.path.join(
                os.path.expanduser('~'+context['user']),data_dict.pop('upload_local')))
            data_dict.pop('upload_remote', None)
        else:
            data_dict.pop('upload_local', None)
            data_dict.pop('upload_remote', None)
        log.debug("After")
        log.debug(pprint.pprint(data_dict))


    def after_map(self, map):
        #log.fatal("==================================> %s" % map)
        return map
