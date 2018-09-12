#! /usr/bin/env python
from ROOT import *
import os, sys, glob
from GridEngineTools import runParallel
import plotter

# STEP 1: create flat histograms from trees:

# set to True if you're running for the first time
recreate_histograms = True
if recreate_histograms:

    parameters = []

    os.system("mkdir -p histos-short")
    os.system("mkdir -p histos-medium")

    cuts = {"loose": ""}
    for iFile in glob.glob("/nfs/dust/cms/user/kutznerv/cmsdas/tracks-mini-short/*.root"):
        parameters.append([iFile, "PreSelection", "histos-short", cuts])
    for iFile in glob.glob("/nfs/dust/cms/user/kutznerv/cmsdas/tracks-mini-medium/*.root"):
        parameters.append([iFile, "PreSelection", "histos-medium", cuts])

    commands = []
    for parameter in parameters:
        command = ("./treeToHist.py " + parameter[0] + " " + parameter[1] + " " + parameter[2] + ' \"' + str(parameter[3]).replace(" ", "").replace("'", "\'") + '\"')
        commands.append( command.replace("\\", "") )

    runParallel(commands, "multi")


# STEP 2: create stacked histograms from previously created individual histograms:

for folder in ["histos-short", "histos-medium"]:

    os.system("mkdir -p plots/%s" % folder)

    histoPath = "."
    stages = ["loose"]

    for stage in stages:

        print "stage:", stage, folder

        plotter.stackedPlot(folder, "samples.cfg", "%s/pt" % stage, "%s;p_{T} (GeV);number of tracks" % stage, "plots/%s/pt-%s.pdf" % (folder, stage.replace(">","more").replace("<","less")))
        plotter.stackedPlot(folder, "samples.cfg", "%s/eta" % stage, "%s;#eta;number of tracks" % stage, "plots/%s/eta-%s.pdf" % (folder, stage.replace(">","more").replace("<","less")))

        plotter.stackedPlot(folder, "samples.cfg", "%s/dxyVtx" % stage, "%s;dxy (cm);number of tracks" % stage, "plots/%s/dxyVtx-%s.pdf" % (folder, stage.replace(">","more").replace("<","less")))
        plotter.stackedPlot(folder, "samples.cfg", "%s/dzVtx" % stage, "%s;dz (cm);number of tracks" % stage, "plots/%s/dzVtx-%s.pdf" % (folder, stage.replace(">","more").replace("<","less")))
        plotter.stackedPlot(folder, "samples.cfg", "%s/matchedCaloEnergy" % stage, "%s;E_{calo} (GeV);number of tracks" % stage, "plots/%s/matchedCaloEnergy-%s.pdf" % (folder, stage.replace(">","more").replace("<","less")))
        plotter.stackedPlot(folder, "samples.cfg", "%s/trkRelIso" % stage, "%s;trkRelIso;number of tracks" % stage, "plots/%s/trkRelIso-%s.pdf" % (folder, stage.replace(">","more").replace("<","less")))
        plotter.stackedPlot(folder, "samples.cfg", "%s/nValidPixelHits" % stage, "%s;valid pixel hits;number of tracks" % stage, "plots/%s/nValidPixelHits-%s.pdf" % (folder, stage.replace(">","more").replace("<","less")), xmin=0, xmax=15)
        plotter.stackedPlot(folder, "samples.cfg", "%s/nValidTrackerHits" % stage, "%s;valid tracker hits;number of tracks" % stage, "plots/%s/nValidTrackerHits-%s.pdf" % (folder, stage.replace(">","more").replace("<","less")))
        plotter.stackedPlot(folder, "samples.cfg", "%s/nMissingOuterHits" % stage, "%s;nMissingOuterHits;number of tracks" % stage, "plots/%s/nMissingOuterHits-%s.pdf" % (folder, stage.replace(">","more").replace("<","less")))
        plotter.stackedPlot(folder, "samples.cfg", "%s/ptErrOverPt2" % stage, "%s;#Delta p_{T} / p_{T}^{2};number of tracks" % stage, "plots/%s/ptErrOverPt2-%s.pdf" % (folder, stage.replace(">","more").replace("<","less")))

        plotter.stackedPlot(folder, "samples.cfg", "%s/nMissingInnerHits" % stage, "%s;#Delta p_{T} / p_{T}^{2};number of tracks" % stage, "plots/%s/nMissingInnerHits-%s.pdf" % (folder, stage.replace(">","more").replace("<","less")))
        plotter.stackedPlot(folder, "samples.cfg", "%s/nMissingMiddleHits" % stage, "%s;#Delta p_{T} / p_{T}^{2};number of tracks" % stage, "plots/%s/nMissingMiddleHits-%s.pdf" % (folder, stage.replace(">","more").replace("<","less")))
        plotter.stackedPlot(folder, "samples.cfg", "%s/nMissingOuterHits" % stage, "%s;#Delta p_{T} / p_{T}^{2};number of tracks" % stage, "plots/%s/nMissingOuterHits-%s.pdf" % (folder, stage.replace(">","more").replace("<","less")))

        plotter.stackedPlot(folder, "samples.cfg", "%s/nValidPixelHits" % stage, "%s/pixelLayersWithMeasurement" % stage, "plots/%s/pixelLayersWithMeasurement-%s.pdf" % (folder, stage.replace(">","more").replace("<","less")))
        plotter.stackedPlot(folder, "samples.cfg", "%s/nValidTrackerHits" % stage, "%s/trackerLayersWithMeasurement" % stage, "plots/%s/trackerLayersWithMeasurement-%s.pdf" % (folder, stage.replace(">","more").replace("<","less")))
        plotter.stackedPlot(folder, "samples.cfg", "%s/chargedPtSum" % stage, "%s;charged PFCand #sum p_{T} (GeV);number of tracks" % stage, "plots/%s/chargedPtSum-%s.pdf" % (folder, stage.replace(">","more").replace("<","less")), xmin=0, xmax=100, logx=False)
        plotter.stackedPlot(folder, "samples.cfg", "%s/neutralPtSum" % stage, "%s;neutral PFCand #sum p_{T} (GeV);number of tracks" % stage, "plots/%s/neutralPtSum-%s.pdf" % (folder, stage.replace(">","more").replace("<","less")), xmin=0, xmax=100, logx=False)   
        plotter.stackedPlot(folder, "samples.cfg", "%s/madHT" % stage, "%s;generator HT (GeV);number of tracks" % stage, "plots/%s/madHT-%s.pdf" % (folder, stage.replace(">","more").replace("<","less")), xmin=50, xmax=3000, logx=False)
        plotter.stackedPlot(folder, "samples.cfg", "%s/HT" % stage, "%s;HT (GeV);number of tracks" % stage, "plots/%s/HT-%s.pdf" % (folder, stage.replace(">","more").replace("<","less")), xmin=50, xmax=3000, logx=False)


