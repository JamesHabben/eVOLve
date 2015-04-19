__author__ = 'james.habben'
#evpath = 'file:///Users/jameshabben/Documents/Evidence Files/GST/PhysicalMemory'
#dbpath = evpath + '.sqlite'

evolveVersion = '1.0'

import argparse
argParser = argparse.ArgumentParser(description='Web interface for Volatility Framework.')
argParser.add_argument('-f', '--file', help='RAM dump to analyze')
argParser.add_argument('-l', '--local', help='Restrict webserver to serving \'localhost\' only')
argParser.add_argument('-p', '--profile', help='Memory profile to use with Volatility')
args = argParser.parse_args()

if not args.file:
    #raise BaseException("RAM dump file is required.")
    print "RAM dump file is required."
    exit()

import sys
import volatility
import bottle
import sqlite3
import json

import volatility.constants as constants
import volatility.registry as registry
import volatility.commands as commands
import volatility.conf as conf
import volatility.obj as obj
import volatility.plugins.taskmods as taskmods
import volatility.addrspace as addrspace
import volatility.utils as utils
import volatility.renderers as render
import volatility.plugins as plugins
#import volatility.plugins.filescan as filescan
#from volatility.plugins import *
from bottle import route, Bottle, run, request

Plugins = {'plugins':[]}
def BuildPluginList():
    Plugins['plugins'] = []
    #cmds = registry.get_plugin_classes(commands.Command, lower = True)
    con = sqlite3.connect(config.OUTPUT_FILE)
    curs = con.cursor()
    for cmdname in sorted(cmds):
        command = cmds[cmdname]
        if command.is_valid_profile(profile):
            curs.execute("select name from sqlite_master where type = 'table' and name like ?;", (cmdname,))
            val=0
            if curs.fetchone() is not None:
                val=1
            Plugins['plugins'].append({'name':cmdname,'data':val,'help':command.help()})
    curs.close()
    con.close()

config = conf.ConfObject()
registry.PluginImporter()
#config = conf.ConfObject()
registry.register_global_options(config, addrspace.BaseAddressSpace)
registry.register_global_options(config, commands.Command)
config.parse_options(False)

profs = registry.get_plugin_classes(obj.Profile)
if args.profile:
    config.PROFILE = args.profile
else:
    config.PROFILE = "WinXPSP2x86"
if config.PROFILE not in profs:
    #raise BaseException("Invalid profile " + config.PROFILE + " selected")
    print "Invalid profile " + config.PROFILE + " selected"
    exit()

config.LOCATION = "file://" + args.file
config.OUTPUT_FILE = args.file +".sqlite"
config.parse_options()
profile = profs[config.PROFILE]()



#print args.file

cmds = registry.get_plugin_classes(commands.Command, lower = True)
BuildPluginList()

print "Volatility Version: " + constants.VERSION

#test = ""

@route('/')
def index():
    return bottle.static_file('evolve.htm',root='web')

@route('/web/:path#.+#', name='web')
def static(path):
    return bottle.static_file(path, root='web')

@route('/data/plugins')
def ajax_plugins():
    BuildPluginList()
    return json.dumps(Plugins)

@route('/data/volversion')
def vol_version():
    return constants.VERSION

@route('/data/evolveversion')
def evolve_version():
    return evolveVersion

@route('/data/filepath')
def evolve_version():
    return config.LOCATION

@route('/data/profilename')
def evolve_version():
    return config.PROFILE

@route('/data/view/<name>', method='GET')
@route('/data/view/<name>', method='POST')
def plugin_data(name):
    result = {"columns":[],"data":[]}
    con = sqlite3.connect(config.OUTPUT_FILE)
    if request.method == 'POST' and request.forms.get('query'):
        query = request.forms.get('query')
    else:
        query = "SELECT * FROM " + name
    curs = con.cursor()
    try:
        curs.execute(query)
        result["data"] = curs.fetchall()
        result["columns"] = [i[0] for i in curs.description]
    except Exception as err:
        result["error"] = err.message
    result["name"] = name
    result["query"] = query
    return json.dumps(result)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@route('/data2/plugin/<name>')
def plugin_data2(name):
    con = sqlite3.connect(config.OUTPUT_FILE)
    curs = con.cursor()
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute("SELECT * FROM " + name)
    return json.dumps( cur.fetchall())

@route('/run/plugin/<name>')
def run_plugin(name):
    config.parse_options()
    command = cmds[name](config)
    calc = command.calculate()
    command.render_sqlite(config.OUTPUT_FILE, calc)
    return "done"

app = Bottle()
run(host='0.0.0.0', port=8080)


