import os
import shutil

import ckan.lib.helpers as h
import ckan.lib.base as base
import requests
from pylons import config
import ckan.plugins.toolkit as toolkit

import cgi
import logging
import json
import pathlib2
import ckan.model as model
import ckan.logic as logic
get_action = logic.get_action

c = base.c
request = base.request
log = logging.getLogger(__name__)


class UploadController(base.BaseController):
    ''' Controller for extended upload functionality.
    '''
    def show_filelist(self):
        user = c.userobj
        data = base.request.params
        log.debug('username: '+user.name)
        log.debug('apikey: '+user.apikey)
        if 'apikey' in data and data['apikey']==user.apikey:
            mypath = os.path.expanduser('~'+user.name)+'/'
            log.debug('my path: '+mypath)
            onlyfiles = [f for f in os.listdir(mypath) if (os.path.isfile(os.path.join(mypath, f)) and not f.startswith('.'))]
            return json.dumps(onlyfiles)
        else:
            return "no API key"

    def upload_file(self):
        # user = c.userobj
        # reqData = base.request.params
        # #ckan_url = config.get('ckan.site_url', '//localhost:5000')
        # mypath = expanduser('~'+user.name)+'/'
        # filename = reqData['filename']
        # url = mypath + reqData['filename']
        # log.debug('upload file url: '+ url)
        # log.debug('upload package id: '+ reqData['package_id'])
        # upload = pathlib2.Path()
        # data={'package_id': reqData['package_id'],
        #     'url': '',
        #     'upload': upload
        # }
        # context = {'model': model, 'session': model.Session,
        #            'user': c.user or c.author, 'auth_user_obj': c.userobj}
        # resource_dict = get_action('resource_create')(context, data)
        # return json.dumps(resource_dict);

        # FIXME get context as parameter
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'auth_user_obj': c.userobj}

        user = c.userobj
        reqData = base.request.params

        # pkg = toolkit.get_action('package_show')(context,{'id':reqData['package_id']})
        # org_name = pkg['organization']['name']

        upl_path = os.path.expanduser('~'+user.name)
        # sto_path = os.path.join(path_fs,org_name,pkg['name'])

        # url = os.path.join(url_prefix,org_name,reqData['package_id'],reqData['filename'])
        # url = h.url_for(controller='package',action='read',id=pkg['name'])
        # url = os.path.join(sto_path,reqData['filename'])
        url = reqData['filename']

        # uid = pwd.getpwnam(user_fs).pw_uid
        # gid = grp.getgrnam(group_fs).gr_gid

        upload = os.path.join(upl_path,reqData['filename'])

        data={'package_id': reqData['package_id'],
              'url': '',
              'upload': upload,
        }
        resource_dict = get_action('resource_create')(context, data)

        return json.dumps(resource_dict);
