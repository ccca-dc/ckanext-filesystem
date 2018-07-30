import ckan.plugins.toolkit as tk
import ckan.lib.uploader as uploader

import os
import ckan.authz as authz
import json

def localimp_show_files(context, data_dict):
    """
    Creates a list that represents the folder structure of the users home directory
    """
    tk.check_access('localimp_show_files', context, data_dict)

    exclude_prefixes = ('__', '.')  # exclusion prefixes
    user_name = context.get('user')
    # TODO undo changes here
    #rootdir = os.path.join(os.path.expanduser('~' + user_name), '')
    rootdir = os.path.join('/e/user/home', user_name, '')

    lst_paths = []
    for path, subdirs, files in os.walk(rootdir):
        lst_paths = lst_paths + \
                    [os.path.join(path, name).split(rootdir)[1]
                    for name in files if not name.startswith(exclude_prefixes)]

    return lst_paths


def localimp_create_symlink(context, data_dict):
    """
    Creates a folder with the packages name and symlinks for uploaded resources
    in the users home directory

    :param id: The id of the pakcage to create the symlinks for (only admin)
    :type id: string
    :returns:
    """
    tk.check_access('localimp_create_symlink', context, data_dict)

    import ipdb; ipdb.set_trace()

    export_folder = "export"

    user_name = context.get('user')
    pkg_dct = tk.get_action("package_show")(context,{"id": data_dict.get("id", None)})

    # TODO undo changes here
    #rootdir = os.path.join(os.path.expanduser('~' + user_name), export_folder)
    dest_dir = os.path.join('/e/user/home', user_name, export_folder, pkg_dct.get("name"))

    # storage_path = tk.config.get('ckan.storage_path')
    # root_dir = os.path.join(storage_path, user_name, export_folder, pkg_dct.get("name"))

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for res in pkg_dct.get('resources', []):
        if res.get("url_type") == "upload":
            upload = uploader.ResourceUpload(rsc)
            file_path = upload.get_path(rsc['id'])
            os.symlink(file_path, os.path.join(dest_dir, res.get("url").split('/')[-1]))
