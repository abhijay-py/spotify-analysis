import os

def update_gitignore(folder_name):
    jsonfiles = [i for i in os.listdir(folder_name) if i[-5:] == ".json"]
    pyfiles = os.listdir("__pycache__")

    with open(".gitignore", "w") as f:
        for file in jsonfiles:
            f.write(folder_name+"/"+file+"\n")
        for file in pyfiles:
            f.write("__pycache__/"+file+"\n")



