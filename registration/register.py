
from flask import jsonify, redirect,request,session
import psycopg2
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

db_connection = {
    "user": "postgres",
    "password": "root@123",
    "host": "localhost",
    "port": "5432",
    "database": "soundsync"
}
SPOTIPY_CLIENT_ID = '352a916cc74b412bb072ec99a1298376'
SPOTIPY_CLIENT_SECRET = '24fd5cdfc91c4853bdf6a0a38e5e0901'
redirect_uri = "http://localhost:5000/redirect"
SCOPE = 'user-library-read user-top-read'
sp_oauth = SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, redirect_uri, scope=SCOPE)

def signup():
    try:
        # Extract user data from the request
        data = request.json
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        bio = data.get('bio')
        #print("bio: "+bio)
        # Create a database connection
        conn = psycopg2.connect(**db_connection)
        cursor = conn.cursor()

        # Insert user data into the "user" table
        cursor.execute(
            'INSERT INTO "user" (name, email, password, bio) VALUES (%s, %s, %s, %s)',
            (name, email, password, bio)
        )
        
        # Commit the transaction and close the connection
        conn.commit()
        cursor.execute('SELECT * FROM "user" WHERE email = %s', (email,))
        #print("Somethin happn: " + email)
        #result = cursor.fetchone()
        res = cursor.fetchone()
        print(type(res))
        # Set the user_id in the session
        if 'id' not in session:
            session['id']=0
        session['id'] = res[0]
        session.modified = True
        if 'id' in session:
            print("Session Updated: ",session['id'])
        else:
            print("Session not updated")
        
        conn.close()
        spotify_authorization_url = sp_oauth.get_authorize_url()
        return jsonify({"success": True, "spotify_authorization_url": spotify_authorization_url,'session_data':session})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def callback(auth_code):
    # Initialize the Spotify client with the access token
    token_info = sp_oauth.get_access_token(auth_code)
    sp = Spotify(auth=token_info['access_token'])

    # Fetch the user's top 10 tracks
    top_tracks = sp.current_user_top_tracks(limit=10)
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(**db_connection)
    cursor = conn.cursor()
    user_id = 132
    for track in top_tracks['items']:
        # Extract features using Spotipy, e.g., acousticness, instrumentalness, danceability, energy, loudness
        track_feature = sp.audio_features(track['id'])
        if(track_feature):
                track_feature = track_feature[0]
                acousticness = track_feature['acousticness']
                instrumentalness = track_feature['instrumentalness']
                danceability = track_feature['danceability']
                energy = track_feature['energy']
                loudness = track_feature['loudness']
        # Insert the song data into the "sound_data" table
                cursor.execute(
                    'INSERT INTO sound_data (songid, userid, acousticness, instrumentalness, danceability, energy, loudness) VALUES (%s, %s, %s, %s, %s, %s, %s)',
                    (track['id'], user_id, acousticness, instrumentalness, danceability, energy, loudness)
                )

    # Commit the transaction and close the database connection
    #conn.commit()
    conn.close()
    
    return redirect('http://localhost:3000/home')



def login():
    try:
        # Extract user data from the request
        data = request.json
        email = data.get('email').strip() if data.get('email') else None
        password = data.get('password').strip() if data.get('password') else None
        # Create a database connection
        conn = psycopg2.connect(**db_connection)
        cursor = conn.cursor()

        # Check if the user with provided email and password exists
        cursor.execute('SELECT * FROM "user" WHERE email=%s AND password=%s', (email, password))
        user = cursor.fetchone()

        if user:
            # Set session variables
            print("This user iz: ",user[0])
            session['id'] = user[0]
            session['name'] = user[1]

            conn.close()
            return jsonify({"message": "Login successful", "user": {"user_id": user[0], "name": user[1]}}), 200
        else:
            conn.close()
            print("Notfound:",email)
            return jsonify({"error": "Invalid email or password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

