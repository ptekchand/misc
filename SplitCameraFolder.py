#!C:/Python27/Python.exe
# -*- coding: utf-8 -*-
# This Python file uses the following encoding: utf-8

#------------------------------------------------------------------------------
# AS IS. NO WARRANTY. DO NOT USE if you're afraid of losing images. Always have a backup.

# These settings are now done by COMMAND LINE ARGUMENTS
# Sample command:
# Using relative path ('-r') from the current directory 'D:/Users/UserName/Pictures/From BlahCamera'
# >	python SplitCameraFolder.py "Camera roll" "ByYearMonth" -r

# Writen to split up the contents of the Camera roll:
# Since having more than a few 100 photos in a folder slows down explorer while
# it loads thumbnails or details.
# This script checks the 'date taken' of pictures (TODO: or 'date modified' of files)
# and moves them into sub folders by year/month (YYYY/YYYY-MM/).
# Writes to a log file with information about the operations it (will/) perform(s).

# Set perform_moves to True if you want the script to do actual moves and not report only.
# Use the argument -f or --move

# NEXT STEP. Get a viewer that will create thumbnails across sub folders to get an overview
# and pick and choose what to share. IrfanView?
#------------------------------------------------------------------------------
import sys
import codecs
if sys.stdout.encoding != 'cp850':
	sys.stdout = codecs.getwriter('cp850')(sys.stdout, 'strict')
if sys.stderr.encoding != 'cp850':
	sys.stderr = codecs.getwriter('cp850')(sys.stderr, 'strict')
#------------------------------------------------------------------------------

import os
import datetime
import exifread # pip install exifread
import errno 
import argparse

#------------------------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("src", help="source path")
parser.add_argument("dst", help="destination base path")
parser.add_argument("-r", "--relative", action="store_true",
		help="'src' and 'dst' are relative to current directory.")
parser.add_argument("-f", "--move", action="store_true",
		help="Perform actual moves on the files; Alternately reports only.")
parser.add_argument("-n", "--nreport", type=int,
		help="Report some progress after iterating over every N files.", default=250)
args = parser.parse_args()

start_path = args.src
writeToBase = args.dst
if args.relative:
	cwd = os.getcwd()
	start_path = os.path.normpath(os.path.join(cwd, start_path))
	start_path = start_path.replace("\\", "/") # Normalize; works on Windows too.
	writeToBase = os.path.normpath(os.path.join(cwd, writeToBase))
	writeToBase = writeToBase.replace("\\", "/")	

#start_path = 'C:/Users/UserName/Pictures/From BlahCamera'
# "{}/Camera roll/".format(start_path)
if os.path.exists(start_path) == False or os.path.isdir(start_path) == False:
	print "Specified source directory '{}' doesn't exist.".format(start_path)
	exit(0)

#writeToBase = '{}/ByYearMonth'.format(start_path)
if os.path.exists(writeToBase) == False or os.path.isdir(writeToBase) == False:
	print "Specified base destination directory '{}' doesn't exist.".format(writeToBase)
	exit(0)
	
perform_moves = args.move
reportProgressEveryN = args.nreport #250

#------------------------------------------------------------------------------
#from PIL import Image
#def get_date_taken(path):
#    return Image.open(path)._getexif()[36867]
#------------------------------------------------------------------------------
def get_exif_date_time_original(imagePath):
	with open(imagePath, 'rb') as fh:
		DateTimeOriginalTAG = "EXIF DateTimeOriginal"
		tags = exifread.process_file(fh, stop_tag=DateTimeOriginalTAG)
		dateTaken = None
		if DateTimeOriginalTAG in tags:
			dateTaken = tags[DateTimeOriginalTAG]
		return dateTaken

def test_get_date_time():
	imagePath = '{}/2015-07-11 to 2015-11-28/WP_003726.jpg'.format(start_path)
	dateTaken = get_exif_date_time_original(imagePath)
	print "Date Taken: {}. (type:{})".format( dateTaken, type(dateTaken) )
	#Date Taken: 2015:07:11 12:17:27. (type:<type 'instance'>) # Type: IfdTag
	print "Date Taken ISO: {}.".format( str(dateTaken) )

#test_get_date_time()
#exit(0)

# For Python >= 3.2, os.makedirs can skip the exception test using the third parameter exist_ok=True.
def mkdir_p(path):
	try:
		os.makedirs(path)
	except OSError as exc:  # Python >2.5
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else:
			raise
#------------------------------------------------------------------------------

# Neaten or throw-away. Wrap sub steps into their own functions.

moveDetailsPath = "MoveDetails-{}.txt".format( datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S") )
moveListHandle = open(moveDetailsPath, 'w') # Just assumes this will succeed

print "Logging details in: {}".format(moveDetailsPath)

def printAndLog(message):
	print message
	moveListHandle.write("{}\n".format(message) )

printAndLog("src: {}".format(start_path))
printAndLog("dst: {}".format(writeToBase))
printAndLog("Perform Moves: {}".format(perform_moves))
	
pathList = []
for filePath in os.listdir( start_path ): # Not walking subdirectories.
	if filePath.lower().endswith('.jpg'):
		pathList.append(filePath)
	else:
		extra = ""
		if os.path.isdir( "{}/{}".format(start_path, filePath) ):
			extra = " [sub directory]"
		message = "Skipping non .jpg: {}{}".format(filePath, extra)
		printAndLog(message)
		# Not .jpg: 0qtA007.tmp
		# Not .jpg: WP_20130223_190927Z.mp4 ..
print "Found {} .jpg files".format(len(pathList))

#with open('fileList.txt', 'w') as listHandle:
#	#listHandle.write(filePath+"\n")
subCounter = 0
counter = 0
pathDateTupleList = []
for filePath in pathList:
	fullFilePath = "{}/{}".format(start_path, filePath)
	dateTaken = get_exif_date_time_original( fullFilePath )
	if dateTaken is not None:
		pathDateTupleList.append( (filePath, dateTaken) )
	else:
		message = "WARN: Couldn't get date taken for '{}'.".format(filePath)
		printAndLog(message)
	counter += 1
	subCounter += 1
	if subCounter >= reportProgressEveryN:
		print "Read date time for {} files".format(counter)
		subCounter = 0
print "Done reading date time for {} files".format(counter)

subCounter = 0
counter = 0

if len(pathDateTupleList) > 0:
	moveListHandle.write("Recorded move details. [src, dst]\n" )

simulatedDirList = []
for filePath, dateTaken in pathDateTupleList:
	fullFilePath = "{}/{}".format(start_path, filePath)
	dateTakenStrComponents = str(dateTaken).split(' ')
	if len(dateTakenStrComponents) == 2:
		dateTaken_DateStr = dateTakenStrComponents[0]
		dateTaken_TimeStr = dateTakenStrComponents[1]
		dateTaken_DateStrSplit = dateTaken_DateStr.split(':')
		if len(dateTaken_DateStrSplit) == 3:
			dateTaken_Year, dateTaken_Month, dateTaken_Day = dateTaken_DateStrSplit
			destDirPath = "{}/{}/{}-{}".format(writeToBase, dateTaken_Year, dateTaken_Year, dateTaken_Month)

			if destDirPath not in simulatedDirList:
				simulatedDirList.append(destDirPath)
				if perform_moves:
					mkdir_p(destDirPath)
				print "INFO: Created dir: {}".format(destDirPath)
					
			fullDestPath = "{}/{}".format(destDirPath, filePath)
			if os.path.exists(fullDestPath) == False:
				if perform_moves:
					os.rename(fullFilePath, fullDestPath)
				moveListHandle.write("{}, {}\n".format(filePath, fullDestPath[len(writeToBase):]) )
			else:
				message = "WARN: Destination '{}' already exists!".format(fullDestPath[len(writeToBase):])
				printAndLog(message)
		else:
			message = "WARN: Unexpected date taken for '{}'.".format(filePath)
			printAndLog(message)
	else:
		message = "WARN: Unexpected Date/Time taken for '{}'.".format(filePath)
		printAndLog(message)
	
	counter += 1
	subCounter += 1
	if subCounter >= reportProgressEveryN:
		print "Set up move for {} files".format(counter)
		subCounter = 0
		
print "Done moving for {} files".format(counter) # Done moving for 3368 files.
moveListHandle.close()