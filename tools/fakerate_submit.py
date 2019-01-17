#!/bin/env python
import sys, os, glob
import multiprocessing
from GridEngineTools import runParallel

runmode = "grid"
output_folder = "."
files_per_job = 3
files_per_sample = -1

os.system("mkdir -p %s" % output_folder)
commands = []

# select DESY location:
#ntuples_folder = "/pnfs/desy.de/cms/tier2/store/user/sbein/NtupleHub/Production2016v2"

# select FNAL location:
# ntuples_folder = "root://cmseos.fnal.gov//store/user/lpcsusyhad/sbein/cmsdas19/Ntuples/"
ntuples_folder = "/eos/uscms/store/user/lpcsusyhad/sbein/cmsdas19/Ntuples"

cmssw8_samples = [
                    "Summer16.WJetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.WJetsToLNu_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.WJetsToLNu_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.WJetsToLNu_HT-600To800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.WJetsToLNu_HT-800To1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.WJetsToLNu_HT-1200To2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.WJetsToLNu_HT-2500ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.TTJets_HT-600to800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.TTJets_HT-1200to2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.TTJets_HT-2500toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.QCD_HT200to300_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.QCD_HT300to500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.ZJetsToNuNu_HT-100To200_13TeV-madgraph",
                    "Summer16.ZJetsToNuNu_HT-200To400_13TeV-madgraph",
                    "Summer16.ZJetsToNuNu_HT-400To600_13TeV-madgraph",
                    "Summer16.ZJetsToNuNu_HT-600To800_13TeV-madgraph",
                    "Summer16.ZJetsToNuNu_HT-800To1200_13TeV-madgraph",
                    "Summer16.ZJetsToNuNu_HT-1200To2500_13TeV-madgraph",
                    "Summer16.ZJetsToNuNu_HT-2500ToInf_13TeV-madgraph",
                    "Summer16.WW_TuneCUETP8M1_13TeV-pythia8",
                    "Summer16.ZZ_TuneCUETP8M1_13TeV-pythia8",
                    "Summer16.WZ_TuneCUETP8M1_13TeV-pythia8",
                    "Summer16.DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.DYJetsToLL_M-50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.DYJetsToLL_M-50_HT-200to400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.DYJetsToLL_M-50_HT-400to600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.DYJetsToLL_M-50_HT-600to800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.DYJetsToLL_M-50_HT-800to1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.DYJetsToLL_M-50_HT-1200to2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Summer16.DYJetsToLL_M-50_HT-2500toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8",
                    "Run2016C-03Feb2017-v1.SingleElectron",
                    "Run2016C-03Feb2017-v1.SingleMuon",
                 ]
 
for sample in cmssw8_samples:

    ifile_list = sorted(glob.glob(ntuples_folder + "/" + sample + "*.root"))
    
    if files_per_sample != -1:
        ifile_list = ifile_list[:files_per_sample]
    
    if len(ifile_list)==0:
        continue

    print "Looping over %s files (%s)" % (len(ifile_list), sample)
    
    file_segments = [ifile_list[x:x+files_per_job] for x in range(0,len(ifile_list),files_per_job)]

    for inFile_segment in file_segments:
                        
        out_tree = output_folder + "/" + inFile_segment[0].split("/")[-1].split(".root")[0] + "_fakes.root"
        commands.append("./fakerate_loop.py %s %s" % (str(inFile_segment).replace(", ", ",").replace("[", "").replace("]", ""), out_tree))

        # for FNAL:
        commands[-1] = commands[-1].replace("/eos/uscms/", "root://cmseos.fnal.gov/")


#FIXME -- remove to submit all jobs
commands = [commands[0]]
#FIXME -- remove to submit all jobs

raw_input("submit %s jobs?" % len(commands))
os.system("cp fakerate_loop.py %s/" % output_folder)
runParallel(commands, runmode, dontCheckOnJobs=True, burst_mode=False)

