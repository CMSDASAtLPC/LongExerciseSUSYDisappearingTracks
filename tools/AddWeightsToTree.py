import os
from glob import glob
from ROOT import *

TestMode = True

uniquestems = [ 'ZJetsToNuNu_HT-200To400',\
                'ZJetsToNuNu_HT-400To600',\
				'ZJetsToNuNu_HT-600To800',\
				#'ZJetsToNuNu_HT-800To1200',\
				#'ZJetsToNuNu_HT-1200To2500',\
				#'ZJetsToNuNu_HT-2500ToInf',\
                'WJetsToLNu_HT-100To200',\
                'WJetsToLNu_HT-200To400',\
                'WJetsToLNu_HT-400To600',\
                #'WJetsToLNu_HT-600To800',\
                'WJetsToLNu_HT-800To1200',\
                'WJetsToLNu_HT-1200To2500',\
                'WJetsToLNu_HT-2500ToInf',\
                'TTJets_TuneCUETP8M1',\
                'TTJets_HT-600to800',\
                #'TTJets_HT-800to1200',\
                'TTJets_HT-1200to2500',\
                'TTJets_HT-2500toInf',\
                'DYJetsToLL_M-50_HT-100to200',\
                'DYJetsToLL_M-50_HT-200to400',\
                'DYJetsToLL_M-50_HT-400to600',\
                'DYJetsToLL_M-50_HT-600to800',\
                'DYJetsToLL_M-50_HT-800to1200',\
                'DYJetsToLL_M-50_HT-1200to2500',\
                'DYJetsToLL_M-50_HT-2500toInf',\
                'QCD_HT200to300',\
                'QCD_HT300to500',\
                'QCD_HT500to700',\
                'QCD_HT700to1000',\
                'QCD_HT1000to1500',\
                'QCD_HT1500to2000',\
                'QCD_HT2000toInf',\
                #'WWTo2L2Nu_13TeV',\
                'WWTo1L1Nu2Q_13TeV',\
                'WZTo1L1Nu2Q_13TeV',\
                'WZTo1L3Nu_13TeV',\
                'ZZTo2Q2Nu_13TeV',\
                'ZZTo2L2Q_13TeV',\
                #'WWZ_TuneCUETP8M1',\
                #'ZZZ_TuneCUETP8M1',\
                'pMSSM12_MCMC1_10_374794',\
                'pMSSM12_MCMC1_12_865833',\
                'pMSSM12_MCMC1_13_547677',\
                'pMSSM12_MCMC1_20_690321',\
                'pMSSM12_MCMC1_22_237840',\
                'pMSSM12_MCMC1_24_345416',\
#'pMSSM12_MCMC1_27_200970',\
                'pMSSM12_MCMC1_27_969542',\
                'pMSSM12_MCMC1_28_737434',\
#'pMSSM12_MCMC1_37_569964',\
                'pMSSM12_MCMC1_44_855871',\
                'pMSSM12_MCMC1_47_872207',\
                'pMSSM12_MCMC1_4_252033',\
                'pMSSM12_MCMC1_5_448429',\
                'pMSSM12_MCMC1_8_373637']
#sourcedir = '/eos/uscms//store/user/sbein/StealthSusy/Production/ntuple/*'
#sourcedir = '/nfs/dust/cms/user/beinsam/LongLiveTheChi/ntuple_sidecar/smallchunks/*'


#Get signal cross section information
sourcedir = 'Output/smallchunks/skim*'
verbosity = 10000

xsecDictSignalsPb = {}
sigfilenames = glob('/nfs/dust/cms/user/beinsam/LongLiveTheChi/xsecs/own_output_nice_*')
for fname in sigfilenames:
	print 'processing', fname
	fxsec = open(fname)
	lines = fxsec.readlines()
	fxsec.close()
	row1 = lines[1].split()
	idx = row1.index('tot')
	row2 = lines[2].split()
	shortname = fname.split('/')[-1].replace('own_output_nice_','').replace('.txt','')
	xsecDictSignalsPb[shortname] = float(row2[idx])    
    
import numpy as np
for stem in uniquestems:
	targetname = stem.replace('SIM','').replace('step3','').replace('___','_').replace('__','_')
	targetnamewithpath = (sourcedir.replace('*','_')+targetname).replace('/smallchunks','/unweighted')+'.root'
	command = 'hadd -f '+ targetnamewithpath + ' ' + sourcedir+stem+'*.root'
	print command
	if TestMode: continue
	if not TestMode: os.system(command)
	fjustcombined = TFile(targetnamewithpath)
	hHt = fjustcombined.Get('hHt')
	try: hHt.SetDirectory(0)
	except: continue
	nsimulated = hHt.GetEntries()
	fjustcombined.Close()
	chain_in = TChain('tEvent')
	chain_in.Add(targetnamewithpath)
	if chain_in.GetEntries()==0: continue
	fileout = TFile(targetnamewithpath.replace('unweighted','weighted'),'recreate')
	tree_out = chain_in.CloneTree(0)
	weight = np.zeros(1, dtype=float)
	b_weight = tree_out.Branch('weight', weight, 'weight/D')
	nentries = chain_in.GetEntries()
	for ientry in range(nentries):
		if ientry % verbosity == 0:
			print 'Processing entry %d of %d' % (ientry, nentries),'('+'{:.1%}'.format(1.0*ientry/nentries)+')'    
		chain_in.GetEntry(ientry)
		if 'pMSSM' in targetname:
			weight[0]=xsecDictSignalsPb[targetname]/nsimulated
		else:
			weight[0] = chain_in.CrossSection*1.0/nsimulated
		if ientry==0: print stem, 'event weight', 100000*weight[0]
		if chain_in.NTags>0:
			tree_out.Fill()	

	fileout.cd()
	tree_out.Write()
	hHt.Write()		
	print 'just created', fileout.GetName()
	fileout.Close()
os.system('mv Output/weighted/*pMSSM*.root Output/Signal/')
os.system('mv Output/weighted/*.root Output/Background/')



