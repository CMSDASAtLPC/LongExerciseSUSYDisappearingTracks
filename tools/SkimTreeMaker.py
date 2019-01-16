#! /usr/bin/env python
# script to create trees with track variables
# created May 3, 2017 -Sam Bein 

#python tools/SkimTreeMaker.py /nfs/dust/cms/user/beinsam/CommonNtuples/MC_BSM/LongLivedSMS/ntuple_sidecar/g1800_chi1400_27_200970_step4_30.root

from ROOT import *
from utils import *
import os, sys
from glob import glob
csv_b = 0.8484

isDasAndSignal = True
#cross sections can be looked up on the SUSY xsec working group page:
#https://twiki.cern.ch/twiki/bin/view/LHCPhysics/SUSYCrossSections#Cross_sections_for_various_S_AN2
if isDasAndSignal: xsecInPb = 0.00276133

#smdir = '/nfs/dust/cms/user/beinsam/CommonNtuples/MC_SM/'
#smdir = '/pnfs/desy.de/cms/tier2/store/user/sbein/CommonNtuples/'
print 'isDasAndSignal?', isDasAndSignal
##########################################################
# files specified with optional wildcards @ command line #
##########################################################
try: infilenames = sys.argv[1]
except: infilenames = '/eos/uscms/store/user/cmsdas/2019/long_exercises/DisappearingTracks/Ntuples/g1800_chi1400_27_200970_step4_30.root'


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
var_Ht = np.zeros(1,dtype=float)
var_MinDeltaPhiMetJets = np.zeros(1,dtype=float)
var_NJets = np.zeros(1,dtype=int)
var_BTags = np.zeros(1,dtype=int)
var_NLeptons = np.zeros(1,dtype=int)
var_NPhotons = np.zeros(1,dtype=int)
var_NTags = np.zeros(1,dtype=int)
var_NPixelTags = np.zeros(1,dtype=int)
var_NLongTags = np.zeros(1,dtype=int)
var_DPhiMetSumTags = np.zeros(1,dtype=float)
var_Track1BdtScore = np.zeros(1,dtype=float)
var_Track1Dedx = np.zeros(1,dtype=float)
var_Track1Dxy = np.zeros(1,dtype=float)
var_Track1Chisquare = np.zeros(1,dtype=float)
var_Track1Pt = np.zeros(1,dtype=float)
var_Track1Eta = np.zeros(1,dtype=float)
var_Track1Phi = np.zeros(1,dtype=float)
var_Track2Phi = np.zeros(1,dtype=float)
var_Track2BdtScore = np.zeros(1,dtype=float)
var_Track1Dedx = np.zeros(1,dtype=float)
var_Track2Dedx = np.zeros(1,dtype=float)
var_Track1MassFromDedx = np.zeros(1,dtype=float)
var_Track2MassFromDedx = np.zeros(1,dtype=float)
var_Track2Dxy = np.zeros(1,dtype=float)
var_Track2Chisquare = np.zeros(1,dtype=float)
var_Track2Pt = np.zeros(1,dtype=float)
var_Track2Eta = np.zeros(1,dtype=float)
var_Track1IsLong = np.zeros(1,dtype=int)
var_Track2IsLong = np.zeros(1,dtype=int)
var_Track1IsGenMatched = np.zeros(1,dtype=int)
var_Track2IsGenMatched = np.zeros(1,dtype=int)

var_SumTagPtOverMht = np.zeros(1,dtype=float)
var_CrossSection = np.zeros(1,dtype=float)
if isDasAndSignal: var_weight = np.zeros(1,dtype=float)

#####################################################
# declare tree and associate branches to containers #
#####################################################
tEvent = TTree('tEvent','tEvent')
tEvent.Branch('Met', var_Met,'Met/D')
tEvent.Branch('Mht', var_Mht,'Mht/D')
tEvent.Branch('Ht', var_Ht,'Ht/D')
tEvent.Branch('MinDeltaPhiMetJets', var_MinDeltaPhiMetJets,'MinDeltaPhiMetJets/D')
tEvent.Branch('NJets', var_NJets,'NJets/I')
tEvent.Branch('BTags', var_BTags,'BTags/I')
tEvent.Branch('NLeptons', var_NLeptons,'NLeptons/I')
tEvent.Branch('NPhotons', var_NPhotons,'NPhotons/I')
tEvent.Branch('NTags', var_NTags,'NTags/I')
tEvent.Branch('NPixelTags', var_NPixelTags,'NPixelTags/I')
tEvent.Branch('NLongTags', var_NLongTags,'NLongTags/I')
tEvent.Branch('Track1Pt', var_Track1Pt,'Track1Pt/D')
tEvent.Branch('Track2Pt', var_Track2Pt,'Track2Pt/D')
tEvent.Branch('Track1Eta', var_Track1Eta,'Track1Eta/D')
tEvent.Branch('Track2Eta', var_Track2Eta,'Track2Eta/D')
tEvent.Branch('Track1Phi', var_Track1Phi,'Track1Phi/D')
tEvent.Branch('Track2Phi', var_Track1Phi,'Track2Phi/D')
tEvent.Branch('Track1BdtScore', var_Track1BdtScore,'Track1BdtScore/D')
tEvent.Branch('Track2BdtScore', var_Track2BdtScore,'Track2BdtScore/D')
tEvent.Branch('Track1Chisquare', var_Track1Chisquare,'Track1Chisquare/D')
tEvent.Branch('Track2Chisquare', var_Track2Chisquare,'Track2Chisquare/D')
tEvent.Branch('Track1Dxy', var_Track1Dxy,'Track1Dxy/D')
tEvent.Branch('Track2Dxy', var_Track1Dxy,'Track2Dxy/D')
tEvent.Branch('Track1Dedx', var_Track1Dedx,'Track1Dedx/D')
tEvent.Branch('Track2Dedx', var_Track2Dedx,'Track2Dedx/D')
tEvent.Branch('Track1MassFromDedx', var_Track1MassFromDedx,'Track1MassFromDedx/D')
tEvent.Branch('Track2MassFromDedx', var_Track2MassFromDedx,'Track2MassFromDedx/D')
tEvent.Branch('Track1IsLong', var_Track1IsLong,'Track1IsLong/I')
tEvent.Branch('Track2IsLong', var_Track2IsLong,'Track2IsLong/I')
tEvent.Branch('Track1IsGenMatched', var_Track1IsGenMatched,'Track1IsGenMatched/I')
tEvent.Branch('Track2IsGenMatched', var_Track2IsGenMatched,'Track2IsGenMatched/I')
tEvent.Branch('SumTagPtOverMht', var_SumTagPtOverMht,'SumTagPtOverMht/D')


tEvent.Branch('CrossSection', var_CrossSection,'CrossSection/D')
if isDasAndSignal: tEvent.Branch('weight', var_weight,'weight/D')

###########################
# declare readers for BDT #
###########################

readerShort = TMVA.Reader()
#pixelXml = '/nfs/dust/cms/user/kutznerv/cmsdas/BDTs/newpresel3-200-4-short-nodxyVtx/weights/TMVAClassification_BDT.weights.xml'
###pixelXml = '/nfs/dust/cms/user/kutznerv/shorttrack/fake-tracks/newpresel3-200-4-short/weights/TMVAClassification_BDT.weights.xml'
pixelXml = '/eos/uscms/store/user/cmsdas/2019/long_exercises/DisappearingTracks/track-tag/cmssw8-newpresel3-200-4-short-updated/weights/TMVAClassification_BDT.weights.xml'
prepareReaderShort(readerShort, pixelXml)
readerLong = TMVA.Reader()
trackerXml = '/eos/uscms/store/user/cmsdas/2019/long_exercises/DisappearingTracks/track-tag/cmssw8-newpresel2-200-4-medium-updated/weights/TMVAClassification_BDT.weights.xml'
prepareReaderLong(readerLong, trackerXml)

c = TChain('TreeMaker2/PreSelection')
filenamelist = glob(infilenames)
print 'adding', filenamelist
filelist = []
for filename in filenamelist:
    fname = filename.strip()
    fname_ = fname.replace('/eos/uscms/','root://cmsxrootd.fnal.gov//')
    c.Add(fname_)

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


    if not (c.MET>120): continue
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

    metvec = TLorentzVector()
    metvec.SetPtEtaPhiE(c.MET, 0, c.METPhi, c.MET)
    mhtvec = TLorentzVector()
    mhtvec.SetPtEtaPhiE(0, 0, 0, 0)
    jets = []
    nb = 0
    ht = 0
    for ijet, jet in enumerate(c.Jets): #need dphi w.r.t. the modified mht
        if not (abs(jet.Eta())<2.4 and jet.Pt()>30): continue
        mhtvec-=jet
        jets.append(jet)
        ht+=jet.Pt()        
        if c.Jets_bDiscriminatorCSV[ijet]>csv_b: nb+=1
    var_NJets[0] = len(jets)
    var_Mht[0] = mhtvec.Pt()
    mindphi = 9999   
    for jet in jets: 
    	if abs(jet.DeltaPhi(mhtvec))<mindphi:
        	mindphi = abs(jet.DeltaPhi(mhtvec))
            
    var_Ht[0] = ht
    var_MinDeltaPhiMetJets[0] = mindphi
    var_BTags[0] = nb
    var_NLeptons[0] = c.NElectrons+c.NMuons

    sumtagvec = TLorentzVector()
    nShort = 0
    nLong = 0
    
    mvas = []
    trkpts = []
    trketas = []
    trkphis = []    
    trkdxys = []
    trkchisqs = [] 
    dedxs = []
    massfromdedxs = []
    ispixelstripss = [0]
    ismatcheds = [0]
    ntags = 0
    npix, npixstrips = 0, 0
    for itrack, track in enumerate(c.tracks):
            if not track.Pt() > 15 : continue
            if not abs(track.Eta()) < 2.4: continue
            if abs(abs(track.Eta()) < 1.566) and abs(track.Eta()) > 1.4442: continue
            mva_ = isDisappearingTrack_(track, itrack, c, readerShort, readerLong)
            if not mva_: continue
            ntags+=1
            mvas.append(mva_)
            trkpts.append(c.tracks[itrack].Pt())
            trketas.append(c.tracks[itrack].Eta())
            trkphis.append(c.tracks[itrack].Phi())
            trkdxys.append(abs(c.tracks_dxyVtx[itrack]))
            trkchisqs.append(c.tracks_chi2perNdof[itrack])
            dedxs.append(c.tracks_deDxHarmonic2[itrack])   
            massfromdedxs.append(TMath.Sqrt((dedxs[-1]-2.557)*pow(c.tracks[itrack].P(),2)/2.579))
            #if moh==0: print 'RunNum=%d, LumiBlockNum=%d, EvtNum=%d' % (c.RunNum, c.LumiBlockNum, c.EvtNum)
            sumtagvec+=track
            phits = c.tracks_nValidPixelHits[itrack]
            thits = c.tracks_nValidTrackerHits[itrack]        
            pixelOnly = phits>0 and thits==phits
            pixelStrips = not pixelOnly
            if pixelStrips: 
            	ispixelstripss.append(1)
            	npix+=1
            else: 
            	ispixelstripss.append(0) 
            	npixstrips+=1
            genParticles = []
            for igp, gp in enumerate(c.GenParticles):
                if not gp.Pt()>3: continue        
                if not abs(c.GenParticles_PdgId[igp]) in [11, 13, 211]: continue                    
                if not c.GenParticles_Status[igp] == 1: continue
                genpart = [gp.Clone(),-int(abs(c.GenParticles_PdgId[igp])/c.GenParticles_PdgId[igp])]
                genParticles.append(genpart)        
            if isMatched_([track, 0], genParticles, 0.01): ismatcheds.append(True)
            else: ismatcheds.append(False)
            
    if len(mvas)==0: continue
    if len(mvas)==1:
        var_Track1BdtScore[0] = mvas[0]
        var_Track1Pt[0] = trkpts[0]
        var_Track1Eta[0] = trketas[0]
        var_Track1Phi[0] = trkphis[0]
        var_Track1Chisquare[0] = trkchisqs[0]
        var_Track1Dxy[0] = trkdxys[0]        
        var_Track1Dedx[0] = dedxs[0] 
        var_Track1MassFromDedx[0] = massfromdedxs[0] 
        var_Track1IsLong[0] = ispixelstripss[0]
        var_Track1IsGenMatched[0] = ismatcheds[0]   
        
        var_Track2BdtScore[0] = -11
        var_Track2Pt[0] = -11
        var_Track2Eta[0] = -11
        var_Track2Phi[0] = -11
        var_Track2Chisquare[0] = -11
        var_Track2Dxy[0] = -11
        var_Track2Dedx[0] = -11
        var_Track2MassFromDedx[0] = -11
        var_Track2IsLong[0] = -11
        var_Track2IsGenMatched[0] = -11
                 
    if len(mvas)>1:
        var_Track2BdtScore[0] = mvas[1]
        var_Track2Pt[0] = trkpts[1]
        var_Track2Eta[0] = trketas[1]
        var_Track2Phi[0] = trkphis[1]
        var_Track2Chisquare[0] = trkchisqs[1]
        var_Track2Dxy[0] = trkdxys[1]        
        var_Track2Dedx[0] = dedxs[1] 
        var_Track2MassFromDedx[0] = massfromdedxs[1] 
        var_Track2IsLong[0] = ispixelstripss[1]
        var_Track2IsGenMatched[0] = ismatcheds[1]   
    var_NTags[0] = ntags
    var_NPixelTags[0] = npix
    var_NLongTags[0] = npixstrips        
        
        
    var_DPhiMetSumTags[0] = abs(mhtvec.DeltaPhi(sumtagvec))
    var_SumTagPtOverMht[0] = sumtagvec.Pt()/mhtvec.Pt()

    
    var_CrossSection[0] = c.CrossSection
    tEvent.Fill()


fnew.cd()
tEvent.Write()
print 'just created', fnew.GetName()
hHt.Write()
hHtWeighted.Write()
fnew.Close()
