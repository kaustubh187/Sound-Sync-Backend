from flask import request,jsonify
import psycopg2 
from datetime import datetime
import base64
db_connection = {
    "user": "postgres",
    "password": "",
    "host": "localhost",
    "port": "5432",
    "database": "soundsync"
}

def request_follow():
    try:
        # Get sender_id and receiver_id from the request parameters
        data = request.json
        sender_id = data.get('sender_id')
        receiver_id = data.get('receiver_id')
        connection = psycopg2.connect(**db_connection)
        cursor = connection.cursor()
        print("Sender: ",sender_id)
        print("Reciever: ",receiver_id)
        # Insert data into the follow_request_info table
        cursor.execute("""
            INSERT INTO follow_request_info (sender_id, receiver_id, timestamp)
            VALUES (%s, %s, NOW());
        """, (sender_id, receiver_id))

        # Commit the changes and close the connection
        connection.commit()
        cursor.close()
        connection.close()

        return {'status': 'success', 'message': 'Follower added successfully'}
    except ValueError as ve:
        # Handle invalid integer values
        return {'status': 'error', 'message': 'Invalid senderid or receiverid'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def handle_follow_action():
    try:
        # Get action, sender_id, and receiver_id from the request parameters
        print('yipee')
        data = request.json
        action = data.get('action')
        sender_id = data.get('senderid')
        receiver_id = data.get('receiverid')
        # Establish a connection to the database
        connection = psycopg2.connect(**db_connection)
        cursor = connection.cursor()
        if action == 'accept':
            # Insert a new row for the sender -> receiver relationship
            cursor.execute("""
                INSERT INTO follower_info (follower, following, timestamp)
                VALUES (%s, %s, NOW());
            """, (sender_id, receiver_id))

            # Insert a new row for the receiver -> sender relationship
            cursor.execute("""
                INSERT INTO follower_info (follower, following, timestamp)
                VALUES (%s, %s, NOW());
            """, (receiver_id, sender_id))

        # Delete the row from follow_request_info
        cursor.execute("""
            DELETE FROM follow_request_info
            WHERE sender_id = %s AND receiver_id = %s;
        """, (sender_id, receiver_id))

        # Commit the changes and close the connection
        connection.commit()
        cursor.close()
        connection.close()
        response = {'status': 'success', 'message': 'Follow action processed successfully'} 
        return jsonify(response)
    
    except ValueError as ve:
        # Handle invalid data or missing fields
        return jsonify({'status': 'error', 'message': 'Invalid data or missing fields'})
    except Exception as e:
        # Handle other exceptions
        return jsonify({'status': 'error', 'message': str(e)})
    

def fetch_requests():
    try:
        # Get userId from the request parameters
        user_id = int(request.args.get('userId'))
        
        connection = psycopg2.connect(**db_connection)
        cursor = connection.cursor()

        # Fetch all rows from follow_request_info where reciever_id = user_id
        cursor.execute("""
            SELECT fr.sender_id, fr.receiver_id, u.profilepic, u.name
            FROM follow_request_info fr
            JOIN "user" u ON fr.sender_id = u.id
            WHERE fr.receiver_id = %s;
        """, (user_id,))
        print("fetched")
        # Fetch all the results
        rows = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()
        
        # Return the fetched rows as a list of dictionaries
        result = [{'sender_id': row[0], 'receiver_id': row[1], 'profilepic': row[2], 'name': row[3]} for row in rows]
        for entry in result:
            #Check if 'profilepic' is a memoryview
            if isinstance(entry['profilepic'], memoryview):
                # Convert memoryview to base64
                entry['profilepic'] = base64.b64encode(entry['profilepic'].tobytes()).decode('utf-8')

        print("result",result)
        return jsonify({'status': 'success', 'data': result})
    
    except ValueError as ve:
        # Handle invalid integer values
        return jsonify({'status': 'error', 'message': 'Invalid userId'})
    except Exception as e:
        # Handle other exceptions
        return jsonify({'status': 'error', 'message': str(e)})
    
