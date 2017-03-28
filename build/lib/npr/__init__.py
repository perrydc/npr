from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import input
from builtins import open
from builtins import str
from builtins import object
from future import standard_library
standard_library.install_aliases()
import requests,json,re,os,ast,sys
class Api(object):
    def __init__(self):
        try:
            configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'npr.conf')
            f=open(configfile,'r')
            config = ast.literal_eval(f.read())
        except:
            print('Authenticate your app and login.  Try:')
            print('  npr.auth()')
            print('  npr.login()')
        try:
            token = config['token']
        except:
            print('Login your user.  Try:')
            print('  npr.login()')
        self.token = token
        self.domain = "https://api.npr.org"
        self.headers = {"Accept":"application/json","Authorization":"Bearer " + self.token}
    def pretty(self):
        print(json.dumps(self.response, sort_keys=True, indent=2, separators=(',', ': ')))
    def view(self,tree, path='.response'):
        if isinstance(tree, str)|isinstance(tree, int)|isinstance(tree, float):
            leaf = tree
            yield(leaf, path)
        elif isinstance(tree, dict):
            if len(tree.items()) > 1:
                for key, value in tree.items():
                    local_path = path + "['" + key + "']"
                    for t in self.view(value, local_path):
                        yield t
        else:
            if tree:
                if len(tree) == 1:
                    local_path = path + "[0]"
                    for t in self.view(tree[0], local_path):
                        yield t
                else:
                    count = 0
                    for value in tree:
                        local_path = path + "[" + str(count) + "]"
                        count = count + 1
                        for t in self.view(value, local_path):
                            yield t
    def find(self, term=''):
        keys = {}
        for t in self.view(self.response):
            keys.update({t[0]:t[1]})
            #print(t[0],t[1])
        if len(term) < 1:
            print(keys)
        else:
            print(term, keys[term])

class User(Api):
    def __init__(self):
        Api.__init__(self)
        self.endpoint = self.domain + "/identity/v2/user"
        self.response = requests.get(self.endpoint,headers=self.headers).json()

class Recommend(Api):
    def __init__(self):
        Api.__init__(self)
        self.endpoint = self.domain + "/listening/v2/recommendations"
        self.response = requests.get(self.endpoint,headers=self.headers).json()

class Search(Api):
    def __init__(self, query):
        Api.__init__(self)
        self.endpoint = self.domain + "/listening/v2/search/recommendations?searchTerms=" + query
        self.response = requests.get(self.endpoint,headers=self.headers).json()

class Station(Api):
    def __init__(self, query):
        Api.__init__(self)
        self.endpoint = self.domain + "/stationfinder/v3/stations?q=" + query
        self.response = requests.get(self.endpoint,headers=self.headers).json()
    def getstream(self):
        for stream in self.response['items'][0]['links']['streams']:
         if stream['isPrimaryStream'] and stream['typeId'] == "10":
           return stream['href']
        for stream in self.response['items'][0]['links']['streams']:
         if stream['isPrimaryStream']:
           return stream['href']
        for stream in self.response['items'][0]['links']['streams']:
         if stream['typeId'] == "10":
          return stream['href']
        return stream['href']
    def pls(self,stream):
        f = requests.get(stream).text
        url = re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',f)
        return url.group(0)
    def m3u(self,stream):
        f = requests.get(stream).text
        url = re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',f)
        return url.group(0)
    def live(self):
        s = self.getstream()
        if re.search(r'pls$',s):
          stream = self.pls(s)
        elif re.search(r'm3u$',s):
          stream = self.m3u(s)
        else:
          stream = s
        return stream

def auth():
    print("To authenticate your app:")
    print("  1. LOGIN to http://dev.npr.org (if it's your first time, you'll need to register.)")
    print("  2. Open the dev console (drop down in the top right corner of dev center)")
    print("  3. Create a new application")
    print("  4. Select that application and enter your credentials below")
    id = input("Application ID:")
    secret = input("Application Secret:")
    config = "{'id':'" + id + "','secret':'" + secret + "'}"
    configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'npr.conf')
    f=open(configfile,'w+')
    f.write(config)
    print('App authenticated.  Now run "npr.login()" to get a bearer token')
def deauth():
    configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'npr.conf')
    os.remove(configfile)
    print('app deauthed')
def login():
    try:
        configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'npr.conf')
        f=open(configfile,'r')
    except:
        print('Authenticate your app. Try: "npr.auth()"')
    config = ast.literal_eval(f.read())
    id = config['id']
    secret = config['secret']
    scope = 'identity.readonly identity.write listening.readonly listening.write localactivation'
    deviceCodeEndpoint = 'https://api.npr.org/authorization/v2/device'
    deviceCodeHeaders = {'Accept': 'application/json'}
    deviceCodeData = {'client_id':id,'client_secret':secret,'scope':scope}
    deviceCodeJson = requests.post(deviceCodeEndpoint, headers=deviceCodeHeaders, data = deviceCodeData).json()
    print("Go to " + deviceCodeJson['verification_uri'] + " login and enter:")
    print(deviceCodeJson['user_code'])
    pause = input("When finished, type 'done' and press enter:")
    tokenEndpoint = 'https://api.npr.org/authorization/v2/token'
    tokenHeaders = {'Accept': 'application/json'}
    tokenData = {'client_id':id,'client_secret':secret,'code':deviceCodeJson['device_code'],'grant_type':'device_code'}
    tokenJson = requests.post(tokenEndpoint, headers=tokenHeaders, data = tokenData).json()
    config = "{'id':'" + id + "','secret':'" + secret + "','token':'" + tokenJson['access_token'] + "'}"
    configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'npr.conf')
    f=open(configfile,'w+')
    f.write(config)
    print('User logged in and stored locally')
def logout():
    try:
        configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'npr.conf')
        f=open(configfile,'r')
    except:
        print('No config.  User logged out.')
    config = ast.literal_eval(f.read())
    config.pop('token', None)
    conf = json.dumps(config)
    f=open(configfile,'w+')
    f.write(conf)
    print('User logged off.')
def npr():
        print("s = npr.Station('wamu')")
        print("  s.pretty()")
        print("  s.find('88.5')")
        print("  print(s.live())")
        print("a = npr.Search('hidden')")
        print("r = npr.Recommend()")
        print("u = npr.User()")
        print("npr.auth()")
        print("npr.deauth()")
        print("npr.login()")
        print("npr.logout()")