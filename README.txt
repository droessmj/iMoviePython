iMovie Fix README
--------------------------------------------------------------------------------------------------------

easygui.py contains the source for the easygui dialog boxes used within OpeniMovie.py and SaveOnExit.py



OpeniMovie.py and SaveOnExit.py are the main loop for each of their respective applications.


ProgressBar.py is a class that is implemented both by the OpeniMovie and SaveOnExit to display the progress of the files being copied over.


ThreadedClient.py is instantiated by the ProgressBar.py to hand off the copying of files.



setupOpen.py and setupSave.py are used in the terminal to generate Mac OS X applications from the source of OpeniMovie.py and SaveOnExit.py

the command syntax to generate an application:
-make sure the current directory is the directory containing the python files
-'python setupOpen.py py2app'
-this will create both a build and dist folder -- the application will be in the dist folder

all the .pyc files are compiled classes for use in the packaged application