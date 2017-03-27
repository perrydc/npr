#app and user authentication functions
import requests,json,re,os,ast,sys
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
