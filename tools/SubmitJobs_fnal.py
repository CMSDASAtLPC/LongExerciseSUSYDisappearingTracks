import os, sys



defaultInfile = "/eos/uscms//store/user/lpcsusyhad/sbein/cmsdas19/Ntuples/Summer16.DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_104_RA2AnalysisTree.root"
defaultkey = defaultInfile.split('/')[-1].split('.root')[0]
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbosity", type=bool, default=False,help="analyzer script to batch")
parser.add_argument("-analyzer", "--analyzer", type=str,default='tools/ResponseMaker.py',help="analyzer")
parser.add_argument("-fin", "--fnamekeyword", type=str,default=defaultInfile,help="file")
parser.add_argument("-dtmode", "--dtmode", type=str, default='PixAndStrips',help="PixAndStrips, PixOnly, PixOrStrips")
parser.add_argument("-pu", "--pileup", type=str, default='Nom',help="Nom, Low, Med, High")
args = parser.parse_args()
fnamekeyword = args.fnamekeyword
dtmode = args.dtmode
analyzer = args.analyzer
pileup = args.pileup
    
istest = True

try: 
	moreargs = ' '.join(sys.argv)
	moreargs = moreargs.split('--fnamekeyword')[-1]	
	moreargs = ' '.join((moreargs.split()[1:]))
except: moreargs = ''

moreargs = moreargs.strip()
print 'moreargs', moreargs



cwd = os.getcwd()

fnamefilename = 'usefulthings/filelist.txt'
print 'fnamefilename', fnamefilename
fnamefile = open(fnamefilename)
fnamelines = fnamefile.readlines()
fnamefile.close()
import random
random.shuffle(fnamelines)

def main():
    for fname_ in fnamelines:
        if not (fnamekeyword in fname_): continue
        fname = fname_.strip()
        job = analyzer.split('/')[-1].replace('.py','').replace('.jdl','')+'-'+fname.strip()
        job = job.replace('.root','')
        #print 'creating jobs:',job
        newjdl = open('jobs/'+job+'.jdl','w')
        newjdl.write(jdltemplate.replace('CWD',cwd).replace('JOBKEY',job))
        newjdl.close()
        newsh = open('jobs/'+job+'.sh','w')
        newshstr = shtemplate.replace('ANALYZER',analyzer).replace('FNAMEKEYWORD',fname).replace('MOREARGS',moreargs)
        newsh.write(newshstr)
        newsh.close()
        if not os.path.exists('output/'+fnamekeyword.replace(' ','')): 
            os.system('mkdir output/'+fnamekeyword.replace(' ',''))
        os.chdir('output/'+fnamekeyword.replace(' ',''))
        cmd =  'condor_submit '+'../../jobs/'+job+'.jdl'        
        print cmd
        os.system(cmd)
        os.chdir('../../')
        if istest: break


jdltemplate = '''
universe = vanilla
Executable = CWD/jobs/JOBKEY.sh
Output = CWD/jobs/JOBKEY.out
Error = CWD/jobs/JOBKEY.err
Log = CWD/jobs/JOBKEY.log
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files=CWD/tools, CWD/usefulthings, /eos/uscms/store/user/cmsdas/2019/long_exercises/DisappearingTracks/track-tag/cmssw8-newpresel3-200-4-short-updated/weights/TMVAClassification_BDT.weights.xml, /eos/uscms/store/user/cmsdas/2019/long_exercises/DisappearingTracks/track-tag/cmssw8-newpresel2-200-4-medium-updated/weights/TMVAClassification_BDT.weights.xml
x509userproxy = $ENV(X509_USER_PROXY)
Queue 1
'''

shtemplate = '''
#!/bin/bash
export SCRAM_ARCH=slc6_amd64_gcc630
echo $PWD
ls
scram project CMSSW_10_1_0
cd CMSSW_10_1_0/src
eval `scramv1 runtime -sh`
cd ${_CONDOR_SCRATCH_DIR}
echo $PWD
ls
python ANALYZER --fnamekeyword FNAMEKEYWORD MOREARGS
'''

main()
print 'done'


