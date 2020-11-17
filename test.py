import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyPKCE

from pprint import pprint
import urllib.request
import numpy as np
import matplotlib.pyplot as plt

import os
import cv2

# use unverified ssl for urllib :/
import ssl
ssl._create_default_https_context = ssl._create_unverified_context


client_id = "CLIENT_ID"
client_secret = "CLIENT_SECRET"

redirect_uri = "http://example.com"

OAUTH_AUTHORIZE_URL= 'https://accounts.spotify.com/authorize'
OAUTH_TOKEN_URL= 'https://accounts.spotify.com/api/token'

def url_to_image(url):
	#Download image and turn into Numpy array
	resp = urllib.request.urlopen(url)
	image = np.asarray(bytearray(resp.read()), dtype='uint8') 
	image = cv2.imdecode(image, cv2.IMREAD_COLOR)

	return image


# Witout user authentication 
#sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

#With user authentication 
# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret,redirect_uri=redirect_uri,scope="user-library-read"))

# results = sp.current_user_saved_tracks()
# for idx, item in enumerate(results['items']):
#    track = item['track']
#    print(idx, track['artists'][0]['name'], " – ", track['name'])

#Set scope to enable read/write playback state 
scope = "user-read-playback-state,user-modify-playback-state, user-library-read"

#With user authentication 
sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret,redirect_uri=redirect_uri,scope=scope))

#sp = spotipy.Spotify(client_credentials_manager=SpotifyPKCE(client_id=client_id, client_secret=client_secret,redirect_uri=redirect_uri,scope=scope))
old_name = " "
run = 1;
while run:
	track = sp.current_user_playing_track()

	#Check to see if the session is running 
	if track!= None:
		
		#Check to see if the track item is avaliable (AKA don't run on podcasts,ads, etc)
		if track['item'] != None:

			name = track['item']['artists'][0]['name']+ " – "+track['item']['name']

			#Only update when song changes 
			if(name != old_name):

				old_name = name
				print(name)

				image_url = track['item']['album']['images'][0]['url']
				image =url_to_image(track['item']['album']['images'][0]['url'])

		
				img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

				rows = len(img)
				cols = len(img[0])

				lum = np.array([0.3, 0.59, 0.11])

				luminance = np.reshape(img, (rows*cols, 3))

				#Dot product every pixel with lum to find the luminance 
				luminance_img = np.dot(luminance, lum)

				#Record max luminantion
				max_lum = np.amax(luminance_img)
				
				#set everytimg below 100 to 0 and above 100 to 1
				luminance_img = np.where(luminance_img < 100, 0, 1)
				luminance_img = np.reshape(luminance_img, (rows, cols))

				#Find the number of pixels that are not clipped
				num_coloured_pixels = np.count_nonzero(luminance_img)

				#dark clipped = 1d array of rgb without "dark" pixels
				dark_clipped = np.zeros((num_coloured_pixels, 3))
				index = 0

				for i in range(rows):
					for j in range(cols):
						if(luminance_img[i][j] != 0):
							dark_clipped[index] = img[i][j]
							index += 1
						

				#True colour average 
				average = img.mean(axis=0).mean(axis=0)
				avg_patch = np.ones(shape=img.shape, dtype=np.uint8)*np.uint8(average)


				#K-Means to find dominant colors  
				pixels = np.float32(dark_clipped)

				n_colors = 5
				criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
				flags = cv2.KMEANS_RANDOM_CENTERS

				_, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
				_, counts = np.unique(labels, return_counts=True)

				dominant = palette[np.argmax(counts)]

				indices = np.argsort(counts)[::-1]   
				freqs = np.cumsum(np.hstack([[0], counts[indices]/float(counts.sum())]))
				rows = np.int_(img.shape[0]*freqs)

				dom_patch = np.zeros(shape=img.shape, dtype=np.uint8)
				for i in range(len(rows) - 1):
					dom_patch[rows[i]:rows[i + 1], :, :] += np.uint8(palette[indices[i]])

				#Stack all images for now 

				# numpy_horizontal = np.hstack((img,avg_patch,dom_patch))

				# plt.ion()
				# plt.show()
				# plt.imshow(numpy_horizontal)
				# plt.pause(0.01)

				red = int(dominant[0])
				green = int(dominant[1])
				blue = int(dominant[2])

				print(dominant)
				urllib.request.urlopen("http://192.168.1.120/colour?r=" + str(red) + "&g="+str(green)+"&b="+str(blue))











			
		

