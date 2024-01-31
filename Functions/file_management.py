import os
import csv
from zipfile import ZipFile


#Callled by get_data_from_zip for each file 
def _get_zip_data(filename, dataFolder, zipFolder, badFiles):
    files = os.listdir()

    with ZipFile("./"+zipFolder+"/"+filename) as f:
        f.extractall()
    
    newFiles = os.listdir()

    try:
        newFolder = [i for i in newFiles if i not in files][0]
    except IndexError:
        print("Temporary Folder from previous runs were not deleted.")
    
    if dataFolder not in files:
        os.rename(newFolder, dataFolder)
        
    else:
        folderFiles = os.listdir(newFolder)
        for file in folderFiles:
            try:
                os.remove("./"+dataFolder+"/"+file)
            except FileNotFoundError:
                pass
            os.rename("./"+newFolder+"/"+file, "./"+dataFolder+"/"+file)
        os.rmdir(newFolder)

    folderFiles = os.listdir(dataFolder)
    for file in folderFiles:
        if badFiles == file[:len(badFiles)]:
            os.remove("./"+dataFolder+"/"+file)
            continue


#Save data to a csv, typechar is {'ll': list of "lists"}
def save_to_csv(info, typeChar, output_file, reverse=False):
    if typeChar == 'll':
        with open("./Spotify_Analysis_Files/"+output_file, 'w', newline='', encoding="utf-8-sig") as f:
            csv_f = csv.writer(f)
            if not reverse:
                csv_f.writerows()
            else:
                for i in range(len(info) - 1, -1, -1):
                    csv_f.writerow(info[i])

#TODO: Modify prints into a log file
#Extract spotify data from all zipfiles in the zipfile folder
def get_data_from_zip(constants):
    folder = constants["Spotify_Zip_Folder"]
    folderFiles = os.listdir(folder)
    for file in folderFiles:
        if file[-4:] != ".zip":
            print("Non zipfile in zipfile folder.")
            continue
        _get_zip_data(file, constants["Spotify_Data_Folder"], constants["Spotify_Zip_Folder"], constants["Remove_Files"])

#Removes all json files that were extracted.
def remove_account_data(constants):
    folder = constants["Spotify_Data_Folder"]
    folderFiles = os.listdir(folder)
    for file in folderFiles:
        os.remove("./"+folder+"/"+file)
    os.rmdir(folder)

#TODO
#Removes all csv files created.
def remove_account_analysis(constants):
    pass
