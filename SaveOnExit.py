#Created by Michael Droessler in Spring 2014
#Future support questions can be sent to ----
#Email: droessmj@gmail.com
#Phone: 608-778-2457

#import other python files necessary to run application
import easygui, webbrowser, distutils.core, getpass, os, errno, Queue, time, ThreadedClient
import ProgressBar

####################################################################################################################################################################################################
#start of the main#

#username of logged in user
username = getpass.getuser()

#have user pick a save location
#easygui.msgbox(msg="Please select a Project Drive folder to save your iMovie Project to...", title="Notice", ok_button="OK")

#get location of movies folder and store as string
src = "/Users/" + username + "/Movies"

if os.path.exists(src+"/.lockfile"):
    fileReader = open(src+"/.lockfile", 'r')
    dest = fileReader.readline()
    dest+="/"
else:
    dest = ""

#should no longer occur unless lockfile failed
while dest is None or len(dest) < 5:
    dest = easygui.diropenbox(msg="Select a Project Drive folder to save your iMovie Project to",default="/Volumes/projects")
    #append a forward slash to the string (just leave it, it's needed)
    dest+="/"

#get all the child directories
dirs = [name for name in os.listdir(src)
            if os.path.isdir(os.path.join(src, name))]

if not dirs == []:
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
    app = ProgressBar.ProgressBar(iMovieDirs, dest, ProjectsDir, EventsDir)
    #give the app the priority loop
    app.mainloop()

#remove the lockfile
if os.path.exists(src+"/.lockfile"):
    os.remove(src+"/.lockfile")

#inform user upload has completed
easygui.msgbox(msg="Your iMovie project has finished uploading!", title="Notice", ok_button="OK")

#exit application
#sys.exit(0)
