#! /usr/bin/env python
# script to create trees with track variables
# created May 3, 2017 -Sam Bein 

#python tools/SkimTreeMaker.py /nfs/dust/cms/user/beinsam/CommonNtuples/MC_BSM/LongLivedSMS/ntuple_sidecar/g1800_chi1400_27_200970_step4_30.root

from ROOT import *
from utils import *
import os, sys
from glob import glob
#csv_b = 0.8484
csv_b = 0.8838

isDasAndSignal = True
#cross sections can be looked up on the SUSY xsec working group page:
#https://twiki.cern.ch/twiki/bin/view/LHCPhysics/SUSYCrossSections#Cross_sections_for_various_S_AN2
if isDasAndSignal: xsecInPb = 0.00276133

#smdir = '/nfs/dust/cms/user/beinsam/CommonNtuples/MC_SM/'
#smdir = '/pnfs/desy.de/cms/tier2/store/user/sbein/CommonNtuples/'

##########################################################
# files specified with optional wildcards @ command line #
##########################################################
try: infilenames = sys.argv[1]
except: infilenames = '/pnfs/desy.de/cms/tier2/store/user/sbein/NtupleHub/Production2016v2/Summer16.WJetsToLNu_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_20_RA2AnalysisTree.root'


#############################################
# Book new file in which to write skim tree #
#############################################
newfilename = 'skim_'+(infilenames.split('/')[-1]).replace('*','')
fnew = TFile(newfilename,'recreate')
hHt = TH1F('hHt','hHt',100,0,3000)
hHtWeighted = TH1F('hHtWeighted','hHtWeighted',100,0,3000)
histoStyler(hHt,kBlack)

########################################
# create data containers for the trees #
########################################
import numpy as np
var_Met = np.zeros(1,dtype=float)
var_Mht = np.zeros(1,dtype=float)
var_Mt2 = np.zeros(1,dtype=float)
var_Ht = np.zeros(1,dtype=float)
var_MinDeltaPhiMhtJets = np.zeros(1,dtype=float)
var_NJets = np.zeros(1,dtype=int)
var_BTags = np.zeros(1,dtype=int)
var_NLeptons = np.zeros(1,dtype=int)
var_NPhotons = np.zeros(1,dtype=int)
var_NPixelTags = np.zeros(1,dtype=int)
var_NPixelStripsTags = np.zeros(1,dtype=int)
var_NTags = np.zeros(1,dtype=int)
var_NPrompt = np.zeros(1,dtype=int)
var_DPhiMetSumTags = np.zeros(1,dtype=float)
var_TrackBdtScore = np.zeros(1,dtype=float)
var_TrackDeDx = np.zeros(1,dtype=float)
var_TrackDxy = np.zeros(1,dtype=float)
var_TrackChisquare = np.zeros(1,dtype=float)
var_SumTagPtOverMht = np.zeros(1,dtype=float)
var_TrackPt = np.zeros(1,dtype=float)
var_TrackP = np.zeros(1,dtype=float)
var_TrackEta = np.zeros(1,dtype=float)
var_CrossSection = np.zeros(1,dtype=float)
if isDasAndSignal: var_weight = np.zeros(1,dtype=float)

#####################################################
# declare tree and associate branches to containers #
#####################################################
tEvent = TTree('tEvent','tEvent')
tEvent.Branch('Met', var_Met,'Met/D')
tEvent.Branch('Mht', var_Mht,'Mht/D')
tEvent.Branch('Mt2', var_Mt2,'Mt2/D')
tEvent.Branch('Ht', var_Ht,'Ht/D')
tEvent.Branch('MinDeltaPhiMetJets', var_MinDeltaPhiMhtJets,'MinDeltaPhiMetJets/D')
tEvent.Branch('NJets', var_NJets,'NJets/I')
tEvent.Branch('BTags', var_BTags,'BTags/I')
tEvent.Branch('NLeptons', var_NLeptons,'NLeptons/I')
tEvent.Branch('NPhotons', var_NPhotons,'NPhotons/I')
tEvent.Branch('NPixelTags', var_NPixelTags,'NPixelTags/I')
tEvent.Branch('NPixelStripsTags', var_NPixelStripsTags,'NPixelStripsTags/I')
tEvent.Branch('NTags', var_NTags,'NTags/I')
tEvent.Branch('NPrompt', var_NPrompt,'NPrompt/I')
tEvent.Branch('TrackPt', var_TrackPt,'TrackPt/D')
tEvent.Branch('TrackP', var_TrackP,'TrackP/D')
tEvent.Branch('TrackEta', var_TrackEta,'TrackEta/D')
tEvent.Branch('SumTagPtOverMht', var_SumTagPtOverMht,'SumTagPtOverMht/D')
tEvent.Branch('TrackBdtScore', var_TrackBdtScore,'TrackBdtScore/D')
tEvent.Branch('TrackChisquare', var_TrackChisquare,'TrackChisquare/D')
tEvent.Branch('TrackDxy', var_TrackDxy,'TrackDxy/D')
tEvent.Branch('TrackDeDx', var_TrackDeDx,'TrackDeDx/D')
tEvent.Branch('CrossSection', var_CrossSection,'CrossSection/D')
if isDasAndSignal: tEvent.Branch('weight', var_weight,'weight/D')

###########################
# declare readers for BDT #
###########################

readerPixelOnly = TMVA.Reader()
pixelXml = '/nfs/dust/cms/user/kutznerv/cmsdas/BDTs/newpresel3-200-4-short-nodxyVtx/weights/TMVAClassification_BDT.weights.xml'
prepareReader(readerPixelOnly, pixelXml)
readerPixelStrips = TMVA.Reader()
trackerXml = '/nfs/dust/cms/user/kutznerv/cmsdas/BDTs/newpresel2-200-4-medium-nodxyVtx/weights/TMVAClassification_BDT.weights.xml'
prepareReader(readerPixelStrips, trackerXml)

c = TChain('TreeMaker2/PreSelection')
filenamelist = glob(infilenames)
print 'adding', filenamelist
filelist = []
for filename in filenamelist:
    fname = filename.strip()
    c.Add(fname)

c.Show(0)
nentries = min(9999999,c.GetEntries())
print 'will analyze', nentries

if isDasAndSignal: var_weight[0] = 1.0*xsecInPb/nentries
verbosity = 100

for ientry in range(nentries):

    if ientry%verbosity==0: 
        print 'analyzing event %d of %d' % (ientry, nentries)+ '....%f'%(100.*ientry/nentries)+'%'

    c.GetEntry(ientry)
    weight = c.CrossSection
    hHt.Fill(c.HT)
    hHtWeighted.Fill(c.HT, weight)


    if not (c.MHT>120): continue
    if not (c.NJets>0): continue
    
    
    if 'TTJets_TuneCUET' in infilenames:
	 if not c.madHT<600: continue
    if 'TTJets_HT' in infilenames:
    	if not c.madHT>600: continue  
    if 'WJetsToLNu_TuneCUET' in infilenames:
    	if not c.madHT<100: continue
    elif 'WJetsToLNu_HT' in infilenames:
	 if not c.madHT>100: continue  	      


    var_Met[0] = c.MET
    var_Mht[0] = c.MHT    
    var_Mt2[0] = c.MT2    
    var_Ht[0] = c.HT

    metvec = TLorentzVector()
    metvec.SetPtEtaPhiE(c.MET, 0, c.METPhi, c.MET)
    mhtvec = TLorentzVector()
    mhtvec.SetPtEtaPhiE(c.MHT, 0, c.MHTPhi, c.MHT)
    mindphi = 9999
    nj = 0
    nb = 0
    for ijet, jet in enumerate(c.Jets): #need dphi w.r.t. the modified mht
        if not (abs(jet.Eta())<5.0 and jet.Pt()>30): continue
        nj+=1
        if c.Jets_bDiscriminatorCSV[ijet]>csv_b: nb+=1
        if abs(jet.DeltaPhi(mhtvec))<mindphi:
            mindphi = abs(jet.DeltaPhi(mhtvec))
    var_MinDeltaPhiMhtJets[0] = mindphi

    var_NJets[0] = nj
    var_BTags[0] = nb
    var_NLeptons[0] = len(c.Electrons)+len(c.Muons)

    sumtagvec = TLorentzVector()
    nPixelOnly = 0
    nPixelStrips = 0

    mva, dedx, trkpt, trketa, trkp = -999, -999, -999, -999, -999
    trkdxy, trkchisq = -888,-888
    nprompt = 0
    pt = -1
    
    
    for itrack, track in enumerate(c.tracks):
        if not track.Pt() > 15 : continue
        if not abs(track.Eta()) < 2.4: continue
        if abs(abs(track.Eta()) < 1.566) and abs(track.Eta()) > 1.4442: continue
        mva_ = isDisappearingTrack_(track, itrack, c, readerPixelOnly, readerPixelStrips)
        if not mva_: continue            
        if mva_>mva: 
        	mva = mva_
        	dedx = c.tracks_deDxHarmonic2[itrack]
        	trkpt = c.tracks[itrack].Pt()
        	trkp = c.tracks[itrack].P()
        	trketa = c.tracks[itrack].Eta()  
        	trkdxy = abs(c.tracks_dxyVtx[itrack])
        	trkchisq = abs(c.tracks_chi2perNdof[itrack])        
        #if moh==0: print 'RunNum=%d, LumiBlockNum=%d, EvtNum=%d' % (c.RunNum, c.LumiBlockNum, c.EvtNum)
        sumtagvec+=track
        phits = c.tracks_nValidPixelHits[itrack]
        thits = c.tracks_nValidTrackerHits[itrack]        
        pixelOnly = phits>0 and thits==phits
        pixelStrips = not pixelOnly
        if pixelOnly: nPixelOnly+=1
        if pixelStrips: nPixelStrips+=1
        
        genParticles = []
        for igp, gp in enumerate(c.GenParticles):
            if not gp.Pt()>3: continue        
            if not abs(c.GenParticles_PdgId[igp]) in [11, 13, 211]: continue                    
            if not c.GenParticles_Status[igp] == 1: continue
            genpart = [gp.Clone(),-int(abs(c.GenParticles_PdgId[igp])/c.GenParticles_PdgId[igp])]
            genParticles.append(genpart)        
            
        if isMatched_([track, 0], genParticles, 0.01): nprompt+=1


    var_TrackDxy[0] = trkdxy
    var_TrackChisquare[0] = trkchisq 
    var_NPixelTags[0] = nPixelOnly
    var_NPixelStripsTags[0] = nPixelStrips
    var_NTags[0] = nPixelOnly+nPixelStrips
    if not var_NTags[0]>0: continue

    var_NPrompt[0] = nprompt
    var_DPhiMetSumTags[0] = abs(mhtvec.DeltaPhi(sumtagvec))
    var_SumTagPtOverMht[0] = sumtagvec.Pt()/mhtvec.Pt()
    var_TrackBdtScore[0] = mva
    var_TrackPt[0] = trkpt
    var_TrackP[0] = trkp
    var_TrackEta[0] = trketa        
    
    var_CrossSection[0] = c.CrossSection
    tEvent.Fill()


fnew.cd()
tEvent.Write()
print 'just created', fnew.GetName()
hHt.Write()
hHtWeighted.Write()
fnew.Close()
