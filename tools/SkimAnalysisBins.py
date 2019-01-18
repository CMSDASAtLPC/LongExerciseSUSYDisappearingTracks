#! /usr/bin/env python
# script to create trees with track variables
# created May 3, 2017 -Sam Bein 
#python tools/SkimTreeMaker.py /nfs/dust/cms/user/beinsam/CommonNtuples/MC_BSM/LongLivedSMS/ntuple_sidecar/g1800_chi1400_27_200970_step4_30.root

from ROOT import *
from utils import *
import os, sys
from glob import glob

distracklibs = os.environ['CMSSW_BASE']+'/src/analysis/tools/distracklibs.py'
execfile(distracklibs)

hAnalysisBins = TH1F('hAnalysisBins','hAnalysisBins',33,0,33)
histoStyler(hAnalysisBins, kBlack)

defaultInfile = '/pnfs/desy.de/cms/tier2/store/user/sbein/NtupleHub/Production2016v2/Summer16.WJetsToLNu_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_20_RA2AnalysisTree.root'
defaultInfile = '/nfs/dust/cms/user/beinsam/CommonNtuples/MC_BSM/LongLivedSMS/ntuple_sidecar/g1800_chi1400_27_200970_step4_100.root'
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbosity", type=bool, default=False,help="analyzer script to batch")
parser.add_argument("-analyzer", "--analyzer", type=str,default='tools/ResponseMaker.py',help="analyzer")
parser.add_argument("-fin", "--fnamekeyword", type=str,default=defaultInfile,help="file")
parser.add_argument("-jersf", "--JerUpDown", type=str, default='Nom',help="JER scale factor (Nom, Up, ...)")
args = parser.parse_args()
fnamekeyword = args.fnamekeyword.strip()
analyzer = args.analyzer
JerUpDown = args.JerUpDown
#smdir = '/nfs/dust/cms/user/beinsam/CommonNtuples/MC_SM/'
#smdir = '/pnfs/desy.de/cms/tier2/store/user/sbein/CommonNtuples/'

isPrivateSignal = True
#cross sections can be looked up on the SUSY xsec working group page:
#https://twiki.cern.ch/twiki/bin/view/LHCPhysics/SUSYCrossSections#Cross_sections_for_various_S_AN2
if isPrivateSignal: 
	xsecInPb = 0.00276133
	#lumi = 135
print 'isPrivateSignal?', isPrivateSignal

lepPtCut = 20
csv_b = 0.8484
csv_b = 0.8838# new with CMSSW_9


'''Must integrate these:
        CSV         DeepCSV
2016   0.8484    0.6324

2017  0.8838     0.4941

2018  0.8838     0.4941
'''



def isDisappearingTrack_(track, itrack, c, readerPixelOnly, readerPixelStrips):###from Akshansh
        moh_ = c.tracks_nMissingOuterHits[itrack]
        phits = c.tracks_nValidPixelHits[itrack]
        thits = c.tracks_nValidTrackerHits[itrack]
        tlayers = c.tracks_trackerLayersWithMeasurement[itrack]
        pixelOnly = phits>0 and thits==phits
        medium = tlayers< 7 and (thits-phits)>0
        long   = tlayers>=7 and (thits-phits)>0
        pixelStrips = medium or long
        if pixelStrips:
                if not moh_>=2: return 0
        if not (c.tracks_nMissingInnerHits[itrack]==0): return 0
        if not (pixelOnly or pixelStrips): return 0                                                                                                         
        if not c.tracks_passPFCandVeto[itrack]: return 0
        pterr = c.tracks_ptError[itrack]/(track.Pt()*track.Pt())        
        dxyVtx = abs(c.tracks_dxyVtx[itrack])
        dzVtx = abs(c.tracks_dzVtx[itrack])        
        if not (c.tracks_trkRelIso[itrack]<0.2 and dzVtx<0.1 and pterr<10): return 0
        if not (c.tracks_trackQualityHighPurity[itrack]): return 0
        nhits = c.tracks_nValidTrackerHits[itrack]
        nlayers = c.tracks_trackerLayersWithMeasurement[itrack]
        if not (nlayers>=2 and nhits>=2): return 0
        matchedCalo = c.tracks_matchedCaloEnergy[itrack]        
        if not dxyVtx < 0.1: return 0
        #if not c.tracks_trackJetIso[itrack]>0.4: return False
        #print c.tracks_trackJetIso[itrack]
        #if not c.tracks_minDrLetpons[itrack]>0.01: return False	        
        trackfv = [dxyVtx, dzVtx, matchedCalo, c.tracks_trkRelIso[itrack], phits, thits, moh_, pterr]
        if pixelOnly:
                mva_ = evaluateBDT(readerPixelOnly, trackfv)
                if not mva_ > -0.2: return 0###.1
                else: return 1
        elif pixelStrips:
                mva_ = evaluateBDT(readerPixelStrips, trackfv)             
                if not mva_ > 0:return 0###.25
                else: return 2
        else:
                return 0
                
                
##########################################################
# files specified with optional wildcards @ command line #
##########################################################

if 'Fall17' in fnamekeyword or 'Run2017' in fnamekeyword: phase = 1
else: phase = 0

#############################################
# Book new file in which to write skim tree #
#############################################
newfilename = 'skim_'+(fnamekeyword.split('/')[-1]).replace('*','')
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
var_MinDeltaPhiMhtJets = np.zeros(1,dtype=float)
var_NJets = np.zeros(1,dtype=int)
var_BTags = np.zeros(1,dtype=int)
var_NLeptons = np.zeros(1,dtype=int)
var_NPhotons = np.zeros(1,dtype=int)
var_NTags = np.zeros(1,dtype=int)
var_NShortTags = np.zeros(1,dtype=int)
var_NLongTags = np.zeros(1,dtype=int)
var_DPhiMhtSumTags = np.zeros(1,dtype=float)
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
var_SearchBin = np.zeros(1,dtype=int)
var_SumTagPtOverMht = np.zeros(1,dtype=float)
var_CrossSection = np.zeros(1,dtype=float)
if isPrivateSignal: var_weight = np.zeros(1,dtype=float)

#####################################################
# declare tree and associate branches to containers #
#####################################################
tEvent = TTree('tEvent','tEvent')
tEvent.Branch('Met', var_Met,'Met/D')
tEvent.Branch('Mht', var_Mht,'Mht/D')
tEvent.Branch('Ht', var_Ht,'Ht/D')
tEvent.Branch('MinDeltaPhiMhtJets', var_MinDeltaPhiMhtJets,'MinDeltaPhiMhtJets/D')
tEvent.Branch('NJets', var_NJets,'NJets/I')
tEvent.Branch('BTags', var_BTags,'BTags/I')
tEvent.Branch('NLeptons', var_NLeptons,'NLeptons/I')
tEvent.Branch('NPhotons', var_NPhotons,'NPhotons/I')
tEvent.Branch('NTags', var_NTags,'NTags/I')
tEvent.Branch('NShortTags', var_NShortTags,'NShortTags/I')
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
tEvent.Branch('SearchBin', var_SearchBin,'SearchBin/I')

if isPrivateSignal: tEvent.Branch('weight', var_weight,'weight/D')


##############################################
# Define feature vector and analysis bins ####
##############################################
binnumbers = {}
listagain = ['Ht',  'Mht',    'NJets','BTags','NTags','NPix', 'NPixStrips', 'MinDPhiMhtJets', 'NElectrons', 'NMuons', 'TrkPt','TrkEta','BinNumber']
binnumbers[((0,inf),(250,400),(1,1),  (0,inf),(1,1),  (0,0),  (1,1),        (0.5,inf))] = 1
binnumbers[((0,inf),(250,400),(2,5),  (0,0),  (1,1),  (0,0),  (1,1),        (0.5,inf))] = 2
binnumbers[((0,inf),(250,400),(2,5),  (1,5),  (1,1),  (0,0),  (1,1),        (0.5,inf))] = 3
binnumbers[((0,inf),(250,400),(6,inf),(0,0),  (1,1),  (0,0),  (1,1),        (0.5,inf))] = 4
binnumbers[((0,inf),(250,400),(6,inf),(1,inf),(1,1),  (0,0),  (1,1),        (0.5,inf))] = 5
binnumbers[((0,inf),(400,700),(1,1),  (0,inf),(1,1),  (0,0),  (1,1),        (0.3,inf))] = 6
binnumbers[((0,inf),(400,700),(2,5),  (0,0),  (1,1),  (0,0),  (1,1),        (0.3,inf))] = 7
binnumbers[((0,inf),(400,700),(2,5),  (1,5),  (1,1),  (0,0),  (1,1),        (0.3,inf))] = 8
binnumbers[((0,inf),(400,700),(6,inf),(0,0),  (1,1),  (0,0),  (1,1),        (0.3,inf))] = 9
binnumbers[((0,inf),(400,700),(6,inf),(1,inf),(1,1),  (0,0),  (1,1),        (0.3,inf))] = 10
binnumbers[((0,inf),(700,inf),(1,1),  (0,inf),(1,1),  (0,0),  (1,1),        (0.3,inf))] = 11
binnumbers[((0,inf),(700,inf),(2,5),  (0,0),  (1,1),  (0,0),  (1,1),        (0.3,inf))] = 12
binnumbers[((0,inf),(700,inf),(2,5),  (1,5),  (1,1),  (0,0),  (1,1),        (0.3,inf))] = 13
binnumbers[((0,inf),(700,inf),(6,inf),(0,0),  (1,1),  (0,0),  (1,1),        (0.3,inf))] = 14
binnumbers[((0,inf),(700,inf),(6,inf),(1,inf),(1,1),  (0,0),  (1,1),        (0.3,inf))] = 15
binnumbers[((0,inf),(250,400),(1,1),  (0,inf),(1,1),  (1,1),  (0,0),        (0.5,inf))] = 16
binnumbers[((0,inf),(250,400),(2,5),  (0,0),  (1,1),  (1,1),  (0,0),        (0.5,inf))] = 17
binnumbers[((0,inf),(250,400),(2,5),  (1,5),  (1,1),  (1,1),  (0,0),        (0.5,inf))] = 18
binnumbers[((0,inf),(250,400),(6,inf),(0,0),  (1,1),  (1,1),  (0,0),        (0.5,inf))] = 19
binnumbers[((0,inf),(250,400),(6,inf),(1,inf),(1,1),  (1,1),  (0,0),        (0.5,inf))] = 20
binnumbers[((0,inf),(400,700),(1,1),  (0,inf),(1,1),  (1,1),  (0,0),        (0.3,inf))] = 21
binnumbers[((0,inf),(400,700),(2,5),  (0,0),  (1,1),  (1,1),  (0,0),        (0.3,inf))] = 22
binnumbers[((0,inf),(400,700),(2,5),  (1,5),  (1,1),  (1,1),  (0,0),        (0.3,inf))] = 23
binnumbers[((0,inf),(400,700),(6,inf),(0,0),  (1,1),  (1,1),  (0,0),        (0.3,inf))] = 24
binnumbers[((0,inf),(400,700),(6,inf),(1,inf),(1,1),  (1,1),  (0,0),        (0.3,inf))] = 25
binnumbers[((0,inf),(700,inf),(1,1),  (0,inf),(1,1),  (1,1),  (0,0),        (0.3,inf))] = 26
binnumbers[((0,inf),(700,inf),(2,5),  (0,0),  (1,1),  (1,1),  (0,0),        (0.3,inf))] = 27
binnumbers[((0,inf),(700,inf),(2,5),  (1,5),  (1,1),  (1,1),  (0,0),        (0.3,inf))] = 28
binnumbers[((0,inf),(700,inf),(6,inf),(0,0),  (1,1),  (1,1),  (0,0),        (0.3,inf))] = 29
binnumbers[((0,inf),(700,inf),(6,inf),(1,inf),(1,1),  (1,1),  (0,0),        (0.3,inf))] = 30
binnumbers[((0,inf),(250,400),(1,inf),(0,inf),(2,inf),(0,inf),(0,inf),      (0.0,inf))] = 31
binnumbers[((0,inf),(400,inf),(1,inf),(0,inf),(2,inf),(0,inf),(0,inf),      (0.0,inf))] = 32

def getBinNumber(fv):
    for binkey in binnumbers:
        foundbin = True
        for iwindow, window in enumerate(binkey):
            if not (fv[iwindow]>=window[0] and fv[iwindow]<=window[1]): 
            	foundbin = False
            	break
        if foundbin: return binnumbers[binkey]
    return -1

##############################################
# declare readers and selection code for BDT #
##############################################
if phase==0:
    pixelXml =       '/nfs/dust/cms/user/kutznerv/disapptrks/track-tag/cmssw8-newpresel3-200-4-short-updated/weights/TMVAClassification_BDT.weights.xml'
    LongXml = '/nfs/dust/cms/user/kutznerv/disapptrks/track-tag/cmssw8-newpresel2-200-4-medium-updated/weights/TMVAClassification_BDT.weights.xml'
else:
    pixelXml = '/nfs/dust/cms/user/kutznerv/disapptrks/track-tag/cmssw10-newpresel3-200-4-short/weights/TMVAClassification_BDT.weights.xml'
    LongXml = '/nfs/dust/cms/user/kutznerv/disapptrks/track-tag/cmssw10-newpresel2-200-4-medium/weights/TMVAClassification_BDT.weights.xml'    
readerShort = TMVA.Reader()
readerLong = TMVA.Reader()
prepareReaderShort(readerShort, pixelXml)
prepareReaderLong(readerLong, LongXml)

fMask = TFile('usefulthings/Masks.root')
if 'Run2016' in fnamekeyword: hMask = fMask.Get('hEtaVsPhiDT_maskData-2016Data-2016')
else: hMask = fMask.Get('hEtaVsPhiDT_maskMC-2016MC-2016')

c = TChain('TreeMaker2/PreSelection')
filenamelist = glob(fnamekeyword)
print 'adding', filenamelist
filelist = []
for filename in filenamelist: c.Add(filename.strip())

#c.Show(0)
nentries = min(9999999,c.GetEntries())
print 'will analyze', nentries

if isPrivateSignal: var_weight[0] = 1.0*xsecInPb/nentries
verbosity = 10000

for ientry in range(nentries):

    if ientry%verbosity==0: 
        print 'analyzing event %d of %d' % (ientry, nentries)+ '....%f'%(100.*ientry/nentries)+'%'

    c.GetEntry(ientry)
    weight = c.CrossSection
    hHt.Fill(c.HT)
    hHtWeighted.Fill(c.HT, weight)

    if not (c.MET>120): continue
    if not (c.NJets>0): continue
    if not passesUniversalSelection(c): continue
    
    if 'TTJets_TuneCUET' in filenamelist[0]:
     if not c.madHT<600: continue
    if 'TTJets_HT' in filenamelist[0]:
        if not c.madHT>600: continue  
    if 'WJetsToLNu_TuneCUET' in filenamelist[0]:
        if not c.madHT<100: continue
    elif 'WJetsToLNu_HT' in filenamelist[0]:
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
    for jet in jets[:4]: 
        if abs(jet.DeltaPhi(mhtvec))<mindphi:
            mindphi = abs(jet.DeltaPhi(mhtvec))
            
    var_Ht[0] = ht
    var_MinDeltaPhiMhtJets[0] = mindphi
    var_BTags[0] = nb
    var_NLeptons[0] = c.NElectrons+c.NMuons

    sumtagvec = TLorentzVector()
    nshortelOnly = 0
    nshortelStrips = 0
    
    mvas = []
    trkpts = []
    trketas = []
    trkphis = []    
    trkdxys = []
    trkchisqs = [] 
    dedxs = []
    massfromdedxs = []
    islong = []
    ismatcheds = []
    ntags = 0
    nshort, nlong = 0, 0
    disappearingTracks = []
    for itrack, track in enumerate(c.tracks):
            if not abs(track.Eta()) < 2.4: continue
            if abs(abs(track.Eta()) < 1.566) and abs(track.Eta()) > 1.4442: continue
            if not (track.Pt()>lepPtCut and track.Pt()<9999): continue
            if not isBaselineTrack(track, itrack, c, hMask): continue
            mva_ = isDisappearingTrack_(track, itrack, c, readerShort, readerLong)
            if mva_==0: continue
            passeslep = True
            drlep = 99
            for ilep, lep in enumerate(c.Electrons):
                drlep = min(drlep, lep.DeltaR(track))
                if drlep<0.01: 
                    passeslep = False
                    break
            for ilep, lep in enumerate(c.Muons):
                drlep = min(drlep, lep.DeltaR(track))
                if drlep<0.01: 
                    passeslep = False
                    break                
            if not passeslep: continue        
            
            ntags+=1
            mvas.append(mva_)
            trkpts.append(c.tracks[itrack].Pt())
            trketas.append(c.tracks[itrack].Eta())
            trkphis.append(c.tracks[itrack].Phi())
            trkdxys.append(abs(c.tracks_dxyVtx[itrack]))
            trkchisqs.append(c.tracks_chi2perNdof[itrack])
            dedxs.append(c.tracks_deDxHarmonic2[itrack])   
            massfromdedxs.append(TMath.Sqrt((dedxs[-1]-2.557)*pow(c.tracks[itrack].P(),2)/2.579))
            sumtagvec+=track
            phits = c.tracks_nValidPixelHits[itrack]
            thits = c.tracks_nValidTrackerHits[itrack]        
            Short = phits>0 and thits==phits
            Long = not Short
            if Long: 
                islong.append(1)
                nshort+=1
            else: 
                islong.append(0) 
                nlong+=1
            disappearingTracks.append(c.tracks[itrack])
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
    
    adjustedMht = TLorentzVector()
    adjustedMht.SetPxPyPzE(0,0,0,0)
    adjustedJets = []
    adjustedHt = 0
    adjustedBTags = 0
    
    for ijet, jet in enumerate(c.Jets):
        if not jet.Pt()>30: continue
        if not abs(jet.Eta())<5.0: continue
        drDt = 9999
        for dt in disappearingTracks: drDt = min(drDt, jet.DeltaR(dt))
        if not drDt>0.4: continue
        adjustedMht-=jet
        if not abs(jet.Eta())<2.4: continue
        adjustedJets.append(jet)            
        adjustedHt+=jet.Pt()
        if c.Jets_bDiscriminatorCSV[ijet]>csv_b: adjustedBTags+=1
    adjustedNJets = len(adjustedJets)
    mindphi = 4
    for jet in adjustedJets[:4]: mindphi = min(mindphi, abs(jet.DeltaPhi(adjustedMht)))
    
    fv = [adjustedHt,adjustedMht.Pt(),adjustedNJets,adjustedBTags, ntags,nshort,nlong, mindphi]
    binnumber = getBinNumber(fv)
    fv.append(binnumber)
    var_SearchBin[0] = binnumber
    
    fillth1(hAnalysisBins, binnumber, var_weight[0])
            
    if len(mvas)==1:
        var_Track1BdtScore[0] = mvas[0]
        var_Track1Pt[0] = trkpts[0]
        var_Track1Eta[0] = trketas[0]
        var_Track1Phi[0] = trkphis[0]
        var_Track1Chisquare[0] = trkchisqs[0]
        var_Track1Dxy[0] = trkdxys[0]        
        var_Track1Dedx[0] = dedxs[0] 
        var_Track1MassFromDedx[0] = massfromdedxs[0] 
        var_Track1IsLong[0] = islong[0]
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
        var_Track2IsLong[0] = islong[1]
        var_Track2IsGenMatched[0] = ismatcheds[1]   
        
    var_NTags[0] = ntags
    var_NShortTags[0] = nshort
    var_NLongTags[0] = nlong        
    var_DPhiMhtSumTags[0] = abs(mhtvec.DeltaPhi(sumtagvec))
    var_SumTagPtOverMht[0] = sumtagvec.Pt()/mhtvec.Pt()

    var_CrossSection[0] = c.CrossSection
    tEvent.Fill()


fnew.cd()
tEvent.Write()
hAnalysisBins.Write()
print 'just created', fnew.GetName()
hHt.Write()
hHtWeighted.Write()
fnew.Close()
