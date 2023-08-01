import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import io
import os

class YouTubeAPIException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)

class YouTubeAPIv3:
    """
        This is a wrapper around the YouTube v3 API.
        
        A 'client_secret.json' file is needed in order for this class to be functional.
        Or should I say ... classy ....
        
        Required Python modules:
            google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client
                
        Keep in mind that you need to have the proper OAuth 2.0 authentication set up and the 
        permissions to manage playlists for an account. Below is a step-by-step guide on how to
        obtain a client_secret.json file. 
        
        Please also note that the steps for setting up OAuth 2.0 authentication and using the 
        client_secret.json file might change over time. For the latest and most detailed 
        instructions, you should refer to the official Google API documentation for the YouTube 
        API and OAuth 2.0 authentication for Python.
        
        1) Google Cloud Console:

            To use the YouTube API or any other Google API, you need to create a project on the 
            Google Cloud Console and enable the APIs you want to use.
            
        2) OAuth 2.0 Credentials:
        
            After creating the project and enabling the YouTube API, you need to create OAuth 2.0 
            credentials. These credentials are used to identify your application and to 
            authenticate and authorize access to the API. The credentials contain a client ID, 
            client secret, and other information.
                
        3) Download Client Secret:

            Once you create OAuth 2.0 credentials, you can download the client_secret.json file 
            from the Google Cloud Console. This file contains the client ID and client secret, 
            which are used in the authentication process.
            
        4) Authentication Flow:
        
            When you run your Python application that interacts with the YouTube API, it will 
            prompt the user to authenticate their Google account through a web browser (if necessary). 
            The client_secret.json file is used during this authentication flow to identify your 
            application and establish a secure connection.
            
        5) Access Tokens:

            After the user grants permission to your application, the authentication server provides 
            your application with an access token. This access token is used in API requests to 
            prove that your application has been granted permission to access the user's resources.

        6) Protecting Client Secret:
            
            The client_secret.json file contains sensitive information (client secret), so it should 
            be kept confidential and not shared or exposed publicly. It is important to store the 
            client_secret.json file securely on the server-side of your application.
            
        When you use the Google API Client Library for Python to interact with the YouTube API, you'll 
        need to set up the OAuth 2.0 authentication flow and provide the path to the client_secret.json 
        file in your code to initiate the authentication process.
        
    """
    def __init__(
        self, 
        _client_secrets_json_path: str,
        _token_file: str="token.pickle", 
        _channel_id: str=None
    ) -> None:
        
        """
            Initializes the YouTubeAPIClient object.
        """

        
        self.CLIENT_SECRETS_JSON_FILE = _client_secrets_json_path
        self.CHANNEL_ID = _channel_id
        
        if _channel_id is not None:
            self.CHANNEL_ID = _channel_id
        
        self.api_obj = {
            "json": self.CLIENT_SECRETS_JSON_FILE
        }
        
        self.TOKEN_FILE = _token_file
        
        self.service = self.get_authenticated_service()
        
    def set_client_secrets_json(self, client_secrets_json: str) -> bool:
        """
        Sets the path to the client_secrets.json file.
        """
        if client_secrets_json.endswith(".json"):
            self.CLIENT_SECRETS_JSON_FILE = client_secrets_json
            return True
        return False    
    
    def get_client_secrets_json(self) -> (str | None):
        if len(self.CLIENT_SECRETS_JSON_FILE) != 0:
            return self.CLIENT_SECRETS_JSON_FILE
        return None
    
    #//////////// AUTHENTICATION ////////////
    
    def _get_authenticated_service(self, credentials) -> object:
        """
        This method is a wrapper around the 'googleapiclient.discovery.build' method.
        It returns the resource needed for interacting with the YouTube API.
        """
        #scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        #flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file("client_secret_671382908634-hudnrlsnhr3gqresomjga29a33s0chml.apps.googleusercontent.com.json", scopes)
        #credentials = flow.run_local_server(port=8080)
        _credentials = credentials
        return googleapiclient.discovery.build("youtube", "v3", credentials=_credentials)

    def get_authenticated_service(self) -> (object | None):
        """
        When you call get_authenticated_service(), it will initiate the OAuth 2.0 authentication 
        flow, prompting the user to grant access to your application to the specified 
        scopes (in this case, "https://www.googleapis.com/auth/youtube.readonly"). Once 
        the user grants permission, the credentials will be stored in a local file named 
        "token.pickle" for future use. Subsequent calls to get_authenticated_service() will 
        load the credentials from the file without re-authentication.
        """
        # Note to self: Think about making 'flow' & 'credentials' available as 
        # class variables instead of a local variable so that this specific 
        # instance can be accessed outside of get_authenticated_service.
        import pickle
        credentials = None
        try:
            # Check if credentials are stored in a local file (to avoid re-authentication)
            if os.path.exists(self.TOKEN_FILE):
                with open(self.TOKEN_FILE, "rb") as token_file:
                    credentials = pickle.load(token_file)
                    
            # If no credentials found, perform the OAuth 2.0 flow
            if not credentials or not credentials.valid:
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    self.CLIENT_SECRETS_JSON_FILE, self.api_scopes)
                credentials = flow.run_local_server(port=0)

                with open(self.TOKEN_FILE, "wb") as token_file:
                    pickle.dump(credentials, token_file)

            from googleapiclient.discovery import build
            youtube_service = self._get_authenticated_service(credentials)
            return youtube_service
        except googleapiclient.errors.HttpError as e:
            print(f"An API error occurred: {e}")
            return None
            
    #//////////// PLAYLISTS ////////////
    
    def save_playlist(self, source_playlist_id: str, destination_playlist_id: str) -> bool:
        """
        Save a playlist using the source and destination playlists IDs. 
        """
        service = self.service
        try:
            videos = self.get_videos_in_playlist(source_playlist_id)
            for video in videos:
                self.save_video_to_playlist(destination_playlist_id, video["video_id"])
            return True
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return False
   
    def create_playlist(self, title: str, description: str, privacy_status: str="public") -> (dict | None):
        service = self.service
        try:
            request = service.playlists().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": title,
                        "description": description
                    },
                    "status": {
                        "privacyStatus": privacy_status
                    }
                }
            )
            response = request.execute()
            new_playlist = {
                "title": response['snippet']['title'],
                "id": response['id']
            }
            return new_playlist
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def delete_playlist(self, playlist_id: str) -> bool:
        """
        With this method, you can provide the playlist_id of the playlist 
        you want to delete, and it will be removed from your YouTube account.
        """
        service = self.service

        try:
            service.playlists().delete(
                id=playlist_id
            ).execute()

            return True

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return False

    def add_video_to_playlist(self, playlist_id: str, video_id: str) -> bool:
        """
        This method allows you to add a video with the specified video_id 
        to a playlist with the specified playlist_id.
        """
        service = self.service
        try:
            request = service.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            )
            response = request.execute()
            return True

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return False
    
    def remove_video_from_playlist(self, playlist_item_id: str) -> bool:
        """
        This method allows you to remove a video from a playlist using the 
        playlist_item_id. Note that you need to retrieve the playlist_item_id 
        of the specific video in the playlist before using this method.
        """
        service = self.service

        try:
            service.playlistItems().delete(
                id=playlist_item_id
            ).execute()
            return True
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return False
    
    def update_playlist(self, playlist_id: str, title: str, description: str) -> (dict | None):
        """
        Update the playlist title and description. Returns the updated
        playlist snippet. 
        """
        service = self.service
        try:
            request = service.playlists().update(
                part="snippet",
                body={
                    "id": playlist_id,
                    "snippet": {
                        "title": title,
                        "description": description
                    }
                }
            )
            response = request.execute()
            return response['snippet']
        except googleapiclient.errors.HttpError as e:
            return None

    def update_playlist_details(self, playlist_id, new_title: str=None, new_description: str=None) -> bool:
        """
        This method allows you to update the title and description of a 
        playlist with the specified playlist_id.
        """
        service = self.service

        try:
            playlist = service.playlists().list(
                part="snippet",
                id=playlist_id
            ).execute()

            snippet = playlist["items"][0]["snippet"]
            if new_title:
                snippet["title"] = new_title
            if new_description:
                snippet["description"] = new_description

            service.playlists().update(
                part="snippet",
                body={
                    "id": playlist_id,
                    "snippet": snippet
                }
            ).execute()
            return True
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return False

    def update_playlist_title(self, playlist_id, new_title=None) -> bool:
        """
        This method allows you to update the title and description of a 
        playlist with the specified playlist_id.
        """
        service = self.service

        try:
            playlist = service.playlists().list(
                part="snippet",
                id=playlist_id
            ).execute()

            snippet = playlist["items"][0]["snippet"]
            if new_title:
                snippet["title"] = new_title

            service.playlists().update(
                part="snippet",
                body={
                    "id": playlist_id,
                    "snippet": snippet
                }
            ).execute()

            return True

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return False
    
    def update_playlist_description(self, playlist_id, new_description: str=None) -> bool:
        """
        This method allows you to update the title and description of a 
        playlist with the specified playlist_id.
        """
        service = self.service

        try:
            playlist = service.playlists().list(
                part="snippet",
                id=playlist_id
            ).execute()

            snippet = playlist["items"][0]["snippet"]
            if new_description:
                snippet["description"] = new_description

            service.playlists().update(
                part="snippet",
                body={
                    "id": playlist_id,
                    "snippet": snippet
                }
            ).execute()
            return True
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return False

    def reorder_playlist_items(self, playlist_id: str, video_ids: list) -> bool:
        """
        This method allows you to reorder videos in a playlist by providing 
        a list of video_ids. The videos in the playlist will be reordered based 
        on the order of the provided video_ids
        """
        service = self.service
        try:
            playlist_items = service.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=len(video_ids)
            ).execute()

            video_positions = {}
            for item in playlist_items["items"]:
                video_positions[item["snippet"]["resourceId"]["videoId"]] = item["snippet"]["position"]
            for video_id in video_ids:
                position = video_positions.get(video_id, 0)
                request = service.playlistItems().update(
                    part="snippet",
                    body={
                        "id": f"{playlist_id}_{video_id}",
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": video_id
                            },
                            "position": position
                        }
                    }
                )
                request.execute()
            return True
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return False
    
    def iterate_videos_in_playlist(self, playlist_id: str, func=None) -> (bool | None):
        if func is not None:
            videos = self.get_videos_in_playlist(playlist_id)
            if videos:
                for video in videos:
                    func(video)
                return True
            else:
                print(f"Unable to fetch videos in playlist with ID {playlist_id}.")
                return False
        return None

    def search_playlists(self, query: str, max_results: int=10) -> (list[dict] | None):
        """
        Returns a list of result snippets that matched the query.
        """
        service = self.service
        try:
            request = service.search().list(
                part="snippet",
                q=query,
                type="playlist",
                maxResults=max_results
            )
            response = request.execute()
            result_snippets = []
            for item in response["items"]:
                result_snippets.append(item["snippet"])
            return result_snippets
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None
    
    def get_playlist_snippet(self, playlist_id: str) -> (str | None):
        """
        Get a playlists snippet using the playlist id.
        """
        service = self.service

        try:
            request = service.playlists().list(
                part="snippet",
                id=playlist_id
            )
            response = request.execute()

            playlist_snippet_info = response.get("items", [])[0]["snippet"]
            return playlist_snippet_info

        except googleapiclient.errors.HttpError as e:
            print(f"An API error occurred: {e}")
            return None

    def get_playlist_name(self, playlist_id: str) -> (str | None):
        """
        Get the name of a playlist using the playlst id.
        """
        playlist_info = self.get_playlist_snippet(playlist_id)
        if playlist_info:
            return playlist_info["title"]
        return None

    def get_playlist_id(self, playlist_title: str, channel_id: str=None, max_results: int=1) -> (str | None):
        service = self.service
        try:
            request = service.search().list(
                part="id",
                channelId=channel_id,
                maxResults=max_results,
                q=playlist_title,
                type="playlist"
            )
            response = request.execute()

            if response.get("items"):
                playlist_id = response["items"][0]["id"]["playlistId"]
                return playlist_id

            return None

        except googleapiclient.errors.HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return None

        except IndexError:
            print(f"No playlist found with title '{playlist_title}'.")
            return None

    def get_playlist_ids(self, max_results=10) -> (list | None):
        service = self.service

        try:
            request = service.playlists().list(
                part="snippet",
                mine=True,
                maxResults=max_results
            )
            response = request.execute()
            ids = []
            for playlist in response["items"]:
                ids.append(playlist["id"])
            return ids
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def get_playlist_etags(self, max_results=10) -> (list | None): 
        service = self.service

        try:
            request = service.playlists().list(
                part="snippet",
                mine=True,
                maxResults=max_results
            )
            response = request.execute()
            etags = []
            print(response['items'])
            for playlist in response["items"]:
                etags.append(playlist["etag"])
            return etags
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None
    
    def get_videos_in_playlist(self, playlist_id: str, max_results: int=50) -> (list | None):
        """
        Returns all videos in a playlist up to the number specified 
        by max_results.
        """
        service = self.service
        try:
            videos = []
            request = service.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=int(max_results)
            )
            while request is not None:
                response = request.execute()
                for item in response.get("items", []):
                    video_id = item["snippet"]["resourceId"]["videoId"]
                    video_title = item["snippet"]["title"]
                    videos.append({
                        "video_id": video_id,
                        "video_title": video_title
                    })

                request = service.playlistItems().list_next(request, response)
            return videos
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def get_playlists(self, max_results: int=10) -> (list | None):
        """
            This method uses the playlists().list method to retrieve the user's playlists. 
            Using the 'mine=True' parameter indicates that we want to retrieve playlists belonging 
            to the authenticated user.
        """
        service = self.service
        try:
            request = service.playlists().list(
                part="snippet",
                mine=True,
                maxResults=max_results
            )
            response = request.execute()
            
            playlists = []
            for playlist in response["items"]:
                playlists.append(playlist["snippet"])
            return playlists
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None
    
    def get_liked_playlist(self) -> (dict | None):
        """
        Retrieve the snippet for the "Liked videos" playlist.
        """
        service = self.service

        try:
            liked_playlist = None
            request = service.playlists().list(
                part="snippet",
                mine=True
            )
            response = request.execute()
            for item in response.get("items", []):
                if item["snippet"]["title"] == "Liked videos":
                    liked_playlist = item
                    return liked_playlist
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None
    
    def get_playlist_titles(self, max_results=10) -> (list | None):
        service = self.service

        try:
            request = service.playlists().list(
                part="snippet",
                mine=True,
                maxResults=max_results
            )
            response = request.execute()
            titles = []
            for playlist in response["items"]:
                titles.append(playlist["snippet"]["title"])
            return titles
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None
            
    def get_playlist_items(self, playlist_id, max_results=10) -> (list | None):
        """
        Returns a list of playlist item snippets for a given playlist. Returns None
        if unsuccessful.
        """
        service = self.service
        try:
            request = service.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=max_results
            )
            response = request.execute()
            playlist_items = []
            for item in response["items"]:
                playlist_items.append(item["snippet"])
            return playlist_items

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None
    
    def set_playlist_privacy_status(self, playlist_id, privacy_status):
        """
        This method allows you to update the privacy status of a playlist 
        with the specified playlist_id. The privacy_status can be set to 
        "private" or "public."
        """
       
        service = self.service

        try:
            playlist = service.playlists().list(
                part="status",
                id=playlist_id
            ).execute()

            status = playlist["items"][0]["status"]
            status["privacyStatus"] = privacy_status

            service.playlists().update(
                part="status",
                body={
                    "id": playlist_id,
                    "status": status
                }
            ).execute()

            return True

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return False

    #//////////// VIDEOS ////////////
    
    def get_video_snippet(self, video_id):
        """
        This method, get_video_snippet(video_id), allows you to retrieve the 
        snippet data of a video with the specified video_id. The snippet data 
        includes information such as the video's title, description, tags, 
        thumbnails, etc.
        """
        service = self.service

        try:
            video = service.videos().list(
                part="snippet",
                id=video_id
            ).execute()

            snippet = video["items"][0]["snippet"]
            return snippet

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def upload_video(self, video_path, title, description, privacy_status="public"):
        """
        The upload_video(video_path, title, description, privacy_status), takes the 
        following parameters:

            video_path:     The local file path of the video you want to upload.
            title:          The title of the video.
            description:    The description of the video.
            privacy_status: (Optional) The privacy status of the uploaded video. It can 
            be set to "public," "private," or "unlisted." The default is "public."
            
        Before using this method or any method in this class, ensure you have the 
        get_authenticated_service() method defined as shown in the previous responses 
        to obtain an authenticated YouTube API service. This ensures that your 
        application is authorized to make API requests and has the necessary permissions 
        to upload videos on behalf of the user.

        """
        import requests
        from googleapiclient.errors import HttpError

        service = self.service

        try:
            request = service.videos().insert(
                part="snippet,status",
                body={
                    "snippet": {
                        "title": title,
                        "description": description
                    },
                    "status": {
                        "privacyStatus": privacy_status
                    }
                }
            )
            response = request.execute()
            upload_url = response.get("uploadURL")
            if upload_url:
                headers = {
                    "Authorization": f"Bearer {service.credentials.token}",
                    "Content-Type": "video/*"
                }

                video_file = open(video_path, "rb")
                response = requests.put(upload_url, data=video_file, headers=headers)

                if response.status_code == 200:
                    print("Video uploaded successfully!")
                else:
                    print("Video upload failed.")

                video_file.close()

            else:
                print("Upload URL not found. Unable to start video upload.")

        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
        except OSError as e:
            print(f"An OS error occurred: {e}")

    def delete_video(self, video_id):
        service = self.service

        try:
            service.videos().delete(
                id=video_id
            ).execute()

            print(f"Video with ID {video_id} deleted successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def like_video(self, video_id):
        """
        This method like_video(video_id) takes the video_id of the video 
        you want to like and calls the videos.rate method with rating="like" 
        to like the video.
        """
        service = self.service

        try:
            request = service.videos().rate(
                id=video_id,
                rating="like"
            )
            response = request.execute()

            print(f"Video with ID {video_id} liked successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def unlike_video(self, video_id):
        service = self.service

        try:
            request = service.videos().rate(
                id=video_id,
                rating="none"
            )
            response = request.execute()

            print(f"Video with ID {video_id} unliked successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_related_videos(self, video_id, max_results=10):
        """
        This method retrieves related videos for a specific video. It prints 
        information about videos related to the given video based on YouTube's 
        recommendation algorithm.
        """
        service = self.service

        try:
            request = service.search().list(
                part="snippet",
                relatedToVideoId=video_id,
                type="video",
                maxResults=max_results
            )
            response = request.execute()

            for video in response["items"]:
                title = video["snippet"]["title"]
                video_id = video["id"]["videoId"]
                print(f"Related Video: {title} (Video ID: {video_id})")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def iterate_related_videos(self, video_id, max_results=10):
        service = self.service

        try:
            request = service.search().list(
                part="snippet",
                relatedToVideoId=video_id,
                type="video",
                maxResults=max_results
            )
            response = request.execute()

            related_videos = response.get("items", [])
            for video in related_videos:
                video_id = video["id"]["videoId"]
                video_title = video["snippet"]["title"]
                channel_title = video["snippet"]["channelTitle"]
                print(f"Video ID: {video_id}, Title: {video_title}, Channel: {channel_title}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def save_video_to_playlist(self, playlist_id, video_id):
        """
        This method allows you to save a video specified by ID to a playlist
        also specified by ID.
        """
        service = self.service

        try:
            service.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            ).execute()

            print(f"Video with ID {video_id} saved to the playlist with ID {playlist_id} successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
    
    def get_all_video_details(self, video_id):
        service = self.service

        try:
            request = service.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()

            video = response["items"][0]
            print(f"Title: {video['snippet']['title']}")
            print(f"Channel: {video['snippet']['channelTitle']}")
            print(f"Published At: {video['snippet']['publishedAt']}")
            print(f"Duration: {video['contentDetails']['duration']}")
            print(f"Views: {video['statistics']['viewCount']}")
            print(f"Likes: {video['statistics']['likeCount']}")
            print(f"Dislikes: {video['statistics']['dislikeCount']}")
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_video_title(self, video_id):
        service = self.service
        try:
            request = service.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()

            video = response["items"][0]
            return video['snippet']['title']
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            
    def get_videos_channel_title(self, video_id):
        service = self.service
        try:
            request = service.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()

            video = response["items"][0]
            return video['snippet']['channelTitle']
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            
    def get_video_published_at(self, video_id):
        service = self.service
        try:
            request = service.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()

            video = response["items"][0]
            return video['snippet']['publishedAt']
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            
    def get_video_duration(self, video_id):
        service = self.service
        try:
            request = service.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()

            video = response["items"][0]
            return video['contentDetails']['duration']
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
       
    def get_video_view_count(self, video_id):
        service = self.service
        try:
            request = service.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()

            video = response["items"][0]
            return video['statistics']['viewCount']
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
      
    def get_video_like_count(self, video_id):
        service = self.service
        try:
            request = service.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()

            video = response["items"][0]
            return video['statistics']['likeCount']
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
      
    def get_video_dislike_count(self, video_id):
        service = self.service
        try:
            request = service.videos().list(
                part="snippet,contentDetails,statistics",
                id=video_id
            )
            response = request.execute()

            video = response["items"][0]
            return video['statistics']['dislikeCount']
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
       
    def get_video_categories(self, region_code="US"):
        service = self.service

        try:
            request = service.videoCategories().list(
                part="snippet",
                regionCode=region_code
            )
            response = request.execute()

            for item in response["items"]:
                print(f"{item['id']} - {item['snippet']['title']}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
     
    def get_videos_by_category(self, category_id, region_code="US", max_results=10):
        service = self.service

        try:
            request = service.search().list(
                part="snippet",
                videoCategoryId=category_id,
                regionCode=region_code,
                type="video",
                maxResults=max_results
            )
            response = request.execute()

            for item in response["items"]:
                print(item["snippet"]["title"])

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
    
    def get_trending_videos(self, region_code="US", max_results=10):
        service = self.service
        try:
            request = service.videos().list(
                part="snippet",
                chart="mostPopular",
                regionCode=region_code,
                maxResults=max_results
            )
            response = request.execute()

            for item in response["items"]:
                print(item["snippet"]["title"])

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_videos_by_tag(self, tag, region_code="US", max_results=10):
        service = self.service
        try:
            request = service.search().list(
                part="snippet",
                q=tag,
                regionCode=region_code,
                type="video",
                maxResults=max_results
            )
            response = request.execute()

            for item in response["items"]:
                print(item["snippet"]["title"])
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
    
    def get_recommended_videos(self, video_id, max_results=10):
        """
        This method will get recommended videos based on a given video's ID.
        """
        service = self.service

        try:
            # Get recommended videos for the given video ID
            request = service.search().list(
                part="snippet",
                relatedToVideoId=video_id,
                type="video",
                maxResults=max_results
            )
            response = request.execute()

            recommended_videos = []
            for item in response["items"]:
                video = item["snippet"]
                recommended_videos.append({
                    "video_id": item["id"]["videoId"],
                    "title": video["title"],
                    "channel": video["channelTitle"]
                })

            return recommended_videos

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None
 
    def set_video_tags(self, video_id, tags):
        """
        This method allows you to set the tags for a video with 
        the specified video_id. Provide a list of tags to update the video's tags.
        """
        service = self.service

        try:
            video = service.videos().list(
                part="snippet",
                id=video_id
            ).execute()

            snippet = video["items"][0]["snippet"]
            snippet["tags"] = tags

            service.videos().update(
                part="snippet",
                body={
                    "id": video_id,
                    "snippet": snippet
                }
            ).execute()

            print(f"Tags for video with ID {video_id} updated successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
 
    def update_video_privacy_status(self, video_id, privacy_status):
        """
        This function allows you to update the privacy status of a video 
        with the specified video_id. The privacy_status can be set to 
        "private," "public," or "unlisted."
        """
        service = self.service

        try:
            video = service.videos().list(
                part="status",
                id=video_id
            ).execute()

            status = video["items"][0]["status"]
            status["privacyStatus"] = privacy_status

            service.videos().update(
                part="status",
                body={
                    "id": video_id,
                    "status": status
                }
            ).execute()

            print(f"Privacy status for video with ID {video_id} updated successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def update_video_details(self, video_id, new_title=None, new_description=None, new_tags=None):
        """
        This method allows you to update the title, description, and tags of a 
        video with the specified video_id. You can provide the new values for these 
        parameters, and the snippet will be updated accordingly.
        """
        service = self.service

        try:
            video = service.videos().list(
                part="snippet",
                id=video_id
            ).execute()

            snippet = video["items"][0]["snippet"]
            if new_title:
                snippet["title"] = new_title
            if new_description:
                snippet["description"] = new_description
            if new_tags:
                snippet["tags"] = new_tags

            service.videos().update(
                part="snippet",
                body={
                    "id": video_id,
                    "snippet": snippet
                }
            ).execute()

            print(f"Video with ID {video_id} snippet updated successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def search_videos(self, query, max_results=10):
        service = self.service

        try:
            request = service.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=max_results
            )
            response = request.execute()

            for item in response["items"]:
                print(item["snippet"]["title"])

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")        

    def search_videos_by_order(self, query, order="relevance", max_results=10):
        service = self.service
        try:
            request = service.search().list(
                part="snippet",
                q=query,
                type="video",
                order=order,
                maxResults=max_results
            )
            response = request.execute()
            for item in response["items"]:
                print(item["snippet"]["title"])
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def search_videos_by_category(self, query, category_id, max_results=10):
        service = self.service
        try:
            request = service.search().list(
                part="snippet",
                q=query,
                type="video",
                videoCategoryId=category_id,
                maxResults=max_results
            )
            response = request.execute()
            for item in response["items"]:
                print(item["snippet"]["title"])
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def search_videos_by_definition(self, query, definition="any", max_results=10):
        service = self.service
        try:
            request = service.search().list(
                part="snippet",
                q=query,
                type="video",
                videoDefinition=definition,
                maxResults=max_results
            )
            response = request.execute()
            for item in response["items"]:
                print(item["snippet"]["title"])
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def search_videos_by_duration(self, query, duration="any", max_results=10):
        service = self.service
        try:
            request = service.search().list(
                part="snippet",
                q=query,
                type="video",
                videoDuration=duration,
                maxResults=max_results
            )
            response = request.execute()

            for item in response["items"]:
                print(item["snippet"]["title"])
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")    

    def search_videos_by_license(self, query, license_type="any", max_results=10):
        service = self.service
        try:
            request = service.search().list(
                part="snippet",
                q=query,
                type="video",
                videoLicense=license_type,
                maxResults=max_results
            )
            response = request.execute()
            for item in response["items"]:
                print(item["snippet"]["title"])
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
    
    def search_videos_by_type(self, query, video_type="any", max_results=10):
        service = self.service
        try:
            request = service.search().list(
                part="snippet",
                q=query,
                type=video_type,
                maxResults=max_results
            )
            response = request.execute()
            for item in response["items"]:
                print(item["snippet"]["title"])
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def search_embeddable_videos(self, query, embeddable="true", max_results=10):
        service = self.service
        try:
            request = service.search().list(
                part="snippet",
                q=query,
                type="video",
                videoEmbeddable=embeddable,
                maxResults=max_results
            )
            response = request.execute()
            for item in response["items"]:
                print(item["snippet"]["title"])
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def search_videos_by_published_date(self, query, published_after, published_before, max_results=10):
        service = self.service
        try:
            request = service.search().list(
                part="snippet",
                q=query,
                type="video",
                publishedAfter=published_after,
                publishedBefore=published_before,
                maxResults=max_results
            )
            response = request.execute()

            for item in response["items"]:
                print(item["snippet"]["title"])

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
     
    #//////////// CHANNELS ////////////

    def get_channel_id(self, channel_identifier):
        service = self.service

        try:
            request = service.channels().list(
                part="id",
                forUsername=channel_identifier  # Use 'forUsername' for channel's username or 'id' for channel URL
            )
            response = request.execute()

            if response.get("items"):
                channel_id = response["items"][0]["id"]
                return channel_id

            return None

        except googleapiclient.errors.HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return None

        except IndexError:
            print(f"Channel not found for '{channel_identifier}'.")
            return None

    def get_channel_name(self, channel_id):
        """
        This method allows you to retrieve the name (title) of a 
        channel with the specified channel_id.
        """
        service = self.service

        try:
            channel = service.channels().list(
                part="snippet",
                id=channel_id
            ).execute()

            channel_name = channel["items"][0]["snippet"]["title"]
            return channel_name

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def get_channel_id_by_name(self, channel_name):
        """ 
        This method takes the channel_name as input and returns 
        the corresponding channel ID. It uses the search.list method 
        with the type="channel" parameter to filter the results and
        fetches the first channel ID that matches the search query.
        """
        service = self.service

        try:
            request = service.search().list(
                part="id",
                q=channel_name,
                type="channel",
                maxResults=1
            )
            response = request.execute()

            if "items" in response:
                channel_id = response["items"][0]["id"]["channelId"]
                return channel_id
            else:
                print("Channel not found.")
                return None

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def change_channel_name(self, channel_id, new_name):
        service = self.service

        try:
            channel = service.channels().list(
                part="snippet",
                id=channel_id
            ).execute()

            snippet = channel["items"][0]["snippet"]
            snippet["title"] = new_name

            service.channels().update(
                part="snippet",
                body={
                    "id": channel_id,
                    "snippet": snippet
                }
            ).execute()

            print(f"Channel with ID {channel_id} name changed to '{new_name}' successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_channels(self):
        """
        Retrieve information about channels that the authenticated user is 
        subscribed to:
        """
        service = self.service

        try:
            channels = []

            request = service.subscriptions().list(
                part="snippet",
                mine=True,
                maxResults=50
            )

            while request is not None:
                response = request.execute()

                for item in response.get("items", []):
                    channel_id = item["snippet"]["resourceId"]["channelId"]
                    channel_title = item["snippet"]["title"]
                    channels.append({
                        "channel_id": channel_id,
                        "channel_title": channel_title
                    })

                request = service.subscriptions().list_next(request, response)

            return channels

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def subscribe_to_channel(self, channel_id):
        """
        Subscribe to a channel using its ID
        """
        service = self.service
        try:
            service.subscriptions().insert(
                part="snippet",
                body={
                    "snippet": {
                        "resourceId": {
                            "kind": "youtube#channel",
                            "channelId": channel_id
                        }
                    }
                }
            ).execute()
            return True
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def unsubscribe_from_channel(self, channel_id):
        """
        Unsubscribe from a channel using it's ID.
        """
        service = self.service

        try:
            # First, get the subscription ID for the specified channel
            request = service.subscriptions().list(
                part="id",
                mine=True,
                forChannelId=channel_id
            )
            response = request.execute()

            if response.get("items"):
                subscription_id = response["items"][0]["id"]

                # Unsubscribe from the channel using the subscription ID
                service.subscriptions().delete(
                    id=subscription_id
                ).execute()

                print(f"Unsubscribed from the channel with ID {channel_id} successfully!")
            else:
                print(f"You are not subscribed to the channel with ID {channel_id}.")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
    
    def iterate_subscriptions_in_channel(self, channel_id):
        """
        Iterate over the subscriptions in a channel.
        """
        service = self.service

        try:
            subscriptions = []

            request = service.subscriptions().list(
                part="snippet",
                channelId=channel_id,
                maxResults=50
            )

            while request is not None:
                response = request.execute()

                for item in response.get("items", []):
                    subscribed_channel_id = item["snippet"]["resourceId"]["channelId"]
                    subscribed_channel_title = item["snippet"]["title"]
                    subscriptions.append({
                        "subscribed_channel_id": subscribed_channel_id,
                        "subscribed_channel_title": subscribed_channel_title
                    })

                request = service.subscriptions().list_next(request, response)

            return subscriptions

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def get_subscriptions_channel_ids(self):
        """
        retrieves the channel IDs of the channels to which the authenticated 
        user is subscribed. The function uses pagination to handle cases 
        where the user has more than 50 subscriptions (the default API result limit).
        """
        service = self.service

        try:
            channel_ids = []

            # Set the 'mine' parameter to True to get subscriptions of the authenticated user
            request = service.subscriptions().list(
                part="snippet",
                mine=True,
                maxResults=50  # Adjust the number of results as needed
            )

            while request is not None:
                response = request.execute()

                # Extract channel IDs from the response
                for item in response.get("items", []):
                    channel_id = item["snippet"]["resourceId"]["channelId"]
                    channel_ids.append(channel_id)

                # Check if there are more subscriptions to fetch
                request = service.subscriptions().list_next(request, response)

            return channel_ids

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def get_channel_snippet(self, channel_id):
        """
        This method allows you to retrieve the snippet of a channel with 
        the specified channel_id. It returns the snippet data, which includes 
        information like the channel's title, description, and profile picture.
        """
        service = self.service

        try:
            channel = service.channels().list(
                part="snippet",
                id=channel_id
            ).execute()

            snippet = channel["items"][0]["snippet"]
            return snippet

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def get_channel_info(self, channel_id):
        service = self.service

        try:
            request = service.channels().list(
                part="snippet,statistics",
                id=channel_id
            )
            response = request.execute()

            channel = response["items"][0]
            print(f"Channel Title: {channel['snippet']['title']}")
            print(f"Subscriber Count: {channel['statistics']['subscriberCount']}")
            print(f"Video Count: {channel['statistics']['videoCount']}")
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_channel_videos(self, channel_id, max_results=100):
        service = self.service
        try:
            request = service.search().list(
            part="snippet",
            channelId=channel_id,
            type="video",
            maxResults=max_results
            )
            response = request.execute()
            for item in response["items"]:
                print(item["snippet"]["title"])
        except googleapiclient.errors.HttpError as e:
            print(f"googleapiclient.errors.HttpError:\n {e}")
        except UnicodeEncodeError as uee:
            print(f"UnicodeEncodeError:\nUnable to encode one or more characters in a video title.\nMost likely an emoji\n{uee}")

    def get_featured_channels(self, channel_id):
        service = self.service

        try:
            request = service.channels().list(
                part="snippet,brandingSettings",
                id=channel_id
            )
            response = request.execute()

            featured_channels = response["items"][0]["brandingSettings"]["channel"]["featuredChannelsUrls"]
            for channel_url in featured_channels:
                print(channel_url)

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_channel_sections(self, channel_id):
        service = self.service

        try:
            request = service.channelSections().list(
                part="snippet",
                channelId=channel_id
            )
            response = request.execute()

            for item in response["items"]:
                print(item["snippet"]["title"] )

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_channel_subscribers(self, channel_id):
        service = self.service

        try:
            request = service.channels().list(
                part="statistics",
                id=channel_id
            )
            response = request.execute()

            subscriber_count = response["items"][0]["statistics"]["subscriberCount"]
            print(f"Channel '{channel_id}' has {subscriber_count} subscribers.")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_latest_subscriptions(self, max_results=10):
        service = self.service
        try:
            request = service.subscriptions().list(
                part="snippet",
                mine=True,
                maxResults=max_results,
                order="newest"
            )
            response = request.execute()

            for subscription in response["items"]:
                channel_title = subscription["snippet"]["title"]
                channel_id = subscription["snippet"]["resourceId"]["channelId"]
                print(f"Subscribed Channel: {channel_title} (Channel ID: {channel_id})")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_subscribed_channels(self, max_results=10):
        service = self.service
        try:
            request = service.subscriptions().list(
                part="snippet",
                mine=True,
                maxResults=max_results
            )
            response = request.execute()

            for subscription in response["items"]:
                channel_title = subscription["snippet"]["title"]
                channel_id = subscription["snippet"]["resourceId"]["channelId"]
                print(f"Subscribed Channel: {channel_title} (Channel ID: {channel_id})")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def is_subscribed_to_channel(self, channel_id):
        service = self.service

        try:
            request = service.subscriptions().list(
                part="snippet",
                mine=True,
                forChannelId=channel_id
            )
            response = request.execute()

            if "items" in response and len(response["items"]) > 0:
                return True
            else:
                return False

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return False

    def subscribe_to_channel(self, channel_id):
        service = self.service

        try:
            request = service.subscriptions().insert(
                part="snippet",
                body={
                    "snippet": {
                        "resourceId": {
                            "kind": "youtube#channel",
                            "channelId": channel_id
                        }
                    }
                }
            )
            response = request.execute()

            print("Subscribed successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def unsubscribe_from_channel(self, channel_id):
        service = self.service

        try:
            request = service.subscriptions().delete(
                id=channel_id
            )
            response = request.execute()

            print("Unsubscribed successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_subscription_count(self, channel_id):
        service = self.service
        try:
            request = service.channels().list(
                part="statistics",
                id=channel_id
            )
            response = request.execute()
            if "items" in response:
                channel_info = response["items"][0]
                if "statistics" in channel_info:
                    subscription_count = channel_info["statistics"].get("subscriberCount", 0)
                    return int(subscription_count)
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
        return 0

    def get_my_subscription_count(self):
        service = self.service

        try:
            request = service.subscriptions().list(
                part="subscriberSnippet",
                mine=True
            )
            response = request.execute()

            subscription_count = response.get("pageInfo", {}).get("totalResults", 0)
            return int(subscription_count)

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

        return 0

    def get_subscriber_counts(self, channel_ids):
        service = self.service
        try:
            request = service.channels().list(
                part="statistics",
                id=",".join(channel_ids)
            )
            response = request.execute()

            subscriber_counts = {}
            for channel_info in response["items"]:
                channel_id = channel_info["id"]
                if "statistics" in channel_info:
                    subscriber_count = channel_info["statistics"].get("subscriberCount", 0)
                    subscriber_counts[channel_id] = int(subscriber_count)

            return subscriber_counts

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

        return {}

    def get_channel_related_channels(self, channel_id, max_results=10):
        service = self.service

        try:
            request = service.channels().list(
                part="snippet",
                relatedToChannelId=channel_id,
                type="channel",
                maxResults=max_results
            )
            response = request.execute()

            for item in response["items"]:
                print(item["snippet"]["title"])

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
    
    def search_channels(self, query, max_results=10):
        service = self.service

        try:
            request = service.search().list(
                part="snippet",
                q=query,
                type="channel",
                maxResults=max_results
            )
            response = request.execute()

            for item in response["items"]:
                print(item["snippet"]["title"])

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
        
    #//////////// COMMENTS ////////////
    
    def get_video_comments(self, video_id, max_results=10):
        service = self.service

        try:
            request = service.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_results
            )
            response = request.execute()

            for item in response["items"]:
                print(item["snippet"]["topLevelComment"]["snippet"]["textDisplay"])

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_comment_replies(self, comment_id, max_results=10):
        service = self.service
        try:
            request = service.comments().list(
                part="snippet",
                parentId=comment_id,
                maxResults=max_results
            )
            response = request.execute()

            for item in response["items"]:
                print(item["snippet"]["textDisplay"])

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def post_video_comment(self, video_id, comment_text):
        service = self.service
        try:
            request = service.commentThreads().insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": video_id,
                        "topLevelComment": {
                            "snippet": {
                                "textOriginal": comment_text
                            }
                        }
                    }
                }
            )
            response = request.execute()

            print("Comment posted successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")    

    def reply_to_comment(self, parent_comment_id, reply_text):
        service = self.service
        try:
            request = service.comments().insert(
                part="snippet",
                body={
                    "snippet": {
                        "parentId": parent_comment_id,
                        "textOriginal": reply_text
                    }
                }
            )
            response = request.execute()

            print("Reply posted successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            
    def update_comment(self, comment_id, updated_text):
        service = self.service
        try:
            request = service.comments().update(
                part="snippet",
                body={
                    "id": comment_id,
                    "snippet": {
                        "textOriginal": updated_text
                    }
                }
            )
            response = request.execute()

            print("Comment updated successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
    
    def delete_comment(self, comment_id):
        service = self.service
        try:
            service.comments().delete(
                id=comment_id
            ).execute()

            print("Comment deleted successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
    
    #//////////// LIVE BROADCASTS/STREAMING ///////////

    def get_live_streams(self, max_results=10):
        service = self.service
        try:
            request = service.liveStreams().list(
                part="snippet",
                maxResults=max_results
            )
            response = request.execute()

            for stream in response["items"]:
                print(stream["snippet"]["title"])

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
    
    def get_live_broadcasts(self, max_results=10):
        service = self.service
        try:
            request = service.liveBroadcasts().list(
                part="snippet",
                maxResults=max_results
            )
            response = request.execute()

            for broadcast in response["items"]:
                print(broadcast["snippet"]["title"])

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
    
    def search_live_broadcasts(self, query, max_results=10):
        service = self.service

        try:
            request = service.search().list(
                part="snippet",
                q=query,
                type="video",
                eventType="live",
                maxResults=max_results
            )
            response = request.execute()

            for item in response["items"]:
                print(item["snippet"]["title"])

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
      
    def get_live_chat_messages(self, live_chat_id, max_results=10):
        service = self.service
        try:
            request = service.liveChatMessages().list(
                liveChatId=live_chat_id,
                part="snippet",
                maxResults=max_results
            )
            response = request.execute()

            for message in response["items"]:
                print(message["snippet"]["displayMessage"])

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
     
    def get_live_chat_moderators(self, live_chat_id, max_results=10):
        service = self.service
        try:
            request = service.liveChatModerators().list(
                liveChatId=live_chat_id,
                part="snippet",
                maxResults=max_results
            )
            response = request.execute()

            for moderator in response["items"]:
                print(moderator["snippet"]["moderatorDetails"]["displayName"])

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
     
    def get_live_chat_bans(self, live_chat_id, max_results=10):
        service = self.service

        try:
            request = service.liveChatBans().list(
                liveChatId=live_chat_id,
                part="snippet",
                maxResults=max_results
            )
            response = request.execute()

            for ban in response["items"]:
                print(ban["snippet"]["bannedUserDetails"]["displayName"])

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def insert_live_chat_message(self, live_chat_id, message_text):
        service = self.service
        try:
            request = service.liveChatMessages().insert(
                part="snippet",
                body={
                    "snippet": {
                        "liveChatId": live_chat_id,
                        "type": "textMessageEvent",
                        "textMessageDetails": {
                            "messageText": message_text
                        }
                    }
                }
            )
            response = request.execute()

            print("Live chat message sent successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_all_live_chat_details(self, live_chat_id):
        service = self.service
        try:
            request = service.liveChat().list(
                id=live_chat_id,
                part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
            )
            response = request.execute()
            chat = response["items"][0]["snippet"]
            status = response["items"][0]["status"]
            _details = (
                chat['liveChatId'], 
                chat['liveChatType'], 
                chat['title'], 
                chat['description'],
                chat['isModerated'], 
                chat['scheduledStartTime'], 
                status['actualStartTime'],
                status['lifeCycleStatus'], 
                status['activeLiveChatId'], 
                status['concurrentViewers'],
                status['activeParticipants']
            )
            return _details
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            
    def get_live_chat_id(self, live_chat_id):
        service = self.service
        try:
            request = service.liveChat().list(
                id=live_chat_id,
                part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
            )
            response = request.execute()
            chat = response["items"][0]["snippet"]
            status = response["items"][0]["status"]
            _id = chat['liveChatId']
            return _id
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_live_chat_type(self, live_chat_id):
        service = self.service
        try:
            request = service.liveChat().list(
                id=live_chat_id,
                part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
            )
            response = request.execute()
            chat = response["items"][0]["snippet"]
            status = response["items"][0]["status"]
            _type = chat['liveChatType']
            return _type
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_live_chat_title(self, live_chat_id):
        service = self.service
        try:
            request = service.liveChat().list(
                id=live_chat_id,
                part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
            )
            response = request.execute()
            chat = response["items"][0]["snippet"]
            status = response["items"][0]["status"]
            _title = chat['title']
            return _title
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_live_chat_description(self, live_chat_id):
        service = self.service
        try:
            request = service.liveChat().list(
                id=live_chat_id,
                part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
            )
            response = request.execute()
            chat = response["items"][0]["snippet"]
            status = response["items"][0]["status"]
            _description = chat['description']
            return _description
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def is_live_chat_moderated(self, live_chat_id):
        service = self.service
        try:
            request = service.liveChat().list(
                id=live_chat_id,
                part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
            )
            response = request.execute()
            chat = response["items"][0]["snippet"]
            status = response["items"][0]["status"]
            _is_moderated = chat['isModerated']
            return _is_moderated
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
    
    def get_live_chat_scheduled_start_time(self, live_chat_id):
        service = self.service
        try:
            request = service.liveChat().list(
                id=live_chat_id,
                part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
            )
            response = request.execute()
            chat = response["items"][0]["snippet"]
            status = response["items"][0]["status"]
            _description = chat['scheduledStartTime']
            return _description
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_live_chat_actual_start_time(self, live_chat_id):
        service = self.service
        try:
            request = service.liveChat().list(
                id=live_chat_id,
                part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
            )
            response = request.execute()
            chat = response["items"][0]["snippet"]
            status = response["items"][0]["status"]
            _actual_start_time = status['actualStartTime']
            return _actual_start_time
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_live_chat_life_cycle_status(self, live_chat_id):
        service = self.service
        try:
            request = service.liveChat().list(
                id=live_chat_id,
                part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
            )
            response = request.execute()
            chat = response["items"][0]["snippet"]
            status = response["items"][0]["status"]
            _life_cycle_status = status['lifeCycleStatus']
            return _life_cycle_status
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_active_live_chat_id(self, live_chat_id):
        service = self.service
        try:
            request = service.liveChat().list(
                id=live_chat_id,
                part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
            )
            response = request.execute()
            chat = response["items"][0]["snippet"]
            status = response["items"][0]["status"]
            _active_chat_id = status['activeLiveChatId']
            return _active_chat_id
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
    
    def get_live_chat_concurrent_viewers(self, live_chat_id):
        service = self.service
        try:
            request = service.liveChat().list(
                id=live_chat_id,
                part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
            )
            response = request.execute()
            chat = response["items"][0]["snippet"]
            status = response["items"][0]["status"]
            _concurrent_viewers = status['concurrentViewers']
            return _concurrent_viewers
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_live_chat_active_participants(self, live_chat_id):
        service = self.service
        try:
            request = service.liveChat().list(
                id=live_chat_id,
                part="snippet,id,status,snippet.type,status.activeLiveChatId,status.actualStartTime,status.scheduledStartTime,status.concurrentViewers,status.activeParticipants,snippet.liveChatId,snippet.liveChatType,snippet.title,snippet.description,snippet.isModerated,snippet.scheduledStartTime,snippet.actualStartTime"
            )
            response = request.execute()
            chat = response["items"][0]["snippet"]
            status = response["items"][0]["status"]
            _active_participants = status['activeParticipants']
            return _active_participants
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    #//////////// THUMBNAILS ////////////
    
    def get_video_thumbnail_urls(self, video_id):
        """
        This method retrieves the available thumbnail URLs for a given video. 
        It returns the URLs for various thumbnail sizes, such as "default", "medium", 
        "high", "standard", and "maxres".
        """
        service = self.service
        try:
            request = service.videos().list(
                part="snippet",
                id=video_id
            )
            response = request.execute()
            thumbnails = response["items"][0]["snippet"]["thumbnails"]
            for thumbnail_type, thumbnail_info in thumbnails.items():
                print(f"{thumbnail_type}: {thumbnail_info['url']}")
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_channel_thumbnail_url(self, channel_id):
        """
        This method retrieves the default thumbnail URL for a specific 
        channel. You can modify the "default" key to get thumbnails of 
        different sizes.
        """
        service = self.service
        try:
            request = service.channels().list(
                part="snippet",
                id=channel_id
            )
            response = request.execute()
            thumbnail_url = response["items"][0]["snippet"]["thumbnails"]["default"]["url"]
            print(f"Channel Thumbnail URL: {thumbnail_url}")
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def upload_video_thumbnail(self, video_id, image_path):
        """
        This method allows you to upload a custom thumbnail image for a video. 
        Provide the video_id of the video you want to set the thumbnail for, and 
        the image_path which points to the local image file (in JPEG format) to 
        be uploaded.
        """
        service = self.service

        try:
            with open(image_path, "rb") as image_file:
                thumbnail_data = image_file.read()

            request = service.thumbnails().set(
                videoId=video_id,
                media_body=googleapiclient.http.MediaIoBaseUpload(
                    io.BytesIO(thumbnail_data),
                    mimetype="image/jpeg",
                    chunksize=-1,
                    resumable=True
                )
            )
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"Uploaded {int(status.progress() * 100)}%.")

            print("Thumbnail uploaded successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_video_default_thumbnail_url(self, video_id):
        """
        This is a simple one-liner that constructs and returns the URL for the 
        default thumbnail of a video given its video_id. 
        """
        return f"https://img.youtube.com/vi/{video_id}/default.jpg"

    def get_playlist_thumbnail_url(self, playlist_id):
        """
        This function retrieves the medium-sized thumbnail URL 
        for a specific playlist. You can modify the "medium" key 
        to get thumbnails of different sizes.
        """
        service = self.service

        try:
            request = service.playlists().list(
                part="snippet",
                id=playlist_id
            )
            response = request.execute()

            thumbnail_url = response["items"][0]["snippet"]["thumbnails"]["medium"]["url"]
            print(f"Playlist Thumbnail URL: {thumbnail_url}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def update_video_thumbnail_with_url(self, video_id, thumbnail_url):
        """
        This function allows you to update the thumbnail of a video using 
        a custom image URL. Provide the video_id of the video you want to update, 
        and the thumbnail_url that points to the new thumbnail image.
        """
        service = self.service
        try:
            request = service.videos().update(
                part="snippet",
                body={
                    "id": video_id,
                    "snippet": {
                        "thumbnails": {
                            "default": {
                                "url": thumbnail_url
                            }
                        }
                    }
                }
            )
            response = request.execute()

            print("Video thumbnail updated successfully!")
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_video_thumbnail_info(self, video_id):
        """
        This function retrieves detailed information about the available 
        thumbnail sizes for a given video, including their URLs, width, and height.
        """
        service = self.service
        try:
            request = service.videos().list(
                part="snippet",
                id=video_id
            )
            response = request.execute()
            thumbnails = response["items"][0]["snippet"]["thumbnails"]
            for thumbnail_type, thumbnail_info in thumbnails.items():
                url = thumbnail_info["url"]
                width = thumbnail_info["width"]
                height = thumbnail_info["height"]
                print(f"{thumbnail_type}: URL: {url}, Width: {width}, Height: {height}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
    
    def get_popular_video_thumbnails(self, channel_id, max_results=10):
        """
        This function retrieves the most popular video thumbnails for 
        a specific channel, ordered by the number of views. It provides 
        the video titles, IDs, and medium-sized thumbnail URLs.
        """
        service = self.service

        try:
            request = service.search().list(
                part="snippet",
                channelId=channel_id,
                maxResults=max_results,
                order="viewCount",
                type="video"
            )
            response = request.execute()
            for video in response["items"]:
                title = video["snippet"]["title"]
                video_id = video["id"]["videoId"]
                thumbnail_url = video["snippet"]["thumbnails"]["medium"]["url"]
                print(f"{title} - Video ID: {video_id}, Thumbnail URL: {thumbnail_url}")
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
    
    #//////////// CHANNEL BANNER ////////////
    
    def set_channel_banner(self, channel_id, banner_image_url):
        service = self.service

        try:
            service.channels().update(
                part="brandingSettings",
                body={
                    "id": channel_id,
                    "brandingSettings": {
                        "image": {
                            "bannerExternalUrl": banner_image_url
                        }
                    }
                }
            ).execute()

            print("Channel banner has been set/updated successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_channel_banner_url(self, channel_id):
        """
        Get the URL of a channel banner using the channel ID. 
        """
        service = self.service

        try:
            request = service.channels().list(
                part="brandingSettings",
                id=channel_id
            )
            response = request.execute()

            branding_settings = response.get("items", [])[0]["brandingSettings"]
            banner_url = branding_settings["image"]["bannerImageUrl"]
            return banner_url

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None
    
    def get_channel_banner_default_url(self):
        """
        Get the default URL of a channel banner.
        """
        service = self.service

        try:
            request = service.channelBanners().insert(
                part="brandingSettings"
            )
            response = request.execute()

            banner_url = response.get("brandingSettings", {}).get("image", {}).get("bannerImageUrl")
            return banner_url

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def delete_channel_banner(self, channel_id):
        service = self.service

        try:
            service.channels().update(
                part="brandingSettings",
                body={
                    "id": channel_id,
                    "brandingSettings": {
                        "image": {
                            "bannerExternalUrl": ""
                        }
                    }
                }
            ).execute()

            print("Channel banner has been deleted successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    
    #//////////// ACTIVITIES ////////////
    
    def get_my_recent_activities(self, max_results=10):
        """
        This function retrieves recent activities for the authenticated user. 
        It prints information about uploaded videos, liked videos, and comments 
        made by the user.
        """
        service = self.service
        try:
            request = service.activities().list(
                part="snippet,contentDetails",
                mine=True,
                maxResults=max_results
            )
            response = request.execute()
            for activity in response["items"]:
                activity_type = activity["snippet"]["type"]
                if activity_type == "upload":
                    video_title = activity["snippet"]["title"]
                    video_id = activity["contentDetails"]["upload"]["videoId"]
                    print(f"Uploaded Video: {video_title} (Video ID: {video_id})")
                elif activity_type == "like":
                    video_title = activity["snippet"]["title"]
                    video_id = activity["contentDetails"]["like"]["resourceId"]["videoId"]
                    print(f"Liked Video: {video_title} (Video ID: {video_id})")
                elif activity_type == "comment":
                    comment_text = activity["snippet"]["displayMessage"]
                    video_title = activity["snippet"]["title"]
                    video_id = activity["contentDetails"]["comment"]["videoId"]
                    print(f"Commented on Video: {video_title} (Video ID: {video_id}) - Comment: {comment_text}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_activities_by_type(self, activity_type, max_results=10):
        """
        This method will retrieve activities of a specific type for the authenticated user. 
        (e.g., "upload", "like", or "comment") 
        """
        service = self.service

        try:
            request = service.activities().list(
                part="snippet,contentDetails",
                mine=True,
                maxResults=max_results,
                type=activity_type
            )
            response = request.execute()

            for activity in response["items"]:
                if activity_type == "upload":
                    video_title = activity["snippet"]["title"]
                    video_id = activity["contentDetails"]["upload"]["videoId"]
                    print(f"Uploaded Video: {video_title} (Video ID: {video_id})")
                elif activity_type == "like":
                    video_title = activity["snippet"]["title"]
                    video_id = activity["contentDetails"]["like"]["resourceId"]["videoId"]
                    print(f"Liked Video: {video_title} (Video ID: {video_id})")
                elif activity_type == "comment":
                    comment_text = activity["snippet"]["displayMessage"]
                    video_title = activity["snippet"]["title"]
                    video_id = activity["contentDetails"]["comment"]["videoId"]
                    print(f"Commented on Video: {video_title} (Video ID: {video_id}) - Comment: {comment_text}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_activities_since_date(self, start_date, max_results=10):
        """
        This method retrieves activities for the authenticated user since a 
        specific date (provided as start_date).
        """
        service = self.service

        try:
            request = service.activities().list(
                part="snippet,contentDetails",
                mine=True,
                maxResults=max_results,
                publishedAfter=start_date
            )
            response = request.execute()

            for activity in response["items"]:
                activity_type = activity["snippet"]["type"]
                if activity_type == "upload":
                    video_title = activity["snippet"]["title"]
                    video_id = activity["contentDetails"]["upload"]["videoId"]
                    print(f"Uploaded Video: {video_title} (Video ID: {video_id})")
                elif activity_type == "like":
                    video_title = activity["snippet"]["title"]
                    video_id = activity["contentDetails"]["like"]["resourceId"]["videoId"]
                    print(f"Liked Video: {video_title} (Video ID: {video_id})")
                elif activity_type == "comment":
                    comment_text = activity["snippet"]["displayMessage"]
                    video_title = activity["snippet"]["title"]
                    video_id = activity["contentDetails"]["comment"]["videoId"]
                    print(f"Commented on Video: {video_title} (Video ID: {video_id}) - Comment: {comment_text}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_video_activities_by_channel(self, channel_id, max_results=10):
        """
        This method retrieves video upload activities for a specific 
        channel (identified by channel_id).
        """
        service = self.service

        try:
            request = service.activities().list(
                part="snippet,contentDetails",
                channelId=channel_id,
                maxResults=max_results,
                type="upload"
            )
            response = request.execute()

            for activity in response["items"]:
                video_title = activity["snippet"]["title"]
                video_id = activity["contentDetails"]["upload"]["videoId"]
                print(f"Uploaded Video: {video_title} (Video ID: {video_id})")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_channel_activity(self, channel_id, max_results=10):
        service = self.service

        try:
            request = service.activities().list(
                part="snippet",
                channelId=channel_id,
                maxResults=max_results
            )
            response = request.execute()

            for activity in response["items"]:
                print(activity["snippet"]["title"])

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_channel_activities(self, channel_id, max_results=10):
        """
        This method retrieves recent activities on a specific channel. 
        It prints information about uploaded videos, liked videos, and 
        comments made on the channel.
        """
        service = self.service

        try:
            request = service.activities().list(
                part="snippet,contentDetails",
                channelId=channel_id,
                maxResults=max_results
            )
            response = request.execute()

            for activity in response["items"]:
                activity_type = activity["snippet"]["type"]
                if activity_type == "upload":
                    video_title = activity["snippet"]["title"]
                    video_id = activity["contentDetails"]["upload"]["videoId"]
                    print(f"Uploaded Video: {video_title} (Video ID: {video_id})")
                elif activity_type == "like":
                    video_title = activity["snippet"]["title"]
                    video_id = activity["contentDetails"]["like"]["resourceId"]["videoId"]
                    print(f"Liked Video: {video_title} (Video ID: {video_id})")
                elif activity_type == "comment":
                    comment_text = activity["snippet"]["displayMessage"]
                    video_title = activity["snippet"]["title"]
                    video_id = activity["contentDetails"]["comment"]["videoId"]
                    print(f"Commented on Video: {video_title} (Video ID: {video_id}) - Comment: {comment_text}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_subscription_activity(self, max_results=10):
        service = self.service

        try:
            request = service.activities().list(
                part="snippet,contentDetails",
                home=True,
                maxResults=max_results
            )
            response = request.execute()

            for activity in response["items"]:
                channel_title = activity["snippet"]["title"]
                video_id = activity["contentDetails"]["upload"]["videoId"]
                print(f"New Upload from {channel_title}: https://www.youtube.com/watch?v={video_id}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_activities_from_playlist(self, playlist_id, max_results=10):
        """
        This method retrieves activities (videos) from a specific playlist. 
        It prints information about videos contained within the playlist.
        """
        service = self.service
        try:
            request = service.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=max_results
            )
            response = request.execute()
            for item in response["items"]:
                video_title = item["snippet"]["title"]
                video_id = item["snippet"]["resourceId"]["videoId"]
                print(f"Video in Playlist: {video_title} (Video ID: {video_id})")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
    
    #//////////// VIDEO CATEGORIES ////////////
    
    def get_all_video_categories(self, country_code):
        """
        This method retrieves all video categories available in a specific 
        region (identified by the regionCode). It prints information about 
        each category, including its ID and title.
        """
        service = self.service

        try:
            request = service.videoCategories().list(
                part="snippet",
                regionCode=f"{country_code}"
            )
            response = request.execute()

            for category in response["items"]:
                category_id = category["id"]
                category_title = category["snippet"]["title"]
                print(f"Category ID: {category_id}, Title: {category_title}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_video_category_by_id(self, category_id):
        """
        This method allows you to retrieve details about a specific 
        video category identified by its category_id. It prints information 
        about the category, including its title.
        """
        service = self.service

        try:
            request = service.videoCategories().list(
                part="snippet",
                id=category_id
            )
            response = request.execute()

            if "items" in response:
                category = response["items"][0]
                category_title = category["snippet"]["title"]
                print(f"Category ID: {category_id}, Title: {category_title}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_videos_in_category(self, category_id, max_results=10):
        """
        This method retrieves videos that belong to a specific video category, 
        identified by category_id. It prints information about each video, including 
        its title and video ID.
        """
        service = self.service

        try:
            request = service.search().list(
                part="snippet",
                type="video",
                maxResults=max_results,
                videoCategoryId=category_id
            )
            response = request.execute()

            for video in response["items"]:
                video_title = video["snippet"]["title"]
                video_id = video["id"]["videoId"]
                print(f"Video Title: {video_title} (Video ID: {video_id})")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_most_popular_videos_in_category(self, category_id, max_results=10):
        """
        This method retrieves the most popular videos in a specific video category, 
        ordered by the number of views.
        """
        service = self.service

        try:
            request = service.search().list(
                part="snippet",
                type="video",
                maxResults=max_results,
                videoCategoryId=category_id,
                order="viewCount"
            )
            response = request.execute()

            for video in response["items"]:
                video_title = video["snippet"]["title"]
                video_id = video["id"]["videoId"]
                print(f"Video Title: {video_title} (Video ID: {video_id})")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_videos_by_categories(self, category_ids, max_results=10):
        """
        This method allows you to retrieve videos that belong to multiple video categories. 
        Provide a list of category_ids, and it will return videos that are associated with 
        any of the specified categories.
        """
        service = self.service

        try:
            request = service.search().list(
                part="snippet",
                type="video",
                maxResults=max_results,
                videoCategoryId=",".join(category_ids)
            )
            response = request.execute()

            for video in response["items"]:
                video_title = video["snippet"]["title"]
                video_id = video["id"]["videoId"]
                print(f"Video Title: {video_title} (Video ID: {video_id})")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def search_video_categories(self, query, max_results=10):
        """
        This method allows you to search for video categories using a query. 
        It prints information about each category that matches the search query.
        """
        service = self.service

        try:
            request = service.videoCategories().list(
                part="snippet",
                maxResults=max_results,
                q=query
            )
            response = request.execute()

            for category in response["items"]:
                category_id = category["id"]
                category_title = category["snippet"]["title"]
                print(f"Category ID: {category_id}, Title: {category_title}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_video_category_details(self, category_id):
        """
        This method retrieves details about a specific video category identified by 
        its category_id, including its title and whether it's assignable to videos.
        """
        service = self.service

        try:
            request = service.videoCategories().list(
                part="snippet",
                id=category_id
            )
            response = request.execute()

            if "items" in response:
                category = response["items"][0]
                category_title = category["snippet"]["title"]
                category_assignable = category["snippet"]["assignable"]
                print(f"Category ID: {category_id}, Title: {category_title}, Assignable: {category_assignable}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    #//////////// CAPTIONS ////////////

    def get_caption_tracks(self, video_id):
        """
        This method retrieves the caption tracks (subtitles) available for 
        a specific video identified by video_id. It prints information about 
        each caption track, including its ID, language, and whether it is 
        auto-generated.
        """
        service = self.service
        try:
            request = service.captions().list(
                part="snippet",
                videoId=video_id
            )
            response = request.execute()

            for caption_track in response["items"]:
                track_id = caption_track["id"]
                language = caption_track["snippet"]["language"]
                is_auto_generated = caption_track["snippet"]["isAutoSynced"]
                print(f"Caption Track ID: {track_id}, Language: {language}, Auto-generated: {is_auto_generated}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def download_caption_track(self, track_id, output_file):
        """
        This function allows you to download a specific caption track 
        identified by track_id and save it to a local file specified by 
        output_file.
        """
        service = self.service

        try:
            request = service.captions().download(
                id=track_id
            )
            with open(output_file, "wb") as file:
                file.write(request.execute())

            print(f"Caption track downloaded and saved to {output_file}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def upload_caption_track(self, video_id, language, caption_file):
        """
        This method allows you to upload a new caption track (subtitle) for 
        a specific video identified by video_id. Provide the language of the 
        subtitle and the path to the caption file (caption_file).
        """
        service = self.service

        try:
            request = service.captions().insert(
                part="snippet",
                body={
                    "snippet": {
                        "videoId": video_id,
                        "language": language,
                        "name": "Caption Track",
                        "isDraft": False
                    }
                },
                media_body=googleapiclient.http.MediaFileUpload(caption_file, mimetype="text/vtt", resumable=True)
            )
            response = request.execute()

            print(f"Caption track uploaded with track ID: {response['id']}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def delete_caption_track(self, track_id):
        """
        This function allows you to delete a specific caption track 
        identified by track_id.
        """
        service = self.service

        try:
            request = service.captions().delete(
                id=track_id
            )
            response = request.execute()

            print(f"Caption track with ID {track_id} deleted successfully.")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def update_caption_track(self, track_id, language, new_name):
        """
        This function allows you to update the language and name of 
        an existing caption track identified by track_id.
        """
        service = self.service

        try:
            request = service.captions().update(
                part="snippet",
                body={
                    "id": track_id,
                    "snippet": {
                        "language": language,
                        "name": new_name
                    }
                }
            )
            response = request.execute()

            print(f"Caption track with ID {track_id} updated successfully.")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_caption_track_by_id(self, track_id):
        """
        This method will directly retrieve the details of a specific caption 
        track by its ID. This can be useful if you already know the caption track 
        ID and want to access its metadata.
        """
        service = self.service

        try:
            request = service.captions().list(
                part="snippet",
                id=track_id
            )
            response = request.execute()

            if "items" in response:
                caption_track = response["items"][0]
                language = caption_track["snippet"]["language"]
                is_auto_generated = caption_track["snippet"]["isAutoSynced"]
                print(f"Caption Track ID: {track_id}, Language: {language}, Auto-generated: {is_auto_generated}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_caption_upload_status(self, track_id):
        """
        When you upload a new caption track, you can check the upload 
        status to see if it is still being processed. This can be helpful 
        if you want to wait until the caption track is fully available 
        before performing further operations.
        """
        service = self.service

        try:
            request = service.captions().list(
                part="snippet",
                id=track_id
            )
            response = request.execute()

            if "items" in response:
                caption_track = response["items"][0]
                status = caption_track["snippet"]["status"]["uploadStatus"]
                if status == "succeeded":
                    print(f"Caption track with ID {track_id} upload succeeded.")
                elif status == "failed":
                    print(f"Caption track with ID {track_id} upload failed.")
                else:
                    print(f"Caption track with ID {track_id} is still being processed.")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    #//////////// LOCALIZATION /////////////
    
    def get_channel_default_language(self, channel_id):
        service = self.service

        try:
            request = service.channels().list(
                part="snippet",
                id=channel_id
            )
            response = request.execute()

            default_language = response.get("items", [])[0]["snippet"]["defaultLanguage"]
            return default_language

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None
        
    def verify_video(self, video_id, country_code):
        """
        Verify if a video is available in a specific country using its ID.
        """
        service = self.service

        try:
            # Get video details for the specified video ID and country code
            request = service.videos().list(
                part="status",
                id=video_id,
                regionCode=country_code
            )
            response = request.execute()

            video_status = response.get("items", [])[0]["status"]
            is_available = video_status["uploadStatus"] == "processed" and video_status["privacyStatus"] == "public"

            return is_available

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
            return None

    def search_videos_by_location(self, query, location, location_radius, max_results=10):
        service = self.service
        try:
            request = service.search().list(
                part="snippet",
                q=query,
                type="video",
                location=location,
                locationRadius=location_radius,
                maxResults=max_results
            )
            response = request.execute()
            for item in response["items"]:
                print(item["snippet"]["title"])
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def search_videos_by_language(self, query, language_code, max_results=10):
        service = self.service
        try:
            request = service.search().list(
                part="snippet",
                q=query,
                type="video",
                relevanceLanguage=language_code,
                maxResults=max_results
            )
            response = request.execute()
            for item in response["items"]:
                print(item["snippet"]["title"])
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_video_details_in_languages(self, video_id, languages):
        """
        This method allows you to retrieve video details (title and description) in 
        different languages for a specific video identified by its video_id.
        """
        service = self.service

        try:
            for language in languages:
                request = service.videos().list(
                    part="snippet",
                    id=video_id,
                    hl=language
                )
                response = request.execute()

                if "items" in response:
                    video = response["items"][0]
                    video_title = video["snippet"]["title"]
                    video_description = video["snippet"]["description"]
                    print(f"Language: {language}, Title: {video_title}, Description: {video_description}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_videos_by_language(self, language_code, region_code="US", max_results=10):
        service = self.service
        try:
            request = service.search().list(
                part="snippet",
                regionCode=region_code,
                relevanceLanguage=language_code,
                type="video",
                maxResults=max_results
            )
            response = request.execute()
            for item in response["items"]:
                print(item["snippet"]["title"])
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")
     
    def get_video_category_by_region_and_language(self, region_code, language_code):
        """
        This method retrieves video categories available in a specific region_code and 
        language_code. It prints information about each category, including its ID and title.
        """
        service = self.service

        try:
            request = service.videoCategories().list(
                part="snippet",
                regionCode=region_code,
                hl=language_code
            )
            response = request.execute()

            for category in response["items"]:
                category_id = category["id"]
                category_title = category["snippet"]["title"]
                print(f"Category ID: {category_id}, Title: {category_title}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def set_video_localizations(self, video_id, localizations):
        """
        This method allows you to set the title and description of a video 
        in different languages. Provide a dictionary localizations where the 
        keys are language codes, and the values are dictionaries containing 
        the localized title and description for each language.
        """
        service = self.service

        try:
            for language, localization_data in localizations.items():
                title = localization_data.get("title", "")
                description = localization_data.get("description", "")

                request = service.videos().update(
                    part="snippet",
                    body={
                        "id": video_id,
                        "snippet": {
                            "title": title,
                            "description": description,
                            "defaultLanguage": language
                        }
                    }
                )
                response = request.execute()

                print(f"Video details for language {language} updated successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_channel_details_in_languages(self, channel_id, languages):
        """
        This method allows you to retrieve channel details (title and description) in 
        different languages for a specific channel identified by its channel_id.
        """
        service = self.service

        try:
            for language in languages:
                request = service.channels().list(
                    part="snippet",
                    id=channel_id,
                    hl=language
                )
                response = request.execute()

                if "items" in response:
                    channel = response["items"][0]
                    channel_title = channel["snippet"]["title"]
                    channel_description = channel["snippet"]["description"]
                    print(f"Language: {language}, Channel Title: {channel_title}, Description: {channel_description}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def set_channel_localizations(self, channel_id, localizations):
        """
        This method allows you to set the title and description of a channel in 
        different languages. Provide a dictionary localizations where the keys are 
        language codes, and the values are dictionaries containing the localized 
        title and description for each language
        """
        service = self.service

        try:
            for language, localization_data in localizations.items():
                title = localization_data.get("title", "")
                description = localization_data.get("description", "")

                request = service.channels().update(
                    part="snippet",
                    body={
                        "id": channel_id,
                        "snippet": {
                            "title": title,
                            "description": description,
                            "defaultLanguage": language
                        }
                    }
                )
                response = request.execute()

                print(f"Channel details for language {language} updated successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def list_available_caption_languages(self, video_id):
        """
        This method will retrieve a list of the available languages 
        for caption tracks on YouTube.
        """
        service = self.service

        try:
            request = service.captions().list(
                part="snippet",
                videoId=f"{video_id}"
            )
            response = request.execute()

            languages = set()
            for caption_track in response["items"]:
                language = caption_track["snippet"]["language"]
                languages.add(language)

            print("Available caption languages:")
            for language in languages:
                print(language)

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_captions_in_languages(self, video_id, languages):
        """
        This method allows you to retrieve captions (subtitles) for a \
        video in different languages. Provide a list of language codes, and 
        it will return information about each caption in the specified languages.
        """
        service = self.service

        try:
            for language in languages:
                request = service.captions().list(
                    part="snippet",
                    videoId=video_id,
                    hl=language
                )
                response = request.execute()

                if "items" in response:
                    caption = response["items"][0]
                    caption_language = caption["snippet"]["language"]
                    caption_name = caption["snippet"]["name"]
                    print(f"Language: {caption_language}, Caption Name: {caption_name}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def set_captions_localizations(self, caption_track_id, localizations):
        """
        This method allows you to set the name and language of a caption track 
        in different languages. Provide a dictionary localizations where the keys 
        are language codes, and the values are dictionaries containing the localized 
        caption name and language for each language.
        """
        service = self.service

        try:
            for language, localization_data in localizations.items():
                caption_name = localization_data.get("caption_name", "")
                caption_language = localization_data.get("caption_language", "")

                request = service.captions().update(
                    part="snippet",
                    body={
                        "id": caption_track_id,
                        "snippet": {
                            "name": caption_name,
                            "language": caption_language
                        }
                    }
                )
                response = request.execute()

                print(f"Caption details for language {caption_language} updated successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_thumbnails_in_languages(self, video_id, languages):
        """
        This method allows you to retrieve video thumbnails in different languages. 
        Provide a list of language codes, and it will return the URL of the default 
        thumbnail in each specified language
        """
        service = self.service

        try:
            for language in languages:
                request = service.thumbnails().set(
                    videoId=video_id,
                    language=language
                )
                response = request.execute()

                if "items" in response:
                    thumbnails = response["items"]
                    thumbnail_default = thumbnails[0]["default"]["url"]
                    print(f"Language: {language}, Default Thumbnail URL: {thumbnail_default}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def set_thumbnail_localizations(self, video_id, localizations):
        """
        This method allows you to set the thumbnail URL for a video in 
        different languages. Provide a dictionary localizations where the 
        keys are language codes, and the values are dictionaries containing 
        the localized thumbnail URL for each language.
        """
        service = self.service

        try:
            for language, localization_data in localizations.items():
                thumbnail_url = localization_data.get("thumbnail_url", "")

                request = service.thumbnails().set(
                    videoId=video_id,
                    language=language,
                    media_body=thumbnail_url
                )
                response = request.execute()

                print(f"Thumbnail URL for language {language} set successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    #//////////// REPORTING ABUSE ////////////
    
    def report_video(self, video_id, reason, additional_comments=None):
        """
        This method allows users to report a video for abuse. The reason parameter 
        specifies the reason for reporting, and additional_comments can be used to 
        provide additional context.
        """
        service = self.service

        try:
            request = service.videos().reportAbuse(
                part="snippet",
                videoId=video_id,
                reasonId=reason,
                comments=additional_comments
            )
            response = request.execute()

            print(f"Video with ID {video_id} reported for abuse successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def report_channel(self, channel_id, reason, additional_comments=None):
        """
        This method allows users to report a channel for abuse. The reason parameter 
        specifies the reason for reporting, and additional_comments can be used to 
        provide additional context.
        """
        service = self.service

        try:
            request = service.channels().reportAbuse(
                part="snippet",
                channelId=channel_id,
                reasonId=reason,
                comments=additional_comments
            )
            response = request.execute()

            print(f"Channel with ID {channel_id} reported for abuse successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def report_playlist(self, playlist_id, reason, additional_comments=None):
        """
        This method allows users to report a playlist for abuse. The reason 
        parameter specifies the reason for reporting, and additional_comments 
        can be used to provide additional context
        """
        service = self.service
        try:
            request = service.playlists().reportAbuse(
                part="snippet",
                playlistId=playlist_id,
                reasonId=reason,
                comments=additional_comments
            )
            response = request.execute()

            print(f"Playlist with ID {playlist_id} reported for abuse successfully!")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_abuse_report_reason_categories(self):
        """
        This method retrieves the categories of abuse report reasons 
        available on YouTube. It lists the categories and their corresponding IDs.
        """
        service = self.service

        try:
            request = service.videoAbuseReportReasons().list(
                part="snippet"
            )
            response = request.execute()

            for reason_category in response["items"]:
                category_id = reason_category["id"]
                category_label = reason_category["snippet"]["label"]
                print(f"Category ID: {category_id}, Label: {category_label}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    def get_abuse_report_reasons_in_category(self, category_id):
        """
        This method retrieves the abuse report reasons available within 
        a specific category_id. It lists the reasons and their corresponding IDs.
        """
        service = self.service

        try:
            request = service.videoAbuseReportReasons().list(
                part="snippet",
                hl="en",
                videoId=category_id
            )
            response = request.execute()

            for reason in response["items"]:
                reason_id = reason["id"]
                reason_label = reason["snippet"]["label"]
                print(f"Reason ID: {reason_id}, Label: {reason_label}")

        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    
    