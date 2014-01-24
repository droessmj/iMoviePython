#Created by Michael Droessler in Spring 2014
#Future support quetions can be sent to ----
#Email: droessmj@gmail.com
#Phone: 608-778-2457

#import other python files necessary to run application
import easygui, webbrowser, distutils.core, getpass, os, shutil, errno, threading, Queue, time, ThreadedClient, subprocess
import Tkinter as tk
import ttk

#define a class to create a progress bar that creates threads to copy files, then
#updates the bar on the return of the finished thread
class ProgressBar(tk.Tk):
    def __init__(self, iMovieDirs, dest, ProjectsDir, EventsDir):
        tk.Tk.__init__(self)
        #define the progress bar gui
        self.wm_title("Please Wait")
        self.queue = Queue.Queue()
        self.listbox = tk.Listbox(self, width=12, height=1)
        self.progressbar = ttk.Progressbar(self, orient='horizontal',
                                           length=500, mode='determinate')
        self.listbox.pack(padx=10, pady=10)
        self.progressbar.pack(padx=10, pady=10)

        #create local copies of the passed in variables
        self.TotalFileCount = 0
        self.iMovieDirs = iMovieDirs
        self.dest = dest
        self.ProjectsDir = ProjectsDir
        self.EventsDir = EventsDir

        #set the maximum value of the progressbar
        self.progressbar["maximum"] = self.TotalFileCount
        #delay one second
        time.sleep(1)
        #start thread creation
        self.spawnthreads()
        time.sleep(1)

    #method that launches threads
    def spawnthreads(self):
        #if there were directories passed in (iMovie Events and Projects)
        if not len(self.iMovieDirs) == 0:
            #for both Events and Projects
            for dir in self.iMovieDirs:
                #copy events folder as individual files
                if "Events" in dir:
                    dirToPass = EventsDir
                    #set the destination "/Users/" + username + "/Movies/iMovie Events"
                    destDir = self.dest+dirToPass+"/"
                    #set the source directory as the project drive directory passed in
                    srcDir = dir

                    #create arrays to hold all files and directories from the source
                    files = []
                    d = []

                    for (dirpath, dirnames, filenames) in os.walk(dir):
                        for child in os.listdir(dir):
                            if os.path.isdir(os.path.join(dir, child)):
                                #append is used for individual strings
                                d.append(child)
                        for file in filenames:
                            files.append(os.path.join(dirpath, file))
                        break

                    #create all necessary directories
                    for directory in d:
                        if not os.path.isdir(destDir+directory):
                            os.makedirs(destDir+directory)  
                        self.copydir(srcDir, destDir+directory, directory, files)           

                    #for each file, copy it over
                    for file in files:
                        #catch hidden ".strings" and ".DS_Store" files and don't copy
                        if not ".strings" in file and not ".DS_Store" in file:
                            self.TotalFileCount += 1
                            #set the maximum value of the progressbar
                            self.progressbar["maximum"] = self.TotalFileCount
            
                            #the destination directory is the full file name with the destination 
                            #replacing the actual source location

                            destStartIndex = file.find("iMovie Events.localized/")
                            if destStartIndex is -1:
                                destStartIndex = file.find("iMovie Events/")

                            #get a substring of the file to pass the correct destination    
                            destLocation = file[destStartIndex:len(file)]
                            #create the final desination directory
                            newDestDir = self.dest + destLocation

                            #create the copy file thread
                            self.thread = ThreadedClient.thread(self.queue, file, newDestDir)
                            #start the thread
                            self.thread.start()
                            #make sure the thread is monitored
                            self.periodiccall()

                #copy the projects folder as a tree
                else:
                    dirToPass = ProjectsDir
                    destDir = self.dest+dirToPass+"/"
                    #create the directory if it isn't present
                    if not os.path.isdir(destDir):
                        os.makedirs(destDir)

                    self.TotalFileCount += 1
                    #set the maximum value of the progressbar
                    self.progressbar["maximum"] = self.TotalFileCount
                    self.thread = ThreadedClient.thread(self.queue, dir, destDir)
                    self.thread.start()
                    self.periodiccall()


    #creates a method that recursively discovers and adds both 
    #directorys and files to lists. These are then returned and 
    #acted upon in the SpawnThread method
    def copydir(self, srcDir, destDir, dir, files):
        #create local copies of passed in variables
        self.files = files
        srcToPass = srcDir + "/" + dir
        d = []

        #get all sub directories and child files of this directory
        for (dirpath, dirnames, filenames) in os.walk(srcToPass):
            #extend is used to add a list to an array
            d.extend(dirnames)
            for file in filenames:
                self.files.append(os.path.join(dirpath, file))
            break

        #check each sub-directory for children and recursively call this method again    
        for directory in d:
            destToPass = destDir + "/" + directory
            if not os.path.isdir(destToPass):
                os.makedirs(destToPass)
            #recursively extend the children
            d.extend(self.copydir(srcToPass, destToPass, directory, self.files))

        return d 

    def periodiccall(self):
        self.checkqueue()
        if self.thread.is_alive():
            self.after(500, self.periodiccall)
        else:
            #if all the threads have returned the finished value
            if self.progressbar["value"] >= (self.progressbar["maximum"]-1):
                    #close out of progress bar class
                    self.quit()
                    self.destroy()
            else:
                #I am aware that the placement here is illogical, however if this is removed and a the logic is 
                #only the if self.progressbar['value'], a tkinter error is thrown as multiple threads attempt to access one 
                #value at once...this is currently the only method to catch any returns made after the projects thread dies
                self.after(500, self.periodiccall)
                

    def checkqueue(self):

        while self.queue.qsize():
            
            try:
                msg = self.queue.get(0)

                #set the progess and update
                progress = int((self.progressbar["value"] / float(self.progressbar["maximum"])) * 100)
                self.listbox.insert('0', (str(progress) + "%  copied..."))

                #move forward each time a file is copied
                self.progressbar["value"] += msg                
            except Queue.Empty:
                pass



####################################################################################################################################################################################################
#start of the main#

#username of logged in user
username = getpass.getuser()

#get location of movies folder and store as string
dest = "/Users/" + username + "/Movies/"

#string constant of path to iMovie
iMovie = "/Applications/iMovie.app"

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
    if not os.path.isdir("/Volumes/project"):
        #map project drive
        print("This feature not yet implemented")

    #get location of Project Drive folder to import
    src = easygui.diropenbox(msg="Select a Project Drive folder to load your iMovie project from...",default="/Volumes/project")


    #get all the child directories
    dirs = [name for name in os.listdir(src)
                if os.path.isdir(os.path.join(src, name))]

    #if an empty folder is selected, just open iMoive
    if dirs == []:
        #add a lock file to the movies directory on the local machine
        #if this file is present, then an open will not overwrite the local 
        #copy with the project drive copy.  This is for dealing with an imovie 
        #crash where there is a more recent local copy than remote copy
        fileWriter = open(dest+".lockfile", 'w')
        fileWriter.write("currently locked -- do not tamper with this file")
        fileWriter.close()
        #launch regular iMovie
        os.system("open -a "+iMovie+"")
        #exit application
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

    #setup and start the progress bar
    app = ProgressBar(iMovieDirs, dest, ProjectsDir, EventsDir)
    #give the app the priority loop
    app.mainloop()

    #if the Movies directory doesn't contain "iMovie Events", create the folder as it is needed for iMovie to run
    if EventsDir == "":
        EventsDir = dest+"iMovie Events.localized"
    eventsExists = os.path.isdir(EventsDir)
    if eventsExists is False:
        os.makedirs(EventsDir) 


    #add a lock file to the movies directory on the local machine
    #if this file is present, then an open will not overwrite the local 
    #copy with the project drive copy.  This is for dealing with an imovie 
    #crash where there is a more recent local copy than remote copy
    fileWriter = open(dest+".lockfile", 'w')
    fileWriter.write("currently locked -- do not tamper with this file")
    fileWriter.close()


#launch regular iMovie
os.system("open -a "+iMovie+"")

#exit application
raise SystemExit