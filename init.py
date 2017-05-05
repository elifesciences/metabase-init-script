# https://github.com/metabase/metabase/blob/master/docs/api-documentation.md

from pprint import pprint
import os, sys, json
from metabase import Metabase
import configparser
import logging

logging.basicConfig()

logging.getLogger('').setLevel(logging.DEBUG)

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
AUTHFILE = '.auth'

def props(path):
    with open(path, 'r') as f:
        config_string = '[dummy_section]\n' + f.read()
    config = configparser.ConfigParser()
    config.read_string(config_string)
    return dict(dict(config['dummy_section'].items()))

def subdict(d, ks):
    return {k: v for k, v in d.items() if k in ks}

def load_session_id():
    if os.path.exists(AUTHFILE):
        LOG.debug(AUTHFILE + " file found")
        return open(AUTHFILE, 'r').read()

def write_session_id(mbase):
    with open('.auth', 'w') as fh:
        fh.write(mbase.session)

def idx(val_list, fn):
    "groups a dictionary by the value returned by given fn"
    _idx = {}
    for val in val_list:
        _idx[fn(val)] = val
    return _idx

def rename(d, kv_list):
    "mutator!"
    for old, new in kv_list:
        d[new] = d[old]
        del d[old]
    return d

#
#
#

cfg = props("app.properties")
kwargs = subdict(cfg, ['endpoint', 'email', 'password'])
kwargs['session'] = load_session_id() # pass in session ID if we have one
kwargs['auth_callback'] = write_session_id # write session ID to AUTHFILE on successful authentication

metabase = Metabase(**kwargs) # connect, authenticate

# we know our database name but can't be certain of it's ID
ret, dbdata = metabase.get('/database')

# 'details' looks like:
#{'dbname': 'foo',
# 'host': 'localhost',
# 'password': '**MetabasePass**',
# 'port': 5432,
# 'ssl': True,
# 'user': 'bar'}
dbdata = idx(dbdata, lambda v: v['details'].get('dbname'))

dbname = cfg['dbname']
assert dbname in dbdata, "database %r not found, cannot update" % dbname

dbdata = dbdata[dbname]
#pprint(dbdata)

kwargs = subdict(dbdata, ['id', 'name', 'engine', 'details', 'is_full_sync', 'description', 'caveats', 'points_of_interest'])
kwargs['details']['host'] = cfg['dbhost']
#pprint(kwargs)

resp = metabase.put("/database/%s" % kwargs['id'], json=kwargs)

if not resp:
    sys.exit(1)
sys.exit(0)
