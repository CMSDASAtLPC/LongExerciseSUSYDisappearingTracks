#!/bin/env python
import sys, os, glob
import multiprocessing
from GridEngineTools import runParallel
import fakes_analyzer

runmode = "grid"

os.system("mkdir -p output")
commands = []

files_per_job = 5
file_list = glob.glob("/pnfs/desy.de/cms/tier2/store/user/sbein/NtupleHub/Production2016v2/Summer16.*")
#file_list = glob.glob("/pnfs/desy.de/cms/tier2/store/user/sbein/NtupleHub/Production2016v2/Summer16.ttHJetTobb_M125_13TeV_amcatnloFXFX_madspin_pythia8_ext3_4*_RA2AnalysisTree.root")

file_segments = [file_list[x:x+files_per_job] for x in range(0,len(file_list),files_per_job)]

for inFile_segment in file_segments:
        
    out_tree = "output/" + inFile_segment[0].split("/")[-1].split(".root")[0] + "_fakes.root"
    commands.append("./fakes_analyzer.py %s %s" % (str(inFile_segment).replace(", ", ","), out_tree))

print commands[0]
runParallel(commands, runmode)

if False:
    print "running hadd..."
    os.system("hadd -f fakes_%s.root output_%s/Summer*.root" % (choose_bdt, choose_bdt))
