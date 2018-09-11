#!/usr/bin/env python
from __future__ import division
import os, sys, re
from string import *
from rgsutil import *
from time import sleep
from ROOT import *
import glob

gROOT.SetBatch(True)
gStyle.SetOptStat(0)

def main(name):

    canvas = TCanvas("roc", "roc", 1000, 1000)
    canvas.SetTopMargin(0.5 * canvas.GetTopMargin())
    canvas.SetBottomMargin(1.3 * canvas.GetBottomMargin())
    canvas.SetLeftMargin(1.3 * canvas.GetLeftMargin())
    canvas.SetRightMargin(0.3 * canvas.GetRightMargin())

    ntuple = Ntuple("output.root", "RGS")
    variables = ntuple.variables()

    variableNames = []
    for cname, count in variables:
        print "\t\t%-30s\t%5d" % (cname, count)        
        variableNames.append(cname)
    print "\tnumber of cut-points: ", ntuple.size()

    setStyle()

    # Create a 2-D histogram for ROC plot
    xbins =   50
    xmin  =  0
    xmax  =  1
    ybins =   50
    ymin  =  0
    ymax  =  1
    hist  = mkhist2("hroc",
                    "#font[12]{#epsilon_{S}}",
                    "background rejection (1 - #font[12]{#epsilon_{B}})",
                    xbins, xmin, xmax,
                    ybins, ymin, ymax,
                    color = kBlue+1)
    hist.SetMinimum(0)

    print "\tfilling ROC plot..."	

    totals = ntuple.totals()

    print "totals", totals
    print "len(totals)", len(totals)

    # get background totals
    tb = 0
    for i in range(1, len(totals)):
        tb += totals[i][0]

    print "len(ntuple)", len(ntuple)

    for row, cuts in enumerate(ntuple):
        c_signal = cuts.count_signal
        c_WJets = cuts.count_WJetsHT100To200 + cuts.count_WJetsHT200To400 + cuts.count_WJetsHT400To600 + cuts.count_WJetsHT800To1200 + cuts.count_WJetsHT1200To2500 + cuts.count_WJetsHT2500ToInf
        c_DYJets  = cuts.count_DYJets + cuts.count_DYJetsHT100To200 + cuts.count_DYJetsHT200To400 + cuts.count_DYJetsHT400To600 + cuts.count_DYJetsHT800To1200 + cuts.count_DYJetsHT1200To2500 + cuts.count_DYJetsHT2500ToInf
        c_TTJets  = cuts.count_TTJets + cuts.count_TTJetsHT600To800 + cuts.count_TTJetsHT1200To2500 + cuts.count_TTJetsHT2500ToInf
        s  = c_signal
        b  = c_WJets + c_DYJets + c_TTJets
        
        fs = s / totals[0][0]
        fb = b / tb
        fb_rejection = 1 - fb
       
        #  Plot signal efficiency vs background rejection
        hist.Fill(fs, fb_rejection)


    hist.Draw()
    canvas.Print("rgs.pdf")

main()
