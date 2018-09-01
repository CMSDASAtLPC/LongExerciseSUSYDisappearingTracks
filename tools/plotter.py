#! /usr/bin/env python
from ROOT import *
import os, sys, glob
import math
import numpy as np
import uuid
from CfgUtils import readSamplesConfig

# original author: Viktor Kutzner
# returns weighted stacked histograms from individual histograms

gROOT.SetBatch(True)
gStyle.SetOptStat(0)

def stackedPlot(path, sampleCfgFile, var, htitle, filename, binSize=False, xmin=False, xmax=False, logy=True, logx=False, unweighted=False):

    histogram_title = htitle.split(";")[0]
    htitle = ";" + ";".join(htitle.split(";")[1:])

    plotinfo = {}

    hasBackground = False

    samples = readSamplesConfig(sampleCfgFile)

    # check if files exist:
    for sample in samples.keys():
        if not os.path.isfile(path + "/h_" + sample + ".root"):
            del samples[sample]

    names = []
    for sample in samples:
        names.append(samples[sample]["descriptor"])
    names = list(set(names))

    # get lumi from data cfg, otherwise set to 1/fb:
    if unweighted:
        lumi = 1
    else:
        lumi = 35900
    for sample in samples:
        if samples[sample]["type"] == 'd':
            lumi = float(samples[sample]["lumi"])

    files = {}
    histos = {}

    # get number of events:
    nev = {}
    for sample in samples.keys():

        files[sample] = TFile(path + "/h_" + sample + ".root")
        histos[sample] = files[sample].Get(var)

        h_nev = files[sample].Get("Nev")
        nev[sample] = h_nev.GetBinContent(1)

    # get efficiency:
    N_bg = 0
    N_sg = 0
    N_bg_weighted = 0
    N_sg_weighted = 0
    for sample in samples:
        N_tracks = histos[sample].GetEntries()
        if samples[sample]["type"] == 'b':
            weight = lumi*samples[sample]["xsec"]/nev[sample]
            N_bg += N_tracks
            N_bg_weighted += weight*N_tracks
        if samples[sample]["type"] == 's':
            weight = lumi*samples[sample]["xsec"]/nev[sample]
            N_sg += N_tracks
            N_sg_weighted += weight*N_tracks

    plotinfo["N_bg"] = N_bg
    plotinfo["N_sg"] = N_sg
    plotinfo["weighted_N_bg"] = N_bg_weighted
    plotinfo["weighted_N_sg"] = N_sg_weighted

    legend = TLegend(0.55, 0.75, 1.0, 0.95)

    if "short" in path:
        legend.SetHeader("pixel-only tracks, " + histogram_title)
    elif "medium" in path:
        legend.SetHeader("tracker tracks, " + histogram_title)
    else:
        legend.SetHeader(histogram_title)

    minimum_y_value = 1e6

    # plot backgrounds:
    mcstack = THStack("mcstack-%s" % str(uuid.uuid1()),"")
    for sample in sorted(samples):
        if samples[sample]["type"] == 'b':
            hasBackground = True
            color = samples[sample]["color"]
            histos[sample].SetFillColor(color)
            histos[sample].SetLineColor(color)
            histos[sample].SetLineWidth(1)
            histos[sample].SetMarkerColor(color)
            if nev[sample] != 0:
                scale = 1.0*lumi*samples[sample]["xsec"]/nev[sample]
            else:
                scale = 1
            if binSize: histos[sample].Rebin(binSize/int(histos[sample].GetBinWidth(0)))
            if not unweighted: histos[sample].Scale(scale)
            mcstack.Add(histos[sample])

            #current_minimum_y_value = histos[sample].GetMinimum()
            current_minimum_y_value = histos[sample].GetBinContent(histos[sample].GetNbinsX()-1)
            if current_minimum_y_value < minimum_y_value:
                minimum_y_value = current_minimum_y_value

    canvas = TCanvas("canvas","canvas", 800, 800)
    canvas.SetFillStyle(4000)       # transparent background

    if binSize: htitle += " / %i (GeV)" % binSize
    #else: htitle += " / %f " % histos[sample].GetBinWidth(0)
    mcstack.SetTitle(htitle)

    mcstack.SetMinimum(1e-2)
    mcstack.SetMaximum(1.2*mcstack.GetMaximum())

    # y-axis autoscaling
    #if minimum_y_value == 0:
    #    minimum_y_value = 1e-1;
    #mcstack.SetMinimum(1e4 * minimum_y_value)

    # add colors for binned backgrounds:
    for name in names:
        colorindex = 0
        for sample in sorted(histos):
            if name == samples[sample]["descriptor"] and "DY" in name:
                #histos[sample].SetFillColor(histos[sample].GetFillColor() + colorindex)
                colorindex += 1   

    if hasBackground:
        mcstack.Draw("hist")
        mcstack.GetYaxis().SetTitleOffset(1.3)
        mcstack.GetXaxis().SetTitleOffset(1.3)
        if xmax:
            mcstack.GetXaxis().SetRangeUser(xmin,xmax)

    # plot signal:
    for sample in samples:
        if samples[sample]["type"] == 's':
            color = samples[sample]["color"]
            histos[sample].SetLineColor(color)
            histos[sample].SetLineWidth(4)
            histos[sample].SetFillColor(0)
            if nev[sample] != 0:
                scale = lumi*samples[sample]["xsec"]/nev[sample]
            else:
                print "no scale!"
                scale = 1
            if binSize: histos[sample].Rebin(binSize/int(histos[sample].GetBinWidth(0)))
            if not unweighted: histos[sample].Scale(scale)
            if mcstack:
                histos[sample].Draw("same hist")
            else:
                histos[sample].Draw("hist")

            if not hasBackground:
                histos[sample].SetTitle(htitle)
                histos[sample].GetYaxis().SetTitleOffset(1.3)
                histos[sample].GetXaxis().SetTitleOffset(1.3)
                if xmax:
                    histos[sample].GetXaxis().SetRangeUser(xmin,xmax)

    # plot data:
    for sample in samples:
        if samples[sample]["type"] == 'd':
            if binSize: histos[sample].Rebin(binSize/int(histos[sample].GetBinWidth(0)))
            histos[sample].SetLineWidth(2)
            histos[sample].SetLineColor(1)
            histos[sample].Sumw2()
            histos[sample].Draw("same E1")
            histos[sample].SetMarkerSize(0)
            histos[sample].SetMarkerStyle(20)

    mcstack.GetXaxis().SetNdivisions(6)
    mcstack.GetXaxis().SetTitleSize(0.04)
    canvas.Update()

    wjets = False

    for name in names:
        for sample in sorted(histos):
            if name == samples[sample]["descriptor"]:
                legend.AddEntry(histos[sample], name)
                break

    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetNColumns(1)
    legend.Draw()
    canvas.SetLogx(logx)
    canvas.SetLogy(logy)

    l = canvas.GetLeftMargin()
    t = canvas.GetTopMargin()
    r = canvas.GetRightMargin()
    b = canvas.GetBottomMargin()

    canvas.SetTopMargin(0.5*t)
    canvas.SetBottomMargin(1.2*b)
    canvas.SetLeftMargin(1.2*l)
    canvas.SetRightMargin(0.7*r)
    
    canvas.Update()

    latex=TLatex()
    latex.SetNDC()
    latex.SetTextAngle(0)
    latex.SetTextColor(kBlack)
    
    latex.SetTextFont(62)
    latex.SetTextAlign(31)
    latex.SetTextSize(0.35*t)

    lumi = lumi/1000
    if not unweighted: latex.DrawLatex(1-0.7*r,1-0.5*t+0.15*0.5*t,"%.1f fb^{-1} (13 TeV)" % lumi)
    
    latex.SetTextSize(0.4*t)
    latex.SetTextFont(52)
    latex.DrawLatex(0.4,1-0.5*t+0.15*0.5*t,"Work in progress")

    if filename:
        canvas.SaveAs(filename)

    return mcstack

