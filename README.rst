NPR
---

Setup:
Begin by authenticating your app.  Auth will walk you through key creation.
Once verified, you must login.

    >>> import npr
    >>> npr.auth()

    >>> npr.login()
	
Go to https://secure.npr.org/device login and enter:
Z3SDM6
When finished, cursor in and press enter:

Example data fetch:

    >>> station = npr.Station('chicago')
    >>> station.live()

'https://stream.wbez.org/wbez128.mp3'

Custom variables:
You can also use a reverse lookup to find the keys to your own variables.

    >>> search = npr.Search('Hidden Brain')
	>>> search.pretty()
	
. . .
	  "audioTitle": "Ep. 64: I'm Right, You're Wrong",
	  "date": "2017-03-13T21:00:19-04:00",
	  "description": "There are some topics
	"items": [],
	"links": {
	  "audio": [
		{
		  "content-type": "audio/mp3",
		  "href": "https://play.podtrac.com/npr-510308...
. . . 

    >>> search.find("Ep. 64: I'm Right, You're Wrong")
Ep. 64: I'm Right, You're Wrong .response['items'][0]['items'][2]['attributes']['audioTitle']

    >>> for episode in search.response['items'][0]['items']:
	...		print(episode['attributes']['audioTitle'])
Ep. 66: Liar, Liar 
Episode 65: Tunnel Vision 
Ep. 64: I'm Right, You're Wrong

Endpoint classes:

npr.Station('query') - returns metadata about an NPR station, where 'query' can be call letters, zip code, city, or any indexed metadata.
npr.Search('query') - returns programs or episode titles with a term that matches your 'query'
npr.User() - returns data (including content preferences) about the logged in user
npr.Recommend() - returns a list of recommended audio for the logged in user.
