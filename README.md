# Shazam-Clone-with-automatic-spotify-playlist-integration
This Shazam clone uses the pyaudiowpactch module to record audio from the current output device. It then writes the recorded audio to a file and sends it to the ACR cloud api for recognition. If the song is recognized it adds it to the spotify playlist of the user
# How to use

## Installation
Install all the necessary modules using pip or pip3
## Getting started 
1. Create a Spotify developer account using this URL:https://accounts.spotify.com/nl/login?continue=https%3A%2F%2Faccounts.spotify.com%2Foauth2%2Fv2%2Fauth%3Fresponse_type%3Dnone%26client_id%3Dcfe923b2d660439caf2b557b21f31221%26scope%3Demail%2Bopenid%2Bprofile%2Buser-self-provisioning%26redirect_uri%3Dhttps%253A%252F%252Fdeveloper.spotify.com%252Floggedin%26state%3D3b82e077-070b-4964-a67a-22ffbc174e35 
2.  Create a project and give it a name
3.   Click on edit settings and copy the client ID, client secret, and redirect url into the script. You could also export them as ENV variables 
4.  Authorize the script using this URL: ttps://accounts.spotify.com/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=YOUR_REDIRECT_URI&scope=playlist-modify-public &state=STATE
The response from the url contains a code as one of it's parameters copy the code for later use
5. Make a  POST request with the following parameters:
- grant_type: Set to "authorization_code".
- code: The authorization code obtained from the redirect URI.
- redirect_uri: The same redirect URI used during the authorization flow.
- client_id: Yheir Spotify client ID.
- client_secret: your Spotify client secret.
The response should contain a refresh token. 
Revert the post-request parameters to their original state and copy the refresh token
 6.  Create an ACR cloud music account using this URL: https://console.acrcloud.com/avr?region=eu-west-1#/register 
 7.  Select Audio and video recognition as your bucket and create a project
 8.   Copy the API key and secret into the script as well as the host
 9.   Copy your spotify playlist id by clicking copy link to playlist
 10.   Enjoy!
