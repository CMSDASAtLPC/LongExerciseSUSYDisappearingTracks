from ROOT import *
from utils import *
from namelib import *
import sys
from random import shuffle

gStyle.SetOptStat(0)
gStyle.SetFrameBorderMode(0)
gStyle.SetLegendBorderSize(0)
gStyle.SetLegendTextSize(0.026)
try:fname =sys.argv[1]
except:
    fname = 'TagProbeTrees/TagnProbe_DYJetsToLL_M-50_100HT.root'
    print 'Histogram file not specified, will run default file:'

try:foname =sys.argv[2]
except:
    foname = 'Kappa.root'
    print 'Output file not specified, will create output as: Kappa.root'
f  = TFile(fname)
keys = f.GetListOfKeys()

c1 = mkcanvas('c1')

fnew = TFile(foname,'recreate')
fnew.cd()
for key in keys:
    name = key.GetName()
#    print name
#    print 10*'*'
    if not ('EtaDTeff' in name or 'PtDTeff' in name or 'ChargeDTeff' in name or 'PlusDTeff' in name or 'MinusDTeff' in name):continue
    hnum   = f.Get(name)

    hden    = f.Get(name.replace('DTeff','RECOeff'))
    if 'vs' in name: 
        hden.GetXaxis().SetTitle('Pt')
        hden.GetYaxis().SetTitle('#eta')
    else:
        hden.GetYaxis().SetTitle('#kappa')
        hden.GetYaxis().SetRangeUser(0,0.02)
        hden.GetXaxis().SetTitle(namelib[name.replace('DTeff','').replace('DTmeff','').replace('RECOeff','').replace('EleProbe','').replace('h','').replace('EleGen','')])
    leg = TLegend(0.56,0.67,0.77,0.89)
    leg.SetTextFont(42)
    leg.SetTextSize(0.035)
    leg.SetHeader("MC sample")
    hnum.Divide(hden)
    print 10*'*'
    leg.AddEntry(hden," DYtoLL  ","lep")
    hden.SetTitle('#kappa ' + name.replace('hPtvsEta','tag and probe').replace('vs','').replace('Minus','').replace('Plus','').replace('Charge','').replace('DTeff','').replace('RECOeff','').replace('Probe','tag and probe').replace('h','').replace('Ele','').replace('Pt','').replace('Eta','').replace('Gen','Gen Info'))

    hden.Reset()
    hden.Draw()
    
    if 'vs' in name: hnum.Draw('samecolz')
    else: hnum.Draw('same')

    leg.SetFillStyle(0)
    leg.Draw()                                                                                                                                                
    c1.Update()

    pause()
    c1.Print('pdfs/kappa/kappa'+name.replace('DTeff','').replace('DTmeff','').replace('RECOeff','').replace('EleProbe','TagandProbe').replace('h','').replace('EleGen','GenInfo')+'.pdf')
    hnum.Write('kappa'+name.replace('DTeff','').replace('DTmeff','').replace('RECOeff','').replace('EleProbe','tagNprobe').replace('h','').replace('EleGen','GenInfo'))
    print 'root file updated with histo', 'kappa'+name.replace('DTeff','').replace('DTmeff','').replace('RECOeff','').replace('EleProbe','tagNprobe').replace('h','').replace('EleGen','GenInfo')
fnew.Close()
print "Kappa file:", fnew, "created."
