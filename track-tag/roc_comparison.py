#!/usr/bin/env python
from __future__ import division
from ROOT import *

gROOT.SetBatch(True)
gStyle.SetOptStat(0)

def get_TMVA_effs(tmva_output_file):

    fin = TFile(tmva_output_file)
    h_mva_bdt_effB = fin.Get("Method_BDT/BDT/MVA_BDT_effB")
    h_mva_bdt_effS = fin.Get("Method_BDT/BDT/MVA_BDT_effS")

    list_classifier = []
    list_sg_eff = []
    list_bg_eff = []

    for i in range(1, h_mva_bdt_effS.GetNbinsX() + 1):
        classifier = h_mva_bdt_effS.GetBinCenter(i)
        S = h_mva_bdt_effS.GetBinContent(i)
        B = h_mva_bdt_effB.GetBinContent(i)
        list_classifier.append(classifier)
        list_sg_eff.append(S)
        list_bg_eff.append(B)

    fin.Close()

    return list_classifier, list_sg_eff, list_bg_eff


def plot_rocs(output_filename, tmva_files):
   
    canvas = TCanvas("roc", "roc", 520, 10, 1000, 1000)
    canvas.SetTopMargin(0.5 * canvas.GetTopMargin())
    canvas.SetBottomMargin(0.9 * canvas.GetBottomMargin())
    canvas.SetLeftMargin(1.0 * canvas.GetLeftMargin())
    canvas.SetRightMargin(0.3 * canvas.GetRightMargin())
    
    legend = TLegend(0.5, 0.2, 0.89, 0.4)
    
    first_histogram = True

    def draw_tmva_roc(tmva_file, hist_list, color):
    
        list_classifier, list_sg_eff, list_bg_eff = get_TMVA_effs(tmva_file)

        hist_list.append(TGraph())
        for i in range(len(list_sg_eff)):
            hist_list[-1].SetPoint(i, list_sg_eff[i], 1 - list_bg_eff[i])

        hist_list[-1].SetMarkerColor(color)
        hist_list[-1].SetFillColor(color)

        if first_histogram:
            hist_list[-1].Draw("")
            hist_list[-1].SetTitle(";signal efficiency;background rejection")
        else:
            hist_list[-1].Draw("p same")
        
        label = tmva_file
        legend.AddEntry(hist_list[-1], label, 'f')

       
    tmva_hists = []
    for i, iFile in enumerate(tmva_files):
        draw_tmva_roc(iFile, tmva_hists, i + 1)

    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetNColumns(1)
    legend.Draw()

    canvas.Update()
    canvas.SaveAs(output_filename)


if __name__ == "__main__":

    plot_rocs("comparison.pdf", ["./output.root"])

