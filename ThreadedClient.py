import threading, os, shutil, errno, Queue

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
                shutil.copytree(self.src, self.dest)
            else:
                #otherwise copy the individual file that is passed in
                shutil.copy(self.src, self.dest)

            #send the message that the progress has moved 1 files worth
            self.queue.put(1)

        except OSError as exc:
            #this will get thrown when copying up/down and the iMovie Projects directory already 
            #exists in the target destination
            if exc.errno == errno.EEXIST:
 
                 #remove the folder and any child files
                shutil.rmtree(self.dest)

                #try to copy again
                if os.path.isdir(self.src):
                    #copy the tree
                    shutil.copytree(self.src, self.dest)
                else:
                    #copy the file
                    shutil.copy(self.src, self.dest)

                self.queue.put(1)
            else:
                #if there is another error, raise it to the OS
                raise