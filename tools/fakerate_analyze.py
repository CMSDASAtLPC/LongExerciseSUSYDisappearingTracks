#!/bin/env python
from __future__ import division
import glob
from ROOT import *
import CfgUtils
import numpy as np
import treeplotter
import uuid
import os

def get_histo_and_weighted_count(variable, cutstring, nBins=False, xmin=False, xmax=False, path="./output", config="samples.cfg", unweighted = False):

    unique = str(uuid.uuid1())
   
    samples = CfgUtils.update_samples_with_filenames(path, config)

    histograms = {}

    weighted_counts = {"total": 0}

    h_bg_combined = 0
    h_data_combined = 0

    for sample in samples.keys():

        if sample == "global" or sample == "total": continue
        if len(samples[sample]["filenames"]) == 0: continue            

        contents = treeplotter.get_histogram_from_file(samples[sample]["filenames"], "Events", variable, nBins=nBins, xmin=xmin, xmax=xmax, cutstring=cutstring)
        histogram = contents[0].Clone()
        histogram.SetDirectory(0)
        histogram.SetName(unique)
        
        count = histogram.GetEntries()
        nev = contents[1]
        xsec = samples[sample]["xsec"]
        lumi = samples["global"]["lumi"]
        
        scale = lumi * xsec / nev
        weighted_count = count * scale
        
        if not unweighted: histogram.Scale(scale)
        
        weighted_counts[sample] = weighted_count
        if samples[sample]["type"] == "b":
            weighted_counts["total"] += weighted_count
            
            if h_bg_combined == 0:
                h_bg_combined = histogram
            else:
                print "adding to combined bg:", sample
                h_bg_combined.Add(histogram)

        elif samples[sample]["type"] == "d":
            
            if h_data_combined == 0:
                h_data_combined = histogram
            else:
                print "adding to combined data:", sample
                h_data_combined.Add(histogram)

    return h_bg_combined, h_data_combined, weighted_counts


def quick_fakerate(variable, binWidth, xmin, xmax, xlabel = "", path = "./output", config = "samples_custom.cfg", cutstring = "PFCaloMETRatio<5", suffix = "", qcdonly = False, folder = "."):
    
    if folder != "." and not os.path.exists(folder):
        os.system("mkdir -p %s" % folder)

    if xlabel == "": xlabel = variable
    
    canvas = TCanvas("fakerate", "fakerate", 800, 800)  

    if len(cutstring) > 0:
        base_cuts = cutstring + " && EvtNumEven==0"
    else:
        base_cuts = "EvtNumEven==0"
   
    nBins = int(xmax/binWidth)

    fakes_numerator_bg, fakes_numerator_data, fakes_numerator_count       = get_histo_and_weighted_count(variable, base_cuts + " && n_DT>0", nBins=nBins, xmin=xmin, xmax=xmax, path=path, config=config)
    fakes_denominator_bg, fakes_denominator_data, fakes_denominator_count = get_histo_and_weighted_count(variable, base_cuts + " && n_DT==0", nBins=nBins, xmin=xmin, xmax=xmax, path=path, config=config)
    fake_rate_bg = fakes_numerator_bg.Clone()
    fake_rate_bg.Divide(fakes_denominator_bg)
    fake_rate_bg.SetName("fake_rate_bg")

    fake_rate_data = fakes_numerator_data.Clone()
    fake_rate_data.Divide(fakes_denominator_data)
    fake_rate_data.SetName("fake_rate_data")
    
    print "fakes_numerator_count", fakes_numerator_count
    print "fakes_denominator", fakes_denominator_count
    
    #check tracks if they are close to a genParticle with status 1:  
    if len(cutstring) > 0:
        base_cuts = cutstring + " && EvtNumEven==1"
    else:
        base_cuts = "EvtNumEven==1"

    fakes_gen_nominator, hist_ignore, fakes_gen_numerator_count     = get_histo_and_weighted_count(variable, base_cuts + " && n_DT_realfake>0", nBins=nBins, xmin=xmin, xmax=xmax, path=path, config=config)
    fakes_gen_denominator, hist_ignore, fakes_gen_denominator_count = get_histo_and_weighted_count(variable, base_cuts + " && n_DT_realfake==0", nBins=nBins, xmin=xmin, xmax=xmax, path=path, config=config)
    fake_rate_gen = fakes_gen_nominator.Clone()
    fake_rate_gen.Divide(fakes_gen_denominator)
    fake_rate_gen.SetName("fake_rate_gen")

    # upper plot:
    canvas.Clear()
    pad1 = TPad("pad1", "pad1", 0, 0.2, 1, 1.0)
    pad1.SetRightMargin(0.05)
    pad1.SetLogy(True)
    pad2 = TPad("pad2", "pad2", 0.0, 0.025, 1.0, 0.27)
    pad2.SetBottomMargin(0.4)
    pad2.SetRightMargin(0.05)
    pad1.Draw()
    pad2.Draw()
    pad1.cd()

    fake_rate_bg.Draw("p")
    fake_rate_bg.GetXaxis().SetLabelSize(0)
    fake_rate_bg.SetMarkerStyle(20)
    fake_rate_bg.SetMarkerColor(kBlue)
    fake_rate_bg.SetLineWidth(2)
    fake_rate_bg.SetLineColor(kBlue)

    fake_rate_data.Draw("same p")
    fake_rate_data.SetMarkerStyle(20)
    fake_rate_data.SetMarkerColor(kBlack)
    fake_rate_data.SetLineWidth(2)
    fake_rate_data.SetLineColor(kBlack)

    fake_rate_gen.Draw("same p")
    fake_rate_gen.SetMarkerStyle(5)
    fake_rate_gen.SetMarkerColor(kRed)
    fake_rate_gen.SetLineWidth(2)
    fake_rate_gen.SetLineColor(kRed)

    ymin = 1e6
    for ibin in range(fake_rate_bg.GetNbinsX()):
        value = fake_rate_bg.GetBinContent(ibin)
        if value < ymin and value > 0:
            ymin = value
    for ibin in range(fake_rate_gen.GetNbinsX()):
        value = fake_rate_gen.GetBinContent(ibin)
        if value < ymin and value > 0:
            ymin = value
    ymax = max(fake_rate_bg.GetMaximum(), fake_rate_data.GetMaximum())

    fake_rate_bg.GetYaxis().SetRangeUser(0.5*ymin, 1.5*ymax)

    fake_rate_bg.SetTitle(";;fake rate")

    legend = TLegend(0.43, 0.75, 0.94, 0.89)
    legend.SetTextSize(0.03)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.AddEntry(fake_rate_data, "Run2016C SingleElectron + SingleMuon")

    if qcdonly:
        legend.AddEntry(fake_rate_bg, "MC (QCD only)")
        legend.AddEntry(fake_rate_gen, "MC (QCD only) + Truth")
    else:
        legend.AddEntry(fake_rate_bg, "MC")
        legend.AddEntry(fake_rate_gen, "MC + Truth information")
    legend.Draw()

    # ratio plot:
    pad2.cd()
    ratio = fake_rate_bg.Clone()
    ratio.Divide(fake_rate_gen)
    ratio.Draw()
    ratio.SetTitle(";%s;MC/Truth" % xlabel)
    pad2.SetGridx(True)
    pad2.SetGridy(True)
    ratio.GetXaxis().SetTitleSize(0.12)
    ratio.GetYaxis().SetTitleSize(0.12)
    ratio.GetYaxis().SetTitleOffset(0.35)
    ratio.GetYaxis().SetRangeUser(0,2)
    ratio.GetYaxis().SetNdivisions(4)
    ratio.GetXaxis().SetLabelSize(0.12)
    ratio.GetYaxis().SetLabelSize(0.12)
  
    canvas.SaveAs("%s/fakerate_%s%s.pdf" % (folder, variable, suffix))
    canvas.SaveAs("%s/fakerate_%s%s.root" % (folder, variable, suffix))

 
if __name__ == "__main__":

    config = "samples_all.cfg"
    path = "output_dileptons/"
    output_folder = "plots_fakerate"
    cutstring = "PFCaloMETRatio<5"

    # z mass plot
    plot_config = {"zmass": {"binw": 2, "xmin": 75, "xmax": 120, "ymin": 1e5, "xlabel": "m_{ll} (GeV)", "ylabel": "events", "logx": False, "logy": True} }
    treeplotter.loop_over_files(path, config, plot_config, tree_folder_name="Events", cutstring = cutstring + " && lepton_type==11", suffix="_ee", ignore_samples="Run201", folder = output_folder)
    treeplotter.loop_over_files(path, config, plot_config, tree_folder_name="Events", cutstring = cutstring + " && lepton_type==13", suffix="_mumu", ignore_samples="Run201", folder = output_folder)

    # plot number of disappearing tracks per event
    plot_config = {"n_DT": {"binw": 1, "xmin": 0, "xmax": 3, "xlabel": "number of DT", "ylabel": "events", "logx": False, "logy": True} }
    treeplotter.loop_over_files(path, config, plot_config, tree_folder_name="Events", cutstring = cutstring, suffix="", ignore_samples="Run201", folder = output_folder)

    # stacked plots, fakes nom/denom, fake rate:
    plot_config = {
        "HT_cleaned": {"binw": 100, "xmin": 0, "xmax": 1000, "xlabel": "H_{T} (GeV)", "logx": False, "logy": True},
        "MHT_cleaned": {"binw": 100, "xmin": 0, "xmax": 1000, "xlabel": "missing H_{T} (GeV)", "logx": False, "logy": True},
        "n_allvertices": {"binw": 5, "xmin": 0, "xmax": 50, "xlabel": "n_{vertex}", "logx": False, "logy": True},
        "MinDeltaPhiMhtJets_cleaned": {"binw": 0.01, "xmin": 0, "xmax": 0.4, "xlabel": "min #Delta#phi(MH_{T}, Jets)", "logx": False, "logy": True},
                  }
    for var in plot_config:
        quick_fakerate(var, plot_config[var]["binw"], plot_config[var]["xmin"], plot_config[var]["xmax"], xlabel = plot_config[var]["xlabel"], path = path, config = config, cutstring = cutstring, folder = output_folder)
        quick_fakerate(var, plot_config[var]["binw"], plot_config[var]["xmin"], plot_config[var]["xmax"], xlabel = plot_config[var]["xlabel"], path = path, config = config, cutstring = cutstring + " && lepton_type==11", suffix="_ee", folder = output_folder)
        quick_fakerate(var, plot_config[var]["binw"], plot_config[var]["xmin"], plot_config[var]["xmax"], xlabel = plot_config[var]["xlabel"], path = path, config = config, cutstring = cutstring + " && lepton_type==13", suffix="_mumu", folder = output_folder)




