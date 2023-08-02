import youtube_api_tools

tube = youtube_api_tools.YouTubeAPIv3(
    "client_secret_671382908634-hudnrlsnhr3gqresomjga29a33s0chml.apps.googleusercontent.com.json",
    ["https://www.googleapis.com/auth/youtube.readonly"]
)
rgr_id = "UCZiVfeN-xX_U-xDyDipTB-A"
hk_pl_id = "PLTppU1ms5hVtoYP1gOPx_6RL7ERh90zpS"
    
print(tube.get_playlist_titles(10)) 
