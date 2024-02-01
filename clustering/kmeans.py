
import psycopg2
from spotipy import Spotify
import spotipy
import re
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from psycopg2.extras import execute_values
import pandas as pd

db_connection = {
    "user": "postgres",
    "password": "",
    "host": "localhost",
    "port": "5432",
    "database": "soundsync"
}
# First fetch all the possible user ids 
# Fetch songs for each user id 
# Create a basic dataframe with song 1 features, song 2 .... 
# Apply K means clustering 
# Store user and their cluster labels 
def clusterize():
    conn = psycopg2.connect(**db_connection)   
    cursor = conn.cursor()
    query = 'SELECT DISTINCT id FROM "user" ORDER BY id ASC;'
    cursor.execute(query)

    # Fetch all the results
    unique_user_ids = cursor.fetchall()
    user_ids = []
    # Store the results
    for user_id in unique_user_ids:
        user_ids.append(user_id[0])

    data = []

    # Fetch 5 songs for each user ID
    for user_id in user_ids:
        query = f"SELECT * FROM sound_data WHERE userid = {user_id} LIMIT 5;"
        cursor.execute(query)

        # Fetch all the results for the current user_id
        songs_for_user = cursor.fetchall()
        user_features={}
        user_features["User ID"] = f"{user_id}"
        
        # Process the results and extract relevant features
        for idx, song in enumerate(songs_for_user):
            user_features[f"Song{idx + 1}_acousticness"] = song[2]  # Assuming acousticness is the third column (index 2)
            user_features[f"Song{idx + 1}_instrumentalness"] = song[3]
            user_features[f"Song{idx + 1}_danceability"] = song[4]
            user_features[f"Song{idx + 1}_energy"] = song[5]
            user_features[f"Song{idx + 1}_loudness"] = song[6]
        data.append(user_features)
    #Create a dataframe for the user wise data
    df = pd.DataFrame(data)

    features = df.columns[1:]  # Exclude the 'User' column
    X = df[features]  # Drop the "User" column
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Create a PCA instance
    pca = PCA()

    # Fit PCA on the standardized data
    pca.fit(X_scaled)

    
    # Transform the data to the reduced-dimensional space
    # For example, to reduce to 2 principal components
    X_pca = pca.transform(X_scaled)

    
    # Create a K-Means instance with the desired number of clusters (e.g., 3 clusters)
    num_clusters = 6  # You can choose the number of clusters based on your problem
    kmeans = KMeans(n_clusters=num_clusters)

    # Fit K-Means on the reduced data
    kmeans.fit(X_pca)
    schema_name = 'clusters'
    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")

    # Drop the existing table if it exists
    cursor.execute(f"DROP TABLE IF EXISTS {schema_name}.cluster_centers;")
    
    # Create the cluster_centers table
    create_table_query = f"""
        CREATE TABLE {schema_name}.cluster_centers (
            cluster_label INTEGER PRIMARY KEY,
            {", ".join([f"feature_{i} FLOAT" for i in range(X_pca.shape[1])])}
        );
    """
    cursor.execute(create_table_query)

    # Insert cluster centers into the table
    insert_query = f"""
        INSERT INTO {schema_name}.cluster_centers (cluster_label, {", ".join([f"feature_{i}" for i in range(X_pca.shape[1])])})
        VALUES %s;
    """
    execute_values(cursor, insert_query, [(label,) + tuple(center) for label, center in enumerate(kmeans.cluster_centers_)])

    # Get cluster labels for each data point
    cluster_labels = kmeans.labels_
    cursor.execute("DROP TABLE IF EXISTS user_clusters;")
    selected_columns = ['User ID', 'Cluster_Labels']
    df_selected = df[selected_columns]
    # Create the table 
    create_table_query = """
        CREATE TABLE user_clusters (
            user_id INTEGER PRIMARY KEY,
            cluster_label INTEGER
        );
    """
    cursor.execute(create_table_query)

    # Insert data into the table
    insert_query = """
        INSERT INTO user_clusters (user_id, cluster_label)
        VALUES %s;
    """

    # Execute the insert query
    execute_values(cursor, insert_query, df_selected.to_numpy())

    # Commit changes and close the connection
    
    # Add cluster labels back to your original DataFrame
    df['Cluster_Labels'] = cluster_labels

    cursor.execute("DROP TABLE IF EXISTS user_clusters;")
    selected_columns = ['User ID', 'Cluster_Labels']
    df_selected = df[selected_columns]
    # Create the table
    create_table_query = """
        CREATE TABLE user_clusters (
            user_id INTEGER PRIMARY KEY,
            cluster_label INTEGER
        );
    """
    cursor.execute(create_table_query)

    # Insert data into the table
    insert_query = """
        INSERT INTO user_clusters (user_id, cluster_label)
        VALUES %s;
    """

    # Execute the insert query
    execute_values(cursor, insert_query, df_selected.to_numpy())

    # Commit changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()


