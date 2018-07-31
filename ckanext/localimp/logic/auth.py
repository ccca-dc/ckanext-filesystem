import ckan.plugins.toolkit as tk

from ckan.common import _

@tk.auth_disallow_anonymous_access
def localimp_show_files(context, data_dict):
    """
    Can the user show his homedirectory. This is only available for
    registered users.

    There is a shortcut where this will not be called for sysadmins
    """
    return {'success': True}

@tk.auth_disallow_anonymous_access
def localimp_create_symlink(context, data_dict):
    """
    Can the user create symlinks in his homedirectory. This is only available for
    registered users.

    There is a shortcut where this will not be called for sysadmins
    """
    return {'success': True}

@tk.auth_disallow_anonymous_access
def localimp_remove_symlink(context, data_dict):
    """
    Can the user remove symlinks from his homedirectory. This is only available for
    registered users.

    There is a shortcut where this will not be called for sysadmins
    """
    return {'success': True}

@tk.auth_disallow_anonymous_access
def localimp_clear_export(context, data_dict):
    """
    Can the user remove symlinks from his homedirectory. This is only available for
    registered users.

    There is a shortcut where this will not be called for sysadmins
    """
    return {'success': True}
