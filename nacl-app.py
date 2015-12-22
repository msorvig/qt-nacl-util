# build Qt applications for several Qt builds.
# usage: nacl-app app-source-dir qt-builds-dir

import argparse
from subprocess import Popen
from os import path
import os
import sys
import glob

parser = argparse.ArgumentParser()
parser.add_argument('input', nargs='*')
parser.add_argument('-d', '--dryrun',   action='store_true',   help='dry run. print commands only. (might create directories)')
args = parser.parse_args()
if len(args.input) <= 0:
    print("Usage: nacl-app <app-sources-dir> <qt-builds-dir>")
    print("")
    print("nacl-app (shadow) builds one or more applications for one or more")
    print("Qt builds. It iterates through the directory structure in <app-sources-dir>,")
    print("recreating it in the current working directory as it goes. When it")
    print("finds a .pro file it stops iterating and builds the profile for")
    print("each Qt build in <qt-builds-dir>, using qmake + make.")
    print("")
    sys.exit(0)

# write command line to file for easy access
with open("ans", "w") as ansFile:
    commandline = ' '.join(sys.argv).replace('.py', '')
    ansFile.write(commandline)
    ansFile.write('\n')

appSourceDir = path.abspath(args.input[0])
qtBuildsDir = path.abspath(args.input[1])
qtBuildNames = os.walk(qtBuildsDir).next()[1]
dryrun = args.dryrun

print ''
print 'app source dir: ' + appSourceDir
print 'qt builds dir : ' + qtBuildsDir
print 'qt build names: ' + str(qtBuildNames)

# build sources in the given directoty (must be relative to appSourceDir)
def processDirectory(directory):
    appSourceDirectory = path.join(appSourceDir, directory)

    print 'processs ' + appSourceDirectory

    # look for .pro files
    profiles = [file for file in os.listdir(appSourceDirectory) if file.endswith(".pro")]

    # if there is one go build it
    if len(profiles) >= 1:
        proFilePath = path.join(appSourceDirectory, profiles[0])
        buildDirectory(directory, proFilePath)
        return
    
    # if not recurse to subdirectories
    dirs = next(os.walk(appSourceDirectory))
    visibleDirs = [dir for dir in dirs[1] if not dir.startswith(".")]

    print visibleDirs
    for dir in visibleDirs:
        processDirectory(path.join(directory, dir))

# build the given .pro file in directory (relative to appSourceDir)
def buildDirectory(directory, profile):
    sourceDirectory = path.join(appSourceDir, directory)
    buildDirectory = directory
    
    # for each Qt build type
    for qtBuildName in qtBuildNames:
        targetDir = path.join(buildDirectory, qtBuildName)
        if not os.path.exists(targetDir):
            os.makedirs(targetDir)

        qtBuildDir = path.join(qtBuildsDir, qtBuildName)
        qmake = path.join(qtBuildDir, 'qtbase', 'bin', 'qmake')
        cmd = qmake + ' ' + profile + ' -r && make -k'
        print cmd
        if not dryrun:
            Popen(cmd, shell=True, cwd=targetDir)
print ''    

processDirectory("")

