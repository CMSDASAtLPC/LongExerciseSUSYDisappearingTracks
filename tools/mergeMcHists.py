from ROOT import *
from utils import *
#from utilsII import *
import os, sys
from glob import glob
gStyle.SetOptStat(0)
gROOT.SetBatch(1)
from time import sleep
lumi = 135000.


####Note: It's good (safe) to delete all the directories with output/closure* before running this script

#For data, do these commands instead of this script: 
#python tools/ahadd.py -f mergedRoots/mergedRun2016SingleEl_Split.root output/smallchunks/PromptBkgHists_*SingleEl*.root && python tools/ahadd.py -f mergedRoots/mergedRun2016SingleMu_Split.root output/smallchunks/PromptBkgHists_*SingleMu*.root
istest = False
os.system('rm -rf output/closure_*')
try: outfile = sys.argv[1]
except: outfile = 'output/totalweightedbkgs.root'

try: infiles = sys.argv[2]
except: infiles = 'output/smallchunks/PromptBkgHists_*Tune*.root'

inputflist = glob(infiles)
indir = '/'.join(infiles.split('/')[:-1])+'/'

firstfive = infiles.split('/')[-1][:5]
print firstfive, 'firstfive'
if 'PixOnly' in infiles: extra = 'PixOnly'
elif 'PixAndStrips' in infiles: extra = 'PixAndStrips'
else: extra = ''

try: fnameOut = sys.argv[2]
except: fnameOut = 'closure.root'

import os
if not os.path.exists("output/closure_lumixsec"): 
	os.system('mkdir output/closure_lumixsec')
	needshadd = True
else: needshadd = False
import os
if not os.path.exists("output/closure_lumixsecOnsim"): os.system('mkdir output/closure_lumixsecOnsim')
if not os.path.exists("output/closure_finalcontribs"): os.system('mkdir output/closure_finalcontribs')


keysforxsec = []
keysforcontrib = []
print 'for inputname in inputflist:'
for inputname in inputflist:
	shortname = inputname.split('Hists_')[-1].split('CUET')[0]
	if not shortname in keysforxsec: keysforxsec.append(shortname)
	else: continue	
	veryshortname = shortname.split('_')[0]
	if not veryshortname in keysforcontrib: keysforcontrib.append(veryshortname)
	print 'this should be nice and short:', shortname
print keysforxsec

keysforxsec = sorted(keysforxsec)
for xkey in keysforxsec:
	import os
	if not os.path.exists("output/closure_lumixsec/"+xkey+'.root'):
		command = 'python tools/ahadd.py -f output/closure_lumixsec/'+xkey+'.root '+indir+firstfive+'*'+xkey+'*'+extra+'*.root'
		print 'first command', command
		if not istest: os.system(command)
while len(glob('output/closure_lumixsec/*.root'))<len(keysforxsec):
	sleep(1.0)
print 'escaped the eternal sleep! (like snow white)'
print 'for xkey in keysforxsec:'
for xkey in keysforxsec:
			if istest: break
			fOld = TFile('output/closure_lumixsec/'+xkey+'.root')
			hHt = fOld.Get('hHt')
			try: nentries = hHt.GetEntries()
			except:
				print 'stuck at ', xkey, fOld.GetName()
				exit(0)
			keys = sorted(fOld.GetListOfKeys())
			fnew = TFile('output/closure_lumixsecOnsim/'+xkey+'.root','recreate')
			for key in keys:
				name = key.GetName()
				if 'c_' in name: continue
				if 'hHt'==name: continue
				h = fOld.Get(name)
				try:
					if nentries>0: h.Scale(lumi*1.0/nentries)
				except:
					fOld.ls()
					print 'that didnt work', xkey, name, h
					exit(0)
					
				fnew.cd()
				h.Write(name)
			fOld.Close()
			print 'just created', fnew.GetName()
			fnew.Close()
print 'for contribname in keysforcontrib:'			
for contribname in keysforcontrib:
	command = 'python tools/ahadd.py -f output/closure_finalcontribs/'+contribname+'.root output/closure_lumixsecOnsim/*'+contribname+'*.root'
	print 'command', command
	if not istest: os.system(command)
biglumpcommand = 'hadd -f '+outfile+' output/closure_finalcontribs/*.root'
print 'biglumpcommand', biglumpcommand
if not istest: os.system(biglumpcommand)
