#Created by Michael Droessler in Spring 2014
#Future support questions can be sent to ----
#Email: droessmj@gmail.com
#Phone: 608-778-2457

#import other python files necessary to run application
import easygui, distutils.core, getpass, os, errno, Queue, time
import ProgressBar, ThreadedClient

####################################################################################################################################################################################################
#start of the main#

#username of logged in user
username = getpass.getuser()

#get location of movies folder and store as string
src = "/Users/" + username + "/Movies"

#get all the child directories of from the source folder
dirs = [name for name in os.listdir(src)
            if os.path.isdir(os.path.join(src, name))]

#if there are directories in the source folder -- aka user didn't run the save with nothing present
if not dirs == []:

    #the destination does not need definition until we have determined that there are files
    #within the source directory
    dest = ""
    if os.path.exists(src+"/.lockfile"):
        fileReader = open(src+"/.lockfile", 'r')
        #destination will be default be the folder from which they selected to open iMovie
        dest = fileReader.readline()
        dest+="/"
    else:
        #user picks save location if for some reason the lockfile is 
        #removed and/or corrupted
        dest = easygui.diropenbox(msg="Select a Project Drive folder to save your iMovie Project to",default="/Volumes/projects")
        #append a forward slash to the string (just leave it, it's needed)
        if dest != None:
            dest+="/"
        else:
            raise SystemExit

    #create a list to hold the iMovie Events and Projects source directories
    iMovieDirs = []

    #create blank strings
    EventsDir = ""
    ProjectsDir = ""

    #copy all directories containing iMovie from Movies folder to Project drive
    for dir in dirs:
        fullPath = src + "/" + dir
        #if the directory contains "iMovie"
        if "iMovie Events.localized" == dir:
            EventsDir = dir
            iMovieDirs.append(fullPath)
        elif "iMovie Projects.localized" == dir:
            ProjectsDir = dir
            iMovieDirs.append(fullPath)

    #when iMovie creates folders itself, it creates .localized folders. However, if a user were to 
    #manually create the Events folder then they would not have a .localized folder

    #if there wasn't a localized set of folders, look for a general set
    if EventsDir == "" and ProjectsDir == "":
        for dir in dirs:
            #create the full source path
            fullPath = src + "/" + dir
            if "iMovie Events" == dir:
                EventsDir = dir
                iMovieDirs.append(fullPath)
            #if the directory contains "iMovie"
            elif "iMovie Projects" == dir:
                ProjectsDir = dir
                #add the string to the list
                iMovieDirs.append(fullPath)

    #setup and start the progress bar
    app = ProgressBar.ProgressBar(iMovieDirs, src, dest, ProjectsDir, EventsDir)
    #give the app the priority loop
    app.mainloop()

#remove the lockfile from the local directory
if os.path.exists(src+"/.lockfile"):
    os.remove(src+"/.lockfile")

#inform user upload has completed
easygui.msgbox(msg="Your iMovie project has finished uploading!", title="Notice", ok_button="OK")

#exit application
os._exit(1)
