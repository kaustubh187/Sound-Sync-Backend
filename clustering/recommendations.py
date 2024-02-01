from sklearn.metrics.pairwise import cosine_similarity
import psycopg2
import pandas as pd
import base64
db_connection = {
    "user": "postgres",
    "password": "root@123",
    "host": "localhost",
    "port": "5432",
    "database": "soundsync"
}
#Returns a list of user_ids most similar

def recommend(user_id):
    conn = psycopg2.connect(**db_connection)
    cursor = conn.cursor()

    # Fetch the users that the current user is already following
    query_following = f'''
    SELECT following
    FROM follower_info
    WHERE follower = {user_id}
    UNION
    SELECT receiver_id
    FROM follow_request_info
    WHERE sender_id = {user_id};
'''
    cursor.execute(query_following)
    users_already_followed = [user[0] for user in cursor.fetchall()]

    query_cluster_label = f'SELECT cluster_label FROM user_clusters WHERE user_id = {user_id};'
    cursor.execute(query_cluster_label)
    cluster_label = cursor.fetchone()[0]

    # Fetch all users within the same cluster
    query_cluster_users = f'SELECT user_id FROM user_clusters WHERE cluster_label = {cluster_label} AND user_id != {user_id};'
    cursor.execute(query_cluster_users)
    users_in_cluster = [user[0] for user in cursor.fetchall()]

    query_cluster_centers = f'SELECT * FROM cluster_centers;'
    cursor.execute(query_cluster_centers)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    # Create a DataFrame using the extracted rows and columns
    cluster_centers = pd.DataFrame(rows, columns=columns)
    cluster_centers_without_target = cluster_centers[cluster_centers['cluster_label'] != cluster_label]

    # Get the features for the target cluster
    target_cluster_features = cluster_centers[cluster_centers['cluster_label'] == cluster_label].iloc[:, 1:]

    # Calculate cosine similarity with the remaining clusters
    similarity = cosine_similarity(cluster_centers_without_target.iloc[:, 1:], target_cluster_features)
    cluster_ordering = similarity.sum(axis=1).argsort()[::-1]
    recommended_users = []

    # Add users from the current cluster, excluding those already followed
    recommended_users.extend([user for user in users_in_cluster if user not in users_already_followed])

    if len(recommended_users) >= 5:
        return recommended_users[:5]

    for cluster_index in cluster_ordering:
        cluster_label = cluster_centers_without_target.iloc[cluster_index]['cluster_label']

        # Fetch users from the current cluster
        query_cluster_users = f'SELECT user_id FROM user_clusters WHERE cluster_label = {cluster_label};'
        cursor.execute(query_cluster_users)
        cluster_users = [user[0] for user in cursor.fetchall()]

        # Add users to the recommended list, excluding those already followed
        recommended_users.extend([user for user in cluster_users if user not in users_already_followed])

        # Break if we have enough users
        if len(recommended_users) >= 5:
            break

    conn.close()
    return recommended_users[:5]


def fetch_suggestions(user_id):
    user_ids = recommend(user_id)
    connection = psycopg2.connect(**db_connection)
    cursor = connection.cursor()

    # Placeholder query for illustration purposes (replace with your actual query)
    query = 'SELECT id, name, profilepic,bio FROM "user" WHERE id IN %s'

    # Execute the query
    cursor.execute(query, (tuple(user_ids),))

    # Fetch the results
    results = cursor.fetchall()

    # Close the database connection
    connection.close()

    # Arrange the results in a list of dictionaries
    user_data_list = []
    for result in results:
        profile_image_data=result[2]
        nudata = ''
        if isinstance(profile_image_data, memoryview):
                nudata = base64.b64encode(profile_image_data.tobytes()).decode('utf-8')
        user_data_list.append({
            'id': result[0],
            'name': result[1],
            'profilepic': nudata,
            'bio':result[3]
        })

    return user_data_list