from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import int
from builtins import input
from builtins import open
from builtins import str
from builtins import object
from future import standard_library
standard_library.install_aliases()
import requests,json,re,os,ast,sys,time,datetime

debug = 1
configfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'npr.conf')
#configfile = 'npr.conf' #dev mode (comment out above) 1.2.0

def fetchConfig():
    if os.path.isfile(configfile):
        f=open(configfile,'r')
        config = ast.literal_eval(f.read())
        if 'id' in config and 'secret' in config:
            if 'token' not in config:
                print('No token.  npr.login() will fetch it for you.')
        else:
            print('app ID and/or app secret is missing.  Try npr.clientauth() or npr.auth()')
        return config
    else:
        print('config file is missing.  Try npr.clientauth() or npr.auth()')
        config = {}
        return config

def promptauth():
    print("To authenticate your app:")
    print("  1. LOGIN to http://dev.npr.org (if it's your first time, you'll need to register.)")
    print("  2. Open the dev console (drop down in the top right corner of dev center)")
    print("  3. Create a new application")
    print("  4. Select that application and enter your credentials below")
    id = input("Application ID:")
    secret = input("Application Secret:")
    return id,secret

def clientauth():
    config = {}
    config['id'], config['secret'] = promptauth()
    tokenEndpoint = 'https://api.npr.org/authorization/v2/token'
    tokenHeaders = {'Accept': 'application/json'}
    tokenData = {'client_id':config['id'],'client_secret':config['secret'],'grant_type':'client_credentials'}
    tokenJson = requests.post(tokenEndpoint, headers=tokenHeaders, data = tokenData).json()
    config['token'] = tokenJson['access_token']
    f=open(configfile,'w+')
    f.write(str(config))
    print(json.dumps(tokenJson, sort_keys=True, indent=2, separators=(',', ': ')))

def auth():
    config = {}
    config['id'],config['secret'] = promptauth()
    f=open(configfile,'w+')
    f.write(str(config))
    print("now type 'npr.login() to login your user'")
    
def deauth():
    os.remove(configfile)
    print('app deauthed')
    
def poll(tokenEndpoint,tokenHeaders,tokenData):
    tokenJson = requests.post(tokenEndpoint, headers=tokenHeaders, data = tokenData).json()
    if 'access_token' in tokenJson:
        config = fetchConfig()
        config['token'] = tokenJson['access_token']
        config['expires_in'] = tokenJson['expires_in']
        config['refresh_token'] = tokenJson['refresh_token']
        f=open(configfile,'w+')
        f.write(str(config))
        print('User logged in and stored locally')
    else:
        time.sleep(5)
        poll(tokenEndpoint,tokenHeaders,tokenData)
        
def login():
    scope = 'identity.readonly identity.write listening.readonly listening.write localactivation'
    deviceCodeEndpoint = 'https://api.npr.org/authorization/v2/device'
    tokenEndpoint = 'https://api.npr.org/authorization/v2/token'
    headers = {'Accept': 'application/json'}
    if os.path.isfile(configfile):
        f=open(configfile,'r')
        config = ast.literal_eval(f.read())
        if 'id' in config and 'secret' in config:
            deviceCodeData = {'client_id':config['id'],'client_secret':config['secret'],'scope':scope}
            deviceCodeJson = requests.post(deviceCodeEndpoint, headers=headers, data = deviceCodeData).json()
            tokenData = {'client_id':config['id'],'client_secret':config['secret'],'code':deviceCodeJson['device_code'],'grant_type':'device_code'}
            print("Go to " + deviceCodeJson['verification_uri'] + " login and enter:")
            print(deviceCodeJson['user_code'])
            poll(tokenEndpoint,headers,tokenData)
        else:
            auth()
    else:
        auth()
           
def logout():
    if os.path.isfile(configfile):
        f=open(configfile,'r')
        config = ast.literal_eval(f.read())
        config.pop('token', None)
        f=open(configfile,'w+')
        f.write(str(config))
        print('User logged off.')
    else:
        print('No config.  User logged out.')

def testr(endpoint,headers):
    response = requests.get(endpoint,headers=headers).json()
    if errors(response) == -1:
        refresh()
        headers = {"Accept":"application/json","Authorization":"Bearer " + config['token']}
        response = requests.get(endpoint,headers=headers).json()
        return response
    elif errors(response) > 0:
        if debug == 1:
            print('To turn off response errors, set npr.debug = 0')
            print(json.dumps(response, sort_keys=True, indent=2, separators=(',', ': ')))
        return response
    else:
        return response

def errors(response):
    c = 0
    if 'errors' in response:
        for error in response['errors']:
            if 'code' in error:
                if bool(re.match(r'^401',str(error['code']))):
                    return -1
                else:
                    c += 1
    return c
        
def refresh():
    f=open(configfile,'r')
    config = ast.literal_eval(f.read())
    if 'refresh_token' in config:
        tokenEndpoint = 'https://api.npr.org/authorization/v2/token'
        tokenHeaders = {'Accept': 'application/json'}
        tokenData = {'client_id':config['id'],'client_secret':config['secret'],'grant_type':'refresh_token','refresh_token':config['refresh_token']}
        tokenJson = requests.post(tokenEndpoint, headers=tokenHeaders, data = tokenData).json()
        config['token'] = tokenJson['access_token']
        config['expires_in'] = tokenJson['expires_in']
        config['refresh_token'] = tokenJson['refresh_token']
        f=open(configfile,'w+')
        f.write(str(config))
        #print('User logged in and stored locally')
    else:
        print('unauthorized.  Try deauth() then auth().')
    
class Api(object):
    def __init__(self):
        self.domain = "https://api.npr.org"
        self.config = fetchConfig()
        self.token = self.config['token']
        self.headers = {"Accept":"application/json","Authorization":"Bearer " + self.token}
        self.a = {}
        
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

class Story(Api):
    def __init__(self, id):
        Api.__init__(self)
        self.endpoint = "https://reading.api.npr.org/v1/news-app/stories/external/" + str(id)
        self.response = testr(self.endpoint, self.headers)
        self.a = self.defineAssets(self.response)
        self.__dict__.update(self.a)

    def defineAssets(self, jsonBlock):
        a = {}
        for resource in jsonBlock['resources']:
            if 'type' in resource and 'value' in resource:
                a.update({resource['type']:resource['value']})
            if resource['type'] == 'slug':
                a.update({'slug':resource['title']})
                a.update({'slugId':resource['externalId']})
            if resource['type'] == 'byline':
                authors = []
                for author in resource['authors']:
                    authors.append(author['title'])
                a.update({'byline':', '.join(authors)})
            if resource['type'] == 'image':
                a.update({'imageAttribution':resource['attribution']})
                a.update({'caption':resource['title']})
                for crop in resource['crops']:
                    if crop['primary'] == True:
                        a.update({'image':crop['href']})
        return a

class Stories(Story):
    def __init__(self, id=0):
        Api.__init__(self)
        if id == 0:
            self.endpoint = "https://reading.api.npr.org/v1/news-app/home"
        else:
            self.endpoint = "https://reading.api.npr.org/v1/news-app/aggregations/external/" + str(id)
            # /v1/news-app/aggregations/{guid}
            # /v1/news-app/aggregations/creator/{guid}/external/{ext-id}
        self.response = testr(self.endpoint, self.headers)
        self.a = self.defineAssets(self.response)
        self.__dict__.update(self.a)
        
    def defineAssets(self, jsonBlock):
        a = {}
        titles = []
        for story in self.response['listItems']:
            titles.append(story['title'])
        a.update({'titles':titles})
        ids = []
        for story in self.response['listItems']:
            ids.append(story['externalId'])
        a.update({'titles':titles, 'ids':ids})
        return a

class User(Api):
    def __init__(self):
        Api.__init__(self)
        self.endpoint = self.domain + "/identity/v2/user"
        self.response = testr(self.endpoint,self.headers)
        self.a = self.defineAssets(self.response)
        self.__dict__.update(self.a)
        
    def defineAssets(self, jsonBlock):
        a = {}
        id = jsonBlock['attributes']['id']
        email = jsonBlock['attributes']['email']
        name = jsonBlock['attributes']['firstName'] + " " + jsonBlock['attributes']['lastName']
        station = jsonBlock['attributes']['organizations'][0]['displayName']
        cohort = jsonBlock['attributes']['cohort']['id']
        a.update({'id':id, 'name':name, 'station':station, 'email':email, 'cohort':cohort})
        return a

class Search(Api):
    def __init__(self, query):
        Api.__init__(self)
        self.endpoint = self.domain + "/listening/v2/search/recommendations?searchTerms=" + query
        self.response = testr(self.endpoint,self.headers)

class Channels(Api):
    def __init__(self, exploreOnly='false'):
        Api.__init__(self)
        self.endpoint = self.domain + "/listening/v2/channels?exploreOnly=" + exploreOnly
        self.response = testr(self.endpoint,self.headers)
    def fetch(self,n):
        self.endpoint = self.response['items'][n]['href']
        self.headers = {"Accept":"application/json","Authorization":"Bearer " + self.token}
        self.row = Recommend(self.endpoint, self.headers)

#    def fetch(self,n):
#        self.endpoint = self.response['items'][n]['href']
#        self.row = Recommend(self.endpoint, self.headers)
        
class Recommend(Api):
    def __init__(self, endpoint, headers):
        self.endpoint = endpoint
        self.response = testr(self.endpoint, headers)
#        self.response = testr(self.endpoint, self.headers)

class Agg(Api):
    def __init__(self, aggId):
        Api.__init__(self)
        self.endpoint = self.domain + "/listening/v2/aggregation/" + aggId + "/recommendations"
        self.response = testr(self.endpoint, self.headers)
        
class Station(Api):
    def __init__(self, query, lon=0):
        Api.__init__(self)
        self.endpoint = self.domain + "/stationfinder/v3/stations/" + str(query)
        self.response = testr(self.endpoint,self.headers)
        #self.streams = self.response['links']['streams']
        self.a = self.defineAssets(self.response)
        self.__dict__.update(self.a)
    
    def unwrap(self, stream):
        if re.search(r'pls$',stream):
            f = requests.get(stream).text
            url = re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',f)
            return url.group(0)
        elif re.search(r'm3u$',stream):
            f = requests.get(stream).text
            url = re.search(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',f)
            return url.group(0)
        else:
            return stream
    
    def defineAssets(self, jsonBlock):
        a = {}
        name = jsonBlock['attributes']['brand']['name']
        id = jsonBlock['attributes']['orgId']
        a.update({'id':id, 'name':name})
        if 'streams' in jsonBlock['links']:
            for stream in jsonBlock['links']['streams']:
                if stream['isPrimaryStream'] and stream['typeId'] == "13":
                    aac = stream['href']
                elif stream['isPrimaryStream'] and stream['typeId'] == "10":
                    mp3 = stream['href']
                    a.update({'mp3': mp3})
            try:
                a.update({'stream': aac})
            except:
                try:
                    a.update({'stream': mp3})
                except:
                    pass
        return a

class Stations(Station):
    def __init__(self, query, lon=0):
        Api.__init__(self)
        if lon != 0:
            self.endpoint = self.domain + "/stationfinder/v3/stations/?lat=" + str(query) + "&lon=" + str(lon)
        else:
            self.endpoint = self.domain + "/stationfinder/v3/stations?q=" + query
        self.response = testr(self.endpoint,self.headers)
        self.a.update({'station':[]})
        for station in self.response['items']:
            self.a['station'].append(self.defineAssets(station))
        #self.a.update(self.defineAssets(self.response['items'][0]))
        self.a.update(self.a['station'][0])
        self.__dict__.update(self.a)

class One(Api):
    def __init__(self):
        Api.__init__(self)
        self.endpoint = self.domain + "/listening/v2/recommendations"
        self.h = self.headers
        self.response = testr(self.endpoint, self.headers)
        self.defineAssets()
        
    def defineAssets(self):
        a = {}
        self.mp3,self.aac = self.getaudio()
        if self.aac != "":
            audio = self.aac
        else:
            audio = self.mp3
        title = self.response['items'][0]['attributes']['title']
        self.start = datetime.datetime.utcnow()
        self.post = {
            'mediaId':self.response['items'][0]['attributes']['rating']['mediaId'],
            'origin':self.response['items'][0]['attributes']['rating']['origin'],
            'duration':self.response['items'][0]['attributes']['duration'],
            'channel':self.response['items'][0]['attributes']['rating']['channel'],
            'cohort':self.response['items'][0]['attributes']['rating']['cohort']
        }
        #id = jsonBlock['attributes']['id']
        a.update({'title':title, 'audio':audio})
        self.__dict__.update(a)
        self.a = a
        
    def getaudio(self):
        aac = ""
        mp3 = ""
        for audio in self.response['items'][0]['links']['audio']:
         if audio['content-type'] == "audio/aac":
          aac = audio['href']
         if audio['content-type'] == "audio/mp3" and 'rel' not in audio:
          mp3 = audio['href']
        return mp3,aac

    def postTime(self):
        timestamp = datetime.datetime.utcnow()
        elapsed = int((timestamp - self.start).total_seconds())
        self.post.update({'timestamp':timestamp.strftime('%Y-%m-%dT%H:%M:%S%z')})
        self.post.update({'elapsed':elapsed})
    def advancePlayer(self):
        self.postTime()
        self.endpoint = self.response['items'][0]['links']['recommendations'][0]['href']
        self.data = json.dumps([self.post])
        self.response = requests.post(self.endpoint, headers=self.h, data=self.data).json()
        self.defineAssets()    
    def skip(self):
        self.post.update({'rating':'SKIP'})
        self.advancePlayer()
    def complete(self):
        self.post.update({'rating':'COMPLETED'})
        self.advancePlayer()

def docs():
    docs = """station = npr.Station(305) # lookup station by orgId
station.a # quick-reference of variables in namespace
station.unwrap(station.stream) # some streams need to be unwrapped for use by FFMPEG
station.pretty() # print raw api response
s.find('88.5') # reverse lookup response keys by value

stations = npr.Stations(38.9072,-77.0369) # npr.Stations('22205') | npr.Stations('WAMU')
stations.station[0]['name'] # example of quick-reference across a list

story = npr.Story(565664321) # lookup story by id
story.title

stories = npr.Stories() # lookup top stories
stories.titles

user = npr.User() # data on the logged in user

player = npr.One() # create a NPR One player object
player.skip() # player.complete()

query = npr.Search('hidden')

hiddenBrain = npr.Agg('510308') # the aggId is listed as the 'affiliation' in search
hiddenBrain.pretty()

explore = npr.Channels()
explore.fetch(2) - fetch segments from third row of explore list
explore.row.pretty()

npr.clientauth()
npr.auth()
npr.deauth()
npr.login()
npr.logout()"""
    print(docs)