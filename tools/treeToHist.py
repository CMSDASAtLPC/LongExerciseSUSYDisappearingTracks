#! /usr/bin/env python

# get histograms from trees on track-level for plotting.
# 
# configure below & run script

from ROOT import *
import os, sys, glob
import math
import numpy as np
import uuid
#from CfgUtils import readSamplesConfig
from optparse import OptionParser

def readSamplesConfig(configFileName):
    
    # read sample configuration file

    samples = {}
    cfg_data = ""
    
    with open(configFileName, 'r') as f:
        cfg_data = f.read()

    # check for imports
    for line in cfg_data.split("\n"):
        if "#import" in line:
            with open(line.split("import")[-1].strip(), 'r') as f:
                cfg_data_import = f.read()
                cfg_data = cfg_data_import + cfg_data
    
    shortname = ""
    xsec = 0.0
    lumi = 0.0
    filtereff = -1
    plot = False
    color = -1
    descriptor = ""
    sampletype = ""
    
    for line in cfg_data.split("\n"):
       
        if len(line)>0 and line[0] == "#":
            continue
       
        try:
            if "[" in line and "]" in line:
                shortname = line.split("[")[1].split("]")[0]
                samples[shortname] = {}
            if "xsec" in line:
                xsec = line.split("=")[-1].strip()
                samples[shortname]["xsec"] = float(xsec)
            if "lumi" in line:
                lumi = line.split("=")[-1].strip()
                samples[shortname]["lumi"] = float(lumi)
            if "filtereff" in line:
                filtereff = line.split("=")[-1].strip()
                samples[shortname]["filtereff"] = float(filtereff)
            if "plot" in line:
                plot = line.split("=")[-1].strip()
                samples[shortname]["plot"] = eval(plot)
            if "descriptor" in line:
                descriptor = line.split("=")[-1].strip()
                samples[shortname]["descriptor"] = descriptor
            if "type" in line:
                sampletype = line.split("=")[-1].strip()
                samples[shortname]["type"] = sampletype
            if "color" in line:
                color = line.split("=")[-1].strip()
                samples[shortname]["color"] = int(color)

        except:
            print "[!] malformed sample configuration file!"

    return samples



gROOT.SetBatch(True)
gStyle.SetOptStat(0)

def treeToHist(tfile, treename, path, cutstrings):

    print "Doing", tfile

    os.system("mkdir -p %s" % path)
    hfile = "%s/h_" % path + tfile.split("/")[-1]  

    fin = TFile(tfile)
    fout = TFile(hfile, "recreate")
    tree = fin.Get(treename)

    if fin.Get("Nev"):
        # we're on track level
        hnev = fin.Get("Nev")
    elif tree.GetBranch("EvtNum"):
        # we're on event level
        hnev = TH1D("Nev", "Nev", 1, 0, 1)
        N = tree.GetEntries()
        for i in range(N):
            hnev.Fill(0.0)
    else:
        print "unclear track/event level"
        return
    hnev.Write()

    def getHistFromTree(tree, var, hName=False, cutstring=False, drawoptions=False, nBins=False, xmin=False, xmax=False):

        # get a histogram from a tree branch, either define your histogram or take it from the tree

        if nBins:
            if not hName: hName = var
            histo = TH1F(hName, hName, nBins, xmin, xmax)
            if (cutstring and drawoptions):
                tree.Draw("%s>>%s" % (var, hName), cutstring, drawoptions)
            if drawoptions:
                tree.Draw("%s>>%s" % (var, hName), drawoptions)
            if cutstring:
                tree.Draw("%s>>%s" % (var, hName), cutstring)
            else:
                tree.Draw("%s>>%s" % (var, hName))
        else:
            if (cutstring and drawoptions):
                tree.Draw(var, cutstring, drawoptions)
            if drawoptions:
                tree.Draw(var, drawoptions)
            if cutstring:
                tree.Draw(var, cutstring)
            else:
                tree.Draw(var)
            histo = tree.GetHistogram().Clone()
            histo.SetDirectory(0)

        return histo

    if not cutstrings:
        cutstrings = {"none": ""}

    for cutname in cutstrings:

        if cutname == "none":
            cutstring = False
        else:
            fout.mkdir(cutname)
            fout.cd(cutname)
            cutstring = cutstrings[cutname]

        print "Selecting cut", cutname, cutstring

        if tree.GetBranch("pt"): pt = getHistFromTree(tree, "pt", cutstring=cutstring, nBins=200, xmin=0, xmax=1000); pt.Write()
        if tree.GetBranch("ptError"): ptError = getHistFromTree(tree, "ptError", cutstring=cutstring, nBins=200, xmin=0, xmax=1000); ptError.Write()
        if tree.GetBranch("ptErrOverPt2"): ptErrOverPt2 = getHistFromTree(tree, "ptErrOverPt2", cutstring=cutstring, nBins=200, xmin=0, xmax=2); ptErrOverPt2.Write()
        if tree.GetBranch("phi"): phi = getHistFromTree(tree, "phi", cutstring=cutstring, nBins=100, xmin=-3.2, xmax=3.2); phi.Write()
        if tree.GetBranch("eta"): eta = getHistFromTree(tree, "eta", cutstring=cutstring, nBins=100, xmin=-3, xmax=3); eta.Write()

        if tree.GetBranch("pixelLayersWithMeasurement"): pixelLayersWithMeasurement = getHistFromTree(tree, "pixelLayersWithMeasurement", cutstring=cutstring, nBins=50, xmin=0, xmax=50); pixelLayersWithMeasurement.Write()
        if tree.GetBranch("trackerLayersWithMeasurement"): trackerLayersWithMeasurement = getHistFromTree(tree, "trackerLayersWithMeasurement", cutstring=cutstring, nBins=50, xmin=0, xmax=50); trackerLayersWithMeasurement.Write()
        if tree.GetBranch("trackQualityHighPurity"): trackQualityHighPurity = getHistFromTree(tree, "trackQualityHighPurity", cutstring=cutstring, nBins=2, xmin=0, xmax=2); trackQualityHighPurity.Write()
        if tree.GetBranch("trackQualityHighPuritySetWithPV"): trackQualityHighPuritySetWithPV = getHistFromTree(tree, "trackQualityHighPuritySetWithPV", cutstring=cutstring, nBins=2, xmin=0, xmax=2); trackQualityHighPuritySetWithPV.Write()
        if tree.GetBranch("trackQualityTight"): trackQualityTight = getHistFromTree(tree, "trackQualityTight", cutstring=cutstring, nBins=2, xmin=0, xmax=2); trackQualityTight.Write()

        if tree.GetBranch("chargedPtSum"): chargedPtSum = getHistFromTree(tree, "chargedPtSum", cutstring=cutstring, nBins=200, xmin=0, xmax=200); chargedPtSum.Write()
        if tree.GetBranch("neutralPtSum"): neutralPtSum = getHistFromTree(tree, "neutralPtSum", cutstring=cutstring, nBins=200, xmin=0, xmax=200); neutralPtSum.Write()
        if tree.GetBranch("neutralWithoutGammaPtSum"): neutralWithoutGammaPtSum = getHistFromTree(tree, "neutralWithoutGammaPtSum", cutstring=cutstring, nBins=200, xmin=0, xmax=200); neutralWithoutGammaPtSum.Write()

        if tree.GetBranch("chi2perNdof"): chi2perNdof = getHistFromTree(tree, "chi2perNdof", cutstring=cutstring, nBins=200, xmin=0, xmax=20); chi2perNdof.Write()
        if tree.GetBranch("deDxHarmonic2"): deDxHarmonic2 = getHistFromTree(tree, "deDxHarmonic2", cutstring=cutstring, nBins=150, xmin=0, xmax=15); deDxHarmonic2.Write()
        if tree.GetBranch("dxyVtx"): dxyVtx = getHistFromTree(tree, "dxyVtx", cutstring=cutstring, nBins=100, xmin=0, xmax=0.03); dxyVtx.Write()
        if tree.GetBranch("dzVtx"): dzVtx = getHistFromTree(tree, "dzVtx", cutstring=cutstring, nBins=100, xmin=0, xmax=0.6); dzVtx.Write()
        if tree.GetBranch("matchedCaloEnergy"): matchedCaloEnergy = getHistFromTree(tree, "matchedCaloEnergy", cutstring=cutstring, nBins=100, xmin=0, xmax=100); matchedCaloEnergy.Write()
        if tree.GetBranch("matchedCaloEnergyJets"): matchedCaloEnergyJets = getHistFromTree(tree, "matchedCaloEnergyJets", cutstring=cutstring, nBins=100, xmin=0, xmax=100); matchedCaloEnergyJets.Write()
        if tree.GetBranch("nMissingInnerHits"): nMissingInnerHits = getHistFromTree(tree, "nMissingInnerHits", cutstring=cutstring, nBins=50, xmin=0, xmax=50); nMissingInnerHits.Write()
        if tree.GetBranch("nMissingMiddleHits"): nMissingMiddleHits = getHistFromTree(tree, "nMissingMiddleHits", cutstring=cutstring, nBins=50, xmin=0, xmax=50); nMissingMiddleHits.Write()
        if tree.GetBranch("nMissingOuterHits"): nMissingOuterHits = getHistFromTree(tree, "nMissingOuterHits", cutstring=cutstring, nBins=50, xmin=0, xmax=50); nMissingOuterHits.Write()
        if tree.GetBranch("nValidPixelHits"): nValidPixelHits = getHistFromTree(tree, "nValidPixelHits", cutstring=cutstring, nBins=50, xmin=0, xmax=50); nValidPixelHits.Write()
        if tree.GetBranch("nValidTrackerHits"): nValidTrackerHits = getHistFromTree(tree, "nValidTrackerHits", cutstring=cutstring, nBins=50, xmin=0, xmax=50); nValidTrackerHits.Write()
        if tree.GetBranch("passExo16044DeadNoisyECALVeto"): passExo16044DeadNoisyECALVeto = getHistFromTree(tree, "passExo16044DeadNoisyECALVeto", cutstring=cutstring, nBins=2, xmin=0, xmax=2); passExo16044DeadNoisyECALVeto.Write()
        if tree.GetBranch("passExo16044GapsVeto"): passExo16044GapsVeto = getHistFromTree(tree, "passExo16044GapsVeto", cutstring=cutstring, nBins=2, xmin=0, xmax=2); passExo16044GapsVeto.Write()
        if tree.GetBranch("passExo16044JetIso"): passExo16044JetIso = getHistFromTree(tree, "passExo16044JetIso", cutstring=cutstring, nBins=2, xmin=0, xmax=2); passExo16044JetIso.Write()
        if tree.GetBranch("passExo16044LepIso"): passExo16044LepIso = getHistFromTree(tree, "passExo16044LepIso", cutstring=cutstring, nBins=2, xmin=0, xmax=2); passExo16044LepIso.Write()
        if tree.GetBranch("passExo16044Tag"): passExo16044Tag = getHistFromTree(tree, "passExo16044Tag", cutstring=cutstring, nBins=2, xmin=0, xmax=2); passExo16044Tag.Write()
        if tree.GetBranch("passPFCandVeto"): passPFCandVeto = getHistFromTree(tree, "passPFCandVeto", cutstring=cutstring, nBins=2, xmin=0, xmax=2); passPFCandVeto.Write()
        if tree.GetBranch("trkMiniRelIso"): trkMiniRelIso = getHistFromTree(tree, "trkMiniRelIso", cutstring=cutstring, nBins=200, xmin=0, xmax=10); trkMiniRelIso.Write()
        if tree.GetBranch("trkRelIso"): trkRelIso = getHistFromTree(tree, "trkRelIso", cutstring=cutstring, nBins=200, xmin=0, xmax=10); trkRelIso.Write()
        if tree.GetBranch("trackJetIso"): trackJetIso = getHistFromTree(tree, "trackJetIso", cutstring=cutstring, nBins=200, xmin=0, xmax=10); trackJetIso.Write()
        if tree.GetBranch("trackLeptonIso"): trackLeptonIso = getHistFromTree(tree, "trackLeptonIso", cutstring=cutstring, nBins=200, xmin=0, xmax=10); trackLeptonIso.Write()
        if tree.GetBranch("nCandPerEevent"): nCandPerEevent = getHistFromTree(tree, "nCandPerEevent", cutstring=cutstring, nBins=40, xmin=0, xmax=40); nCandPerEevent.Write()

        if tree.GetBranch("madHT"): madHT = getHistFromTree(tree, "madHT", cutstring=cutstring, nBins=200, xmin=0, xmax=3000); madHT.Write()
        if tree.GetBranch("MET"): MET = getHistFromTree(tree, "MET", cutstring=cutstring, nBins=200, xmin=0, xmax=3000); MET.Write()
        if tree.GetBranch("HT"): HT = getHistFromTree(tree, "HT", cutstring=cutstring, nBins=200, xmin=0, xmax=3000); HT.Write()

        if tree.GetBranch("matchedGenElectron"): matchedGenElectron = getHistFromTree(tree, "matchedGenElectron", cutstring=cutstring, nBins=2, xmin=0, xmax=2); matchedGenElectron.Write()
        if tree.GetBranch("matchedGenMuon"): matchedGenMuon = getHistFromTree(tree, "matchedGenMuon", cutstring=cutstring, nBins=2, xmin=0, xmax=2); matchedGenMuon.Write()
        if tree.GetBranch("matchedRecoElectron"): matchedRecoElectron = getHistFromTree(tree, "matchedRecoElectron", cutstring=cutstring, nBins=2, xmin=0, xmax=2); matchedRecoElectron.Write()
        if tree.GetBranch("matchedRecoMuon"): matchedRecoMuon = getHistFromTree(tree, "matchedRecoMuon", cutstring=cutstring, nBins=2, xmin=0, xmax=2); matchedRecoMuon.Write()

        if tree.GetBranch("chiCandGenMatchingDR"): chiCandGenMatchingDR = getHistFromTree(tree, "chiCandGenMatchingDR", cutstring=cutstring, nBins=100, xmin=0, xmax=0.001); chiCandGenMatchingDR.Write()

    fin.Close()
    fout.Close()
    

if __name__ == "__main__":

    parser = OptionParser()
    (options, args) = parser.parse_args()

    print args

    treeToHist(args[0], args[1], args[2], eval(args[3]))
