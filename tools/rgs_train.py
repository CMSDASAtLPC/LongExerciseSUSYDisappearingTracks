#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  File:        train.py
#  Description: SO1: Example of Random Grid Search to find the results of an
#               ensemble cuts. 
#  Created:     10-Jan-2015 Harrison B. Prosper and Sezen Sekmen
# -----------------------------------------------------------------------------
import os, sys, re
from string import *
try:
	from ROOT import *
except:
	sys.exit("** ROOT with PyROOT is needed to run this example")
# -----------------------------------------------------------------------------
def error(message):
	print "** %s" % message
	exit(0)
# Return the name of a file with the extension and path stripped away.
def nameonly(s):
	import posixpath
	return posixpath.splitext(posixpath.split(s)[1])[0]    
# -----------------------------------------------------------------------------

skimDirectory = '/eos/uscms/store/user/cmsdas/2019/long_exercises/DisappearingTracks/Skims/'

def main():
	NAME = 'LLSUSY'
	print "="*80
	print "\t\t=== %s ===" % NAME
	print "="*80

	# ---------------------------------------------------------------------
	# Load the RGS shared library and check that the various input files
	# exist.
	# ---------------------------------------------------------------------
	gSystem.AddDynamicPath("$RGS_PATH/lib")
	if gSystem.Load("libRGS") < 0: error("unable to load libRGS")

	# Name of file containing cut definitions
	# Format of file:
	#   variable-name  cut-type (>, <, <>, |>, |<, ==)
	# or, for staircase cuts,
	#   \staircase number of cut-points
	#      variable-name cut-type (>, <, |>, |<, ==)
	#           :           :
	#   \end
	varfilename = "tools/%s.cuts" % NAME
	if not os.path.exists(varfilename):
		error("unable to open variables file %s" % varfilename)

	# Name of signal file
	sigfilename = "Signal/skim_g1800_chi1400_27_200970_step4_30.root"
	if not os.path.exists(sigfilename):
		error("unable to open signal file %s" % sigfilename)

	# Name of background file        
	bkgfilename = skimDirectory+"/Background/skim_allBackgrounds.root"
	if not os.path.exists(bkgfilename):
		error("unable to open background file %s" % bkgfilename)

	# ---------------------------------------------------------------------
	#  Create RGS object
	#  
	#   The file (cutdatafilename) of cut-points is usually a signal file,
	#   which ideally differs from the signal file on which the RGS
	#   algorithm is run.
	# ---------------------------------------------------------------------
	cutdatafilename = sigfilename
	start      = 0           # start row 
	maxcuts    = -1 #30000   # maximum number of cut-points to consider
	treename   = "tEvent"  # name of Root tree 
	weightname = "weight"    # name of event weight variable
	#lumi = 35900 # in 1/pb
	lumi = 150000
	# One can add an optional selection, which, if true, keeps the event.
	selection  = "(Mht >= 150 && NTags==1)"

	rgs = RGS(cutdatafilename, start, maxcuts, treename, weightname, selection, lumi)

	# ---------------------------------------------------------------------
	#  Add signal and background data to RGS object.
	#  Weight each event using the value in the field weightname, if
	#  present.
	#  NB: We asssume all files are of the same format.
	# ---------------------------------------------------------------------
	# 1) The first optional argument is a string, which, if given, will be
	# appended to the "count" and "fraction" variables. The "count" variable
	# contains the number of events that pass per cut-point, while "fraction"
	# is count / total, where total is the total number of events per file.
	# If no string is given, the default is to append an integer to the
	# "count" and "fraction" variables, starting at 0, in the order in which
	# the files are added to the RGS object.
	# 2) The second optional argument is the weight to be assigned per file. If
	# omitted the default weight is 1.
	# 3) The third optional argument is the selection string. If omitted, the
	# selection provided in the constructor is used.

	start   =  0                   # start row
	numrows = -1                   # read all rows

	rgs.add(bkgfilename, start, numrows, "_b")
	rgs.add(sigfilename, start, numrows, "_s")

	print "background yield: %10.2f +/- %-10.2f" % (rgs.total(0), rgs.etotal(0))
	print "SUSY  yield: %10.2f +/- %-10.2f" % (rgs.total(1), rgs.etotal(1))

	# ---------------------------------------------------------------------	
	#  Run RGS and write out results
	# ---------------------------------------------------------------------	    
	rgs.run(varfilename)

	# Write to a root file
	rgsfilename = "%s.root" % NAME
	print 'writing file', rgsfilename
	rgs.save(rgsfilename)
# -------------------------------------------------------------------------
try:
	main()
except KeyboardInterrupt:
	print "\tciao!\n"



