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
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions, inherit=True)
    plugins.implements(plugins.IUploader)
    plugins.implements(plugins.IResourceController, inherit=True)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'localimp')

    # IRoutes
    def before_map(self, map):
        # Local file import
        map.connect('sftp_filelist', '/sftp_filelist',
                    controller='ckanext.localimp.controllers.upload:UploadController',
                    action='show_filelist')
        return map

    # IActions
    def get_actions(self):
        import ckanext.localimp.logic.action as action
        actions = {
            'localimp_show_files': action.localimp_show_files,
            'localimp_create_symlink': action.localimp_create_symlink,
            'localimp_remove_symlink': action.localimp_remove_symlink,
            'localimp_clear_export': action.localimp_clear_export,
            }
        return actions

    # IAuthFunctions
    def get_auth_functions(self):
        import ckanext.localimp.logic.auth as auth
        auths = {
            'localimp_show_files': auth.localimp_show_files,
            'localimp_create_symlink': auth.localimp_create_symlink,
            'localimp_remove_symlink': auth.localimp_remove_symlink,
            'localimp_clear_export': auth.localimp_clear_export,
        }
        return auths

    # IUploader
    def get_uploader(self, upload_to, old_filename=None):
        '''Return an uploader object used to upload general files.'''
        return ckanext.localimp.lib.uploader.LocalimpUpload(upload_to, old_filename)
    def get_resource_uploader(self, data_dict):
        '''Return an uploader object used to upload resource files.'''
        return ckanext.localimp.lib.uploader.LocalimpResourceUpload(data_dict)

    # IResourceController
    def before_create(self, context, data_dict):
        # Check form fields (remote file or local path)
        upload_remote = data_dict.pop('upload_remote', None)
        upload_local = data_dict.pop('upload_local', None)
        if upload_remote or isinstance(upload_remote,cgi.FieldStorage):
            data_dict['upload'] = upload_remote
        if upload_local and pathlib2.Path.exists(pathlib2.Path(os.path.join(
                os.path.expanduser('~'+context['user']),upload_local))):
            data_dict['upload'] = pathlib2.Path(os.path.join(
                os.path.expanduser('~'+context['user']),upload_local))


    def before_update(self, context, orig_data_dict, data_dict):
        # Check form fields (remote file or local path)
        upload_remote = data_dict.pop('upload_remote', None)
        upload_local = data_dict.pop('upload_local', None)
        if upload_remote or isinstance(upload_remote,cgi.FieldStorage):
            data_dict['upload'] = upload_remote
        if upload_local and pathlib2.Path.exists(pathlib2.Path(os.path.join(
                os.path.expanduser('~'+context['user']),upload_local))):
            data_dict['upload'] = pathlib2.Path(os.path.join(
                os.path.expanduser('~'+context['user']),upload_local))
