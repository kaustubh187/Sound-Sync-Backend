
from spotipy import Spotify
SPOTIPY_CLIENT_ID = '352a916cc74b412bb072ec99a1298376'
SPOTIPY_CLIENT_SECRET = '24fd5cdfc91c4853bdf6a0a38e5e0901'
from spotipy.oauth2 import SpotifyClientCredentials
import psycopg2

db_connection = {
    "user": "postgres",
    "password": "",
    "host": "localhost",
    "port": "5432",
    "database": "soundsync"
}

def fetch_top_songs(user_id):
    # Connect to the database
    conn = psycopg2.connect(**db_connection)
    cursor = conn.cursor()

    # Query to fetch all songs for the given user_id
    query_song_data = f'SELECT songid FROM sound_data WHERE userid = {user_id};'
    cursor.execute(query_song_data)
    song_ids = [song[0] for song in cursor.fetchall()]

    # Close the database connection
    conn.close()

    # Initialize Spotipy client
    sp = Spotify(client_credentials_manager=SpotifyClientCredentials(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET))

    # Fetch additional information for each song from Spotipy
    top_songs = []
    for song_id in song_ids:
        track_info = sp.track(song_id)
        title = track_info['name']
        album_art_url = track_info['album']['images'][0]['url']  # Assuming the first image for simplicity
        artist_name = track_info['artists'][0]['name']  # Assuming the first artist for simplicity

        # Create a dictionary with song information
        song_info = {
            'id':song_id,
            'title': title,
            'album_art_url': album_art_url,
            'artist_name': artist_name
        }

        top_songs.append(song_info)

    return top_songs
