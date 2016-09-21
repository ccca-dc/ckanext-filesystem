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
        if 'apikey' in data and data['apikey']==user.apikey:
            mypath = os.path.expanduser('~'+user.name)+'/'
            onlyfiles = [f for f in os.listdir(mypath) if (os.path.isfile(os.path.join(mypath, f)) and not f.startswith('.'))]
            return json.dumps(onlyfiles)
        else:
            return "no API key"
