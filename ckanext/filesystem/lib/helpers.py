import ckan.plugins.toolkit as toolkit

def show_filelist(*args, **kw):
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
