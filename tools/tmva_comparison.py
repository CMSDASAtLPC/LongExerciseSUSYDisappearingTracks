#!/usr/bin/env python
from __future__ import division
import os, sys, re
from string import *
from ROOT import *
import glob
import best_tmva_significance
import getCutEfficiencies

gROOT.SetBatch(True)
gStyle.SetOptStat(0)

def get_TMVA_effs(tmva_output_file):

    fin = TFile(tmva_output_file)
    h_mva_bdt_effB = fin.Get("Method_BDT/BDT/MVA_BDT_effB")
    h_mva_bdt_effS = fin.Get("Method_BDT/BDT/MVA_BDT_effS")

    list_classifier = []
    list_sg_eff = []
    list_bg_eff = []

    for i in range(h_mva_bdt_effS.GetNbinsX()):
        classifier = h_mva_bdt_effS.GetBinCenter(i)
        S = h_mva_bdt_effS.GetBinContent(i)
        B = h_mva_bdt_effB.GetBinContent(i)
        list_classifier.append(classifier)
        list_sg_eff.append(S)
        list_bg_eff.append(B)

    fin.Close()
    return list_classifier, list_sg_eff, list_bg_eff


def get_tmva_info(path):

    # get BDT configuration details from tmva.cxx

    training_variables = []
    spectator_variables = []
    preselection = ""
    method = ""
    configuration = ""
    count_mycutb = 0
    
    with open(path + "/tmva.cxx", 'r') as tmva_macro:
        for line in tmva_macro.readlines():
            if "AddVariable" in line and "//" not in line.split()[0]:
                variable = line.split('"')[1]
                training_variables.append(variable)
            elif "AddSpectator" in line and "//" not in line.split()[0]:
                spectator_variables.append(line.split('"')[1])
            elif 'mycutb=("' in line and "Entry" not in line and "//" not in line.split()[0]:
                preselection = line.split('"')[1]
            elif "BookMethod" in line and "//" not in line.split()[0]:
                method = line.split('"')[1]
                configuration = line.split('"')[3]
                configuration = configuration.replace(":", ", ")

    return {"method": method, "configuration": configuration, "variables": training_variables, "spectators": spectator_variables, "preselection": preselection}


def main(output_filename, tmva_files):
    
    canvas = TCanvas("roc", "roc", 520, 10, 1000, 1000)
    canvas.SetTopMargin(0.5 * canvas.GetTopMargin())
    canvas.SetBottomMargin(0.9 * canvas.GetBottomMargin())
    canvas.SetLeftMargin(1.4 * canvas.GetLeftMargin())
    canvas.SetRightMargin(0.3 * canvas.GetRightMargin())
       
    legend = TLegend(0.3, 0.30, 0.89, 0.45)
    colors = range(1,10)[::-1]

    def draw_tmva_roc(label, tmva_file, trees_folder, configuration_file, hist_list, additional_selection = ""):

        # include comparison to TMVA results:
        # different scale needed because TMVA numerical_values are w.r.t. to the TMVA preselection, not the initial set:

        tmva_info = get_tmva_info(tmva_file.replace("/output.root", ""))
        tmva_preselection = tmva_info["preselection"] + additional_selection
        print "tmva_preselection", tmva_preselection

        tmva_efficiency_scaling = getCutEfficiencies.get_efficiency_for_cut(trees_folder, tmva_preselection, configuration_file = configuration_file)
        eff_scale_sg = tmva_efficiency_scaling["eff_sg"]    
        eff_scale_bg = tmva_efficiency_scaling["eff_bg"]

        eff_scale_sg = 1.0
        eff_scale_bg = 1.0

        color = colors.pop()
        list_classifier, list_sg_eff, list_bg_eff = get_TMVA_effs(tmva_file)

        hist_list.append(TGraph())
        for i in range(len(list_sg_eff)):
            hist_list[-1].SetPoint(i, eff_scale_sg * list_sg_eff[i], 1 - (eff_scale_bg * list_bg_eff[i]))
        hist_list[-1].SetMarkerColor(color)
        hist_list[-1].SetFillColor(color)

        if len(hist_list) == 1:
            hist_list[-1].Draw("ap")
        else:
            hist_list[-1].Draw("p same")
        
        hist_list[-1].SetTitle(";#epsilon_{S};background rejection (1 - #epsilon_{B})")
        hist_list[-1].GetXaxis().SetLimits(0,1)
        hist_list[-1].GetYaxis().SetRangeUser(0.9,1)
        hist_list[-1].GetYaxis().SetTitleOffset(2.0)
        hist_list[-1].GetYaxis().SetNdivisions(3)

        legend.AddEntry(hist_list[-1], label, 'f')

    tmva_hists = []
    for label in sorted(tmva_files):
        draw_tmva_roc(label, tmva_files[label][0], tmva_files[label][1], tmva_files[label][2], tmva_hists)

    latex=TLatex()
    latex.SetNDC()
    latex.SetTextAngle(0)
    latex.SetTextColor(kBlack)
    latex.SetTextFont(42)
    latex.SetTextSize(0.035)
    latex.DrawLatex(0.3, 0.5, "#epsilon = #frac{# tracks passing selection}{# tracks with p_{T}>10 GeV}")

    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetNColumns(1)
    legend.Draw()

    canvas.Update()
    canvas.SaveAs(output_filename)
   
   
cfg_dict = {
            "configuration 1": ["./path/to/tmva/output.root", "/eos/uscms/store/user/cmsdas/2019/long_exercises/DisappearingTracks/track-tag/tracks-pixelonly/*.root", "samples.cfg"],
           }
           
main("bdt-comparison.pdf", cfg_dict)


