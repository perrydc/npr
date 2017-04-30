NPR
===

This module provides a simple framework for working with NPR's cloud services.

You can install this module via:
	pip install npr

Setup:
------

Begin by authenticating your app.  Auth will walk you through key creation.

    >>> import npr
    >>> npr.auth()

	To authenticate your app:
	  1. LOGIN to http://dev.npr.org (if it's your first time, you'll need to register.)
	  2. Open the dev console (drop down in the top right corner of dev center)
	  3. Create a new application
	  4. Select that application and enter your credentials below
	Application ID:
	Application Secret:

Once verified, you must login. 

    >>> npr.login()
	
	| Go to https://secure.npr.org/device login and enter:
	| Z3SDM6

This will poll the npr auth server every 5 seconds until you login and it gets a token.

Example data fetch:
-------------------

    >>> station = npr.Station('chicago')
    >>> station.live()

	'https://stream.wbez.org/wbez128.mp3'

Custom variables:
-----------------

You can also use a reverse lookup to find the keys to your own variables::

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

To grab more than the last three episodes from this aggregation, you'll need to lookup the affiliate code and pass it to the Agg class:

	>>> hiddenBrain = Agg('510308')
	>>> hiddenBrain.pretty()

Build an NPR One app:
---------------------

This won't help you play audio through a speaker, but it'll get you the data you need.  First, initialize your player:

	>>> player = npr.One()
	
Now pass the title of the story to your display and the story audio to your player, use:

	>>> player.title
	>>> player.audio

To get the next segment, use:

	>>> player.skip()
	
or

	>>> player.complete()
	
...depending on the user action.  Then you call player.audio to play the next segment.

Explore Tab:
------------

The channel endpoint just lets you know what collections are available.  You'll need a distinct call for each row (collection) in the explore tab.  So to initialize the explore object and see all the stories in the third row, use:

	>>> explore = npr.Channels()
	>>> explore.fetch(2)
	>>> explore.row.pretty()

Authentication functions:
-------------------------

	| **npr.auth()** - authenticates your app with your developer credentials from dev.npr.org
	| **npr.login()** - returns a short code your user can enter at secure.npr.org/device, which will deliver a bearer token to your app
	| **npr.logout()** - removes the user's bearer token from your app.  Remember to logout before distributing your app.
	| **npr.deauth()** - removes your developer credentials from the app by deleting the npr.conf file

Endpoint classes:
-----------------

	| **npr.Station('query')** - returns metadata about an NPR station, where 'query' can be call letters, zip code, city, or any indexed metadata.
	| **npr.Station(orgId)** - returns metadata about an NPR station, where 'orgId' is the orgId of the station.
	| **npr.Station(lat,lon)** - returns metadata about an NPR station, lon should be negative, because all our stations are west of the meridian
	| **npr.Search('query')** - returns programs or episode titles with a term that matches your 'query'
	| **npr.User()** - returns data (including content preferences) about the logged in user
	| **npr.Recommend()** - returns a list of recommended audio for the logged in user.
	| **npr.One()** - Like recommend, except you can advance to the next segment via skip() and complete()
	| **npr.Agg()** - returns audio segments from the selected aggregation (aka affiliation)
	| **npr.Channels()** - returns channels from the explore tab, which, along with fetch(row) will also return segments.
	
Endpoint helper functions:
--------------------------

	| **npr.docs()** - Lists example endpoint calls
	| <YOUR OBJECT NAME> **.response** - the json response from the endpoint
	| <YOUR OBJECT NAME> **.pretty()** - prints the json output in human-readable form
	| <YOUR OBJECT NAME> **.find('your json value')** - returns the json key path for the value you entered
	
Full endpoint documentation is available at http://dev.npr.org
