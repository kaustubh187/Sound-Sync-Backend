from flask import request,jsonify
import psycopg2

db_connection = {
    "user": "postgres",
    "password": "root@123",
    "host": "localhost",
    "port": "5432",
    "database": "soundsync"
}


def like_post():
    data = request.json
    userid = data.get('userid')
    parentid = data.get('parentid')
    with psycopg2.connect(**db_connection) as conn:
        with conn.cursor() as cursor:
                # Insert a new row into the likes table
            cursor.execute("INSERT INTO likes(type, parentid, userid) VALUES (%s, %s, %s);", ('post', parentid, userid))

            # Increment the like_count in the post table
            cursor.execute("UPDATE post SET like_count = like_count + 1 WHERE postid = %s;", (parentid,))

            # Commit the changes
            conn.commit()
    return jsonify({'status': 'success'})
    
def remove_like():
    data = request.json
    userid = data.get('userid')
    parentid = data.get('parentid')
    
    with psycopg2.connect(**db_connection) as conn:
            with conn.cursor() as cursor:
                # Delete the like from the likes table
                cursor.execute("DELETE FROM likes WHERE type = %s AND parentid = %s AND userid = %s;", ('post', parentid, userid))

                # Decrement the like_count in the post table
                cursor.execute("UPDATE post SET like_count = like_count - 1 WHERE postid = %s AND like_count > 0;", (parentid,))

                # Commit the changes
                conn.commit()
    return jsonify({'status': 'success'})