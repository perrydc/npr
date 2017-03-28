NPR
===

This module provides a simple framework for working with NPR's cloud services.
| If you're new to python, the simplist way to get started is to install anaconda
on your computer (https://www.continuum.io/downloads) and open a new notebook in
Jupyter notebooks (included in the anaconda package).  
|You can then install this module via:
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

Once verified, you must login.

    >>> npr.login()
	
	| Go to https://secure.npr.org/device login and enter:
	| Z3SDM6
	| When finished, cursor in and press enter:

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

Authentication functions:
-------------------------

	| **npr.auth()** - authenticates your app with your developer credentials from dev.npr.org
	| **npr.login()** - returns a short code your user can enter at secure.npr.org/device, which will deliver a bearer token to your app
	| **npr.logout()** - removes the user's bearer token from your app.  Remember to logout before distributing your app.
	| **npr.deauth()** - removes your developer credentials from the app by deleting the npr.conf file

Endpoint classes:
-----------------

	| **npr.Station('query')** - returns metadata about an NPR station, where 'query' can be call letters, zip code, city, or any indexed metadata.
	| **npr.Search('query')** - returns programs or episode titles with a term that matches your 'query'
	| **npr.User()** - returns data (including content preferences) about the logged in user
	| **npr.Recommend()** - returns a list of recommended audio for the logged in user.

Endpoint helper functions:
--------------------------

	| <YOUR OBJECT NAME> **.response** - the json response from the endpoint
	| <YOUR OBJECT NAME> **.pretty()** - prints the json output in human-readable form
	| <YOUR OBJECT NAME> **.find('your json value')** - returns the json key path for the value you entered
	
Full endpoint documentation is available at http://dev.npr.org