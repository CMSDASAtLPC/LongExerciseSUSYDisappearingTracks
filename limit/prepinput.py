#!/usr/bin/env python

import os,sys
from ROOT import *
from string import *

ctau = sys.argv[1]

fs = TFile('skim_g1800_chi1400_27_200970_step4_'+ctau+'.root')
fb = TFile('totalweightedbkgsDataDrivenMC.root')

# Get all histograms
hele = fb.Get('hElBaseline_BinNumberMethod')
#print hele.Integral()

helet = fb.Get('hElBaseline_BinNumberTruth')
#print helet.Integral()

hmu = fb.Get('hMuBaseline_BinNumberMethod')
#print hmu.Integral()

hmut = fb.Get('hMuBaseline_BinNumberTruth')
#print hmut.Integral()

hfake = fb.Get('hFakeBaseline_BinNumberTruth')
#print hfake.Integral()

hsig = fs.Get('hAnalysisBins')
hsig.Scale(135000.)
#print hsig.Integral()
hsig.SetName('Signal')

# Get prompt ele histograms
# Up-down uncertainties are the difference between method and truth histograms / 2 
hele.SetName('PrEle')
helediff = hele.Clone('PrEle_unc')
for i in range(helediff.GetNbinsX()):
    diff = abs(hele.GetBinContent(i) - helet.GetBinContent(i)) / 2.
    helediff.SetBinContent(i, diff)
heleup = hele.Clone('PrEle_ClosureUp')
heleup.Add(helediff)
heledown = hele.Clone('PrEle_ClosureDown')
heledown.Add(helediff, -1)


# Get prompt mu histograms
# Up-down uncertainties are the difference between method and truth histograms / 2 
hmu.SetName('PrMu')
hmudiff = hmu.Clone('PrMu_unc')
for i in range(hmudiff.GetNbinsX()):
    diff = abs(hmu.GetBinContent(i) - hmut.GetBinContent(i)) / 2.
    hmudiff.SetBinContent(i, diff)
hmuup = hmu.Clone('PrMu_ClosureUp')
hmuup.Add(hmudiff)
hmudown = hmu.Clone('PrMu_ClosureDown')
hmudown.Add(hmudiff, -1)


# Get the fake histograms
# Uncertainty is within random +-10% for each bin
r = TRandom3()
unc = 0.1
hfake.SetName('Fake')
hfakediffup = hfake.Clone('Fake_uncUp')
hfakediffdown = hfake.Clone('Fake_uncDown')
for i in range(hfake.GetNbinsX()):
    x = hfake.GetBinContent(i)
    hfakediffup.SetBinContent(i, x*r.Uniform(0, unc))
    hfakediffdown.SetBinContent(i, x*r.Uniform(0, unc))
hfakeup = hfake.Clone('Fake_ClosureUp')
hfakeup.Add(hfakediffup)
hfakedown = hfake.Clone('Fake_ClosureDown')
hfakedown.Add(hfakediffdown, -1)

# Get the observed data
# Obs data is the sum of all central BG contributions smeared with some random uncertainties depending on the bin content
hobsraw = hele.Clone('data_obs_raw')
hobsraw.Add(hmu)
hobsraw.Add(hfake)
hobsraw2 = hobsraw.Clone('data_obs_raw2')
hobs = TH1D('data_obs', 'data_obs', 33, 0., 33.)
for i in range(hobsraw.GetNbinsX()):
    n = hobsraw.GetBinContent(i)*r.Uniform(0.9, 1.1)
    if hobsraw.GetBinContent(i) < 50:
        n = hobsraw.GetBinContent(i)*r.Uniform(0.7, 1.4)
    hobsraw2.SetBinContent(i, n)

#print int(hobsraw2.Integral())
for i in range(int(hobsraw2.Integral())):
    hobsraw2.GetRandom()
    hobs.Fill(hobsraw2.GetRandom())

# Write into the root file

f = TFile('distrack_'+ctau+'_datacard_input.root', 'RECREATE') 
hsig.Write()
hele.Write()
heledown.Write()
heleup.Write()
hmu.Write()
hmudown.Write()
hmuup.Write()
hfake.Write()
hfakedown.Write()
hfakeup.Write()
hobs.Write()
print 'just created file', f.GetName()




