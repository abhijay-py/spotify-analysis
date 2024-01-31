import os

def update_gitignore(folder_name):
    jsonFiles = [i for i in os.listdir(folder_name) if i[-5:] == ".json"]
    zipFiles = [i for i in os.listdir() if i[-4:] == ".zip"]

    with open(".gitignore", "w") as f:
        for file in jsonFiles:
            f.write(folder_name+"/"+file+"\n")
        for file in zipFiles:
            f.write(file+"\n")
        f.write("__pycache__\n")
        f.write("testing.py\n")
        f.write("Spotify_Analysis_Files\n")
        f.write("Spotify_Zipfiles\n")