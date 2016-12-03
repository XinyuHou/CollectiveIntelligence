import pylast

API_KEY = "aecd01ba8736c26a6fba924a0a085d85" # this is a sample key
API_SECRET = "0ac7fd8e9a7e4d9a8816a97c1288c271"

network = pylast.LastFMNetwork(api_key = API_KEY, api_secret =
    API_SECRET, username = 'XinyuHou', password_hash = '3ad4d90ad3635223d99d4499f81a8763')

def getTopArtists() :
	
	artists = network.get_top_artists()
	print artists