from flask import Flask, abort,jsonify,request,redirect,session
from flask_session import Session
import psycopg2
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from registration.register import signup,callback,sp_oauth,login
from clustering.recommendations import recommend,fetch_suggestions
from flask_cors import CORS
from feed.newsfeed import feed,make_post,profile_feed,profile_data
from follow.follow import request_follow,handle_follow_action,fetch_requests
from likes.likes import like_post,remove_like
from comments.comments import add_comment,fetch_comment
from spotify_data.top_song import fetch_top_songs
app = Flask(__name__)
app.secret_key = "232234dfs2"
CORS(app) 
CORS(app, supports_credentials=True)  # Enable CORS with support for credentials

db_connection = {
    "user": "postgres",
    "password": "",
    "host": "localhost",
    "port": "5432",
    "database": "soundsync"
}
# Configure the session to use server-side session storage
app.config['SESSION_TYPE'] = 'filesystem' 
Session(app)
app.config['SESSION_COOKIE_SECURE']=True
app.config['SESSION_COOKIE_SAMESITE'] = "None"

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/signup', methods=['POST'])
def register():
    return signup()

@app.route('/spotify_login')
def spotify_login():  
    # Redirect the user to Spotify OAuth for authorization
    response = redirect(sp_oauth.get_authorize_url())
    response.headers['Access-Control-Allow-Origin'] = '*'  # Set the appropriate origin(s) or use a variable
    return response


@app.route('/redirect')
def spotify_redirect():
    auth_code = request.args.get('code')
    if 'id' in session: 
        print('ID: ',session['id'])
    else:
        print("session didnt work until here")
    return callback(auth_code)


@app.route('/recommend/<user_id>')
def recommend_users(user_id):
    return recommend(user_id=user_id)

@app.route('/login',methods=['POST'])
def direct_login():
    data = request.json
    print("Email", data['email'])
    return login()



@app.route('/newsfeed/<userid>',methods=['GET'])
def newsfeed(userid):
    posts = feed(userid)
    if not posts:
        # If the list is empty, return a 401 Unauthorized status
        print("No posts found")
        #abort(401, description="No data available")

    response = jsonify(posts)

    # Set CORS headers
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'  # Set the appropriate origin
    response.headers['Access-Control-Allow-Credentials'] = 'true' # Set the appropriate origin(s) or use a variable
    return response

@app.route('/profilefeed/<userid>',methods=['GET'])
def profilefeed(userid):
    posts = profile_feed(userid)
    if not posts:
        # If the list is empty, return a 401 Unauthorized status
        abort(401, description="No data available")

    response = jsonify(posts)
    # Set CORS headers
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'  # Set the appropriate origin
    response.headers['Access-Control-Allow-Credentials'] = 'true' # Set the appropriate origin(s) or use a variable
    return response

@app.route('/suggestions/<userid>',methods=['GET'])
def suggestions(userid):
    suggested_users = fetch_suggestions(userid)
    if not suggested_users:
        print('no users')
        abort(401, description="No data available")
    response = jsonify(suggested_users)

    # Set CORS headers
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'  # Set the appropriate origin
    response.headers['Access-Control-Allow-Credentials'] = 'true' # Set the appropriate origin(s) or use a variable
    #print("i was about to though")
    return response


@app.route('/isAuthenticated',methods=['GET'])
def checkAuth():
    print('Session Contents:', session)

    if 'id' in session: 
        print('id: ',session['id'])
        return jsonify({'authenticated': True}), 200
    else:
        print("junk")
        return jsonify({'authenticated': False}), 401 
    
@app.route('/create_post',methods=['POST'])
def create_post():
    return make_post()

@app.route('/create_comment',methods=['POST'])
def create_comment():
    return add_comment()

@app.route('/fetch_comments',methods=['GET'])
def fetch_comms():
    return fetch_comment()

@app.route('/follow_request',methods=['POST'])
def follow_request():
    return request_follow()

@app.route('/follow_action',methods=['POST'])
def follow_action():
    return handle_follow_action()

@app.route('/fetch_follow_requests',methods=['GET'])
def fetch_follow():
    print("called!")
    
    return fetch_requests()

@app.route('/like',methods=['POST'])
def add_like():
    return like_post()

@app.route('/unlike',methods=['POST'])
def unlike():
    return remove_like()

@app.route('/fetch_top_songs/<userId>',methods=['GET'])
def fetch_songs(userId):
    songs = fetch_top_songs(userId)
    if not songs:
        abort(401, description="No data available")
    response = jsonify(songs)
    #print("i was about to though: ",posts)
    # Set CORS headers
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'  # Set the appropriate origin
    response.headers['Access-Control-Allow-Credentials'] = 'true' # Set the appropriate origin(s) or use a variable
    return response

@app.route('/profile_data/<userid>',methods=['GET'])
def fetch_profile_data(userid):
    data = profile_data(userid)
    return jsonify(data)



app.run(debug=True)
