import json
import os
from github_helper import *

def get_constants():
    constants = {}

    with open("constants.txt", "r") as f:
        text = f.readlines()

    for line in text:
        field, value = line.split("=")
        constants[field] = value

    return constants

def extract_data(folder_name):
    files = [i for i in os.listdir(folder_name) if i[-5:] == ".json"]
    data = {}

    for file in files:
        with open(file, "r") as f:
            pass




def main():
    constants = get_constants()
    #data = extract_data(constants["Spotify_Data_Folder"])
    #print(data)
    update_gitignore(constants["Spotify_Data_Folder"])


if __name__ == "__main__":
    main()
