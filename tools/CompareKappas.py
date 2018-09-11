from ROOT import *
from utils import *
from histlib import *
import sys


gStyle.SetOptStat(0)
gStyle.SetFrameBorderMode(0)
gStyle.SetLegendBorderSize(0)
gStyle.SetLegendTextSize(0.026)

try:fname =sys.argv[1]
except:
    fname = 'Kappa.root'
    print 'files not specified, using', fname

f  = TFile(fname)

keys = f.GetListOfKeys()

c1 = mkcanvas('c1')

for key in keys:
    hist = key.GetName()
    if 'ckappa' in hist: continue
    if not ('GenInfo' in hist):continue 
    h     =  f.Get(hist)
    h2    =  f.Get(hist.replace('GenInfo','tagNprobe'))
    overflow(h)
    overflow(h2)
    leg = TLegend(0.56,0.67,0.77,0.89)
    leg.SetTextFont(42)
    leg.SetTextSize(0.035)
    leg.SetHeader("#kappa from MC:DYtoLNuLNu")
    histoStyler(h,2)
    h.SetLineWidth(2)
    h.SetLineStyle(1)
    h.GetXaxis().SetTitle(histlib[hist[1:]])
    h.GetYaxis().SetRangeUser(0.0001,1.2*(max(h.GetMaximum(),h2.GetMaximum())))
    h.GetYaxis().SetTitle('#kappa')
    h.SetTitle("")
    h.Draw('hist e1')
    histoStyler(h2,4)
    h2.SetLineWidth(2)
    h2.SetLineStyle(1)
    leg.AddEntry(h,"Gen Info ","l")
    leg.AddEntry(h2,"Tag and Probe","l")
    h2.Draw('histsame e1')
    leg.SetFillStyle(0)
    leg.Draw()
    stamp()
    c1.Update()
    pause()
    #saveHistAs = hist.replace('GenInfo','').replace('tagNprobe','')+ 'comparision'
    #c1.Print('compHist_pdf/'+saveHistAs+'.pdf')

