import threading, os, shutil, errno, Queue

#creates a thread class to copy both file trees and individual files
class thread(threading.Thread):
    def __init__(self, queue, src, dest):
        threading.Thread.__init__(self)
        self.queue = queue
        self.src=src
        self.dest=dest 

        #print self.src
    def run(self):
        try:
            #if the passed source is a tree (iMovie Projects only)
            #copy the entire tree to the destination
            if os.path.isdir(self.src):
                shutil.copytree(self.src, self.dest)
            else:
                shutil.copy(self.src, self.dest)

            #send the message that the progress has moved 1 files worth
            self.queue.put(1)

        except OSError as exc:
            #if the directory already exits
            if exc.errno == errno.EEXIST:
                #in future change this to compare files
                #if lock file exists in location, do nothing

                #remove the file and any child files
                shutil.rmtree(self.dest)

                #try to copy again
                if os.path.isdir(self.src):
                    shutil.copytree(self.src, self.dest)
                else:
                    shutil.copy(self.src, self.dest)

                self.queue.put(1)
            else:
                raise