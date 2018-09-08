#!/usr/bin/env python
# ---------------------------------------------------------------------
#  File:        analysis.py
#  Description: SO1: Analyze the results of RGS staircase cuts and find
#               the best cuts.
# ---------------------------------------------------------------------
#  Created:     10-Jan-2015 Harrison B. Prosper and Sezen Sekmen
#               15-Oct-2016 HBP now refer to staircase cuts
#               17-Jun-2017 HBP adapt to latest version of OuterHull
# ---------------------------------------------------------------------
import os, sys, re
sys.path.append('../python')
sys.path.append('../../tools')
from string import *
from rgsutil import *
from time import sleep
from ROOT import *
from array import array
from utils import *
gStyle.SetOptStat(0)

#from rgsexamples import *
# ---------------------------------------------------------------------
NAME = 'LLSUSY'

# ---------------------------------------------------------------------
def main():
	global cut

	print "="*80
	print "\t=== SO1: find best staircase cuts ==="
	print "="*80

	treename = "RGS"
	varfilename  = "%s.cuts" % NAME
	resultsfilename= "%s.root" % NAME

	print "\n\topen RGS file: %s"  % resultsfilename

	f = TFile(resultsfilename)
	f.ls()
	t = f.Get(treename)

	nentries = t.GetEntries()
	n = nentries
	x, y = array( 'd' ), array( 'd' )
	zmax = 0
	izmax = -1
	sys = 0.05 #fractional uncertainty on b

	msize = 0.30  # marker size for points in ROC plot
	xbins =  25   # number of bins in x (background)
	xmin  =  0.0    # lower bound of x
	xmax  =  0.03    # upper bound of y
	ybins =  25
	ymin  =  0.0
	ymax  =  0.6
	hroc  = mkhist2("hroc",
					"#font[12]{#epsilon_{B}}",
					"#font[12]{#epsilon_{S}}",
					xbins, xmin, xmax,
					ybins, ymin, ymax)
	hroc.SetMinimum(0)
	hroc.SetMarkerSize(msize)
	xaxRoc = hroc.GetXaxis()
	yaxRoc = hroc.GetYaxis()
	for ientry in range(nentries):
		t.GetEntry(ientry)
		s = t.count_s
		b = t.count_b
		if not t.NJets<7: continue
		if b<.1: continue
		if not s>0.01: continue
		z = s/TMath.Sqrt(b+pow(sys*b,2))
		if z>zmax: 
			zmax = z
			izmax = ientry
		fs = t.fraction_s
		fb = t.fraction_b	
		x.append(fb)
		y.append(fs)
		ibinx = min(xaxRoc.FindBin(fb),xaxRoc.GetNbins())
		ibiny = min(yaxRoc.FindBin(fs),yaxRoc.GetNbins())
		hroc.SetBinContent(ibinx, ibiny, max(z, hroc.GetBinContent(ibinx, ibiny)))
			
	t.GetEntry(izmax)
	t.Show(izmax)
	s = t.count_s
	b = t.count_b
	z = s/TMath.Sqrt(b+pow(sys*b,2))
	print 's=%.2f, b=%.2f, z=%.2f' % (s, b, z)
	groc = TGraph( n, x, y )
	groc.SetLineColor( 1 )
	groc.SetLineWidth( 1 )
	groc.SetMarkerColor( kBlack )
	groc.SetMarkerStyle( 1 )		
	croc = TCanvas("h_%s_ROC" % NAME, "ROC", 520, 10, 500, 500)
	croc.SetLogz()
	croc.cd()
	hroc.Draw('colz')
	groc.Draw('same P')
	tl.DrawLatex(0.85,0.946,'max #sigma')	
	tl.DrawLatex(0.85,0.906,'of bin')		
	stamp2(35.9)
	croc.Update()
	pause()
	gSystem.ProcessEvents()    

	
# ---------------------------------------------------------------------
try:
	main()
except KeyboardInterrupt:
	print '\nciao!'


