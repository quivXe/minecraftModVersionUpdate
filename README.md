# minecraftModVersionUpdate
Updates every mod to given version and copies setting from last instance.
Before using you need to configure config.json.
"apiKey" you can get from https://console.curseforge.com/
"userPaths"["minecraftInstancesPath"] is path to Minecraft's instances directory
"toCopyFiles" are files to copy from last instance ("tempToCopyFiles" is useless, but there hotbar too so you can copy it)
"toCopyDirs" same as "toCopyFiles" but for directories
"modProjectsIds" is dictionary where key is display name (not important) and value is project id obtained from curseforge.com. Every mod has About project label where is project id. (listed mods are common used, but feel free to delete these)

