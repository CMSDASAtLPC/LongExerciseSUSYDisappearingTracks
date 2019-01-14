#!/bin/env python
# by viktor.kutzner@desy.de

import os, sys
from glob import glob
from time import sleep
import datetime
import subprocess
import multiprocessing

jobscript = '''#!/bin/zsh
echo "$QUEUE $JOB $HOST"
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc6_amd64_gcc530
cd CMSBASE
#cmsenv
eval `scramv1 runtime -sh`
echo $CMSSW_BASE
cd CWD
COMMAND
if [ $? -eq 0 ]
then
    echo "Success"
else
    echo "Failed"
fi
'''

def ShellExec(command):
    os.system(command)


def runParallel(commands, runmode, dryrun=False, cmsbase=False, qsubOptions=False, ncores_percentage=0.70, dontCheckOnJobs=True, use_more_mem=False, use_more_time=False, burst_mode=False):

    if runmode == "multi":

        nCores = int(multiprocessing.cpu_count() * ncores_percentage)
        print "Using %i cores" % nCores

        pool = multiprocessing.Pool(nCores)
        return pool.map(ShellExec, commands)

    if runmode == "grid":
        
        if not cmsbase:
            if "CMSSW_BASE" in os.environ:
                cmsbase = os.environ["CMSSW_BASE"]
            else:
                print "No CMSSW environment set, you probably want to do this. Let's stop here..."
                return False

        print "Using CMSSW base", cmsbase

        return runCommands(commands, dryrun=dryrun, cmsbase=cmsbase, qsubOptions=qsubOptions, dontCheckOnJobs=dontCheckOnJobs, use_more_mem=use_more_mem, use_more_time=use_more_time, burst_mode=burst_mode)


def runCommands(commands, dryrun=False, birdDir="bird", cmsbase=False, qsubOptions=False, dontCheckOnJobs=False, useGUI=False, use_more_mem=False, use_more_time=False, burst_mode=False):

    print "Starting submission..."

    cwd = os.getcwd()

    if qsubOptions == False:
        qsubOptions = "h_vmem=4G,h_fsize=100G"

    os.system("mkdir -p %s" % birdDir)

    jobs = []
    nJobsDone = 0
    nJobsFailed = 0

    timestamp = datetime.datetime.now().strftime("%y-%m-%d-%H-%M-%S")
    for ifname, command in enumerate(commands):

        JobsPercentProcessed = int( 80 * float(ifname) / len(commands) )
        print "[" + JobsPercentProcessed * "#" + (80 - JobsPercentProcessed) * " " + "]"

        jobname = "job_%s_%s" % (timestamp, ifname)
        jobs.append(jobname)
        fjob = open('%s/' % birdDir + jobname + '.sh','w')

        if not cmsbase: cmsbase = cwd

        fjob.write(jobscript.replace('CWD',cwd).replace('COMMAND',command).replace('CMSBASE',cmsbase))
        fjob.close()
        os.chdir(birdDir)

        # actual job submission depending on host:
        if os.path.isfile("/usr/bin/condor_qsub"):

            additional_parameters = ""
            if use_more_mem:
                if use_more_mem == 1:
                    use_more_mem = 4096
                additional_parameters += "RequestMemory = %s\n" % use_more_mem
            if use_more_time:
                if use_more_time == 1:
                    use_more_time = 86400
                additional_parameters += "+RequestRuntime = %s\n" % use_more_time

            submission_file_content = """
                universe = vanilla
                should_transfer_files = IF_NEEDED
                log = %s.sh.log$(Cluster)
                executable = /bin/bash
                arguments = %s.sh
                initialdir = %s
                error = %s.sh.e$(Cluster)
                output = %s.sh.o$(Cluster)
                notification = Never
                %s
                priority = 0
                Queue
            """ % (jobname, jobname, cwd + "/" + birdDir, jobname, jobname, additional_parameters)

            with open(jobname + ".submit", 'w') as outfile:
                outfile.write(submission_file_content)

            cmd = "condor_submit %s.submit" % jobname
            if burst_mode:
                cmd = cmd + " &"

            print cmd
        elif os.path.isfile("/usr/sge/bin/lx-amd64/qsub"):
            cmd = 'qsub -l %s -cwd ' % qsubOptions + jobname + '.sh > /dev/null 2>&1 &'
            print cmd
        else:
            print "Not a submission node, exiting!"
            quit()

        if not dryrun:
            os.system(cmd)
            
        os.chdir('..')

    print "Jobs are running..."

    if dontCheckOnJobs: return

    # Check if jobs are finished:

    if not useGUI:

        interval = 5
        counter = 0
        while(len(jobs) != nJobsDone + nJobsFailed):
            counter += 1
            nJobsDone = 0
            nJobsFailed = 0
            for job in jobs:
                try:
                    jobOutputFile = glob("%s/%s.sh.o*" % (birdDir,job))[0]
                    ofile = open(jobOutputFile)
                    ofileContents = ofile.read()
                    if "Success" in ofileContents:
                        nJobsDone += 1
                    if "Failed" in ofileContents:
                        nJobsFailed += 1
                except:
                    pass

            PercentProcessed = int( 20 * float(nJobsDone + nJobsFailed) / len(jobs) )
            line = "[" + PercentProcessed*"#" + (20-PercentProcessed)*" " + "]\t" + "%s jobs, running: %s, done: %s, failed: %s. Running since %is..." % (len(jobs), len(jobs)-nJobsDone-nJobsFailed, nJobsDone, nJobsFailed, counter*interval)
            print line

            sleep(interval)
            
        return 0

    else:
   
        line = ""
        import curses

        class curses_screen:
            def __enter__(self):
                self.stdscr = curses.initscr()
                curses.cbreak()
                curses.noecho()
                self.stdscr.keypad(1)
                SCREEN_HEIGHT, SCREEN_WIDTH = self.stdscr.getmaxyx()
                return self.stdscr
            def __exit__(self,a,b,c):
                curses.nocbreak()
                self.stdscr.keypad(0)
                curses.echo()
                curses.endwin()

        with curses_screen() as stdscr:

            interval = 5
            counter = 0

            while(len(jobs) != nJobsDone + nJobsFailed):
                counter += 1
                nJobsDone = 0
                nJobsFailed = 0
                for job in jobs:
                    try:
                        jobOutputFile = glob("%s/%s.sh.o*" % (birdDir,job))[0]
                        ofile = open(jobOutputFile)
                        ofileContents = ofile.read()
                        if "Success" in ofileContents:
                            nJobsDone += 1
                        if "Failed" in ofileContents:
                            nJobsFailed += 1
                    except:
                        pass

                PercentProcessed = int( 20 * float(nJobsDone + nJobsFailed) / len(jobs) )
                line = "[" + PercentProcessed*"#" + (20-PercentProcessed)*" " + "]\t" + "%s jobs, running: %s, done: %s, failed: %s. Running since %is..." % (len(jobs), len(jobs)-nJobsDone-nJobsFailed, nJobsDone, nJobsFailed, counter*interval)
                stdscr.addstr(2,4, line)
                stdscr.refresh()

                sleep(interval)

        print line

    if nJobsFailed>0:

        print "There were failed jobs. Check error output files:\n"
        jobErrorFiles = glob("%s/%s.sh.e*" % (birdDir,job))
        for jobErrorFile in jobErrorFiles:
            print jobErrorFile

        print "\nAfter checking, resubmit with the following commands:"
        for shFile in glob("%s/%s.sh" % (birdDir,job)):
            print 'qsub -l %s -cwd ' % qsubOptions + shFile + '&'

        quit()

    return 0

