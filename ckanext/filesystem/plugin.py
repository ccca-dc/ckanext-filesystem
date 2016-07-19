import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckanext.filesystem.lib.uploader as uploader

config = {}

class ConfigError(Exception):
    pass

class FilesystemPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IUploader)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'filesystem')

    # IConfigurable

    def configure(self, main_config):
        """Implementation of IConfigurable.configure"""
        schema = {
            'ckanext.filesystem.storage_path': {'required': True},
            # 'ckanext.ldap.auth.dn': {},
            # 'ckanext.ldap.auth.password': {'required_if': 'ckanext.ldap.auth.dn'},
            # 'ckanext.ldap.search.alt': {},
            # 'ckanext.ldap.search.alt_msg': {'required_if': 'ckanext.ldap.search.alt'},
            # 'ckanext.ldap.organization.role': {'default': 'member', 'validate': _allowed_roles},
            # 'ckanext.ldap.ckan_fallback': {'default': False, 'parse': p.toolkit.asbool},
            # 'ckanext.ldap.prevent_edits': {'default': False, 'parse': p.toolkit.asbool}
        }
        errors = []
        for i in schema:
            v = None
            if i in main_config:
                v = main_config[i]
            elif i.replace('ckanext.', '') in main_config:
                log.warning('Filesystem configuration options should be prefixed with \'ckanext.\'. ' +
                            'Please update {0} to {1}'.format(i.replace('ckanext.', ''), i))
                # Support filesystem.* options for backwards compatibility
                main_config[i] = main_config[i.replace('ckanext.', '')]
                v = main_config[i]

            if v:
                if 'parse' in schema[i]:
                    v = (schema[i]['parse'])(v)
                try:
                    if 'validate' in schema[i]:
                        (schema[i]['validate'])(v)
                    config[i] = v
                except ConfigError as e:
                    errors.append(str(e))
            elif schema[i].get('required', False):
                errors.append('Configuration parameter {} is required'.format(i))
            elif schema[i].get('required_if', False) and schema[i]['required_if'] in config:
                errors.append('Configuration parameter {} is required when {} is present'.format(i,schema[i]['required_if']))
            elif 'default' in schema[i]:
                config[i] = schema[i]['default']
        if len(errors):
            raise ConfigError("\n".join(errors))

    # IUploader

    # def get_uploader(self, upload_to, old_filename=None):
    #     '''Return an uploader object used to upload general files.'''
    #     return ckanext.s3filestore.uploader.FilesystemResourceUpload(upload_to,
    #                                                    old_filename)

    def get_resource_uploader(self, data_dict):
        '''Return an uploader object used to upload resource files.'''
        return uploader.FileSystemResourceUpload(data_dict)

    # IRoutes

    # def before_map(self, map):
    #     with SubMapper(map, controller='ckanext.s3filestore.controller:S3Controller') as m:
    #         # Override the resource download links
    #         m.connect('resource_download',
    #                   '/dataset/{id}/resource/{resource_id}/download',
    #                   action='resource_download')
    #         m.connect('resource_download',
    #                   '/dataset/{id}/resource/{resource_id}/download/{filename}',
    #                   action='resource_download')

    #         # fallback controller action to download from the filesystem
    #         m.connect('filesystem_resource_download',
    #                   '/dataset/{id}/resource/{resource_id}/fs_download/{filename}',
    #                   action='filesystem_resource_download')

    #         # Intercept the uploaded file links (e.g. group images)
    #         m.connect('uploaded_file', '/uploads/{upload_to}/{filename}',
    #                   action='uploaded_file_redirect')

    #     return map
