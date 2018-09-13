from ROOT import *
from utils import *
from histlib import *
import sys


gStyle.SetOptStat(0)
gStyle.SetFrameBorderMode(0)
gStyle.SetLegendBorderSize(0)
gStyle.SetLegendTextSize(0.026)


fnames = ['KappaDY.root','KappaData.root']

f0 = TFile(fnames[0])
keys = f0.GetListOfKeys().Clone()
f0.ls()
f0.Close()
c1 = mkcanvas('c1')

leg = TLegend(0.5,0.67,0.7,0.89)
leg.SetTextFont(42)
leg.SetTextSize(0.035)

hists = []
for key in keys:
  colors = [1,2,4]
  icolor=0
  arg = ''
  histname = key.GetName()
  print 'ahistname', histname
  if 'ckappa' in histname: continue
  print 'bhistname', histname
  if not ('GenInfo' in histname):continue
  print 'doing key', key.GetName()
  for fname in fnames:
    f = TFile(fname)
    h     =  f.Get(histname).Clone(histname+fname)
    h2    =  f.Get(histname.replace('GenInfo','tagNprobe')).Clone(histname.replace('GenInfo','tagNprobe')+fname)
    h.SetDirectory(0)
    h2.SetDirectory(0)
    hists.append(h)
    hists.append(h2)
    overflow(h)
    overflow(h2)
    leg.SetTextFont(42)
    leg.SetTextSize(0.035)
    h.GetXaxis().SetTitle(histlib[histname[1:]])
    h.GetYaxis().SetRangeUser(0.0001,1.2*(max(h.GetMaximum(),h2.GetMaximum())))
    h.GetYaxis().SetTitle('#kappa')
    h.SetTitle("")
    histoStyler(h2,4)
    h2.SetLineWidth(2)
    h2.SetLineStyle(1)
    print 'test A'
    if h.GetEntries()>0:
       histoStyler(h, colors[icolor])
       h.SetLineWidth(2)
       h.SetLineStyle(1)
       icolor+=1
       h.Draw('hist e1'+arg)
       arg = 'same'
       leg.AddEntry(h,"Gen Info "+f.GetName().replace('.root','').replace('DY','DY MC').replace('Kappa',''),"l")
       print 'here in 1', fname
    if h2.GetEntries()>0:
       histoStyler(h2,colors[icolor])
       icolor+=1
       h2.SetLineWidth(2)
       h2.SetLineStyle(1)
       print 'here in 2', fname
       leg.AddEntry(h2,"Tag and Probe " + fname.replace('Kappa','').replace('.root','').replace('DY','Drell-Yan MC').replace('Kappa','Kappa ').replace('Data','data (2016C)'),"l") 
       h2.Draw('hist e1'+arg)
       arg = 'same'
  leg.SetFillStyle(0) 
  leg.Draw()
  stamp()
  c1.Update()
  pause()
  #saveHistAs = hist.replace('GenInfo','').replace('tagNprobe','')+ 'comparision'
  #c1.Print('compHist_pdf/'+saveHistAs+'.pdf')


leg.Draw()
c1.Update()
stamp()
pause()


