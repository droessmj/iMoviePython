#Created by Michael Droessler in Spring 2014
#Future support questions can be sent to ----
#Email: droessmj@gmail.com
#Phone: 608-778-2457

#import other python files necessary to run application
import easygui, webbrowser, distutils.core, getpass, os, shutil, errno, threading, Queue, time, subprocess
import ProgressBar, ThreadedClient

####################################################################################################################################################################################################
#start of the main#


#username of logged in user
username = getpass.getuser()

#get location of movies folder and store as string
dest = "/Users/" + username + "/Movies/"

#string constant of path to iMovie
iMovie = "/Applications/iMovie.app"

#define a method that will allow the application to exit in a situation where there is a new project being created -- ie there is no
#current project that is actually being opened by the application
def exitNewProject():
    #add a lock file to the movies directory on the local machine
    #if this file is present, then an open will not overwrite the local 
    #copy with the project drive copy.  This is for dealing with an imovie 
    #crash where there is a more recent local copy than remote copy
    fileWriter = open(dest+".lockfile", 'w')
    fileWriter.write(src)
    fileWriter.close()
    #launch regular iMovie
    os.system("open -a "+iMovie+"")
    #exit application
    raise SystemExit

if not os.path.exists(dest+".lockfile"):

    #query the user as to whether they have a project drive folder
    hasProjectDrive = easygui.ynbox(msg="Do you already have a folder on the Project Drive to save to?", title="Please confirm", choices=("Yes","No"))

    #if the user does not have a project drive folder direct them to where they can create one
    if hasProjectDrive == 0:
        #inform the user that they will have to create a project drive folder
        easygui.msgbox(msg="Please create a Project Drive folder...")
        #open default browser to the necessary page
        webbrowser.open("http://mass.uwec.edu",new="2")
        #exit application
        raise SystemExit

    #check if project drive is mapped else map it
    if not os.path.isdir("/Volumes/project") and not os.path.isdir("/Volumes/projects"):
        #create projects folder
        os.makedirs("/Volumes/projects")
        #map project drive making a terminal call
        subprocess.call(["/sbin/mount", "-t", "smbfs", "//"+username+"@mass.uwec.edu/projects", "/Volumes/projects"])
    
    #get location of Project Drive folder to import
    src = easygui.diropenbox(msg="Select a Project Drive folder to load your iMovie project from...",default="/Volumes/projects")
    if src == None:
        raise SystemExit("No source location was selected. Please run the application again and select a source directory.")

    #get all the child directories from source
    dirs = [name for name in os.listdir(src)
                if os.path.isdir(os.path.join(src, name))]

    #if an empty folder is selected, just open iMovie after creating the lockfile with the location
    if dirs == []:
        exitNewProject()

    #create a list to hold the iMovie Events and Projects source directories
    iMovieDirs = []

    #create blank strings
    EventsDir = ""
    ProjectsDir = ""

    #copy all directories containing iMovie from Project Drive to Movies folder
    for dir in dirs:
        fullPath = src + "/" + dir
        #if the directory contains "iMovie"
        if "iMovie Projects.localized" == dir:
            ProjectsDir = dir
            iMovieDirs.append(fullPath)
        elif "iMovie Events.localized" == dir:
            EventsDir = dir
            iMovieDirs.append(fullPath)

    #if there wasn't a localized set of folders, look for a general set
    if EventsDir == "" and ProjectsDir == "":
        for dir in dirs:
            #create the full source path
            fullPath = src + "/" + dir
            #if the directory contains "iMovie"
            if "iMovie Projects" == dir:
                ProjectsDir = dir
                #add the string to the list
                iMovieDirs.append(fullPath)
            elif "iMovie Events" == dir:
                EventsDir = dir
                iMovieDirs.append(fullPath)

    if iMovieDirs == []:
        exitNewProject()


    print(EventsDir)
    #setup and start the progress bar
    app = ProgressBar.ProgressBar(iMovieDirs, src, dest, ProjectsDir, EventsDir)
    #give the app the priority loop
    app.mainloop()

    #if the Movies directory doesn't contain "iMovie Events" or and "iMovie Events.localized"
    #create the folder as it is needed for iMovie to run
    checkforevents1= "iMovie Events.localized"
    checkforevents2 = "iMovie Events"
    #if there is no Events directory
    if not os.path.isdir(dest+checkforevents1) and not os.path.isdir(dest+checkforevents2) and not EventsDir == "":
        os.makedirs(EventsDir) 

    #add a lock file to the movies directory on the local machine
    #if this file is present, then an open will not overwrite the local 
    #copy with the project drive copy.  This is for dealing with an imovie 
    #crash where there is a more recent local copy than remote copy
    fileWriter = open(dest+".lockfile", 'w')
    fileWriter.write(src)
    fileWriter.close()


#launch regular iMovie
os.system("open -a "+iMovie+"")

#exit application
raise SystemExit