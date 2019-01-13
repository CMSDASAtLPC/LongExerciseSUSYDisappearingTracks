#! /usr/bin/env python
from __future__ import division
from ROOT import *
import glob
import uuid
from CfgUtils import readSamplesConfig
import os

gROOT.SetBatch(True)
gStyle.SetOptStat(0)
TH1D.SetDefaultSumw2()

def get_histogram_from_tree(tree, var, hName=False, cutstring=False, drawoptions=False, nBins=False, xmin=False, xmax=False, overflow=False):

    # get a histogram from a tree branch, either define your histogram or take it from the tree

    if nBins:
        if not hName: hName = str(uuid.uuid1()).replace("-", "")
        histo = TH1F(hName, hName, nBins, xmin, xmax)
        if (cutstring and drawoptions):
            tree.Draw("%s>>%s" % (var, hName), cutstring, drawoptions)
        if drawoptions:
            tree.Draw("%s>>%s" % (var, hName), drawoptions)
        if cutstring:
            tree.Draw("%s>>%s" % (var, hName), cutstring)
        else:
            tree.Draw("%s>>%s" % (var, hName))
        histo.SetDirectory(0)
        
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

    # do overflow bin
    if overflow:       
        h_overflow = get_histogram_from_tree(tree, var, hName=hName, cutstring=cutstring, drawoptions=drawoptions, nBins=1, xmin=xmax, xmax=1e6, overflow=False)
        n_overflow = h_overflow.GetBinContent(1)
        histo.SetBinContent(histo.GetNbinsX(), n_overflow)
        print "overflow:", histo.GetNbinsX(), n_overflow

    return histo


def get_histogram_from_file(tree_files, tree_folder_name, variable, cutstring=False, nBins=False, xmin=False, xmax=False, file_contains_histograms=False):

    # get a histogram from either a file containing a collection of histograms or a tree.
    # if file contains a tree, one can apply a cutstring and xmin/xmax settings

    histo = -1
    nev = -1

    if file_contains_histograms:

        if len(tree_files) == 1:          
            tree_file = tree_files[0]
            fin = TFile(tree_file)
            histo = fin.Get(tree_folder_name + "/" + variable)

            histo = histo.Clone()
            histo.SetDirectory(0)
            nev = histo.GetEntries()

        else:
            print "empty histo / multiple histograms not yet implemented"

    else:

        tree = TChain(tree_folder_name)       
        for tree_file in tree_files:
            try:
                tree.Add(tree_file)
            except:
                pass
        try:
            histo = get_histogram_from_tree(tree, variable, cutstring=cutstring, nBins=nBins, xmin=xmin, xmax=xmax)
        except:
            histo = False

        # get number of entries:
        nev = 0
        for tree_file in tree_files:
            fin = TFile(tree_file)
            if fin.Get("Nev"):
                # we're on track level
                hnev = fin.Get("Nev")
                i_nev = hnev.GetBinContent(1)
            elif fin.Get("nev"):
                # we're on track level
                hnev = fin.Get("nev")
                i_nev = hnev.GetBinContent(1)
            elif tree.GetBranch("EvtNum"):
                # event level:
                i_nev = tree.GetEntries()
            elif tree.GetBranch("MET"):
                # event level:
                i_nev = tree.GetEntries()
            else:
                i_nev = 0 
            nev += i_nev
            fin.Close()
    
    return histo, nev


def stack_histograms(histos, samples, plot_config, var, signal_scaling_factor=1.0, unweighted=False, suffix="", debug=False, folder=".", root_file = False):

    print "\nStacking histograms:", var

    first = True

    # get lumi from data cfg:
    if unweighted:
        lumi = 1
    else:
        lumi = samples["global"]["lumi"]

    if "signalscalingfactor" in samples["global"]:
        signal_scaling_factor = samples["global"]["signalscalingfactor"]
        print "using signal_scaling_factor:", signal_scaling_factor

    canvas = TCanvas("canvas", "canvas", 900, 800)

    l = canvas.GetLeftMargin()
    t = canvas.GetTopMargin()
    r = canvas.GetRightMargin()
    b = canvas.GetBottomMargin()

    canvas.SetTopMargin(0.5*t)
    canvas.SetBottomMargin(1.2*b)
    canvas.SetLeftMargin(1.2*l)
    canvas.SetRightMargin(0.7*r)
    
    canvas.SetLogx(plot_config["logx"])
    canvas.SetLogy(plot_config["logy"])

   
    if not "xlabel" in plot_config:
        plot_config["xlabel"] = var
    if not "ylabel" in plot_config:
        plot_config["ylabel"] = "events"

    #legend = TLegend(0.40, 0.70, 0.94, 0.94)
    #legend = TLegend(0.70, 0.70, 0.94, 0.94)
    legend = TLegend(0.50, 0.70, 0.94, 0.94)
    legend.SetTextSize(0.03)
    minimum_y_value = 1e6

    global_minimum = -1
    global_maximum = -1
    
    mcstack = THStack("mcstack-%s" % str(uuid.uuid1()), "")

    samples_for_sorting = []

    # plot backgrounds:
    for sample in sorted(samples):
        if sample == "global": continue      
        if samples[sample]["type"] == 'b':
            color = samples[sample]["color"]
            histos[sample].SetFillColor(color)
            histos[sample].SetLineColor(color)
            histos[sample].SetLineWidth(0)
            histos[sample].SetMarkerColor(color)
            #histos[sample].SetFillStyle(3001)

            if not unweighted and samples[sample]["nev"]>0:
                scale = lumi * samples[sample]["xsec"]/samples[sample]["nev"]
                samples[sample]["count-before-weighting"] = histos[sample].Integral()
                histos[sample].Scale(scale)
                samples[sample]["count-after-weighting"] = histos[sample].Integral()
            else:
                samples[sample]["count-before-weighting"] = histos[sample].Integral()
                samples[sample]["count-after-weighting"] = histos[sample].Integral()
          
            samples_for_sorting.append([sample, samples[sample]["count-after-weighting"]])

            #first = False
            #mcstack.Add(histos[sample])

    # print out scaling information:
    print "Individual bg before/after weighting:"
    combined_bg_samples_counts = []
    combined_bg_samples = {"total": {"count-before-weighting": 0, "count-after-weighting": 0}}
    for sample in sorted(samples):
        if "count-before-weighting" in samples[sample]:
            print sample, "\t", samples[sample]["count-before-weighting"], "\t", samples[sample]["count-after-weighting"]

            label = samples[sample]["descriptor"]
            if label not in combined_bg_samples:
                combined_bg_samples[label] = {"count-before-weighting": 0, "count-after-weighting": 0}
            combined_bg_samples[label]["count-before-weighting"] += samples[sample]["count-before-weighting"]
            combined_bg_samples[label]["count-after-weighting"] += samples[sample]["count-after-weighting"]

            combined_bg_samples["total"]["count-before-weighting"] += samples[sample]["count-before-weighting"]
            combined_bg_samples["total"]["count-after-weighting"] += samples[sample]["count-after-weighting"]
            
    print "\nCombined bg before/after weighting:"
    for label in combined_bg_samples:
        print label, "\t", combined_bg_samples[label]["count-before-weighting"], "\t", combined_bg_samples[label]["count-after-weighting"]
        combined_bg_samples_counts.append([label, combined_bg_samples[label]["count-after-weighting"]])

    # stack histograms with the largest integral to appear on the top of the stack:
    def Sort(sub_li, i_index): 
        return(sorted(sub_li, key = lambda x: x[i_index]))     

    print "Stacking"   
    for combined_sample in Sort(combined_bg_samples_counts, 1):
        if combined_sample[0] == "global" or combined_sample[0] == "total": continue
        
        last_sample = False
        
        for sample in samples:
            if "type" in samples[sample] and samples[sample]["type"] == 'b':
                if "descriptor" in samples[sample]:
                    if combined_sample[0] == samples[sample]["descriptor"]:
                        first = False
                        mcstack.Add(histos[sample])
                        print "adding", sample
                        last_sample = sample
                        
        if last_sample: histos[last_sample].SetLineWidth(1)
        
    
    mcstack.Draw("hist")
    mcstack.SetTitle(";%s;%s" % (plot_config["xlabel"], plot_config["ylabel"]))

    if "ymin" in plot_config:
        global_minimum = plot_config["ymin"]
    else:
        global_minimum = mcstack.GetMinimum()

    if "ymax" in plot_config:
        global_maximum = plot_config["ymax"]
    else:
        global_maximum = mcstack.GetMaximum()
    
    if global_minimum != 0:
        print "global_minimum", global_minimum
        mcstack.SetMinimum(global_minimum)
    else:
        mcstack.SetMinimum(1e-1)
   
    if plot_config["logy"]:
        global_maximum_scale = 10
    else:
        global_maximum_scale = 1
    
    mcstack.SetMaximum(global_maximum_scale * global_maximum)
    mcstack.GetYaxis().SetTitleOffset(1.3)
    mcstack.GetXaxis().SetTitleOffset(1.3)
    
    # plot signal:
    for sample in samples:
        if sample == "global": continue
        
        if samples[sample]["type"] == 's':
            color = samples[sample]["color"]
            histos[sample].SetLineColor(color)
            histos[sample].SetLineWidth(2)
            histos[sample].SetFillColor(0)

            if not unweighted and samples[sample]["nev"]>0:
                scale = signal_scaling_factor * lumi * samples[sample]["xsec"]/samples[sample]["nev"]
                samples[sample]["count-before-weighting"] = histos[sample].Integral()
                histos[sample].Scale(scale)
                samples[sample]["count-after-weighting"] = histos[sample].Integral()

            if first:
                histos[sample].Draw("hist")
                if histos[sample].GetEntries()>0:
                    first = False

            else:
                histos[sample].Draw("same hist")
                if "ymin" not in plot_config and global_minimum > histos[sample].GetMinimum():
                    global_minimum = histos[sample].GetMinimum()
                    if global_minimum != 0:
                        mcstack.SetMinimum(global_minimum)
                    else:
                        mcstack.SetMinimum(1e-1)
                
            histos[sample].GetYaxis().SetTitleOffset(1.3)
            histos[sample].GetXaxis().SetTitleOffset(1.3)
            
    # plot data:
    for sample in samples:
        if sample == "global": continue
        
        if samples[sample]["type"] == 'd':
            histos[sample].SetLineWidth(2)
            histos[sample].SetLineColor(1)
            if first:
                histos[sample].Draw("E1")
                if histos[sample].GetEntries()>0:
                    first = False
            else:
                histos[sample].Draw("same E1")
            histos[sample].SetMarkerSize(0)
            histos[sample].SetMarkerStyle(20)
            
            histos[sample].GetYaxis().SetTitleOffset(1.3)
            histos[sample].GetXaxis().SetTitleOffset(1.3)

    
    def add_to_legend(sample_type):

        names = []

        for sample in samples:
            if sample == "global": continue
            if samples[sample]["type"] != sample_type: continue
            names.append(samples[sample]["descriptor"])
        names = list(set(names))

        for name in sorted(names):
            for sample in histos:
                if sample == "global": continue

                if name == samples[sample]["descriptor"]:
                    
                    if "chi" in name and signal_scaling_factor != 1:
                        name = name + " x%i" % signal_scaling_factor
                    
                    legend.AddEntry(histos[sample], name)
                    break

    add_to_legend("b")
    add_to_legend("s")
    add_to_legend("d")
    
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.Draw()

    latex=TLatex()
    latex.SetNDC()
    latex.SetTextAngle(0)
    latex.SetTextColor(kBlack)
    
    latex.SetTextFont(62)
    latex.SetTextAlign(31)
    latex.SetTextSize(0.35 * t)

    lumi = lumi/1000
    if not unweighted: latex.DrawLatex(1-0.7*r, 1-0.5*t+0.15*0.5*t, "%.1f fb^{-1} (13 TeV)" % lumi)
    
    latex.SetTextSize(0.35*t)
    latex.SetTextFont(52)
    #latex.DrawLatex(0.4, 1-0.5*t+0.15*0.5*t, "CMS Simulation")
    
    if folder != ".":
        os.system("mkdir -p %s" % folder)
    canvas.SaveAs("%s/%s%s.pdf" % (folder, var, suffix))
    canvas.SaveAs("%s/%s%s.root" % (folder, var, suffix))

    if root_file:
        output_file = TFile(folder + root_file, "update")
        gDirectory.mkdir("stacked")
        output_file.cd("stacked")
        canvas.SetName("%s%s" % (var, suffix)) 
        canvas.Write()
        output_file.Close()


def loop_over_files(tree_folder, configuration_file, plot_config, tree_folder_name="PreSelection", file_contains_histograms=False, cutstring=False, suffix="", unweighted=False, debug=False, ignore_samples="", folder=".", root_file = False):

    samples = readSamplesConfig(configuration_file)

    # if necessary, ignore some samples
    if len(ignore_samples)>0:
        for sample in samples.keys():
            for ignore_sample in ignore_samples.split(","):
                if ignore_sample in sample:
                    del samples[sample]

    for file_name in glob.glob(tree_folder + "/*.root"):

        for sample in samples:

            sample_name = sample.replace("_RA2AnalysisTree", "")

            if "filenames" not in samples[sample]:
                samples[sample]["filenames"] = []
            if sample_name in file_name:
                samples[sample]["filenames"].append(file_name)
                break

    for sample in samples.keys():
        if sample != "global" and len(samples[sample]["filenames"]) == 0:
            #print "No files found for sample, ignoring:", sample
            del samples[sample]

    for var in plot_config:
        
        histograms = {}
        
        for sample in samples.keys():
         
            if sample == "global": continue
            if len(samples[sample]["filenames"]) == 0: continue            

            if plot_config[var]["xmin"] > 0:
                nBins = int( (plot_config[var]["xmax"] - plot_config[var]["xmin"])/plot_config[var]["binw"] )
            else:
                nBins = int( (plot_config[var]["xmax"] + abs(plot_config[var]["xmin"]))/plot_config[var]["binw"] )
            
            contents = get_histogram_from_file(samples[sample]["filenames"], tree_folder_name, var, cutstring=cutstring, nBins=nBins, xmin=plot_config[var]["xmin"], xmax=plot_config[var]["xmax"], file_contains_histograms=file_contains_histograms)

            if contents[0]:
                histograms[sample] = contents[0]
                samples[sample]["nev"] = contents[1]
          
        stack_histograms(histograms, samples, plot_config[var], var, suffix=suffix, unweighted=unweighted, debug=debug, folder=folder, root_file = root_file)


if __name__ == "__main__":

    # example how to use the treeplotter on a set of files containing trees with a "pt" branch:

    plot_config = {
                    "pt": {"binw": 25, "xmin": 0, "xmax": 1000, "xlabel": "p_{T} (GeV)", "logx": False, "logy": True},
                  }

    cutstring = "pt>30 && abs(eta)<2.4 && MET>250 && MHT>250"
    
    loop_over_files("../DisappTrksNtuple-cmssw10/tracks-short", "cfg/samples_cmssw10.cfg", plot_config, cutstring=cutstring)

