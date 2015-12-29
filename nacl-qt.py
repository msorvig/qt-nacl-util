# the swiss army knife of qt-nacl configuration and build tools

import argparse
from subprocess import Popen
from os import path
import os
import itertools
import sys

# possible configuration valuues
hostPlatform = 'mac'
possibleTargets = ['x86_glibc', 'x86_newlib', 'arm_newlib', 'pnacl'] 
possibleVariants = ['debug', 'release', 'debug-release']
possibleActions = ['configure', 'build', 'build-manual-tests', 'build-auto-tests']

# set up and parse command line configuration values
parser = argparse.ArgumentParser()
parser.add_argument('-q', '--qtsource', nargs=1,   help='Qt source code ')
parser.add_argument('-p', '--platform', nargs='*',   help='NaCl target platform: '+ ' '.join(possibleTargets))
parser.add_argument('-v', '--variant',  nargs='*',   help='build variant: ' + ' '.join(possibleVariants))
parser.add_argument('-a', '--action',   nargs='*',   help='action: ' + ' '.join(possibleActions))
parser.add_argument('-m', '--module',   nargs='*',   help='build additional modules')
parser.add_argument('-c', '--configure',nargs='*',   help='extra qt configure args')
parser.add_argument('-d', '--dryrun',   action='store_true',   help='dry run. print commands only. (might create directories)')
args = parser.parse_args()

# write command line to file for easy access
with open("ans", "w") as ansFile:
    commandline = ' '.join(sys.argv).replace('.py', '')
    ansFile.write(commandline)
    ansFile.write('\n')

# use default values for missing command line configuration values
qtsource = args.qtsource
platforms = args.platform # no default platform
variants = ['release'] if args.variant == None else args.variant
actions = ['configure', 'build'] if args.action == None else args.action
modules = ['qtbase'] if args.module == None else args.module
configure = [] if args.configure == None else args.configure
dryrun = args.dryrun

# print help and exit if no platform was specified
if len(platforms) == 0:
    parser.print_help()
    exit(0)

print ''
print 'qt source:  ' + ' '.join(qtsource)
print 'platforms : ' + ' '.join(platforms)
print 'variants  : ' + ' '.join(variants)
print 'actions   : ' + ' '.join(actions)
print 'modules   : ' + ' '.join(modules)
print 'conf. args: ' + ' '.join(configure)
print ''

# find the Qt root dir (expect the standard setup with qtbase, qtdeclarative, ect subdirs)
scriptfile =  __file__
qtdir = ''.join(qtsource)
qtbasedir = path.join(qtdir, "qtbase")
naclconfigureScript = path.join(qtbasedir, 'nacl-configure')
print 'Qt sources in: ' + qtdir

# perform each platform, variant, action
for platform, variant, action in itertools.product(platforms, variants, actions):
    print ''
    print '# ' + platform + ' ' + variant + ' ' + action
    buildwd = path.abspath(path.join(os.getcwd(), platform + '-' + variant))
    if not os.path.exists(buildwd):
        os.makedirs(buildwd)
    print 'build working directory: ' + buildwd

    if action == 'configure':
        # configure Qt
        configurearglist = ' '.join(["-"  + configurearg for configurearg in configure])
        cmd = naclconfigureScript
        if platform in ['host', 'emscripten']:
            cmd += ' ' + platform
        else:
            cmd +=  ' ' + hostPlatform + '_' + platform
        cmd += ' ' + variant + ' ' + configurearglist
        print 'call ' + cmd
        if not dryrun:
            Popen(cmd, shell=True, cwd=buildwd)
    elif action == 'build':
        # build Qt
        makeCommand = 'make ' + ' '.join(['module-' + module for module in modules])
        print makeCommand
        if not dryrun:
            Popen(makeCommand, shell=True, cwd=buildwd)

    elif action == 'build-manual-tests':
        # build nacl manual tests in tests/manual/nacl/
        qmake = path.abspath(path.join(buildwd, 'qtbase', 'bin', 'qmake'))
        naclTests = 'tests/manual/nacl/'
        testswd = path.join(buildwd, 'qtbase', naclTests)
        if not os.path.exists(testswd):
            os.makedirs(testswd)
        profile = path.join(qtbasedir, naclTests, 'nacl.pro')
        cmd = qmake + ' -r ' + profile + ' && make'
        print 'qmake: ' + qmake
        print 'build tests working directory: ' + testswd
        print 'cmd: ' + cmd
        if not dryrun:
            Popen(cmd, shell=True, cwd=testswd)

    elif action == 'build-auto-tests':
        # build Qt auto tests in tests/auto
        qmake = path.abspath(path.join(buildwd, 'qtbase', 'bin', 'qmake'))
        qtTests = 'tests/auto'
        testswd = path.join(buildwd, 'qtbase', qtTests)
        if not os.path.exists(testswd):
            os.makedirs(testswd)
        profile = path.join(qtbasedir, qtTests, 'auto.pro')
        cmd = qmake + ' -r ' + profile
        print 'qmake: ' + qmake
        print 'build tests working directory: ' + testswd
        print 'cmd: ' + cmd
        if not dryrun:
            Popen(cmd, shell=True, cwd=testswd)

    
    
    