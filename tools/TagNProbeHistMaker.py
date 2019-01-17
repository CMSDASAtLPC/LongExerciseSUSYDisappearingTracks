#ls /eos/uscms//store/user/lpcsusyhad/sbein/cmsdas19/Ntuples/ > usefulthings/filelist.txt
from ROOT import *
import sys
import numpy as np
from glob import glob
from utils import *
from distracklibs import *
gROOT.SetBatch()
gROOT.SetStyle('Plain')

GenOnly = False
RelaxGenKin = True
verbose = False
SmearLeps = False


defaultInfile = "/eos/uscms//store/user/lpcsusyhad/sbein/cmsdas19/Ntuples/Summer16.DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_104_RA2AnalysisTree.root"
defaultkey = defaultInfile.split('/')[-1].split('.root')[0]
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbosity", type=bool, default=False,help="analyzer script to batch")
parser.add_argument("-analyzer", "--analyzer", type=str,default='tools/ResponseMaker.py',help="analyzer")
parser.add_argument("-fin", "--fnamekeyword", type=str,default=defaultkey,help="file")
parser.add_argument("-dtmode", "--dtmode", type=str, default='PixAndStrips',help="PixAndStrips, PixOnly, PixOrStrips")
parser.add_argument("-pu", "--pileup", type=str, default='Nom',help="Nom, Low, Med, High")
args = parser.parse_args()
fnamekeyword = args.fnamekeyword
inputFiles = glob(fnamekeyword)
dtmode = args.dtmode


print 'going to analyze events in file matching with', fnamekeyword
if 'Run20' in fnamekeyword: isdata = True
else: isdata = False
if 'Run2016' in fnamekeyword or 'Summer16' in fnamekeyword:
    phase_ = 0
else:
	phase_ = 1

print 'dtmode', dtmode
if dtmode == 'PixOnly': 
	PixMode = True
	PixStripsMode = False
	CombineMode = False
elif dtmode == 'PixAndStrips': 
	PixMode = False
	PixStripsMode = True
	CombineMode = False	
elif dtmode == 'PixOrStrips':
	PixMode = False
	PixStripsMode = False
	CombineMode = True	

identifier = fnamekeyword
newfname = 'TagnProbeHists_'+identifier+'.root'
if PixMode: newfname = newfname.replace('.root','_PixOnly.root')
if PixStripsMode: newfname = newfname.replace('.root','_PixAndStrips.root')
if CombineMode: newfname = newfname.replace('.root','_PixOrStrips.root')
newfname = newfname.replace('RA2AnalysisTree_','').replace('_PixOnly.root_PixOnly.root','_PixOnly.root').replace('_PixAndStrips.root_PixAndStrips.root','_PixAndStrips.root')
fnew = TFile(newfname,'recreate')


lepPtCut = 30


c = TChain("TreeMaker2/PreSelection")

# Load in chain #
fnamefile = open('usefulthings/filelist.txt')
lines = fnamefile.readlines()
fnamefile.close()

c = TChain('TreeMaker2/PreSelection')
for line in lines:
    shortfname = fnamekeyword
    if not shortfname in line: continue
    fname = '/eos/uscms/store/user/lpcsusyhad/sbein/cmsdas19/Ntuples/'+line
    fname = fname.strip().replace('/eos/uscms/','root://cmseos.fnal.gov//')
    print 'adding', fname
    c.Add(fname)
    break



#if isdata: fsmearname = 'usefulthings/DataDrivenSmear_2016Data.root'
#else: fsmearname = 'usefulthings/DataDrivenSmear_2016MC.root'
if isdata: fsmearname = 'usefulthings/DataDrivenSmear_Run2016_'+dtmode+'.root'
else: fsmearname = 'usefulthings/DataDrivenSmear_DYJets_'+dtmode+'.root'

fSmear  = TFile(fsmearname)


hEtaVsPhiDT = TH2F('hEtaVsPhiDT','hEtaVsPhiDT',160,-3.2,3.2,250,-2.5,2.5)
fMask = TFile('usefulthings/Masks.root')
fMask.ls()
if 'Run2016' in fnamekeyword: hMask = fMask.Get('hEtaVsPhiDT_maskRun2016')
else: hMask = fMask.Get('hEtaVsPhiDT_maskRun2016')


#=====This sets up the smearing
dResponseHist_el = {}
dResponseHist_mu = {}
for iPtBinEdge, PtBinEdge in enumerate(PtBinEdgesForSmearing[:-1]):
    for iEtaBinEdge, EtaBinEdge_ in enumerate(EtaBinEdgesForSmearing[:-1]):
       newHistKey = ((EtaBinEdge_,EtaBinEdgesForSmearing[iEtaBinEdge + 1]),(PtBinEdge,PtBinEdgesForSmearing[iPtBinEdge + 1]))
       print 'attempting to get', "htrkresp"+str(newHistKey)
       if '(1.4442,' in str(newHistKey): continue
       dResponseHist_el[newHistKey] = fSmear.Get("htrkresp"+str(newHistKey)+'El')
       dResponseHist_mu[newHistKey] = fSmear.Get("htrkresp"+str(newHistKey)+'Mu')       
       
print 'smearing factors', dResponseHist_el, dResponseHist_mu
def getSmearFactor(Eta, Pt, dResponseHist):
    for histkey in  dResponseHist:
       if abs(Eta) > histkey[0][0] and abs(Eta) < histkey[0][1] and Pt > histkey[1][0] and Pt < histkey[1][1]:
           SF_trk = 10**(dResponseHist[histkey].GetRandom())
           return SF_trk #/SF_ele
    print 'returning 1'
    return 1

hHt       = makeTh1("hHt","HT for number of events", 250,0,5000)
hHtWeighted       = makeTh1("hHtWeighted","HT for number of events", 250,0,5000)
hElTagPt        = makeTh1VB("hElTagPt"  , "pt of the ElTags", len(PtBinEdges)-1,PtBinEdges)
hElTagEta       = makeTh1VB("hElTagEta"  , "Eta of the ElTags", len(EtaBinEdges)-1,EtaBinEdges)

hMuTagPt        = makeTh1VB("hMuTagPt"  , "pt of the MuTags", len(PtBinEdges)-1,PtBinEdges)
hMuTagEta       = makeTh1VB("hMuTagEta"  , "Eta of the MuTags", len(EtaBinEdges)-1,EtaBinEdges)
hGenPtvsResp    = makeTh2_("hGenPtvsResp","hGenPtvsResp",50, 10, 400, 20, -2 ,3)    

hNTrackerLayersDT_el = TH1F('hNTrackerLayersDT_el','hNTrackerLayersDT_el',11,0,11)
hNTrackerLayersDT_mu = TH1F('hNTrackerLayersDT_mu','hNTrackerLayersDT_mu',11,0,11)

#=====This sets up histograms for the pT response of the tracks
dProbeElTrkResponseDT_ = {}
dProbeElTrkResponseRECO_= {}
dProbeMuTrkResponseDT_ = {}
dProbeMuTrkResponseRECO_= {}
for iPtBin, PtBin in enumerate(PtBinEdges[:-1]):
    for iEtaBin, EtaBin in enumerate(EtaBinEdges[:-1]):
       newHistKey = ((EtaBin,EtaBinEdges[iEtaBin + 1]),(PtBin,PtBinEdges[iPtBin + 1]))    
       specialpart = '_eta'+str(newHistKey).replace('), (', '_pt').replace('(','').replace(')','').replace(', ','to')
       dProbeElTrkResponseDT_[newHistKey] = makeTh1("hProbeElTrkrespDT"+specialpart,"hProbeElTrkrespDT"+specialpart, 100,-2,2)    
       histoStyler(dProbeElTrkResponseDT_[newHistKey], 1)
       dProbeElTrkResponseRECO_[newHistKey] = makeTh1("hProbeElTrkrespRECO"+specialpart,"hProbeElTrkrespRECO"+specialpart, 100,-2,2)    
       histoStyler(dProbeElTrkResponseRECO_[newHistKey], 1)       
       
       dProbeMuTrkResponseDT_[newHistKey] = makeTh1("hProbeMuTrkrespDT"+specialpart,"hProbeMuTrkrespDT"+specialpart, 100,-2,2)    
       histoStyler(dProbeMuTrkResponseDT_[newHistKey], 1)
       dProbeMuTrkResponseRECO_[newHistKey] = makeTh1("hProbeMuTrkrespRECO"+specialpart,"hProbeMuTrkrespRECO"+specialpart, 100,-2,2)    
       histoStyler(dProbeMuTrkResponseRECO_[newHistKey], 1)             

#=====This sets up histograms for the invariant mass and kappas    
dInvMassElRECOHist = {}
dInvMassElDTHist = {}
hElProbePt_DTnums = {}
hElProbePt_RECOdens = {}
hGenElProbePt_DTnums = {}
hGenElProbePt_RECOdens = {}

dInvMassMuRECOHist = {}
dInvMassMuDTHist = {}
hMuProbePt_DTnums = {}
hMuProbePt_RECOdens = {}
hGenMuProbePt_DTnums = {}
hGenMuProbePt_RECOdens = {}

for iEtaBin, EtaBin in enumerate(EtaBinEdges[:-1]):
    etakey = (EtaBin,EtaBinEdges[iEtaBin + 1])
    specialpart = '_eta'+str(etakey).replace('(','').replace(')','').replace(', ','to')
    hElProbePt_DTnums[etakey] = makeTh1VB("hElProbePtDT"+specialpart+"_num", "pt of the ElProbes", len(PtBinEdges)-1,PtBinEdges)
    hElProbePt_RECOdens[etakey]    = makeTh1VB("hElProbePtRECO"+specialpart+"_den", "pt of the ElProbes", len(PtBinEdges)-1,PtBinEdges)
    hGenElProbePt_DTnums[etakey] = makeTh1VB("hGenElProbePtDT"+specialpart+"_num", "pt of the ElProbes", len(PtBinEdges)-1,PtBinEdges)
    hGenElProbePt_RECOdens[etakey]    = makeTh1VB("hGenElProbePtRECO"+specialpart+"_den", "pt of the ElProbes", len(PtBinEdges)-1,PtBinEdges)
    hMuProbePt_DTnums[etakey] = makeTh1VB("hMuProbePtDT"+specialpart+"_num", "pt of the MuProbes", len(PtBinEdges)-1,PtBinEdges)
    hMuProbePt_RECOdens[etakey]    = makeTh1VB("hMuProbePtRECO"+specialpart+"_den", "pt of the MuProbes", len(PtBinEdges)-1,PtBinEdges)
    hGenMuProbePt_DTnums[etakey] = makeTh1VB("hGenMuProbePtDT"+specialpart+"_num", "pt of the MuProbes", len(PtBinEdges)-1,PtBinEdges)
    hGenMuProbePt_RECOdens[etakey]    = makeTh1VB("hGenMuProbePtRECO"+specialpart+"_den", "pt of the MuProbes", len(PtBinEdges)-1,PtBinEdges)    
       
    for iPtBin, PtBin in enumerate(PtBinEdges[:-1]):
       newHistKey = ((EtaBin,EtaBinEdges[iEtaBin + 1]),(PtBin,PtBinEdges[iPtBin + 1]))
       specialpart = '_eta'+str(newHistKey).replace('), (', '_pt').replace('(','').replace(')','').replace(', ','to')
       dInvMassElRECOHist[newHistKey] = makeTh1("hInvMassEl"+specialpart+"_RECOden"  , "hInvMassEl"+specialpart+"_RECOden", 40, 60, 120)
       histoStyler(dInvMassElRECOHist[newHistKey], 1)
       newHistKey = ((EtaBin,EtaBinEdges[iEtaBin + 1]),(PtBin,PtBinEdges[iPtBin + 1]))
       dInvMassElDTHist[newHistKey] = makeTh1("hInvMassEl"+specialpart+"_DTnum"  , "hInvMassEl"+specialpart+"_DTnum", 40, 60, 120)
       histoStyler(dInvMassElDTHist[newHistKey], 1)
       dInvMassMuRECOHist[newHistKey] = makeTh1("hInvMassMu"+specialpart+"_RECOden"  , "hInvMassMu"+specialpart+"_RECOden", 40, 60, 120)
       histoStyler(dInvMassMuRECOHist[newHistKey], 1)
       newHistKey = ((EtaBin,EtaBinEdges[iEtaBin + 1]),(PtBin,PtBinEdges[iPtBin + 1]))
       dInvMassMuDTHist[newHistKey] = makeTh1("hInvMassMu"+specialpart+"_DTnum"  , "hInvMassMu"+specialpart+"_DTnum", 40, 60, 120)
       histoStyler(dInvMassMuDTHist[newHistKey], 1)       

##adapt script for BDT disappearing track

readerShort = TMVA.Reader()
#pixelXml = '/nfs/dust/cms/user/kutznerv/cmsdas/BDTs/newpresel3-200-4-short-nodxyVtx/weights/TMVAClassification_BDT.weights.xml'
###pixelXml = '/nfs/dust/cms/user/kutznerv/shorttrack/fake-tracks/newpresel3-200-4-short/weights/TMVAClassification_BDT.weights.xml'
pixelXml = 'usefulthings/cmssw8-newpresel3-200-4-short-updated/weights/TMVAClassification_BDT.weights.xml'
prepareReaderShort(readerShort, pixelXml)
readerLong = TMVA.Reader()
trackerXml = 'usefulthings/cmssw8-newpresel2-200-4-medium-updated/weights/TMVAClassification_BDT.weights.xml'
prepareReaderLong(readerLong, trackerXml)

def isGenMatched(lep, pdgid):
    for igenm, genm in enumerate(c.GenParticles):
       if not genm.Pt() > 5: continue
       #if not abs(c.GenParticles_ParentId[igenm]) == 23: continue
       if not (abs(c.GenParticles_PdgId[igenm]) == pdgid and c.GenParticles_Status[igenm] == 1):continue
       drm = genm.DeltaR(lep)
       if drm < .01: return genm.Pt()
    return 0



nentries = c.GetEntries()
c.Show(0)
print nentries, ' events to be analyzed'
verbosity = 10000


triggerIndecesV2 = {}
#triggerIndecesV2['SingleEl'] = [36,39]
triggerIndecesV2['SingleElCocktail'] = [14, 15, 16, 17, 18, 19, 20, 21]
#triggerIndecesV2['MhtMet6pack'] = [108,110,114,123,124,125,126,128,129,130,131,132,133,122,134]#123
#triggerIndecesV2["SingleMu"] = [48,50,52,55,63]
triggerIndecesV2["SingleMuCocktail"] = [24,25,26,27,28,30,31,32]

triggerIndeces = triggerIndecesV2

def PassTrig(c,trigname):
	for trigidx in triggerIndeces[trigname]: 
		if c.TriggerPass[trigidx]==1: 
			return True
	return False
	
	
for ientry in range(nentries):
    if verbose:
       if not ientry in [8841]: continue
    if ientry%verbosity==0: print 'now processing event number', ientry, 'of', nentries
    c.GetEntry(ientry)
    if isdata: weight = 1
    else: weight = c.CrossSection
    fillth1(hHt, c.HT, 1)
    fillth1(hHtWeighted, c.HT, weight)
    TagPt  =  0
    TagEta  =  0
    ProbePt  =  0
    ProbeEta = 0
    probeTlv = TLorentzVector()
    probeTlv.SetPxPyPzE(0, 0, 0, 0)
    if not c.BTags==0: continue
    if ientry==0:
        for itrig in range(len(c.TriggerPass)):
            print itrig, c.TriggerNames[itrig], c.TriggerPrescales[itrig], c.HT
        print '='*20
    genels = []
    genmus = []  
    if not isdata:     
        for igp, gp in enumerate(c.GenParticles):
            if not gp.Pt()>5: continue       
            if not (abs(c.GenParticles_PdgId[igp])==11 or abs(c.GenParticles_PdgId[igp])==13) : continue
            if not c.GenParticles_Status[igp]==1 : continue          
            if not abs(gp.Eta())<2.4: continue
            if not (abs(gp.Eta())<1.445 or abs(gp.Eta())>1.56): continue                    
            if abs(c.GenParticles_PdgId[igp])==11: genels.append([gp,igp])
            if abs(c.GenParticles_PdgId[igp])==13: genmus.append([gp,igp])          

	if isdata:
		if not (PassTrig(c, 'SingleElCocktail') or PassTrig(c, 'SingleMuCocktail')): continue
		
    basicTracks = []
    disappearingTracks = []       
    for itrack, track in enumerate(c.tracks):
       if not track.Pt() > 10 : continue
       if not abs(track.Eta()) < 2.4: continue
       if not (abs(track.Eta()) > 1.566 or abs(track.Eta()) < 1.4442): continue
       if not isBaselineTrack(track, itrack, c, hMask): continue
       basicTracks.append([track,c.tracks_charge[itrack], itrack])
       if not (track.Pt()>lepPtCut and track.Pt()<9999): continue
       dtstatus = isDisappearingTrack_(track, itrack, c, readerShort, readerLong)
       if dtstatus==0: continue
       if PixMode:
           if not dtstatus==1: continue
       if PixStripsMode:
           if not dtstatus==2: continue          
       drlep = 99
       passeslep = True
       for ilep, lep in enumerate(list(c.Electrons)+list(c.Muons)): 
          drlep = min(drlep, lep.DeltaR(track))
          if drlep<0.01: 
             passeslep = False
             break
       if not passeslep: continue
       fillth2(hEtaVsPhiDT, track.Phi(), track.Eta())
       print 'found disappearing track w pT =', track.Pt()       
       disappearingTracks.append([track,itrack])
          
            
    SmearedElectrons = []
    TightElectrons = []       
    for ilep, lep in enumerate(c.Electrons):
       if not lep.Pt()>10: continue               
       if (abs(lep.Eta()) < 1.566 and abs(lep.Eta()) > 1.4442): continue
       if not abs(lep.Eta())<2.4: continue     
       if not c.Electrons_passIso[ilep]: continue          
       if (lep.Pt() > 10 and c.Electrons_passIso[ilep] and bool(c.Electrons_mediumID[ilep])):
          TightElectrons.append([lep,c.Electrons_charge[ilep]])
       matchedTrack = TLorentzVector()           
       drmin = 9999
       for trk in basicTracks:
             if not c.tracks_nMissingOuterHits[trk[2]]==0: continue
             drTrk = trk[0].DeltaR(lep)
             if drTrk<drmin:
                drmin = drTrk
                matchedTrack = trk[0]
                if drTrk<0.01: break
       if not drmin<0.01: continue
       smear = getSmearFactor(abs(matchedTrack.Eta()), min(matchedTrack.Pt(),299.999), dResponseHist_el)
       smearedEl = TLorentzVector()          
       smearedEl.SetPtEtaPhiE(smear*matchedTrack.Pt(),matchedTrack.Eta(),matchedTrack.Phi(),smear*matchedTrack.E())
       if not (smearedEl.Pt()>lepPtCut and smearedEl.Pt()<9999): continue
       SmearedElectrons.append([smearedEl, c.Electrons_charge[ilep], matchedTrack])
       
            
    SmearedMuons = []
    TightMuons = []       
    for ilep, lep in enumerate(c.Muons):
       if not lep.Pt()>10: continue               
       if (abs(lep.Eta()) < 1.566 and abs(lep.Eta()) > 1.4442): continue
       if not abs(lep.Eta())<2.4: continue     
       if not c.Muons_passIso[ilep]: continue          
       if (lep.Pt() > 30 and c.Muons_passIso[ilep]):
          TightMuons.append([lep,c.Muons_charge[ilep]])
       matchedTrack = TLorentzVector()           
       drmin = 9999
       for trk in basicTracks:
             if not c.tracks_nMissingOuterHits[trk[2]]==0: continue
             drTrk = trk[0].DeltaR(lep)
             if drTrk<drmin:
                drmin = drTrk
                matchedTrack = trk[0]
                if drTrk<0.01: break
       if not drmin<0.01: continue
       smear = getSmearFactor(abs(matchedTrack.Eta()), min(matchedTrack.Pt(),299.999), dResponseHist_mu)
       smearedMu = TLorentzVector()          
       smearedMu.SetPtEtaPhiE(smear*matchedTrack.Pt(),matchedTrack.Eta(),matchedTrack.Phi(),smear*matchedTrack.E())
       if not (smearedMu.Pt()>lepPtCut and smearedMu.Pt()<9999): continue
       SmearedMuons.append([smearedMu, c.Muons_charge[ilep], matchedTrack])
                    
    adjustedHt = 0
    adjustedMht = TLorentzVector()
    adjustedMht.SetPxPyPzE(0,0,0,0)
    adjustedNJets = 0
    for jet in c.Jets:
       if not jet.Pt()>30: continue
       if not abs(jet.Eta())<5: continue
       if len(SmearedElectrons)>0:
          if not jet.DeltaR(SmearedElectrons[0][0])>0.5: continue
       if len(SmearedMuons)>0:
          if not jet.DeltaR(SmearedMuons[0][0])>0.5: continue
       if len(disappearingTracks)>0:
          if not jet.DeltaR(disappearingTracks[0][0])>0.5: continue
       adjustedMht-=jet
       if not abs(jet.Eta())<2.4: continue####update to 2.4       
       adjustedHt+=jet.Pt()
       adjustedNJets+=1
    if not adjustedNJets<3: continue
          
    for igen, genlep in enumerate(genels):
        for idistrk, distrk in enumerate(disappearingTracks):
            dr = genlep[0].DeltaR(distrk[0])
            if not dr < 0.02: continue
            if RelaxGenKin: pt, eta = distrk[0].Pt(),abs(distrk[0].Eta())
            else: pt, eta = genlep[0].Pt(), abs(genlep[0].Eta())
            fillth2(hGenPtvsResp, TMath.Log10(distrk[0].Pt()/genlep[0].Pt()),genlep[0].Pt(),weight)             
            for histkey in  hGenElProbePt_DTnums:
                if abs(eta) > histkey[0] and abs(eta) < histkey[1]:
                    fillth1(hGenElProbePt_DTnums[histkey], pt, weight)
            print ientry, 'found a nice dt', distrk[0].Pt()
            break       
            
        idlep   = -1
        drminSmearedlepGenlep = 9999
        gotthematch = False      
        for ie, lep in enumerate(SmearedElectrons):
            dr = genlep[0].DeltaR(lep[0])
            if not dr < 0.02: continue #here we have a probe dt
            if SmearLeps: pt = lep[0].Pt()
            else: pt = lep[2].Pt() 
            for histkey in  hGenElProbePt_RECOdens:
                if abs(lep[0].Eta()) > histkey[0] and abs(lep[0].Eta()) < histkey[1]:
                    #fillth1(hGenElProbePt_RECOdens[histkey], lep[0].Pt(), weight)
                    fillth1(hGenElProbePt_RECOdens[histkey], pt, weight)
                    gotthematch = True
                    break
            if gotthematch: break
             
    for igen, genlep in enumerate(genmus):
        for idistrk, distrk in enumerate(disappearingTracks):
            dr = genlep[0].DeltaR(distrk[0])
            if not dr < 0.02: continue
            if RelaxGenKin: pt, eta = distrk[0].Pt(),abs(distrk[0].Eta())
            else: pt, eta = genlep[0].Pt(), abs(genlep[0].Eta())
            fillth2(hGenPtvsResp, TMath.Log10(distrk[0].Pt()/genlep[0].Pt()),genlep[0].Pt(),weight)             
            for histkey in  hGenMuProbePt_DTnums:
                if abs(eta) > histkey[0] and abs(eta) < histkey[1]:
                    fillth1(hGenMuProbePt_DTnums[histkey], pt, weight)
            print ientry, 'found a nice dt', distrk[0].Pt()
            break       
        idlep   = -1
        drminSmearedlepGenlep = 9999
        gotthematch = False      
        for ie, lep in enumerate(SmearedMuons):
            dr = genlep[0].DeltaR(lep[0])
            if not dr < 0.02: continue #here we have a probe dt
            if SmearLeps: pt = lep[0].Pt()
            else: pt = lep[2].Pt() 
            for histkey in  hGenMuProbePt_RECOdens:
                if abs(lep[0].Eta()) > histkey[0] and abs(lep[0].Eta()) < histkey[1]:
                    #fillth1(hGenMuProbePt_RECOdens[histkey], lep[0].Pt(), weight)
                    fillth1(hGenMuProbePt_RECOdens[histkey], pt, weight)
                    gotthematch = True
                    break
            if gotthematch: break            
  
	if GenOnly: continue
	tagTlv = TLorentzVector()
	tagTlv.SetPxPyPzE(0,0,0,0)
       
    for charge in range(-1,2,2):
    	#electrons
        for itag, tag in enumerate(TightElectrons):    
            if not tag[1]==charge: continue
            IM  =  0 
            TagPt, TagEta = tag[0].Pt(), tag[0].Eta()
            probeIsReco, probeIsDt = False, False
            dmMin = 999
            dtindex  =-1
            for idt, dt in enumerate(disappearingTracks):
                if not (tag[1] + c.tracks_charge[dt[1]] == 0): continue
                if dt[0].DeltaR(tag[0])<0.01: continue       
                IMleplep = (tag[0] + dt[0]).M()
                if (IMleplep < 0): 
                    print 'something horribly wrong, space-like event'
                    continue
                dIM = abs(IMleplep - 91)
                if(dIM < dmMin):
                    dmMin = dIM
                    IM = IMleplep
                    probeTlv =  dt[0]
                    dtindex = dt[1]
                    probeIsDt = True                    
                    probeIsReco = False          
            for iSmearedEl, smearedEl in enumerate(SmearedElectrons):
                if not (tag[1] + smearedEl[1] == 0): continue
                if smearedEl[0].DeltaR(tag[0])<0.01: continue                
                IMleplep = (tag[0] + smearedEl[0]).M()
                dIM = abs(IMleplep - 91)
                if(dIM < dmMin):
                    dmMin = dIM
                    IM    = IMleplep
                    if SmearLeps: probeTlv  = smearedEl[0]
                    else: probeTlv = smearedEl[2]
                    probeIsReco = True
                    probeIsDt = False                    

            if (IM > 60 and IM < 120):
                fillth1(hElTagPt, TagPt, weight)
                fillth1(hElTagEta, TagEta, weight)
                if probeIsDt:
                    ProbePt = probeTlv.Pt()
                    fillth1(hNTrackerLayersDT_el, c.tracks_trackerLayersWithMeasurement[dtindex], weight)
                    print 'just filled the el thing with layers ',c.tracks_trackerLayersWithMeasurement[dtindex]
                    ProbeEta = abs(probeTlv.Eta())
                    if not isdata: isgenmatched  = isGenMatched(probeTlv, 11)
                    else: isgenmatched = 1
                    #if isgenmatched == 0: continue #uncomment to skip isGenMatcheding of Probes

                    for histkey in  dInvMassElDTHist:
                        if abs(ProbeEta) > histkey[0][0] and abs(ProbeEta) < histkey[0][1] and ProbePt > histkey[1][0] and ProbePt < histkey[1][1]:
                            fillth1(dInvMassElDTHist[histkey],IM,weight)                    
                    for histkey in  hElProbePt_DTnums:
                        if abs(ProbeEta) > histkey[0] and abs(ProbeEta) < histkey[1]:
                            fillth1(hElProbePt_DTnums[histkey], ProbePt, weight)                    
                    for histkey in  dProbeElTrkResponseDT_:
                        if abs(ProbeEta) > histkey[0][0] and abs(ProbeEta) < histkey[0][1] and isgenmatched > histkey[1][0] and isgenmatched < histkey[1][1]:
                            fillth1(dProbeElTrkResponseDT_[histkey],TMath.Log10(ProbePt/isgenmatched),weight)

                if probeIsReco:
                    if not isdata: isgenmatched  = isGenMatched(probeTlv, 11)
                    else: isgenmatched = 1                    
                    #if isgenmatched == 0: continue #uncomment to skip isGenMatcheding of Probes
                    ProbePt   = probeTlv.Pt()
                    ProbeEta = abs(probeTlv.Eta())
                    for histkey in  dInvMassElRECOHist:
                        if abs(ProbeEta) > histkey[0][0] and abs(ProbeEta) < histkey[0][1] and ProbePt > histkey[1][0] and ProbePt < histkey[1][1]:
                            fillth1(dInvMassElRECOHist[histkey],IM, weight)       
                    for histkey in  hElProbePt_RECOdens:
                        if abs(ProbeEta) > histkey[0] and abs(ProbeEta) < histkey[1]:
                            fillth1(hElProbePt_RECOdens[histkey], ProbePt, weight)   
                    for histkey in  dProbeElTrkResponseRECO_:
                        if abs(ProbeEta) > histkey[0][0] and abs(ProbeEta) < histkey[0][1] and isgenmatched > histkey[1][0] and isgenmatched < histkey[1][1]:
                            fillth1(dProbeElTrkResponseRECO_[histkey],TMath.Log10(ProbePt/isgenmatched),weight) 

    	#muons
        for itag, tag in enumerate(TightMuons):    
            if not tag[1]==charge: continue
            IM  =  0 
            TagPt, TagEta = tag[0].Pt(), tag[0].Eta()
            probeIsReco, probeIsDt = False, False
            dmMin = 999
            dtindex = -1
            for idt, dt in enumerate(disappearingTracks):
                if not (tag[1] + c.tracks_charge[dt[1]] == 0): continue
                if dt[0].DeltaR(tag[0])<0.01: continue       
                IMleplep = (tag[0] + dt[0]).M()
                if (IMleplep < 0): 
                    print 'something horribly wrong, space-like event'
                    continue
                dIM = abs(IMleplep - 91)
                if(dIM < dmMin):
                    dmMin = dIM
                    IM = IMleplep
                    probeTlv =  dt[0]
                    dtindex = dt[1]
                    probeIsDt = True
                    #fill layers hist here
                    probeIsReco = False          
            for iSmearedMu, smearedMu in enumerate(SmearedMuons):
                if not (tag[1] + smearedMu[1] == 0): continue
                if smearedMu[0].DeltaR(tag[0])<0.01: continue                
                IMleplep = (tag[0] + smearedMu[0]).M()
                dIM = abs(IMleplep - 91)
                if(dIM < dmMin):
                    dmMin = dIM
                    IM    = IMleplep
                    if SmearLeps: probeTlv = smearedMu[0]
                    else: probeTlv = smearedMu[2]
                    probeIsReco = True
                    probeIsDt = False                    

            if (IM > 60 and IM < 120):
                fillth1(hMuTagPt, TagPt, weight)
                fillth1(hMuTagEta, TagEta, weight)
                if probeIsDt:
                    ProbePt = probeTlv.Pt()
                    fillth1(hNTrackerLayersDT_mu, c.tracks_trackerLayersWithMeasurement[dtindex], weight)
                    print 'just filled the mu thing with layers ',c.tracks_trackerLayersWithMeasurement[dtindex]
                    ProbeEta = abs(probeTlv.Eta())
                    if not isdata: isgenmatched  = isGenMatched(probeTlv, 13)
                    else: isgenmatched = 1
                    #if isgenmatched == 0: continue #uncomment to skip isGenMatcheding of Probes
                    print 'here at the muon threshold', ProbePt, ProbeEta
                    for histkey in  dInvMassMuDTHist:
                        if abs(ProbeEta) > histkey[0][0] and abs(ProbeEta) < histkey[0][1] and ProbePt > histkey[1][0] and ProbePt < histkey[1][1]:
                            fillth1(dInvMassMuDTHist[histkey],IM,weight)                    
                    for histkey in  hMuProbePt_DTnums:
                        if abs(ProbeEta) > histkey[0] and abs(ProbeEta) < histkey[1]: 
                            fillth1(hMuProbePt_DTnums[histkey], ProbePt, weight)                    
                    for histkey in  dProbeMuTrkResponseDT_:
                        if abs(ProbeEta) > histkey[0][0] and abs(ProbeEta) < histkey[0][1] and isgenmatched > histkey[1][0] and isgenmatched < histkey[1][1]:
                            fillth1(dProbeMuTrkResponseDT_[histkey],TMath.Log10(ProbePt/isgenmatched),weight)

                if probeIsReco:
                    if not isdata: isgenmatched  = isGenMatched(probeTlv, 13)
                    else: isgenmatched = 1                
                    #if isgenmatched == 0: continue #uncomment to skip isGenMatcheding of Probes
                    ProbePt   = probeTlv.Pt()
                    ProbeEta = abs(probeTlv.Eta())
                    for histkey in  dInvMassMuRECOHist:
                        if abs(ProbeEta) > histkey[0][0] and abs(ProbeEta) < histkey[0][1] and ProbePt > histkey[1][0] and ProbePt < histkey[1][1]:
                            fillth1(dInvMassMuRECOHist[histkey],IM, weight)       
                    for histkey in  hMuProbePt_RECOdens:
                        if abs(ProbeEta) > histkey[0] and abs(ProbeEta) < histkey[1]:
                            fillth1(hMuProbePt_RECOdens[histkey], ProbePt, weight)   
                    for histkey in  dProbeMuTrkResponseRECO_:
                        if abs(ProbeEta) > histkey[0][0] and abs(ProbeEta) < histkey[0][1] and isgenmatched > histkey[1][0] and isgenmatched < histkey[1][1]:
                            fillth1(dProbeMuTrkResponseRECO_[histkey],TMath.Log10(ProbePt/isgenmatched),weight) 
                  
                                                    

fnew.cd()
hHt.Write()
hHtWeighted.Write()
hElTagPt.Write()
hElTagEta.Write()
hMuTagPt.Write()
hMuTagEta.Write()
hEtaVsPhiDT.Write()

#Dictionaries:
for histkey in hElProbePt_DTnums: 
    hElProbePt_DTnums[histkey].Write()    
    hElProbePt_RECOdens[histkey].Write()
    hGenElProbePt_DTnums[histkey].Write()    
    hGenElProbePt_RECOdens[histkey].Write() 
    
    hMuProbePt_DTnums[histkey].Write()    
    hMuProbePt_RECOdens[histkey].Write()
    hGenMuProbePt_DTnums[histkey].Write()    
    hGenMuProbePt_RECOdens[histkey].Write()       
for histkey in  dProbeElTrkResponseDT_: 
    dProbeElTrkResponseDT_[histkey].Write()
    dProbeElTrkResponseRECO_[histkey].Write()
    dProbeMuTrkResponseDT_[histkey].Write()
    dProbeMuTrkResponseRECO_[histkey].Write()    
for histkey in  dInvMassElRECOHist:
    dInvMassElRECOHist[histkey].Write()
    dInvMassElDTHist[histkey].Write()
    dInvMassMuRECOHist[histkey].Write()
    dInvMassMuDTHist[histkey].Write()    

hGenPtvsResp.Write()

print "just created file:", fnew.GetName()
hNTrackerLayersDT_el.Write()
hNTrackerLayersDT_mu.Write()
fnew.Close()
