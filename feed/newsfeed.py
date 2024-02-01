import psycopg2
from datetime import datetime
from flask import session,request,jsonify
import base64
db_connection = {
    "user": "postgres",
    "password": "root@123",
    "host": "localhost",
    "port": "5432",
    "database": "soundsync"
}

def feed(userid):
    
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_connection)

# Create a cursor object
        cursor = conn.cursor()

        # Fetch userids the given userid is following
        print("User id: ", userid)
        cursor.execute("SELECT following FROM follower_info WHERE follower = %s", (userid,))
        following_userids = [row[0] for row in cursor.fetchall()]
        following_userids.append(userid)
        print(following_userids)

        # Fetch posts from users that the given userid is following
        posts = []
        for following_userid in following_userids:
            cursor.execute('SELECT post.*, "user"."profilepic" FROM post JOIN "user" ON post.authorid = "user"."id" WHERE post.authorid = %s', (following_userid,))
            posts.extend(cursor.fetchall())

        # Order the list of posts by timestamp (newest posts first)
        posts.sort(key=lambda x: x[2], reverse=True)
        # Convert the list of posts to a list of dictionaries
        post_list = [{'postid': post[0], 'authorid': post[1], 'timestamp': post[2], 'text': post[3], 'image': post[4], 'type': post[5],'name':post[6],'profile_pic':post[10],'comment_count':post[7],'like_count':post[8],'have_liked':post[9]} for post in posts]
        
        for post in post_list:
            cursor.execute('SELECT userid FROM likes WHERE parentid = %s AND userid = %s', (post['postid'], userid))
            like_row = cursor.fetchone()
            
            post['have_liked'] = like_row is not None
            post_image_data = post['image']
            profile_image_data=post['profile_pic']
            
            if post_image_data:
                post['image'] = base64.b64encode(post_image_data).decode('utf-8')
            if isinstance(profile_image_data, memoryview):
                post['profile_pic'] = base64.b64encode(profile_image_data.tobytes()).decode('utf-8')
        conn.close()
        cursor.close()
        
        return post_list

    except Exception as e:
        print("Error:", e)
        return None

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def image_to_bytea(image_data):
    try:
        return image_data.read()

    except Exception as e:
        print("Error:", e)
        return None
def profile_feed(userid):
    
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_connection)

# Create a cursor object
        cursor = conn.cursor()

        # Fetch userids the given userid is following
        print("User id: ", userid)
        
        # Fetch posts from users that the given userid is following
        posts = []
        
        cursor.execute('SELECT post.*, "user"."profilepic" FROM post JOIN "user" ON post.authorid = "user"."id" WHERE post.authorid = %s', (userid,))
        posts.extend(cursor.fetchall())

        # Order the list of posts by timestamp (newest posts first)
        posts.sort(key=lambda x: x[2], reverse=True)
        print("posopopts: ",posts)
        
        # Convert the list of posts to a list of dictionaries
        post_list = [{'postid': post[0], 'authorid': post[1], 'timestamp': post[2], 'text': post[3], 'image': post[4], 'type': post[5],'name':post[6],'profile_pic':post[10],'comment_count':post[7],'like_count':post[8],'have_liked':post[9]} for post in posts]
        
        for post in post_list:
            cursor.execute('SELECT userid FROM likes WHERE parentid = %s AND userid = %s', (post['postid'], userid))
            like_row = cursor.fetchone()
            post['have_liked'] = like_row is not None
            post_image_data = post['image']
            profile_image_data=post['profile_pic']
            if post_image_data:
                post['image'] = base64.b64encode(post_image_data).decode('utf-8')
            if isinstance(profile_image_data, memoryview):
                post['profile_pic'] = base64.b64encode(profile_image_data.tobytes()).decode('utf-8')
        #print("posts: ",post_list)
        conn.close()
        cursor.close()
        
        return post_list
    except psycopg2.Error as e:
        # Log the error for debugging purposes
        print("Postgres Error:", e)

        # Check the error code to determine the type of error
        if e.pgcode == '23505':
            # Integrity violation (e.g., unique constraint violation)
            return {'error': 'Integrity violation. Duplicate key.'}, 400
        elif e.pgcode == '23503':
            # Foreign key violation
            return {'error': 'Foreign key violation.'}, 400
        else:
            # General database error
            return {'error': 'Database error.'}, 500

    except Exception as e:
        # Log the general exception for debugging purposes
        print("Error:", e)

        # Return a generic error response
        return {'error': 'An unexpected error occurred.'}, 500

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def make_post():
    try:
        # Extract data from the POS
        authorid = request.form.get('authorid')
        text = request.form.get('thoughts')
        image_data = request.files.get('selectedImage')
        print('heju')
        
        # Establish a connection to the database
        connection = psycopg2.connect(**db_connection)
        cursor = connection.cursor()
        types='text'
        if image_data:
            image = image_to_bytea(image_data)
            types = 'image'
        # Insert data into the post table
        query = """
            INSERT INTO post (authorid, timestamp, text, image, type, authorname, comment_count, like_count, haveliked)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute('SELECT name FROM "user" WHERE id = %s', (authorid,))
        authorname = cursor.fetchone()[0]
        # Use current timestamp for the 'timestamp' field
        timestamp = datetime.now()
        # Execute the query
        if(types=='image'):
            cursor.execute(query, (authorid, timestamp, text, image, types, authorname, 0, 0, False))
        else:
            cursor.execute(query, (authorid, timestamp, text, None, types, authorname, 0, 0, False))
            
        # Commit changes and close the database connection
        connection.commit()
        connection.close()

        return jsonify({"message": "Post successfully created"}), 201

    except Exception as e:
        # Handle exceptions appropriately
        return jsonify({"error": str(e)}), 500

def profile_data(userid):
    try:
        query = 'SELECT name, profilepic FROM "user" WHERE id=%s'
        connection = psycopg2.connect(**db_connection)
        cursor = connection.cursor()
        cursor.execute(query, (userid,))
        response = cursor.fetchone()
        cursor.close()
        connection.close()

        if response is not None:
            name = response[0]
            profile_pic = response[1]
            data = {}
            data['name'] = name
            if isinstance(profile_pic, memoryview):
                data['profilepic'] = base64.b64encode(response[1].tobytes()).decode('utf-8')
            else:
                data['profilepic'] = None
            
            return (data)
        else:
            return jsonify({'error': f'User with ID {userid} not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

