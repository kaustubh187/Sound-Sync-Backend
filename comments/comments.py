from flask import request,jsonify
import psycopg2
import base64
from datetime import datetime


db_connection = {
    "user": "postgres",
    "password": "",
    "host": "localhost",
    "port": "5432",
    "database": "soundsync"
}




def add_comment():
    try:
        data = request.get_json()
        text = data.get('text')
        authorid = data.get('authorid')
        parentid = data.get('parentid')
        comment_type = data.get('ctype')
        connection = psycopg2.connect(**db_connection)
        cursor = connection.cursor()

        # Get the current timestamp
        timestamp = datetime.utcnow()

        # Insert data into the comments table
        cursor.execute("""
            INSERT INTO comments (commentid, type, parentid, text, timestamp, authorid)
            VALUES (DEFAULT, %s, %s, %s, %s, %s)
        """, (comment_type, parentid, text, timestamp, authorid))

        # Increment the comment_count in the post table
        cursor.execute("""
            UPDATE post
            SET comment_count = comment_count + 1
            WHERE postid = %s
        """, (parentid,))

        # Commit the changes and close the connection
        connection.commit()
        cursor.close()
        connection.close()

        return 'Comment added successfully'
    except Exception as e:
        # Handle exceptions appropriately
        print('Error:', str(e))
        return 'Error adding comment'


def fetch_comment():
    try:
        # Fetch parentid from the request
        parentid = request.args.get('parentid')
        connection = psycopg2.connect(**db_connection)
        cursor = connection.cursor()

        # Fetch comments and user details based on parentid
        cursor.execute("""
            SELECT c.commentid, c.type, c.text, c.timestamp, c.authorid, u.name, u.profilepic
            FROM comments c
            JOIN "user" u ON c.authorid = u."id"
            WHERE c.parentid = %s
        """, (parentid,))

        # Fetch all the rows
        comments_data = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()
        comments = []
        for comment in comments_data:
            comment_id, comment_type, text, timestamp, author_id, author_name, author_profilepic = comment
            if isinstance(author_profilepic, memoryview):
                # Convert memoryview to bytes and encode in base64
                author_profilepic = base64.b64encode(author_profilepic.tobytes()).decode('utf-8')

            comments.append({
                'commentid': comment_id,
                'type': comment_type,
                'name': author_name,
                'text': text,
                'profilepic': author_profilepic,
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })

        return jsonify(comments)
    except Exception as e:
        # Handle exceptions appropriately
        print('Error:', str(e))
        return 'Error fetching comments'
    

