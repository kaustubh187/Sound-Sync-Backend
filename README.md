## SoundSync: Where Music Connects friends
This project is a social media platform that recommends friends based on users' Spotify listening data. By analyzing the top tracks of each user and clustering similar music preferences, the system helps users discover others with similar music tastes. This application leverages Spotify's API to retrieve listening trends and extract key audio features from a user's most-listened songs.

# Overview
The system works by retrieving the top 5 most-played songs for each user from Spotify. It then extracts five key audio features for each track:

- Acousticness
- Instrumentalness
- Danceability
- Energy
- Loudness
These features generate a 25-feature matrix (5 songs × 5 features) that represents each user.

# Key Components
1. **OAuth2 Authentication**
The project uses OAuth2 to authenticate users and access their Spotify data. After authentication, it retrieves the top tracks for each user via the Spotify API.

2. **Data Extraction**
For each user's top 5 tracks, the project extracts a range of audio features using the Spotify API. These features are stored in a PostgreSQL database for further analysis.

3. **Clustering with K-Means**
To group users with similar musical tastes, the project performs clustering using K-Means. Each user is represented as a 25-dimensional feature vector (corresponding to the 5 audio features for each of their 5 top tracks). Principal Component Analysis (PCA) is applied to reduce dimensionality, simplifying the clustering process.

4. **User Recommendations**
After clustering, the system recommends users to each other based on their proximity in feature space. Users within the same cluster are considered to have similar music preferences and are suggested as potential friends.

# Flowchart
![image](https://github.com/user-attachments/assets/b0fcc830-a59e-4e80-baec-cceccfe44a75)

# Database Structure
**sound_data**: Stores each user's song details and their respective audio features.
**user_clusters**: Maps each user to a cluster based on the K-Means clustering results, grouping users with similar music tastes.
**cluster_centers**: Stores the centroid values of each cluster, useful for analysis and visualization.

# Processing Flow
**Data Collection**: After authenticating the user via OAuth, the system fetches their top tracks from Spotify and extracts relevant audio features.

**Feature Extraction**: The extracted audio features (acousticness, instrumentalness, etc.) are stored in the database for each user and track.

**Clustering**: A K-Means clustering algorithm is applied to the 25-dimensional feature vectors. Before clustering, PCA reduces the dimensionality for more efficient computation.

**Friend Recommendations**: Once users are assigned to clusters, the system suggests potential friends within the same or neighboring clusters.

# Tools & Technologies
- Spotify API: Used for retrieving user data and audio features.
- PostgreSQL: Database for storing user information, audio features, and cluster assignments.
- Python: Handles data extraction, processing, and clustering.
- Libraries: Spotipy, Scikit-learn, Pandas, Psycopg2
- OAuth2: Authentication protocol used to access Spotify data.
