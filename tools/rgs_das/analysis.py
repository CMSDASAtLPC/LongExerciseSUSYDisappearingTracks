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
from string import *
#from rgsutil import *
from time import sleep
from ROOT import *

sys.path.append('../../python')
#from rgsexamples import *
# ---------------------------------------------------------------------
NAME = 'LLSUSY'
def cut(event):
	skip = \
	  (event.njet <     3) or \
	  (event.j1pT <=  200) or \
	  (event.nb   <     1) or \
	  (event.nW   <     1)
	return skip
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
	t = f.Get(treename)

	t.Show(0)
	exit(0)
	nentries = t.GetEntries()
	for ientry in range(nentries):
		t.GetEntry(ientry)

	# Create a 2-D histogram for ROC plot
	msize = 0.30  # marker size for points in ROC plot

	xbins =  10000   # number of bins in x (background)
	xmin  =  0.0    # lower bound of x
	xmax  =  1.0    # upper bound of y

	ybins =  50
	ymin  =  0.0
	ymax  =  1.0

	color = kBlue+1
	hroc  = mkhist2("hroc",
					"#font[12]{#epsilon_{B}}",
					"#font[12]{#epsilon_{S}}",
					xbins, xmin, xmax,
					ybins, ymin, ymax,
					color=color)
	hroc.SetMinimum(0)
	hroc.SetMarkerSize(msize)



	drawSUSYLegend('with preselection', left=False)
	cmass.Update()
	gSystem.ProcessEvents()    
	cmass.SaveAs('.pdf')

	print "\t== plot ROC ==="	
	croc = TCanvas("h_%s_ROC" % NAME, "ROC", 520, 10, 500, 500)
	croc.cd()
	croc.SetLogx()
	hroc.Draw()
	croc.Update()
	gSystem.ProcessEvents()    
	croc.SaveAs(".pdf")  

	sleep(5)
# ---------------------------------------------------------------------
try:
	main()
except KeyboardInterrupt:
	print '\nciao!'


