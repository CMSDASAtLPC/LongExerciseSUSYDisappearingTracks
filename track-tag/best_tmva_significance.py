#!/bin/env python
from __future__ import division
import math
from ROOT import *
gROOT.SetBatch(True)
gStyle.SetOptStat(0)

def do_significance_plot(h_significance, h_mva_bdt_effB, h_mva_bdt_effS, eff_sg, eff_bg, max_cut_value, output_filename):

    canvas_significance = TCanvas("significance", "significance", 520, 10, 1000, 1000)
    canvas_significance.SetTopMargin(0.5 * canvas_significance.GetTopMargin())
    canvas_significance.SetBottomMargin(0.9 * canvas_significance.GetBottomMargin())
    canvas_significance.SetLeftMargin(0.9 * canvas_significance.GetLeftMargin())
    canvas_significance.SetRightMargin(0.3 * canvas_significance.GetRightMargin())
    canvas_significance.cd()
    h_significance.SetLineColor(kRed)
    h_significance.SetLineWidth(2)
    h_significance.SetTitle(";BDT classifier; #epsilon, normalized Z")
    h_significance.SetFillColor(0)
    h_significance.Draw("")
    h_significance.GetYaxis().SetTitleOffset(1.2)
    h_mva_bdt_effB.SetLineColor(kBlack)
    h_mva_bdt_effB.SetFillColor(0)
    h_mva_bdt_effB.Draw("same")
    h_mva_bdt_effB.SetLineWidth(2)
    h_mva_bdt_effS.SetLineColor(kBlue)
    h_mva_bdt_effS.SetLineWidth(2)
    h_mva_bdt_effS.SetFillColor(0)
    h_mva_bdt_effS.Draw("same")

    line = TLine(max_cut_value,0,max_cut_value,1)
    line.SetLineWidth(2)
    line.SetLineStyle(3)
    line.Draw()

    legend_significance = TLegend(0.5, 0.2, 0.89, 0.4)
    legend_significance.SetHeader("short tracks")
    legend_significance.AddEntry(h_mva_bdt_effS, "#epsilon (signal)")
    legend_significance.AddEntry(h_mva_bdt_effB, "#epsilon (background)")
    legend_significance.AddEntry(h_significance, "Z = S/#sqrt{S+B}")
    legend_significance.SetBorderSize(0)
    legend_significance.SetFillStyle(0)
    legend_significance.SetNColumns(1)
    legend_significance.Draw()

    latex_significance=TLatex()
    latex_significance.SetNDC()
    latex_significance.SetTextAngle(0)
    latex_significance.SetTextColor(kBlack)
    latex_significance.SetTextFont(42)
    latex_significance.SetTextSize(0.035)
    latex_significance.DrawLatex(0.15, 0.45, "maximum Z:")
    latex_significance.DrawLatex(0.15, 0.4, "#epsilon_{sg}=%.2f, #epsilon_{bg}=%.4f" % (eff_sg, eff_bg))

    canvas_significance.SaveAs(output_filename)


def get_get_bdt_cut_value(tmva_output_file, output_filename, fNSignal=-1, fNBackground=-1):

    print "Getting best TMVA significance..."

    # get TMVA histograms
    fin = TFile(tmva_output_file)
    h_mva_bdt_B = fin.Get("Method_BDT/BDT/MVA_BDT_B")
    h_mva_bdt_S = fin.Get("Method_BDT/BDT/MVA_BDT_S")
    h_mva_bdt_effB = fin.Get("Method_BDT/BDT/MVA_BDT_effB")
    h_mva_bdt_effS = fin.Get("Method_BDT/BDT/MVA_BDT_effS")

    if fNSignal<0 or fNBackground<0:
        fNSignal = h_mva_bdt_S.GetEntries()
        fNBackground = h_mva_bdt_B.GetEntries()
        print "Using N_sg=%i, N_bg=%i" % (fNSignal, fNBackground)

    # custom histograms
    h_significance = TH1D("significance", "significance", h_mva_bdt_effS.GetNbinsX(), h_mva_bdt_effS.GetXaxis().GetXmin(), h_mva_bdt_effS.GetXaxis().GetXmax())

    for i in range(h_significance.GetNbinsX()):

        S = h_mva_bdt_effS.GetBinContent(i) * fNSignal
        B = h_mva_bdt_effB.GetBinContent(i) * fNBackground
        if (S+B)>0:
            sign = 1.0 * S/math.sqrt(S+B)
            h_significance.SetBinContent(i, sign)
            h_significance.SetBinError(i, 0)

    # normalize significance:
    h_significance.Scale(1.0/h_significance.GetMaximum())

    max_cut_value = h_significance.GetBinCenter(h_significance.GetMaximumBin())
    Z = h_significance.GetBinContent(h_significance.GetMaximumBin())
    eff_sg = h_mva_bdt_effS.GetBinContent(h_significance.GetMaximumBin())
    eff_bg = h_mva_bdt_effB.GetBinContent(h_significance.GetMaximumBin())

    if output_filename:
        do_significance_plot(h_significance, h_mva_bdt_effB, h_mva_bdt_effS, eff_sg, eff_bg, max_cut_value, output_filename)

    fin.Close()

    output = {"max_cut_value": max_cut_value, "eff_sg": eff_sg, "eff_bg": eff_bg}

    return output


if __name__ == "__main__":

    print get_get_bdt_cut_value("./output.root", "significance.pdf")

