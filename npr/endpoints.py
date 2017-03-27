import requests,json,re,os,ast,sys
class Api:
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
