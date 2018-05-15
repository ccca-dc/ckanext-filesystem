import ckan.logic
import ckan.plugins.toolkit as tk

import os
import ckan.authz as authz
from ckan.common import _
import json

ValidationError = ckan.logic.ValidationError
NotFound = ckan.logic.NotFound
_check_access = ckan.logic.check_access
_get_or_bust = ckan.logic.get_or_bust
_get_action = ckan.logic.get_action

def localimp_ls(context, data_dict):
    """
    Creates a nested dictionary that represents the folder structure of rootdir
    """
    if authz.auth_is_anon_user(context):
        tk.abort(401, _('Unauthorized to list files'))
    else:
        user_name = context.get('user')
        rootdir = os.path.join(os.path.expanduser('~' + user_name))
        dir = {}
        rootdir = rootdir.rstrip(os.sep)
        start = rootdir.rfind(os.sep) + 1
        for path, dirs, files in os.walk(rootdir):
            folders = path[start:].split(os.sep)
            subdir = dict.fromkeys(files)
            parent = reduce(dict.get, folders[:-1], dir)
            parent[folders[-1]] = subdir
        return dir

def localimp_show_files(context, data_dict):
    """
    Creates a nested dictionary that represents the folder structure of rootdir
    """
    if authz.auth_is_anon_user(context):
        tk.abort(401, _('Unauthorized to list files'))
    else:
        user_name = context.get('user')
        rootdir = os.path.join(os.path.expanduser('~' + user_name))
        lst_paths = []
        for path, subdirs, files in os.walk(rootdir):
            for name in files:
                lst_paths.append(os.path.join(path, name).split(rootdir)[1])

        return lst_paths 
