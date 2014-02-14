import distutils.core, os, shutil, errno, threading, Queue, time, ThreadedClient, subprocess
import Tkinter as tk
import ttk



#define a class to create a progress bar that creates threads to copy files, then
#updates the bar on the return of the finished thread
class ProgressBar(tk.Tk):
    #takes in two directories, a destination, and the specific name of the projects and events directories
    def __init__(self, iMovieDirs, src, dest, ProjectsDir, EventsDir):
        tk.Tk.__init__(self)

        #define the progress bar gui
        self.wm_title("Please Wait")
        self.queue = Queue.Queue()
        self.listbox = tk.Listbox(self, width=18, height=1)
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
        self.src = src+"/"

        self.threads = []

        #set the initial maximum value of the progressbar
        self.progressbar["value"] = 0

        #set the initial maximum value of the progressbar
        self.progressbar["maximum"] = self.TotalFileCount

        #start thread creation
        self.spawnthreads()

    #method that launches threads
    def spawnthreads(self):
        #if there were directories passed in (iMovie Events and Projects)
        if not len(self.iMovieDirs) == 0:
            #for both Events and Projects
            for dir in self.iMovieDirs:
                #copy events folder as individual files
                if "Events" in dir:
                    #each file within the events folder will be discoverd, its directory created
                    #and the individual file copied to its destination

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
                        #define a default boolean for checking for file match
                        file_match = False

                        #if the file is greater than ~10mb check if it needs to be copied
                        #10000000 is number of bytes the file is
                        if os.stat(file).st_size > 10000000:
                            #if false is returned, copy up the file
                            file_match = self.fileCompare(file)

                            

                        #catch hidden ".strings" and ".DS_Store" files and don't copy
                        if not ".strings" in file and not ".DS_Store" in file and not file_match:
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
                            self.threads.append(self.thread)
                            #start the thread
                            self.thread.start()
                            #print file

                
                else:
                    #copy the projects folder as a tree as passing it as individual files
                    #resulted in iMovie being unable to read the resulting object
                    #also, projects folder is generally fairly small

                    dirToPass = self.ProjectsDir
                    destDir = self.dest+dirToPass+"/"

                    #create the directory if it isn't present
                    if not os.path.isdir(destDir):
                        os.makedirs(destDir)

                    self.TotalFileCount += 1
                    #set the maximum value of the progressbar
                    self.progressbar["maximum"] = self.TotalFileCount
                    self.thread = ThreadedClient.thread(self.queue, dir, destDir)
                    self.threads.append(self.thread)
                    self.thread.start()
                    #print dir
        #start monitoring the thread
        self.periodiccall()

    #this method will look to see if the large file matches a itself on the destination
    #if it matches, no changes have been made to this file and there is no need to copy it
    #this will speed up opens and saves -- all saves after the first one should be faster, and all
    #opens on a computer the user has used before will be sped up
    def fileCompare(self, file):
        file_match = False
        #concatenate the size of the file in bytes with a dash and the file's name
        fileData = str(os.stat(file).st_size) + "-" + os.path.basename(file)
        #if there is a hashlist in the destination, read from it to see if the current file
        #matches the hosted file, if so -- don't copy by setting file_hash_match to true
        if os.path.exists(self.dest+".matchlist"):
            with open(self.dest+".matchlist", "r") as myfile:
                data=myfile.read().replace('\n', '')

            if fileData in data:
                #print(fileData)
                file_match = True

        #when writing to the local drive, create a list of matches on the src drive
        #that track the large files being sent down

        #add the file to the remote location hash list
        if os.path.exists(self.src+".matchlist"):
            with open(self.src+".matchlist", "a+") as myfile:
                myfilecontents = myfile.read()
                #print(myfilecontents)
                if fileData not in myfilecontents:
                    myfile.write(fileData+"\n")
        else:
            fileWriter = open(self.src+".matchlist", 'w')
            fileWriter.write(fileData+"\n")
            fileWriter.close()

        return file_match


    #creates a method that recursively discovers and adds both 
    #directorys and files to lists. These are then returned and 
    #acted upon in the SpawnThread method

    #this will also create directories in the destination as they are discovered
    def copydir(self, srcDir, destDir, dir, files):
        #create local copies of passed in variables
        self.files = files
        srcToPass = srcDir + "/" + dir

        #create a local copy of the directories that is recursively extendend
        d = []

        #get all sub directories and child files of this directory
        for (dirpath, dirnames, filenames) in os.walk(srcToPass):
            #extend is used to add a list to an array
            d.extend(dirnames)
            #for each file
            for file in filenames:
                self.files.append(os.path.join(dirpath, file))
            break

        #check each sub-directory for children and recursively call this method again    
        for directory in d:
            destToPass = destDir + "/" + directory
            #if the directory does not exist in the destination
            if not os.path.isdir(destToPass):
                #create the directory
                os.makedirs(destToPass)
            #recursively extend the children
            d.extend(self.copydir(srcToPass, destToPass, directory, self.files))
        #returns the directories list
        return d 

    #method that monitors threads and updates upon completion
    def periodiccall(self):
        
        newCall = False
        for thread in self.threads:
            self.checkqueue()
            #if the thread is alive
            if thread.is_alive():
                if newCall == False:
                    newCall = True
                    #the thread is still working
                    self.after(500, self.periodiccall)

            else:
                self.threads.remove(thread)
                self.checkqueue()
                
                #print (self.progressbar["value"])
                #print (self.progressbar["maximum"])
                #if all the threads have returned the finished value
                if self.progressbar["value"] == (self.progressbar["maximum"]):
                    self.listbox.insert('0', "     100%  copied")
                    #close out of progress bar class
                    self.after(500, self.quit())

            print(len(self.threads))
        
        #if there are still threads alive, go and rescue them
        if len(self.threads) > 0:
            self.checkqueue()
            self.after(500, self.periodiccall)

    #method for checking the queue
    def checkqueue(self):

        while self.queue.qsize():
            try:
                #msg will be 1 if it can access the queue
                msg = self.queue.get(0)

                if(msg == 1):
                    #set the progess and update
                    progress = int((self.progressbar["value"] / float(self.progressbar["maximum"])) * 100)
                
                    #insert the new progress into the progress box
                    self.listbox.insert('0', (str(progress) + "%  copied..."))

                    #move forward each time a file is copied
                    self.progressbar["value"] += msg
                else:
                    self.listbox.insert('0', msg)                
            except Queue.Empty:
                pass




