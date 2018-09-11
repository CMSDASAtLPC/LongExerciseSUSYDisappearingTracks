import sys
import time
import numpy as np
from ROOT import *
from utils import *
from utilsII import *
from glob import glob
from random import shuffle
import random


weight = 1 #################################WEIGHT 
 
gROOT.SetBatch()
gROOT.SetStyle('Plain')

verbose = False
try: inputFileNames = sys.argv[1]
except: inputFileNames = "/pnfs/desy.de/cms/tier2/store/user/sbein/NtupleHub/Production2016v2/Summer16.WJetsToLNu_HT-1200To2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_88_RA2AnalysisTree.root"
inputFiles = glob(inputFileNames)
x = len(inputFiles)

c = TChain("TreeMaker2/PreSelection")
datamc = 'mc'
mZ = 91
print mZ
##pause()
doGenVersion = True
RelaxGenKin = True

fileKappa = 'Kappa.root'
fKappa  = TFile(fileKappa)
KappaMap = fKappa.Get("kappaPtvsEta")
KappaMapPlus = fKappa.Get("kappaPtvsEtaPlus")
KappaMapMinus = fKappa.Get("kappaPtvsEtaMinus")
KappaMapPt = fKappa.Get("kappaGenInfoPt")

print KappaMapPt.GetBinContent(0)
print KappaMapPt.GetBinContent(1)
print KappaMapPt.GetBinContent(2)
print KappaMapPt.GetBinContent(3)
print KappaMapPt.GetBinContent(4)
print KappaMapPt.GetBinContent(5)
print KappaMapPt.GetBinContent(6)
print KappaMapPt.GetBinContent(7)
print KappaMapPt.GetBinContent(8)
print KappaMapPt.GetBinContent(9)
print KappaMapPt.GetBinContent(10)
print KappaMapPt.GetBinContent(11)


print KappaMap.GetBinContent(1,1)
print KappaMap.GetBinContent(2,2)
print KappaMap.GetBinContent(3,3)
print KappaMap.GetBinContent(4,4)
print KappaMap.GetBinContent(5,1)
print KappaMap.GetBinContent(6,2)
print KappaMap.GetBinContent(7,3)
print KappaMap.GetBinContent(8,4)
print KappaMap.GetBinContent(9,1)
print KappaMap.GetBinContent(10,2)

#pause()
hPtControl        = TH1D("hPtControl", "PtControl", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
hPtMethod        = TH1D("hPtMethod", "PtMethod", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
hPtTruth        = TH1D("hPtTruth", "PtTruth", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
histoStyler(hPtControl,1)
histoStyler(hPtMethod,1)
histoStyler(hPtTruth ,1)
# (Ptbin,Etabin)::(x,y)
for f in range(0,x):
	print 'file number:', f, ':',inputFiles[f]
	c.Add(inputFiles[f])
nentries = c.GetEntries()

verbosity = 1000
identifier = inputFiles[0][inputFiles[0].rfind('/')+1:].replace('.root','').replace('Summer16.','').replace('RA2AnalysisTree','')
identifier+='nFiles'+str(len(inputFiles))
print 'Identifier', identifier


newfname = 'PromptBkgHists_'+identifier+'.root'

if doGenVersion: newfname = newfname.replace('.root','Truth.root')
fnew_ = TFile(newfname,'recreate')
print 'Will write results to', newfname

hHt = TH1F('hHt','hHt',100,0,3000)
hHtWeighted = TH1F('hHtWeighted','hHtWeighted',100,0,3000)

inf = 999999999
regionCuts = {}
regionCuts['NoCuts']              = [(0,inf),(0,inf),(0,inf),(0,inf),(0,2.4),(0,inf)]
regionCuts['LowMhtBaseline']      = [(200,inf),(150,inf),(1,inf),(15,inf),(0,2.4),(0,inf)]


dKappaBinList = {}
for iPtBin, PtBin in enumerate(PtBinEdges[:-1]):
        for iEtaBin, EtaBin in enumerate(EtaBinEdges[:-1]):
                newHistKey = ((EtaBin,EtaBinEdges[iEtaBin + 1]),(PtBin,PtBinEdges[iPtBin + 1]))
                dKappaBinList[newHistKey] = [iPtBin+1,iEtaBin+1]



varlist_ = ['Ht','Mht','NJets','TrkPt','TrkEta','BTags']
indexVar = {}
for ivar, var in enumerate(varlist_): indexVar[var] = ivar
histoStructDict = {}
for region in regionCuts:
    for var in varlist_:
        histname = region+'_'+var
        histoStructDict[histname] = mkHistoStruct(histname)

def selectionFeatureVector(fvector, regionkey='', omitcuts=''):
    iomits = []
    for cut in omitcuts.split('Vs'): iomits.append(indexVar[cut])
    for i, feature in enumerate(fvector):
        if i in iomits: continue
        if not (feature>=regionCuts[regionkey][i][0] and feature<=regionCuts[regionkey][i][1]):
            return False
    return True


#sfname = 'ScaleFactors/EleDtSfMC.root'
#if doGenVersion: sfname = sfname.replace('.root','Truth.root')
'''
fSF = TFile(sfname)
fSF.ls()
hDtElRatioDict = {}

ptbins = []
print binning['TrkPt']
for ibin, bin in enumerate(binning['TrkPt'][:-1]):
	ptbins.append((binning['TrkPt'][ibin],binning['TrkPt'][ibin+1]))
print 'ptbins', ptbins

etabins = []
print binning['TrkEta']
for ibin, bin in enumerate(binning['TrkEta'][:-1]):
	etabins.append((binning['TrkEta'][ibin],binning['TrkEta'][ibin+1]))
print etabins


for etabin_ in etabins:
	for ptbin in ptbins:
		name = 'hInvMassDtElRatio_eta%dto%d_pt%dto%d' % (10*etabin_[0],10*etabin_[1],ptbin[0],ptbin[1])
		name = name.replace('9999','Inf')
		hDtElRatioDict[(etabin_,ptbin)] = fSF.Get(name)
'''
for histkey in dKappaBinList:
	print histkey, 'Ptbin', dKappaBinList[histkey][0],'EtaBin', dKappaBinList[histkey][1]
#pause()
fname = '/nfs/dust/cms/user/singha/LLCh/BACKGROUNDII/CMSSW_8_0_20/src/MCTemplatesBinned/BinnedTemplatesIIDY_WJ_TT.root'
fname = '/nfs/dust/cms/user/beinsam/LongLiveTheChi/Analyzer/CMSSW_8_0_21/src/DataDrivenSmear.root'
fSmear  = TFile(fname)

dResponseHist = {}
for iPtBin, PtBin in enumerate(PtBinEdges[:-1]):
        for iEtaBin, EtaBin in enumerate(EtaBinEdges[:-1]):
                newHistKey = ((EtaBin,EtaBinEdges[iEtaBin + 1]),(PtBin,PtBinEdges[iPtBin + 1]))
                dResponseHist[newHistKey] = fSmear.Get("htrkresp"+str(newHistKey))



##pause()
#c.Show(0)
nEvents = c.GetEntries()
verbosity = round(100000)

import numpy as np
_dxyVtx_ = array('f',[0])
_dzVtx_ = array('f',[0])
_matchedCaloEnergy_ = array('f',[0])
_trkRelIso_ = array('f',[0])
_nValidPixelHits_ = array('f',[0])
_nValidTrackerHits_ = array('f',[0])
_nMissingOuterHits_ = array('f',[0])
_ptErrOverPt2_ = array('f',[0])
_trkRelIsoSTARpt_ = array('f',[0])
_neutralPtSum_ = array('f',[0])
_chargedPtSum_ = array('f',[0])
_pixelLayersWithMeasurement_ = array('f',[0])
_trackerLayersWithMeasurement_ = array('f',[0])
_pt_ = array('f',[0])
_eta_ = array('f',[0])
_phi_ = array('f',[0])
_nMissingMiddleHits_ = array('f',[0])
_deDxHarmonic2_ = array('f',[0])
_trkMiniRelIso_ = array('f',[0])
_passExo16044JetIso_ = array('f',[0])
_passExo16044LepIso_ = array('f',[0])
_passExo16044Tag_ = array('f',[0])
_trackJetIso_ = array('f',[0])
_trackLeptonIso_ = array('f',[0])
_madHT_ = array('f',[0])
_MET_ = array('f',[0])
_HT_ = array('f',[0])
_nCandPerEevent_ = array('f',[0])


def prepareReader(reader, xmlfilename):
        reader.AddVariable("dxyVtx",_dxyVtx_)
        reader.AddVariable("dzVtx",_dzVtx_)
        reader.AddVariable("matchedCaloEnergy",_matchedCaloEnergy_)
        reader.AddVariable("trkRelIso",_trkRelIso_)
        reader.AddVariable("nValidPixelHits",_nValidPixelHits_)
        reader.AddVariable("nValidTrackerHits",_nValidTrackerHits_)
        reader.AddVariable("nMissingOuterHits",_nMissingOuterHits_)
        reader.AddVariable("ptErrOverPt2",_ptErrOverPt2_)
        reader.AddSpectator("trkRelIso*pt",_trkRelIso_)
        reader.AddSpectator("neutralPtSum",_neutralPtSum_)
        reader.AddSpectator("chargedPtSum",_chargedPtSum_)
        reader.AddSpectator("pixelLayersWithMeasurement",_pixelLayersWithMeasurement_)
        reader.AddSpectator("trackerLayersWithMeasurement",_trackerLayersWithMeasurement_)
        reader.AddSpectator("pt",_pt_)
        reader.AddSpectator("eta",_eta_)
        reader.AddSpectator("phi",_phi_)
        reader.AddSpectator("nMissingMiddleHits",_nMissingMiddleHits_)
        reader.AddSpectator("deDxHarmonic2",_deDxHarmonic2_)
        reader.AddSpectator("trkMiniRelIso",_trkMiniRelIso_)
        reader.AddSpectator("passExo16044JetIso",_passExo16044JetIso_)
        reader.AddSpectator("passExo16044LepIso",_passExo16044LepIso_)
        reader.AddSpectator("passExo16044Tag",_passExo16044Tag_)
        reader.AddSpectator("trackJetIso",_trackJetIso_)
        reader.AddSpectator("trackLeptonIso",_trackLeptonIso_)
        reader.AddSpectator("madHT",_madHT_)
        reader.AddSpectator("MET",_MET_)
        reader.AddSpectator("HT",_HT_)
        reader.AddSpectator("nCandPerEevent",_nCandPerEevent_)
        _deDxHarmonic2_[0] = 0.0
        _chargedPtSum_[0] = 0.0
        _nMissingMiddleHits_[0] = 0.0
        _trkMiniRelIso_[0] = 0.0
        _passExo16044JetIso_[0] = 0.0
        _passExo16044LepIso_[0] = 0.0
        _passExo16044Tag_[0] = 0.0
        _trackJetIso_[0] = 0.0
        _trackLeptonIso_[0] = 0.0
        _madHT_[0] = 0.0
        _MET_[0] = 0.0
        _HT_[0] = 0.0
        _nCandPerEevent_[0] = 0.0
        _pixelLayersWithMeasurement_[0] = 0.0
        _trackerLayersWithMeasurement_[0] = 0.0
        _pt_[0] = 0.0
        _eta_[0] = 0.0
        _phi_[0] = 0.0
        reader.BookMVA("BDT", xmlfilename)

def evaluateBDT(reader, trackfv):
        _dxyVtx_[0] = trackfv[0]
        _dzVtx_[0] = trackfv[1]
        _matchedCaloEnergy_[0] = trackfv[2]
        _trkRelIso_[0] = trackfv[3]
        _nValidPixelHits_[0] = trackfv[4]
        _nValidTrackerHits_[0] = trackfv[5]
        _nMissingOuterHits_[0] = trackfv[6]
        _ptErrOverPt2_[0] = trackfv[7]
        return  reader.EvaluateMVA("BDT")

readerPixelOnly = TMVA.Reader()
pixelXml = '/nfs/dust/cms/user/kutznerv/shorttrack/CMSSW_10_1_7/src/shorttrack/cutoptimization/tmva/newpresel3-200-4-short/wei\
ghts/TMVAClassification_BDT.weights.xml'
prepareReader(readerPixelOnly, pixelXml)
readerPixelStrips = TMVA.Reader()
trackerXml = '/nfs/dust/cms/user/kutznerv/shorttrack/CMSSW_10_1_7/src/shorttrack/cutoptimization/tmva/newpresel2-200-4-medium/\
weights/TMVAClassification_BDT.weights.xml'
prepareReader(readerPixelStrips, trackerXml)


def isBaselineTrack(track, track_id):
	etaMax = 2.4
	flag = 1
#                if not (track.Pt() > 15 and abs(track.Eta())< etaMax): return 0
	if not abs(track.Eta())< etaMax : return 0
	if (abs(track.Eta()) > 1.4442 and abs(track.Eta()) < 1.566): return 0
	if (abs(track.Eta()) > 1.4442 and abs(track.Eta()) < 1.566): print abs(track.Eta()), 'eta in gap'
	if not bool(c.tracks_trackQualityHighPurity[track_id]) : return 0
	if not (c.tracks_ptError[track_id]/(track.Pt()*track.Pt()) < 0.2): return 0
	if not c.tracks_dxyVtx[track_id] < 0.02: return 0
	if not c.tracks_dzVtx[track_id] < 0.05 : return 0
	if not c.tracks_trkRelIso[track_id] < 0.2: return 0
	if not c.tracks_trkRelIso[track_id]*track.Pt() < 10: return 0
	if not (c.tracks_trackerLayersWithMeasurement[track_id] >= 2 and c.tracks_nValidTrackerHits[track_id] >= 2): return 0
	if not c.tracks_nMissingInnerHits[track_id]==0: return 0
	return flag

def isDisappearingTrack_(track, itrack):
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
        #preselection                                                                                                          
        if not c.tracks_passPFCandVeto[itrack]: return 0
	if not (c.tracks_trkRelIso[itrack]<0.2 and c.tracks_dxyVtx[itrack]<0.1 and c.tracks_dzVtx[itrack]<0.1 and c.tracks_ptError[itrack]/c.tracks[itrack].Pt()<10 and c.tracks_nMissingMiddleHits[itrack]==0): return 0
        if not (c.tracks_trackQualityHighPurity[itrack]): return 0
        nhits = c.tracks_nValidTrackerHits[itrack]
        nlayers = c.tracks_trackerLayersWithMeasurement[itrack]
        if not (nlayers>=2 and nhits>=2): return 0
        pterr = c.tracks_ptError[itrack]/(track.Pt()*track.Pt())
        dxyVtx = abs(c.tracks_dxyVtx[itrack])
        dzVtx = abs(c.tracks_dzVtx[itrack])
        matchedCalo = c.tracks_matchedCaloEnergy[itrack]
        trackfv = [dxyVtx, dzVtx, matchedCalo, c.tracks_trkRelIso[itrack], phits, thits, moh_, pterr]
        if pixelOnly:
                mva_ = evaluateBDT(readerPixelOnly, trackfv)
                if not mva_ > 0.117:return 0
                else: return 1
        elif pixelStrips:
                mva_ = evaluateBDT(readerPixelStrips, trackfv)
                if not mva_ > 0.179:return 0
                else: return 1
        else:
                return 0



def getSF(Eta, Pt, Draw = False):
	for histkey in  dResponseHist:
		if abs(Eta) > histkey[0][0] and abs(Eta) < histkey[0][1] and Pt > histkey[1][0] and Pt < histkey[1][1]:
			SF_trk = 10**(dResponseHist[histkey].GetRandom())
			return SF_trk
	return 1

def getKappa_(Eta, Pt, charge = 0):
        for histkey in dKappaBinList:
                if abs(Eta) > histkey[0][0] and abs(Eta) < histkey[0][1] and Pt > histkey[1][0] and Pt < histkey[1][1]:
			if charge == 0:kappa = KappaMap.GetBinContent(dKappaBinList[histkey][0],dKappaBinList[histkey][1])  #10**(dResponseHist[histkey].GetRandom())
			#kappa = KappaMapPt.GetBinContent(dKappaBinList[histkey][0])
			if charge == 1  : kappa = KappaMapPlus.GetBinContent(dKappaBinList[histkey][0],dKappaBinList[histkey][1])
			if charge == -1 : kappa = KappaMapMinus.GetBinContent(dKappaBinList[histkey][0],dKappaBinList[histkey][1])
			#print kappa
                        return kappa
        return 1

import time
t1 = time.time()
i0=0
verbosity = 1000
print c.GetEntries(), 'evets to be Analysed'
for ientry in range(nentries):
	if ientry%verbosity==0:
		a = 1
		print 'now processing event number', ientry
	if verbose:
		if not ientry in [15385]: continue
#	print 'getting entry', ientry
	c.GetEntry(ientry) 
	hHt.Fill(c.HT)
	#hHtWeighted.Fill(c.HT,c.CrossSection)
#	weight = c.CrossSection
	if doGenVersion:
		genels = []
		for igp, gp in enumerate(c.GenParticles):
			if not gp.Pt()>10: continue
			if not abs(gp.Eta())<2.4: continue
			if not abs(c.GenParticles_ParentId[igp]) == 24: continue 
			if not (abs(c.GenParticles_PdgId[igp])==11 and c.GenParticles_Status[igp] == 1) : continue
			genels.append(gp)
#		if doGenVersion:
		if not len(genels)==1: continue

	basicTracks = []
	for itrack, track in enumerate(c.tracks):
		if not track.Pt() > 15 : continue
		if not abs(track.Eta()) < 2.4: continue
		if abs(abs(track.Eta()) < 1.566) and abs(track.Eta()) > 1.4442: continue
		if not isBaselineTrack(track, itrack): continue
		basicTracks.append(track)
	disappearingTracks = []
	mva, dedx, trkpt, trketa, trkp = -999, -999, -999, -999, -999
	nprompt = 0
	moh = -1
	pt = -1

	for itrack, track in enumerate(c.tracks):
		if not track.Pt() > 15 : continue
	#	if verbose: print ientry, itrack,'track with Pt' ,track.Pt()
		if not abs(track.Eta()) < 2.4: continue
		if abs(abs(track.Eta()) < 1.566) and abs(track.Eta()) > 1.4442: continue
		if not isDisappearingTrack_(track, itrack): continue
	#	if verbose: print ientry, itrack,'Passed disp track with Pt' ,track.Pt()
                disappearingTracks.append(track)

	RecoElectrons = []
	SmearedElectrons = []
	for iel, ele in enumerate(c.Electrons):
		if verbose: print ientry, iel,'ele with Pt' , ele.Pt()
		smearedEle = TLorentzVector()
		smearedEle.SetPtEtaPhiE(0, 0, 0, 0)
		if ((abs(ele.Eta()) < 1.566) and abs(ele.Eta()) > 1.4442): continue
		if not abs(ele.Eta())<2.4: continue
		if verbose: print 'passed eta and Pt'
		if not c.Electrons_passIso[iel]: continue
		drBig4Trk = 9999
		matchedTrk = TLorentzVector()
		for trk in basicTracks:
			drTrk = trk.DeltaR(c.Electrons[iel])
			if drTrk<drBig4Trk:
				drBig4Trk = drTrk
				matchedTrk = trk
				if drTrk<0.01: break
		if verbose: print 'passed baseline track'
		RecoElectrons.append(ele)
		sf = getSF(abs(matchedTrk.Eta()), min(matchedTrk.Pt(),299.999))
		smearedEle.SetPtEtaPhiE(sf*matchedTrk.Pt(),matchedTrk.Eta(),matchedTrk.Phi(),sf*matchedTrk.E())
		if not (smearedEle.Pt()>15): continue
		SmearedElectrons.append([smearedEle,c.Electrons_charge[iel]])
	muons = []		
	for imu, muon in enumerate(c.Muons):
		if not muon.Pt()>15: continue
		if abs(abs(muon.Eta()) < 1.566) and abs(muon.Eta()) > 1.4442: continue
		if not abs(muon.Eta())<2.4: continue	
		muons.append([muon,c.Muons_charge[imu]])

	if not len(muons)==0: continue	

	singleEleEvent_ = bool(len(SmearedElectrons)==1)
#	print len(SmearedElectrons), "SmearedElectrons"
	#print ientry, 'SmearedElectrons', SmearedElectrons, 'disappearingTracks', disappearingTracks
	singleDisTrkEvent = bool(len(disappearingTracks)==1)
#	print len(disappearingTracks), "disappearing tracks"
	#pause()
	if not (singleEleEvent_ or singleDisTrkEvent): continue
	#print 'D'
#	if (len(SmearedElectrons)>0 and len(disappearingTracks)>0): continue	
	#print 'passed event cuts'
	
	metvec = TLorentzVector()
	metvec.SetPtEtaPhiE(c.MET, 0, c.METPhi, c.MET)

	if singleEleEvent_:
		if doGenVersion: yo =1
			#if not SmearedElectrons[0][0].DeltaR(genels[0])<0.02: continue
		#adjustedMet = metvec.Pt()-RecoElectrons[0]
		adjustedMht = TLorentzVector()
		adjustedMht.SetPxPyPzE(0,0,0,0)
		adjustedNJets = 0
		for jet in c.Jets:
			if not jet.Pt()>30: continue
			if not abs(jet.Eta())<5.0: continue
			if not jet.DeltaR(RecoElectrons[0])>0.5: continue
			adjustedMht-=jet
			adjustedNJets+=1
		#if not adjustedNJets>0: continue
		if doGenVersion:
                        if RelaxGenKin:
				pt = SmearedElectrons[0][0].Pt()
				eta = abs(SmearedElectrons[0][0].Eta())
                        else:
				pt = genels[0].Pt()
                                eta = abs(genels[0].Eta())
		else:
			pt = SmearedElectrons[0][0].Pt()
			eta = abs(SmearedElectrons[0][0].Eta())		
	#	ptbin = findbin(ptbins,pt)
	#	etabin = findbin(etabins,abs(eta))
	#	if abs(eta) > 1.4442 and abs(eta) < 1.566 : print abs(eta), 'eta of electron'
		fv = [c.HT,adjustedMht.Pt(),adjustedNJets,pt,abs(SmearedElectrons[0][0].Eta()),c.BTags]		
		k = getKappa_(abs(eta),min(pt,309.99),SmearedElectrons[0][1])
		#print 'Kappa is', k
#		fillth1(hPtControl,fv[3],1*weight)
#		fillth1(hPtMethod,fv[3],k*weight)
		for regionkey in regionCuts:
			for ivar, varname in enumerate(varlist_):
				hname = regionkey+'_'+varname
				if selectionFeatureVector(fv,regionkey,varname):
					#print 'In filling place', fv[ivar]
					
					#pause()
					#if 'NoCuts' in regionkey and 'TrkPt' in varname:
					#	if (fv[3] < 20) : print ientry, 'found electron, pT=', fv[3], 'kappa is ', k#, SmearedElectrons, disappearingTracks
					fillth1(histoStructDict[hname].Control,fv[ivar], weight)	
					fillth1(histoStructDict[hname].Method,fv[ivar], k*weight)						
#	pause()
	if singleDisTrkEvent:
		adjustedNJets = 0
		if not disappearingTracks[0].DeltaR(genels[0])<0.02: continue
		#if doGenVersion:
		#	if not disappearingTracks[0].DeltaR(genels[0])<0.02: continue
		adjustedNJets = 0
		adjustedMht = TLorentzVector()
		adjustedMht.SetPxPyPzE(0,0,0,0)		
		for jet in c.Jets:
			if not jet.Pt()>30: continue
			if not abs(jet.Eta())<5.0: continue
			if not jet.DeltaR(disappearingTracks[0])>0.5: continue	
			adjustedMht-=jet			
			adjustedNJets+=1	
	#	if not adjustedNJets>0: continue				
		if doGenVersion:
			if RelaxGenKin: 
				pt = disappearingTracks[0].Pt()
				eta = abs(disappearingTracks[0].Eta())
			else: 
				pt = genels[0].Pt()
				eta = abs(genels[0].Eta())
		else: 
			pt = disappearingTracks[0].Pt()
			eta = abs(disappearingTracks[0].Eta())			
		fv = [c.HT,adjustedMht.Pt(),adjustedNJets,pt,abs(disappearingTracks[0].Eta()),c.BTags]					
#		fillth1(hPtTruth,fv[3], weight)
		for regionkey in regionCuts:
			for ivar, varname in enumerate(varlist_):
				hname = regionkey+'_'+varname
				if selectionFeatureVector(fv,regionkey,varname):
#					if 'NoCuts' in regionkey and 'TrkPt' in varname:
#						print ientry,'found disappearing track, pT=', fv[3]
					fillth1(histoStructDict[hname].Truth,fv[ivar], weight)
	
fnew_.cd()
hHt.Write()
hHtWeighted.Write()
writeHistoStruct(histoStructDict)
print 'just created', fnew_.GetName()
fnew_.Close()

#TestFile = TFile('BkgEstTestwithPtKappa.root','recreate')
#TestFile.cd()
#hPtTruth.Write()
#hPtMethod.Write()
#hPtControl.Write()
#print 'just created', TestFile.GetName()
#TestFile.Close()
