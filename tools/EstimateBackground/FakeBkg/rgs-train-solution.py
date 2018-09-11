#!/usr/bin/env python
import os, sys, re
from string import *
from rgsutil import *
from ROOT import *
import multiprocessing

def start(name, folder):

    Lumi = 35900.0 # 1/pb

    print "="*80
    print "\t=== %s ===" % name
    print "="*80

    gSystem.AddDynamicPath('$RGS_PATH/lib')
    if gSystem.Load("libRGS") < 0: error("unable to load libRGS")

    cutdatafilename = folder + "/signal.root"
    start      = 0                # start row 
    maxcuts    = -1             # maximum number of cut-points to consider
    treename   = "PreSelection"   # name of Root tree 
    weightname = ""

    # preselection:
    selection = "pt>15 && abs(eta)<2.4 && passPFCandVeto==1 && trkRelIso<0.2 && dzVtx<0.1 && ptErrOverPt2<10 && nMissingMiddleHits==0 && trackQualityHighPurity==1"

    rgs = RGS(cutdatafilename, start, maxcuts, treename, weightname, selection)
   
    start    =  0   #  start row
    numrows  = -1   #  scan all the data from the files

    def rgs_add_weighted(filename, start, numrows, shortname, xsection):

        # get number of events (depending on selected numrows) for weight:
        fin = TFile(filename)
        if numrows < 0:
            h_nev = fin.Get("Nev")
            nev = h_nev.GetEntries()
        else:
            tree = fin.Get("PreSelection")
            tree.Draw("event","Entry$<%s" % numrows, "COLZ")
            h_event = tree.GetHistogram()
            maxbin = h_event.GetXaxis().GetLast()
            nev = h_event.GetXaxis().GetBinCenter( maxbin )

        print "using nev=", nev, filename

        fin.Close()
        weight = 1.0 * xsection * Lumi / nev
        print "adding %s, using weight = %f" % (filename, weight)
        rgs.add(filename,  start, numrows, shortname, weight)
    
    rgs_add_weighted("%s/signal.root" % folder,  start, numrows, "_signal", 0.00276133)

    rgs_add_weighted("%s/Summer16.WJetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root" % folder, start, numrows, "_WJetsHT100To200", 1627)
    rgs_add_weighted("%s/Summer16.WJetsToLNu_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root" % folder, start, numrows, "_WJetsHT200To400", 435.2)
    rgs_add_weighted("%s/Summer16.WJetsToLNu_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root" % folder, start, numrows, "_WJetsHT400To600", 59.18)
    rgs_add_weighted("%s/Summer16.WJetsToLNu_HT-800To1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root" % folder, start, numrows, "_WJetsHT800To1200", 6.66)
    rgs_add_weighted("%s/Summer16.WJetsToLNu_HT-1200To2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root" % folder, start, numrows, "_WJetsHT1200To2500", 1.608)
    rgs_add_weighted("%s/Summer16.WJetsToLNu_HT-2500ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root" % folder, start, numrows, "_WJetsHT2500ToInf", 0.03891)

    rgs_add_weighted("%s/Summer16.DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_RA2AnalysisTree.root" % folder, start, numrows, "_DYJets", 6025)
    rgs_add_weighted("%s/Summer16.DYJetsToLL_M-50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root" % folder, start, numrows, "_DYJetsHT100To200", 181.3)
    rgs_add_weighted("%s/Summer16.DYJetsToLL_M-50_HT-200to400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root" % folder, start, numrows, "_DYJetsHT200To400", 50.42)
    rgs_add_weighted("%s/Summer16.DYJetsToLL_M-50_HT-400to600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root" % folder, start, numrows, "_DYJetsHT400To600", 6.984)
    rgs_add_weighted("%s/Summer16.DYJetsToLL_M-50_HT-800to1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root" % folder, start, numrows, "_DYJetsHT800To1200", 0.7754)
    rgs_add_weighted("%s/Summer16.DYJetsToLL_M-50_HT-1200to2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root" % folder, start, numrows, "_DYJetsHT1200To2500", 0.1862)
    rgs_add_weighted("%s/Summer16.DYJetsToLL_M-50_HT-2500toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root" % folder, start, numrows, "_DYJetsHT2500ToInf", 0.004385)

    rgs_add_weighted("%s/Summer16.TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root" % folder, start, numrows, "_TTJets", 831.8)
    rgs_add_weighted("%s/Summer16.TTJets_HT-600to800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_RA2AnalysisTree.root" % folder, start, numrows, "_TTJetsHT600To800", 2.734)
    rgs_add_weighted("%s/Summer16.TTJets_HT-1200to2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_RA2AnalysisTree.root" % folder, start, numrows, "_TTJetsHT1200To2500", 0.1979)
    rgs_add_weighted("%s/Summer16.TTJets_HT-2500toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_RA2AnalysisTree.root" % folder, start, numrows, "_TTJetsHT2500ToInf", 0.002368)

    rgs.run("variables.cuts")
    rgsfilename = "%s.root" % name
    rgs.save(rgsfilename)


if __name__ == "__main__":
  
    start("output", "/nfs/dust/cms/user/kutznerv/cmsdas/tracks-mini-short-bdt")


