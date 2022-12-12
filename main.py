import requests, json, sys, shutil, os

with open("config.json") as f:
    CONFIG = json.load(f)

URL = "https://api.curseforge.com"
API_KEY = CONFIG["apiKey"]

PAGE_SIZE = 50
MAX_RESPONSE_INDEX = 10000
    
modIds = CONFIG["modProjectsIds"]

def handleResponse(response):
    if response == 200:
        return True
    
    elif response == 404:
        print(f"Mod for project id {download_urls['data'][0]} not found")
        input("Press enter to exit")
        sys.exit()
                
    elif response == 500:
        print("Internal Server Error <500>")
        input("Press enter to exit")
        sys.exit()

    else:
        print(f"Response error code: <{download_urls['responseCode']}>")
        input("Press enter to exit")
        sys.exit()
    
def getFiles(modIds, game_versions):
    headers = {
        "Accept": "application/json",
        "x-api-key": API_KEY
    }

    params = {
        "gameId": "432", # Minecraft Game ID
        "pageSize": PAGE_SIZE
    }

    urls = {}
    for modName in modIds:
        modId = modIds[modName]
        downloadUrl = None
        fileName = None
        
        for responseIndex in range(0, MAX_RESPONSE_INDEX, PAGE_SIZE):
            params["index"] = responseIndex
            
            response = requests.get(URL + f"/v1/mods/{modId}/files", params=params, headers=headers)
            if response.status_code == 200:
                responseJson = json.loads(response.text)
                
                if responseJson["pagination"]["totalCount"] == 0:
                    break
                
                filesData = responseJson["data"]
                try:
                    fileInfo = next(file for file in filesData if game_versions.issubset(file["gameVersions"]))
                    downloadUrl = fileInfo["downloadUrl"]
                    fileName = fileInfo["fileName"]
                    break
                
                except StopIteration:
                    continue
            else:
                return {"responseCode": response.status_code, "data": [modId]}
                
        urls[modName] = {"downloadUrl": downloadUrl, "fileName": fileName}
    
    return {"responseCode": 200, "data": urls}

def copyFilesFromOldInstance(oldInstancePath, newInstancePath):
    toCopyFiles = CONFIG["toCopyFiles"]
    toCopyDirs = CONFIG["toCopyDirs"]
    
    try:
        for file in toCopyFiles:
            shutil.copy(os.path.join(oldInstancePath, file), newInstancePath)
        for dir in toCopyDirs:
            shutil.copytree(os.path.join(oldInstancePath, dir), os.path.join(newInstancePath, dir), dirs_exist_ok=True)
    except FileNotFoundError as e:
        print(e)
        sys.exit()



# game versions
userInput = input("Type Minecraft versions to work with (seperate with `;`(no space between) (Fabric starts with uppercase `F`): ")
game_versions = set(userInput.split(";"))

# paths

try:
    availableDirs = next(os.walk(CONFIG["userPaths"]["minecraftInstancesPath"]))[1]
except StopIteration:
    print("Wrong Minecraft instances path (check config.json)")
    input("Press enter to exit")
    sys.exit()
    
print()
for i, elem in enumerate(availableDirs):
    print(f"{i+1}) {elem}\n")

userInput = input(f"Choose last instance (type number) (last used - {CONFIG['lastUsedDir']}) (leave empty if use last): ")
oldPath = os.path.join(CONFIG["userPaths"]["minecraftInstancesPath"], (CONFIG['lastUsedDir'] if userInput == "" else availableDirs[int(userInput)-1]), ".minecraft/")
userInput = input(f"Choose new instance (type number): ")
selectedNewDir = availableDirs[int(userInput)-1]
newPath = os.path.join(CONFIG["userPaths"]["minecraftInstancesPath"], selectedNewDir, ".minecraft/")

download_urls = getFiles(modIds, game_versions)

if handleResponse(download_urls["responseCode"]):
    filesInfo = download_urls["data"]
    
    notAvailableMods = [name for name in filesInfo if filesInfo[name]["downloadUrl"] is None]
    
    if len(notAvailableMods) > 0:
        print("List of mods that are not available for given Minecraft versions:")
        for name in filesInfo:
            print(name)
        
        if input("Do you want to download rest anyway? (y/n)").lower() == "n":
            sys.exit()
            
    try:
        os.mkdir(os.path.join(newPath, "mods"))
    except FileExistsError:
        pass
    
    for modName in filesInfo:
        response = requests.get(filesInfo[modName]["downloadUrl"])
        if handleResponse(response.status_code):
            with open(os.path.join(newPath, "mods/", filesInfo[modName]["fileName"]), "wb") as f:
                f.write(response.content)
    
    copyFilesFromOldInstance(oldPath, newPath)
    
    CONFIG["lastUsedDir"] = selectedNewDir
    with open("config.json", "w") as f:
        f.write(json.dumps(CONFIG))
        
elif download_urls["responseCode"] == 404:
    print(f"Mod for project id {download_urls['data'][0]} not found")
    input("Press enter to exit")
    sys.exit()
                
elif download_urls["responseCode"] == 500:
    print("Internal Server Error <500>")
    input("Press enter to exit")
    sys.exit()

else:
    print(f"Response error code: <{download_urls['responseCode']}>")
    input("Press enter to exit")
    sys.exit()
