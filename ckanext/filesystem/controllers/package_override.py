import cgi
import paste.fileapp
import mimetypes
import json
import logging
import os
import pathlib2
import ckan.model as model
import ckan.logic as logic
import pylons.config as config
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.plugins as p
from ckan.common import request, c, g, response
import ckan.lib.uploader as uploader
import ckan.lib.navl.dictization_functions as dictization_functions
import ckan.lib.dictization as dictization
from pylons.i18n.translation import _, ungettext
import ckan.lib.i18n as i18n
from ckan.controllers.package import PackageController
import ckan.lib.navl.dictization_functions as dict_fns

from urlparse import urlparse
from posixpath import basename, dirname

render = base.render
abort = base.abort
redirect = base.redirect

NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params

log = logging.getLogger(__name__)

class PackageContributeOverride(p.SingletonPlugin, PackageController):
    ''' Package Controller
        Extended for local file upload
    '''
    def new_resource(self, id, data=None, errors=None, error_summary=None):
        ''' FIXME: This is a temporary action to allow styling of the
        forms. '''
        if request.method == 'POST' and not data:
            save_action = request.params.get('save')
            data = data or \
                clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(
                                                           request.POST))))
            # we don't want to include save as it is part of the form
            del data['save']
            resource_id = data['id']
            del data['id']

            context = {'model': model, 'session': model.Session,
                       'user': c.user, 'auth_user_obj': c.userobj}

            # Check form fields (remote file or local path)
            if isinstance(data['upload_file'],cgi.FieldStorage):
                data['upload'] = data.pop('upload_file')
                del data['upload_path']
            elif pathlib2.Path.exists(pathlib2.Path(os.path.join(
                    os.path.expanduser('~'+c.userobj.name),data.get('upload_path')))):
                data['upload'] = pathlib2.Path(os.path.join(
                    os.path.expanduser('~'+c.userobj.name),data.pop('upload_path')))
                del data['upload_file']

            # see if we have any data that we are trying to save
            data_provided = False
            for key, value in data.iteritems():
                if ((value or isinstance(value, cgi.FieldStorage))
                        and key != 'resource_type'):
                    data_provided = True
                    break

            if not data_provided and save_action != "go-dataset-complete":
                if save_action == 'go-dataset':
                    # go to final stage of adddataset
                    redirect(h.url_for(controller='package',
                                       action='edit', id=id))
                # see if we have added any resources
                try:
                    data_dict = get_action('package_show')(context, {'id': id})
                except NotAuthorized:
                    abort(403, _('Unauthorized to update dataset'))
                except NotFound:
                    abort(404, _('The dataset {id} could not be found.'
                                 ).format(id=id))
                if not len(data_dict['resources']):
                    # no data so keep on page
                    msg = _('You must add at least one data resource')
                    # On new templates do not use flash message
                    if g.legacy_templates:
                        h.flash_error(msg)
                        redirect(h.url_for(controller='package',
                                           action='new_resource', id=id))
                    else:
                        errors = {}
                        error_summary = {_('Error'): msg}
                        return self.new_resource(id, data, errors,
                                                 error_summary)
                # XXX race condition if another user edits/deletes
                data_dict = get_action('package_show')(context, {'id': id})
                get_action('package_update')(
                    dict(context, allow_state_change=True),
                    dict(data_dict, state='active'))
                redirect(h.url_for(controller='package',
                                   action='read', id=id))

            data['package_id'] = id
            try:
                if resource_id:
                    data['id'] = resource_id
                    get_action('resource_update')(context, data)
                else:
                    get_action('resource_create')(context, data)
            except ValidationError, e:
                errors = e.error_dict
                error_summary = e.error_summary
                return self.new_resource(id, data, errors, error_summary)
            except NotAuthorized:
                abort(403, _('Unauthorized to create a resource'))
            except NotFound:
                abort(404, _('The dataset {id} could not be found.'
                             ).format(id=id))
            if save_action == 'go-metadata':
                # XXX race condition if another user edits/deletes
                data_dict = get_action('package_show')(context, {'id': id})
                get_action('package_update')(
                    dict(context, allow_state_change=True),
                    dict(data_dict, state='active'))
                redirect(h.url_for(controller='package',
                                   action='read', id=id))
            elif save_action == 'go-dataset':
                # go to first stage of add dataset
                redirect(h.url_for(controller='package',
                                   action='edit', id=id))
            elif save_action == 'go-dataset-complete':
                # go to first stage of add dataset
                redirect(h.url_for(controller='package',
                                   action='read', id=id))
            else:
                # add more resources
                redirect(h.url_for(controller='package',
                                   action='new_resource', id=id))

        # get resources for sidebar
        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'auth_user_obj': c.userobj}
        try:
            pkg_dict = get_action('package_show')(context, {'id': id})
        except NotFound:
            abort(404, _('The dataset {id} could not be found.').format(id=id))
        try:
            check_access(
                'resource_create', context, {"package_id": pkg_dict["id"]})
        except NotAuthorized:
            abort(403, _('Unauthorized to create a resource for this package'))

        package_type = pkg_dict['type'] or 'dataset'

        errors = errors or {}
        error_summary = error_summary or {}
        vars = {'data': data, 'errors': errors,
                'error_summary': error_summary, 'action': 'new',
                'resource_form_snippet': self._resource_form(package_type),
                'dataset_type': package_type}
        vars['pkg_name'] = id
        # required for nav menu
        vars['pkg_dict'] = pkg_dict
        template = 'package/new_resource_not_draft.html'
        if pkg_dict['state'].startswith('draft'):
            vars['stage'] = ['complete', 'active']
            template = 'package/new_resource.html'
        return render(template, extra_vars=vars)


    def resource_edit(self, id, resource_id, data=None, errors=None,
                      error_summary=None):
        if request.method == 'POST' and not data:
            data = data or clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(
                request.POST))))
            # we don't want to include save as it is part of the form
            del data['save']

            context = {'model': model, 'session': model.Session,
                       'api_version': 3, 'for_edit': True,
                       'user': c.user or c.author, 'auth_user_obj': c.userobj}

            data['package_id'] = id
            try:
                if resource_id:
                    data['id'] = resource_id
                    get_action('resource_update')(context, data)
                else:
                    get_action('resource_create')(context, data)
            except ValidationError, e:
                errors = e.error_dict
                error_summary = e.error_summary
                return self.resource_edit(id, resource_id, data,
                                          errors, error_summary)
            except NotAuthorized:
                abort(401, _('Unauthorized to edit this resource'))


	    redirect(h.url_for(controller='package', action='resource_read',
                               id=id, resource_id=resource_id))

        context = {'model': model, 'session': model.Session,
                   'api_version': 3, 'for_edit': True,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}
        pkg_dict = get_action('package_show')(context, {'id': id})
        if pkg_dict['state'].startswith('draft'):
            # dataset has not yet been fully created
            resource_dict = get_action('resource_show')(context, {'id': resource_id})
            fields = ['url', 'resource_type', 'format', 'name', 'description', 'id']
            data = {}
            for field in fields:
                data[field] = resource_dict[field]
            return self.new_resource(id, data=data)
        # resource is fully created
        try:
            resource_dict = get_action('resource_show')(context, {'id': resource_id})
        except NotFound:
            abort(404, _('Resource not found'))
        c.pkg_dict = pkg_dict
        c.resource = resource_dict
        # set the form action
        c.form_action = h.url_for(controller='package',
                                  action='resource_edit',
                                  resource_id=resource_id,
                                  id=id)
        if not data:
            data = resource_dict

        package_type = pkg_dict['type'] or 'dataset'

        errors = errors or {}
        error_summary = error_summary or {}
        vars = {'data': data, 'errors': errors, 'resource_form_snippet': self._resource_form(package_type),
                'error_summary': error_summary, 'action': 'new'}
        return render('package/resource_edit.html', extra_vars=vars)

    # resource_download() also checking 'resource access' field that we added
    def resource_download(self, id, resource_id, filename=None):
        """
        Provides a direct download by either redirecting the user to the url
        stored or downloading an uploaded file directly.
        """
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}

        if request.method == 'POST':
            data = data or clean_dict(dict_fns.unflatten(tuplize_dict(parse_params(
                request.POST))))

        # check if resources in package are publicly accessible
        pkg_dict = get_action('package_show')(context, {'id': id})
        res_access = True;
        if 'res_access' in pkg_dict:
            res_access = pkg_dict['res_access']

        try:
            rsc = get_action('resource_show')(context, {'id': resource_id, 'res_access': res_access})
            get_action('package_show')(context, {'id': id})
        except NotFound:
            abort(404, _('Resource not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read resource %s') % id)

        if rsc.get('url_type') == 'upload':
            upload = uploader.ResourceUpload(rsc)
            filepath = upload.get_path(rsc['id'])
            fileapp = paste.fileapp.FileApp(filepath)
            try:
                status, headers, app_iter = request.call_application(fileapp)
            except OSError:
                abort(404, _('Resource data not found'))
            response.headers.update(dict(headers))
            content_type, content_enc = mimetypes.guess_type(
                rsc.get('url', ''))
            if content_type:
                response.headers['Content-Type'] = content_type
            response.status = status
            return app_iter
        elif rsc.get('url_type') == 'sftp':
        # FIXME New class for IUploader would be better
        # Example: https://github.com/okfn/ckanext-s3filestore
            path_fs = '/e/user/data'
            user = c.userobj
            org_name = pkg_dict.get('organization').get('name')

            file_name = os.path.basename(rsc.get('url'))
            # Make paths
            dow_path = os.path.expanduser('~'+user.name)
            sto_path = os.path.join(path_fs,org_name,pkg_dict.get('name'))

            os.symlink(os.path.join(sto_path,file_name),os.path.join(dow_path,file_name))

            h.flash_success('''You can download this file from your
            homedirectory on our sftp Server
            inp.ccca.ac.at''')
            redirect(h.url_for(controller='package',
                                  action='read',
                                  id=id))
        elif not 'url' in rsc:
            abort(404, _('No download is available'))
        redirect(rsc['url'])
