import distutils.core, os, shutil, errno, threading, Queue, time, ThreadedClient, subprocess
import Tkinter as tk
import ttk

#define a class to create a progress bar that creates threads to copy files, then
#updates the bar on the return of the finished thread
class ProgressBar(tk.Tk):
    #takes in two directories, a destination, and the specific name of the projects and events directories
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
                    dirToPass = self.EventsDir
                    #set the destination "/Users/" + username + "/Movies/iMovie Events"
                    destDir = self.dest+dirToPass+"/"
                    #set the source directory as the project drive directory passed in
                    srcDir = dir

                    #create arrays to hold all files and directories from the source
                    files = []
                    d = []

                    #for all the files and directories in the parent directory
                    for (dirpath, dirnames, filenames) in os.walk(dir):
                        #for each item in the parent directory
                        for child in os.listdir(dir):
                            if os.path.isdir(os.path.join(dir, child)):
                                #append is used for individual strings
                                d.append(child)
                        for file in filenames:
                            #add each file
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
                    dirToPass = self.ProjectsDir
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