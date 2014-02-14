import threading, os, shutil, errno, Queue, time
import subprocess


MAX_NORMAL_FILE_SIZE = 3221225472

#creates a thread class to copy both file trees and individual files
#file trees are copied in the case of the project file
#all the event files are copied as individual files
class thread(threading.Thread):
    def __init__(self, queue, src, dest):
        threading.Thread.__init__(self)

        #the queue is an object contained within ProgressBar that contains the threads
        #and how much progress has been accomplished.
        self.queue = queue

        self.src=src
        self.dest=dest 

    def run(self):
        try:
            #if the passed source is a tree (iMovie Projects only)
            #copy the entire tree to the destination
            if os.path.isdir(self.src):
                if os.path.isdir(self.dest):
                    #remove the folder and any child files
                    shutil.rmtree(self.dest)

                shutil.copytree(self.src, self.dest)
                self.queue.put(1)   
            else:
                self.fileCopy()

        except OSError as exc:
                #print "error caught"
                #if there is another error, raise it to the OS
                raise exc

    def fileCopy(self):
        #otherwise copy the individual file that is passed in
        if os.stat(self.src).st_size > MAX_NORMAL_FILE_SIZE:
            fileSize = os.stat(self.src).st_size

            #os system call to copy files larger than 3GB -- 'cp' is unix for copy
            copyProcess = subprocess.Popen(["cp", self.src, self.dest])

            n = 0
            #do not return the thread until the copyProcess is complete
            while copyProcess.poll() is None:
                time.sleep(1)
                if n % 5 == 0:
                    self.queue.put("  Moving large file.")
                elif n % 5 == 1:
                    self.queue.put("  Moving large file..")
                elif n % 5 == 2:
                    self.queue.put("  Moving large file...")
                elif n % 5 == 3:
                    self.queue.put("  Moving large file....")
                else:
                    self.queue.put("  Moving large file.....")
                n=n+1
            #copy any file metadata over
            shutil.copystat(self.src, self.dest)
        else:
            shutil.copy2(self.src, self.dest)

        #send the message that the progress has moved 1 files worth
        #print (self.dest + " --- finished")
        self.queue.put(1)       