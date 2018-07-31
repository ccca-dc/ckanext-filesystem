import ckan.plugins.toolkit as tk
import ckan.lib.uploader as uploader

import shutil
import os
import ckan.authz as authz
import json

@tk.side_effect_free
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

    return json.dumps(lst_paths)


@tk.side_effect_free
def localimp_create_symlink(context, data_dict):
    """
    Creates a folder with the packages name and symlinks for uploaded resources
    in the users home directory under the configured export_folder

    :param id: The id of the package to create the symlinks for
    :type id: string
    :param directory_name: A higher level folder to put the package_name folders in (e.g for Baskets) (optional)
    :type directory_name: string
    :returns:
    """
    tk.check_access('localimp_create_symlink', context, data_dict)

    # TODO set as config
    export_folder = "export"

    if "directory_name" in data_dict:
        export_folder = os.path.join(export_folder, data_dict.get("directory_name"))

    user_name = context.get('user')
    pkg_dct = tk.get_action("package_show")(context,{"id": data_dict.get("id", None)})

    # TODO undo changes here
    #rootdir = os.path.join(os.path.expanduser('~' + user_name), export_folder, pkg_dct.get("name"))
    dest_dir = os.path.join('/e/user/home', user_name, export_folder, pkg_dct.get("name"))

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for res in pkg_dct.get('resources', []):
        if res.get("url_type") == "upload":
            upload = uploader.ResourceUpload(res)
            file_path = upload.get_path(res['id'])
            os.symlink(file_path, os.path.join(dest_dir, res.get("url").split('/')[-1]))


@tk.side_effect_free
def localimp_remove_symlink(context, data_dict):
    """
    Removes a folder with the packages name and symlinks for uploaded resources
    from the users home directory

    :param id: The id of the package
    :type id: string
    :param directory_name: A higher level folder, where the package_name folders are located (e.g for Baskets) (optional)
    :type directory_name: string
    :returns:
    """
    tk.check_access('localimp_remove_symlink', context, data_dict)

    export_folder = "export"

    if "directory_name" in data_dict:
        export_folder = os.path.join(export_folder, data_dict.get("directory_name"))

    user_name = context.get('user')
    pkg_dct = tk.get_action("package_show")(context,{"id": data_dict.get("id", None)})

    # TODO undo changes here
    #rootdir = os.path.join(os.path.expanduser('~' + user_name), export_folder, pkg_dct.get("name"))
    dest_dir = os.path.join('/e/user/home', user_name, export_folder, pkg_dct.get("name"))

    # storage_path = tk.config.get('ckan.storage_path')
    # root_dir = os.path.join(storage_path, user_name, export_folder, pkg_dct.get("name"))

    if not os.path.exists(dest_dir):
        tk.ObjectNotFound("The path to the resource does not exist")
    else:
        # Remove the whole package folder
        shutil.rmtree(dest_dir)


@tk.side_effect_free
def localimp_clear_export(context, data_dict):
    """
    Removes all symlinks in export folder from the users home directory
    :param directory_name: A higher level folder, where the package_name folders are located (e.g for Baskets) (optional)
    :type directory_name: string
    :returns:
    """
    tk.check_access('localimp_clear_export', context, data_dict)

    export_folder = "export"

    if "directory_name" in data_dict:
        export_folder = os.path.join(export_folder, data_dict.get("directory_name"))

    user_name = context.get('user')

    # TODO undo changes here
    #rootdir = os.path.join(os.path.expanduser('~' + user_name), export_folder)
    dest_dir = os.path.join('/e/user/home', user_name, export_folder)

    # storage_path = tk.config.get('ckan.storage_path')
    # root_dir = os.path.join(storage_path, user_name, export_folder, pkg_dct.get("name"))

    if not os.path.exists(dest_dir):
        tk.ObjectNotFound("The path to the resource does not exist")
    else:
        # Remove the whole package folder
        shutil.rmtree(dest_dir)
