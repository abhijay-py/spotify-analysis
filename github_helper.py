import os

def update_gitignore(folder_name):
    jsonfiles = [i for i in os.listdir(folder_name) if i[-5:] == ".json"]

    with open(".gitignore", "w") as f:
        for file in jsonfiles:
            f.write(folder_name+"/"+file+"\n")
        f.write("__pycache__\n")
        f.write("testing.py\n")
        f.write("Spotify_Analysis_Files\n")