from ROOT import *
import sys
import numpy as np
from DataFormats.FWLite import Events, Handle
import scipy.constants as scc
import math
from glob import glob
from FWCore.ParameterSet.VarParsing import VarParsing
from random import shuffle
from utils import *
import random

isData = True
if isData: doGen = False #false for real data
else: doGen = True

weight = 1 
gROOT.SetBatch()
gROOT.SetStyle('Plain')
verbose = False

hNTrackerLayersDT = TH1F('hNTrackerLayersDT','hNTrackerLayersDT',11,0,11)

try: inputFileNames = sys.argv[1]
except: 
    inputFileNames = "/pnfs/desy.de/cms/tier2/store/user/sbein/NtupleHub/Production2016v2/Summer16.DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_391_RA2AnalysisTree.root"
    print 'running on small default DYtoLL sample', inputFileNames
    
inputFiles = glob(inputFileNames)
x_ = len(inputFiles)

c = TChain("TreeMaker2/PreSelection")

#fname = '/nfs/dust/cms/user/singha/LLCh/BACKGROUNDII/CMSSW_8_0_20/src/MCTemplatesBinned/BinnedTemplatesIIDY_WJ_TT.root'
fname = '/nfs/dust/cms/user/beinsam/LongLiveTheChi/Analyzer/CMSSW_8_0_21/src/DataDrivenSmear.root'
fSmear  = TFile(fname)

dResponseHist = {}
for iPtBin, PtBin in enumerate(PtBinEdges[:-1]):
    for iEtaBin, EtaBin_ in enumerate(EtaBinEdges[:-1]):
        newHistKey = ((EtaBin_,EtaBinEdges[iEtaBin + 1]),(PtBin,PtBinEdges[iPtBin + 1]))
        dResponseHist[newHistKey] = fSmear.Get("htrkresp"+str(newHistKey))

dEleResponseHist = {}
for iPtBin, PtBin in enumerate(PtBinEdges[:-1]):
    for iEtaBin, EtaBin in enumerate(EtaBinEdges[:-1]):
        newHistKey = ((EtaBin,EtaBinEdges[iEtaBin + 1]),(PtBin,PtBinEdges[iPtBin + 1]))
        dEleResponseHist[newHistKey] = fSmear.Get("heleresp"+str(newHistKey))

dSmearedEleResponseHist = {}
for iPtBin, PtBin in enumerate(PtBinEdges[:-1]):
    for iEtaBin, EtaBin in enumerate(EtaBinEdges[:-1]):
        newHistKey = ((EtaBin,EtaBinEdges[iEtaBin + 1]),(PtBin,PtBinEdges[iPtBin + 1]))
        dSmearedEleResponseHist[newHistKey] = makeTh1("hsmearedeleresp"+str(newHistKey),"hsmearedeleresp"+str(newHistKey), 100,-2,2)
        histoStyler(dSmearedEleResponseHist[newHistKey], 1)

dProbeTrkResponseHist_ = {}
for iPtBin, PtBin in enumerate(PtBinEdges[:-1]):
    for iEtaBin, EtaBin in enumerate(EtaBinEdges[:-1]):
        newHistKey = ((EtaBin,EtaBinEdges[iEtaBin + 1]),(PtBin,PtBinEdges[iPtBin + 1]))
        dProbeTrkResponseHist_[newHistKey] = makeTh1("hProbeTrkresp"+str(newHistKey),"hProbeTrkresp"+str(newHistKey), 100,-2,2)
        histoStyler(dProbeTrkResponseHist_[newHistKey], 1)


dInvMassRECOHist = {}
for iPtBin, PtBin in enumerate(PtBinEdges[:-1]):
    for iEtaBin, EtaBin in enumerate(EtaBinEdges[:-1]):
        newHistKey = ((EtaBin,EtaBinEdges[iEtaBin + 1]),(PtBin,PtBinEdges[iPtBin + 1]))
        dInvMassRECOHist[newHistKey] = makeTh1("hInvMass"+str(newHistKey)+"RECO_den"  , "hInvMass"+str(newHistKey)+"RECO_den", 40, 60, 120)
        histoStyler(dInvMassRECOHist[newHistKey], 1)

dInvMassDTHist = {}
for iPtBin, PtBin in enumerate(PtBinEdges[:-1]):
    for iEtaBin, EtaBin in enumerate(EtaBinEdges[:-1]):
        newHistKey = ((EtaBin,EtaBinEdges[iEtaBin + 1]),(PtBin,PtBinEdges[iPtBin + 1]))
        dInvMassDTHist[newHistKey] = makeTh1("hInvMass"+str(newHistKey)+"DT_num"  , "hInvMass"+str(newHistKey)+"DT_num", 40, 60, 120)
        histoStyler(dInvMassDTHist[newHistKey], 1)

##adapt script for BDT disappearing track
readerPixelOnly = TMVA.Reader()
pixelXml = '/nfs/dust/cms/user/kutznerv/cmsdas-res/BDTs/newpresel3-200-4-short-nodxyVtx/weights/TMVAClassification_BDT.weights.xml'
prepareReader(readerPixelOnly, pixelXml)
readerPixelStrips = TMVA.Reader()
trackerXml = '/nfs/dust/cms/user/kutznerv/cmsdas-res/BDTs/newpresel2-200-4-medium-nodxyVtx/weights/TMVAClassification_BDT.weights.xml'
prepareReader(readerPixelStrips, trackerXml)

def main():
    
    for f in range(0,x_):
        print 'file number:', f, ':',inputFiles[f]
        c.Add(inputFiles[f])
    c.Show(0)
    nentries = c.GetEntries()
    print nentries, ' events to be analyzed'
    verbosity = 1000
    identifier = inputFiles[0][inputFiles[0].rfind('/')+1:].replace('.root','').replace('Summer16.','').replace('RA2AnalysisTree','')
    identifier+='nFiles'+str(len(inputFiles))

    hHTnum        = makeTh1("hHTnum","HT for number of events", 150,40,2500)
    hne          = makeTh1("hne", "number of electrons", 4, 0, 4)
    hIMcheck          = makeTh1("hIMcheck"  , "IM  ", 60, 20, 180)
    hEleGenPt         = makeTh1VB("hEleGenPt", ";m [GeV] ;pt of the gen Ele;;", len(PtBinEdges)-1,PtBinEdges)
    hEleGenPtRECO_den      = makeTh1VB("hEleGenPtRECO_den", ";m [GeV] ;pt of the RECO Ele;;", len(PtBinEdges)-1,PtBinEdges)
    hEleGenChargeRECO_den      = makeTh1("hEleGenChargeRECO_den", ";m [GeV] ;charge of the RECO Ele;;", 9,-4,4)
    hEleGenPtDT_num    = makeTh1VB("hEleGenPtDT_num", "pt of the DT Ele", len(PtBinEdges)-1,PtBinEdges)
    hEleGenChargeDT_num    = makeTh1("hEleGenChargeDT_num", "pt of the DT Ele", 9,-4,4)
    hEleGenPtbarrelRECO_den      = makeTh1VB("hEleGenPtbarrelRECO_den", ";m [GeV] ;pt of the RECO Ele;;", len(PtBinEdges)-1,PtBinEdges)
    hEleGenPtbarrelDT_num    = makeTh1VB("hEleGenPtbarrelDT_num", "pt of the DT Ele", len(PtBinEdges)-1,PtBinEdges)
    hEleGenPtECRECO_den      = makeTh1VB("hEleGenPtECRECO_den", ";m [GeV] ;pt of the RECO Ele;;", len(PtBinEdges)-1,PtBinEdges)
    hEleGenPtECDT_num    = makeTh1VB("hEleGenPtECDT_num", "pt of the DT Ele", len(PtBinEdges)-1,PtBinEdges)
    hEleGenEta        = makeTh1VB("hEleGenEta", "Eta of the gen Ele", len(EtaBinEdges)-1,EtaBinEdges)
    hEleGenEtaRECO_den     = makeTh1VB("hEleGenEtaRECO_den", "Eta of the gen Ele", len(EtaBinEdges)-1,EtaBinEdges)
    hEleGenEtaDT_num       = makeTh1VB("hEleGenEtaDT_num", "Eta of the reco Ele", len(EtaBinEdges)-1,EtaBinEdges)
    hEleProbePt       = makeTh1VB("hEleProbePt", "pt of the EleProbes", len(PtBinEdges)-1,PtBinEdges)
    hEleProbePtDT_num      = makeTh1VB("hEleProbePtDT_num", "pt of the EleProbes", len(PtBinEdges)-1,PtBinEdges)
    hEleProbeChargeDT_num      = makeTh1("hEleProbeChargeDT_num", "charge of the EleProbes", 9,-4,4)
    hEleProbePtbarrelDT_num      = makeTh1VB("hEleProbePtbarrelDT_num", "pt of the EleProbes", len(PtBinEdges)-1,PtBinEdges)
    hEleProbePtECDT_num      = makeTh1VB("hEleProbePtECDT_num", "pt of the EleProbes", len(PtBinEdges)-1,PtBinEdges)
    hEleProbePtRECO_den    = makeTh1VB("hEleProbePtRECO_den", "pt of the EleProbes", len(PtBinEdges)-1,PtBinEdges)
    hEleProbeChargeRECO_den    = makeTh1("hEleProbeChargeRECO_den", "pt of the EleProbes", 9,-4,4)
    hEleProbePtbarrelRECO_den    = makeTh1VB("hEleProbePtbarrelRECO_den", "pt of the EleProbes", len(PtBinEdges)-1,PtBinEdges)
    hEleProbePtECRECO_den    = makeTh1VB("hEleProbePtECRECO_den", "pt of the EleProbes", len(PtBinEdges)-1,PtBinEdges)
    #hEleProbePtDTmeff      = makeTh1VB("hEleProbePtDTmeff", "pt of the EleProbes", len(PtBinEdges)-1,PtBinEdges)
    hEleProbeEta      = makeTh1VB("hEleProbeEta", "Eta of the EleProbes", len(EtaBinEdges)-1,EtaBinEdges)
    hEleProbeEtaDT_num     = makeTh1VB("hEleProbeEtaDT_num", "Eta of the EleProbes", len(EtaBinEdges)-1,EtaBinEdges)
    hEleProbeEtaDTmeff     = makeTh1VB("hEleProbeEtaDTmeff", "Eta of the EleProbes", len(EtaBinEdges)-1,EtaBinEdges)
    hEleProbeEtaRECO_den   = makeTh1VB("hEleProbeEtaRECO_den", "Eta of the EleProbes", len(EtaBinEdges)-1,EtaBinEdges)
    hEleTagPt         = makeTh1VB("hEleTagPt"  , "pt of the EleTags", len(PtBinEdges)-1,PtBinEdges)
    hEleTagEta        = makeTh1VB("hEleTagEta"  , "Eta of the EleTags", len(EtaBinEdges)-1,EtaBinEdges)
    hbkgID              = makeTh1("hbkgID", "background pdgID", 100, -25, 25)
    hEleControlPt         = makeTh1VB("hEleControlPt"  , "hEleControlPt", len(PtBinEdges)-1,PtBinEdges)
    hEleSmearedControlPt         = makeTh1VB("hEleSmearedControlPt"  , "hEleSmearedControlPt", len(PtBinEdges)-1,PtBinEdges)
    hprobe        = makeTh1("hprobe"  , "probe status", 2, 0, 2)
    hIMmuZ        = makeTh1("hIMmuZ"  , "IM z ", 60, 20, 150)
    hIMmuZsmear       = makeTh1("hIMmuZsmear"  , "IM z smeared ", 60, 20, 150)
    hIMZ          = makeTh1("hIMZ"  , "IM z ", 40, 60, 120)
    hIMZRECO_den       = makeTh1("hIMZRECO_den"  , "IM tag + RECOing probe ", 40, 60, 120)
    hIMZDT_num         = makeTh1("hIMZDT_num"  , "IM tag + DTing probe ", 40, 60, 120)
    hIMZDTmeff        = makeTh1("hIMZDTmeff"  , "IM tag + DTing probe ", 40, 60, 120)
    hmuonresp         =makeTh1("hmuonresp","muon response", 50,-3,3.2)
    hmuonresptest     =makeTh1("hmuonresptest","muon response test", 50,-3,3.2)
    hRelErrPtvsptMu    = TH2D("hRelErrPtvsptMu","hRelErrPtvsptMu",50, 10, 400, 20, 0 ,2)
    hRelErrPtvsptTrk       = TH2D("hRelErrPtvsptTrk","hRelErrPtvsptTrk",50, 10, 400, 20, 0 ,2)
    hGenPtvsResp    = TH2D("hGenPtvsResp","hGenPtvsResp",50, 10, 400, 20, -2 ,3)     
    hGenPtvsRespS    = TH2D("hGenPtvsRespS","hGenPtvsRespS",50, 10, 400, 20, -2 ,3)
    hGenPtvsRespM    = TH2D("hGenPtvsRespM","hGenPtvsRespM",50, 10, 400, 20, -2 ,3)
    hGenPtvsRespL    = TH2D("hGenPtvsRespL","hGenPtvsRespL",50, 10, 400, 20, -2 ,3)
    hPtvsEtaRECO_den    = TH2D("hPtvsEtaRECO_den","hPtvsEtaRECO_den",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
    hPtvsEtaDT_num    = TH2D("hPtvsEtaDT_num","hPtvsEtaDT_num",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
    hGenPtvsEtaRECO_den    = TH2D("hGenPtvsEtaRECO_den","hGenPtvsEtaRECO_den",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
    hGenPtvsEtaDT_num    = TH2D("hGenPtvsEtaDT_num","hGenPtvsEtaDT_num",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
    hPtvsEtaPlusRECO_den    = TH2D("hPtvsEtaPlusRECO_den","hPtvsEtaPlusRECO_den",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
    hPtvsEtaPlusDT_num    = TH2D("hPtvsEtaPlusDT_num","hPtvsEtaPlusDT_num",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
    hGenPtvsEtaPlusRECO_den    = TH2D("hGenPtvsEtaPlusRECO_den","hGenPtvsEtaPlusRECO_den",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
    hGenPtvsEtaPlusDT_num    = TH2D("hGenPtvsEtaPlusDT_num","hGenPtvsEtaPlusDT_num",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
    hPtvsEtaMinusRECO_den    = TH2D("hPtvsEtaMinusRECO_den","hPtvsEtaMinusRECO_den",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
    hPtvsEtaMinusDT_num    = TH2D("hPtvsEtaMinusDT_num","hPtvsEtaMinusDT_num",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
    hGenPtvsEtaMinusRECO_den    = TH2D("hGenPtvsEtaMinusRECO_den","hGenPtvsEtaMinusRECO_den",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
    hGenPtvsEtaMinusDT_num    = TH2D("hGenPtvsEtaMinusDT_num","hGenPtvsEtaMinusDT_num",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
    hEleProbePtDTmeff      = makeTh1VB("hEleProbePtDTmeff", "pt of the EleProbes", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
    

    jentry=0
    n = 0
    f = 0
    rand = 1
    e1 = 0
    e2 = 0
    e3 = 0
    etaMax = 2.4
        
    for ientry in range(nentries):
    
        #if not ientry==4207: continue
        if ientry%verbosity==0:
            a = 1
            print 'now processing event number', ientry, 'of', nentries
        if verbose:
            if not ientry in [15385]: continue
#        print 'getting entry', ientry
        c.GetEntry(ientry)
#        print 'getting entry', ientry
#        if not (c.HT > 100): continue
        if ientry==0:
           for itrig in range(len(c.TriggerNames)):
                  print itrig, c.TriggerNames[itrig], c.TriggerPass[itrig]
        if not c.TriggerPass[19]: continue
        full = 2.4 
        weight = 1 #(c.CrossSection*35.9)/(1*.001)
        deemedgen_elePt = 0
        discisionPtele = 0
        SmearedelePt = 0
        fillth1(hHTnum, c.HT)
        flag_DT = -1
        recof = 0
        nmu = -1
        P1  =  0
        Eta1  =  0
        Phi1 = 0
        C1 = 0
        P2  =  0
        Eta2 = 0
        C2 = 0
        IM  =  0 
        dIM =  0
        dIMmax = 999
        track_id = -1
        dumTlvsum = TLorentzVector()
        dumTlvsum.SetPxPyPzE(0, 0, 0, 0)
        theTag = TLorentzVector()
        theTag.SetPxPyPzE(0, 0, 0, 0)
        tagProbeTlvSum = TLorentzVector()
        tagProbeTlvSum.SetPxPyPzE(0, 0, 0, 0)
        smearedEleProbe = TLorentzVector()
        smearedEleProbe.SetPtEtaPhiE(0, 0, 0, 0)
        probeTlv = TLorentzVector()
        probeTlv.SetPxPyPzE(0, 0, 0, 0)
        dtTlvsum = TLorentzVector()
        dtTlvsum.SetPxPyPzE(0, 0, 0, 0)
        checkTlvsum = TLorentzVector()
        checkTlvsum.SetPxPyPzE(0, 0, 0, 0)
        ne = 0
        chargeCheck = 0
        muons = []

        #event variable cuts
#        if not (c.HT > 100): continue
#        if not (c.MHT > 150): continue
#        if not (c.NJets > 0): continue
        for imu, muon in enumerate(c.Muons):
            if not muon.Pt()>15: continue
            if not (abs(muon.Eta()) < 2.4): continue
            if abs(muon.Eta()) < 1.566 and abs(muon.Eta()) > 1.4442: continue
            muons.append(muon)
        if not len(muons)==0: continue
	if not isData:
          genels = []
          for igp, gp in enumerate(c.GenParticles):
            if not gp.Pt()>10: continue
            if not abs(gp.Eta())<2.4: continue
            if not abs(c.GenParticles_ParentId[igp]) == 23: continue # 24 for Wpm 23 for DY
            if not (abs(c.GenParticles_PdgId[igp])==11 and c.GenParticles_Status[igp] == 1) : continue
            genels.append([gp,igp])

        basicTracks = []
        for itrack, track in enumerate(c.tracks):
            if not track.Pt() > 15 : continue
            if not abs(track.Eta()) < 2.4: continue
            if abs(abs(track.Eta()) < 1.566) and abs(track.Eta()) > 1.4442: continue
            if not isBaselineTrack(track, itrack, c): continue
            basicTracks.append([track,itrack])
        disappearingTracks = []
        mva, dedx, trkpt, trketa, trkp = -999, -999, -999, -999, -999
        nprompt = 0
        moh = -1
        pt = -1

        for itrack, track in enumerate(c.tracks):
            if not track.Pt() > 15 : continue
            if not abs(track.Eta()) < 2.4: continue
            if abs(abs(track.Eta()) < 1.566) and abs(track.Eta()) > 1.4442: continue
            if not isDisappearingTrack_(track, itrack, c, readerPixelOnly, readerPixelStrips): continue
            disappearingTracks.append([track,itrack])

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
            matchedTrack = TLorentzVector() 
            for trk in basicTracks:
                    drTrk = trk[0].DeltaR(c.Electrons[iel])
                    if drTrk<drBig4Trk:
                            drBig4Trk = drTrk
                            matchedTrack = trk[0]
                            if drTrk<0.01: break
            if not drBig4Trk<0.01: continue
            if verbose: print 'passed baseline track'
            RecoElectrons.append([ele,iel])
            #sf = 1
            #sf = getSF(abs(c.Electrons[iel].Eta()), min(c.Electrons[iel].Pt(),309.999))
            #smearedEle.SetPtEtaPhiE(sf*c.Electrons[iel].Pt(),c.Electrons[iel].Eta(),c.Electrons[iel].Phi(),sf*c.Electrons[iel].E())
            sf = getSF(abs(matchedTrack.Eta()), min(matchedTrack,299.999))
            smearedEle.SetPtEtaPhiE(sf*matchedTrack.Pt(),matchedTrack.Eta(),matchedTrack.Phi(),sf*matchedTrack.E())
        #    if not (smearedEle.Pt()>15): continue
            SmearedElectrons.append([smearedEle,iel])

        tightElectrons = []
        for ie, e in enumerate(c.Electrons):
            if not (e.Pt() > 25): continue # and bool(c.Electrons_tightID[ie])): continue
            if not (abs(e.Eta())<etaMax): continue
            if abs(e.Eta()) < 1.566 and abs(e.Eta()) > 1.4442: continue
            if not c.Electrons_passIso[ie]: continue
            tightElectrons.append([e,c.Electrons_charge[ie]])
            ne = ne + 1
            if ie > 1: continue
            chargeCheck =chargeCheck + c.Electrons_charge[ie]
            checkTlvsum = checkTlvsum + e
        fillth1(hne, ne, weight)
        if (chargeCheck == 0):
            fillth1(hIMcheck, checkTlvsum.M(), weight)
        if ne == 1 : e1 +=1
        if ne == 2 : e2 +=1
        if ne >  2 : e3 +=1

        if doGen:
          for igen, gen in enumerate(genels):
            if not len(genels) <3: continue
            drsmall = .2
            drsmal  = .2
            drsmal  = .2
            drsmal  = .2
            idtrk   = -1
            idlep   = -1
            fillth1(hEleGenPt, gen[0].Pt(), weight)
            fillth1(hEleGenEta, abs(gen[0].Eta()), weight)
            for ie, e in enumerate(SmearedElectrons):
                dr = gen[0].DeltaR(e[0])
                if dr < drsmall:
                    drsmall = dr
                    idlep   = e[1]
            if drsmall < .02:
                fillth2(hGenPtvsEtaRECO_den, e[0].Pt(), abs(e[0].Eta()), weight )
                   #replace gen[0].Pt() with # e[0].Pt() for reco kappa
                   #if (gen[0].Pt() > 70 and gen[0].Pt() < 90): print ientry, 'found electron, pT=', gen[0].Pt()
                   #print ientry, '***********Just filled with RECO elec Pt', gen[0].Pt()
                if c.Electrons_charge[idlep] == 1:fillth2(hGenPtvsEtaPlusRECO_den, e[0].Pt(), abs(e[0].Eta()), weight )
                if c.Electrons_charge[idlep] == -1:fillth2(hGenPtvsEtaMinusRECO_den, e[0].Pt(), abs(e[0].Eta()), weight )
                fillth1(hEleGenPtRECO_den, e[0].Pt(), weight)
                fillth1(hEleGenChargeRECO_den, c.GenParticles_PdgId[gen[1]]/11, weight)
                fillth1(hEleGenEtaRECO_den, abs(c.Electrons[idlep].Eta()), weight)
                fillth1(hmuonresp, math.log10(c.Electrons[idlep].Pt()/gen[0].Pt()),weight)
                fillth1(hmuonresptest, math.log10(gen[0].Pt()/gen[0].Pt()),weight)
                                #continue
            for idistrk, distrk in enumerate(disappearingTracks):
                if not distrk[0].Pt() < 600: continue
                dr = gen[0].DeltaR(distrk[0])
                if dr < drsmal:
                    drsmal = dr
                    idtrk  = distrk[1]
                    dtTlvsum = distrk
            if drsmal < .02:
                fillth2(hGenPtvsEtaDT_num, dtTlvsum[0].Pt(),abs(dtTlvsum[0].Eta()), weight)
#            if gen[0].Pt()>300:
#            print ientry, 'found disappearing track, pT=', gen[0].Pt()
                if c.tracks_charge[idtrk] == 1:fillth2(hGenPtvsEtaPlusDT_num, dtTlvsum[0].Pt(),abs(dtTlvsum[0].Eta()), weight)
                if c.tracks_charge[idtrk] ==-1:fillth2(hGenPtvsEtaMinusDT_num, dtTlvsum[0].Pt(),abs(dtTlvsum[0].Eta()), weight)
                fillth1(hEleGenPtDT_num, dtTlvsum[0].Pt(), weight)
                fillth1(hbkgID, c.GenParticles_PdgId[gen[1]], weight)
                fillth1(hEleGenChargeDT_num, c.GenParticles_PdgId[gen[1]]/11, weight)
                fillth1(hEleGenEtaDT_num, abs(dtTlvsum[0].Eta()), weight)
                fillth2(hGenPtvsResp, math.log10(dtTlvsum[0].Pt()/gen[0].Pt()),gen[0].Pt(),weight)
        
#        continue # uncomment to calculate Kappa only from Gen Information
        theTag = TLorentzVector()
        theTag.SetPxPyPzE(0,0,0,0)
        for charge in range(-1,2,2):
            for itag, tag in enumerate(tightElectrons):
                if len(tightElectrons)> 2: continue
                if not charge == tightElectrons[itag][1]: continue
                C1 = tightElectrons[itag][1]
                P1 = tightElectrons[itag][0].Pt()#mu.Pt()
                Eta1 = tightElectrons[itag][0].Eta()#abs(mu.Eta())
                Phi1 = tightElectrons[itag][0].Phi()#mu.Phi()
                theTag = tightElectrons[itag][0]
                probeIsEl, probeIsDt = False, False
                dIMmax = 999
                for itrack, track in enumerate(disappearingTracks):
                    if not track[0].Pt() < 600: continue
                    if not (C1 + c.tracks_charge[track[1]] == 0): continue
                    if track[0].DeltaR(theTag)<0.01: continue        
                    tagProbeTlvSum = theTag + track[0]
                    IMleplep = tagProbeTlvSum.M()
                    if (IMleplep < 0): continue
                    dIM = abs(IMleplep - 91)
                    if(dIM < dIMmax):
                        dIMmax = dIM
                        IM     = IMleplep
                        track_id  = track[1]
                        probeTlv =  track[0]
                        C2 = c.tracks_charge[track_id]
                        probeIsDt = True
                        probeIsEl = False
                                
                for ismearE, smearE in enumerate(SmearedElectrons):
                    if not smearE[0].Pt() < 600: continue
                    if not (C1 + c.Electrons_charge[smearE[1]] == 0): continue
                    if smearE[0].DeltaR(theTag)<0.01: continue
                #    if not (bool(c.Electrons_tightID[smearE[1]]) ==1): continue ## NOT sure about this criteria
                    if (C1 + c.Electrons_charge[smearE[1]] ==0):
                        tagProbeTlvSum = theTag + smearE[0]
                        fillth1(hIMmuZ, tagProbeTlvSum.M(), weight)
                    if not smearE[0].Pt()>15: continue
                    tagProbeTlvSum = theTag + smearE[0]
                    IMleplep = tagProbeTlvSum.M()
                    if (C1 + c.Electrons_charge[smearE[1]] ==0):
                        fillth1(hIMmuZsmear, tagProbeTlvSum.M(), weight)
                    if (IMleplep < 0): continue
                    dIM = abs(IMleplep - 91)
                    if(dIM < dIMmax):
                        dIMmax = dIM
                        IM     = IMleplep
                        deemedgen_elePt = c.Electrons[smearE[1]].Pt()
                        discisionPtele = min(c.Electrons[smearE[1]].Pt(),309.999)
                        SmearedelePt = smearE[0].Pt()
                        track_id  = smearE[1]
                        probeTlv  = smearE[0]
                        ControlPt = RecoElectrons[ismearE][0].Pt() # should be same as deemedgen_elePt
                    #    probeTlv =  smearE
                        C2 = c.Electrons_charge[smearE[1]]
                        probeIsEl = True
                        probeIsDt = False                        


                if (IM > 60 and IM < 120 and (C1+C2 )==0):
                    gm = 0
            #print ientry, '', dIMmax, 'inv mass', IM, 'track_id', track_id, 'probeIsDt', probeIsDt, 'probeIsEl', probeIsEl                                                
                    if probeIsDt:
                        P2 = probeTlv.Pt()
                        Eta2 = abs(probeTlv.Eta())
                        fillth1(hEleTagPt, P1, weight)
                        fillth1(hEleProbePt, P2, weight)
                        fillth1(hEleTagEta, Eta1, weight)
                        fillth1(hEleProbeEta, Eta2, weight)
                        print ientry, 'inside disappearing track', IM        
                        fillth1(hIMZ, IM, weight)
                        fillth1(hIMZDTmeff, IM, weight)
                        fillth1(hEleProbePtDTmeff, P2, weight)
                        fillth1(hEleProbeEtaDTmeff, Eta2, weight)
                        #gm  = genMatch(probeTlv)
#                        if gm == 0: continue #uncomment to skip genMatching of Probes
                        fillth2(hPtvsEtaDT_num, P2, Eta2, weight)
                        if C2 == 1:fillth2(hPtvsEtaPlusDT_num, P2, Eta2, weight)
                        if C2 == -1:fillth2(hPtvsEtaMinusDT_num, P2, Eta2, weight)
                        fillth1(hIMZDT_num, IM, weight)
                        fillIMdt(Eta2, P2,IM)
                        fillth1(hEleProbePtDT_num, P2, weight)
                        fillth1(hEleProbeChargeDT_num, C2, weight)
                        fillth1(hEleProbeChargeRECO_den, C2, weight)
                        fillResponse(Eta2, P2, gm,min(gm, 309.99), dProbeTrkResponseHist_)
                        if Eta2 < 1.4442: fillth1(hEleProbePtbarrelDT_num, P2, weight)
                        if Eta2 > 1.4442: fillth1(hEleProbePtECDT_num, P2, weight)
                        fillth1(hEleProbeEtaDT_num, Eta2, weight)
                        fillth2(hRelErrPtvsptTrk, P2,c.tracks_ptError[track_id]/(P2*P2),weight)
                    if probeIsEl:
                        #gm  = genMatch(probeTlv)
                        fillth1(hEleControlPt, ControlPt, weight)
                        fillth1(hEleSmearedControlPt, P2, weight)
#                        if gm == 0: continue #uncomment to skip genMatching of Probes
                        fillth1(hIMZ, IM, weight)  ##try to use this to get counts
                        P2   = probeTlv.Pt()
                        Eta2 = abs(probeTlv.Eta())
                        fillth2(hPtvsEtaRECO_den, P2, Eta2, weight)    
                        if C2 == 1:fillth2(hPtvsEtaPlusRECO_den, P2, Eta2, weight)
                        if C2 == -1:fillth2(hPtvsEtaMinusRECO_den, P2, Eta2, weight)
                        fillth1(hEleTagPt, P1, weight)
                        #fillth1(hEleProbePt, P2, weight)
                        fillth1(hEleTagEta, Eta1, weight)
                        fillth1(hEleProbeEta, Eta2, weight)
                        fillth1(hIMZRECO_den, IM, weight)
                        fillIMreco(Eta2, P2, IM)
                        fillth1(hEleProbePtRECO_den, P2, weight)
                        fillth1(hEleProbeChargeRECO_den, C2, weight)
                        fillResponse(Eta2, SmearedelePt, deemedgen_elePt, min(discisionPtele,309.999), dSmearedEleResponseHist)
                        if Eta2 < 1.4442 : fillth1(hEleProbePtbarrelRECO_den, P2, weight)
                        if Eta2 > 1.4442 : fillth1(hEleProbePtECRECO_den, P2, weight)
                        fillth1(hEleProbeEtaRECO_den, Eta2, weight)
                        recof = 1                

    print "RECOing probe", f , "DTing probes", n

    fnew = TFile('TagnProbeEleHists_'+identifier+'.root','recreate')
    print 'making', 'TagnProbeEleHists_'+identifier+'.root'
    fnew.cd()
    hbkgID.Write()
    hEleSmearedControlPt.Write()
    hEleControlPt.Write()
    hGenPtvsEtaRECO_den.Write()
    hGenPtvsEtaDT_num.Write()
    hPtvsEtaRECO_den.Write()
    hPtvsEtaDT_num.Write()

    hGenPtvsEtaPlusRECO_den.Write()
    hGenPtvsEtaPlusDT_num.Write()
    hPtvsEtaPlusRECO_den.Write()
    hPtvsEtaPlusDT_num.Write()

    hGenPtvsEtaMinusRECO_den.Write()
    hGenPtvsEtaMinusDT_num.Write()
    hPtvsEtaMinusRECO_den.Write()
    hPtvsEtaMinusDT_num.Write()

    hEleProbeChargeRECO_den.Write()
    hEleProbeChargeDT_num.Write()
    hIMcheck.Write()
    hHTnum.Write()

    hEleGenPt.Write()
    hEleGenEta.Write()

    hEleGenPtRECO_den.Write()
    hEleGenChargeRECO_den.Write()
    hEleGenPtbarrelRECO_den.Write()
    hEleGenPtECRECO_den.Write()
    hEleGenEtaRECO_den.Write()

    hEleGenPtDT_num.Write()
    hEleGenChargeDT_num.Write()
    hEleGenPtbarrelDT_num.Write()
    hEleGenPtECDT_num.Write()
    hEleGenEtaDT_num.Write()
    hEleTagPt.Write()
    hEleTagEta.Write()

    hEleProbePt.Write()
    hEleProbeEta.Write()
    hIMZ.Write()
    hIMmuZsmear.Write()
    hIMmuZ.Write()
    hprobe.Write()

    hIMZRECO_den.Write()
    hEleProbePtRECO_den.Write()
    hEleProbePtbarrelRECO_den.Write()
    hEleProbePtECRECO_den.Write()
    hEleProbeEtaRECO_den.Write()
    hIMZDT_num.Write()
    hEleProbePtDT_num.Write()
    hEleProbePtbarrelDT_num.Write()
    hEleProbePtECDT_num.Write()
    hEleProbeEtaDT_num.Write()

    #InvMassRECO
    for histkey in  dProbeTrkResponseHist_: dProbeTrkResponseHist_[histkey].Write()
    for histkey in  dSmearedEleResponseHist: dSmearedEleResponseHist[histkey].Write()
    for histkey in  dInvMassRECOHist: dInvMassRECOHist[histkey].Write()
    for histkey in  dInvMassDTHist: dInvMassDTHist[histkey].Write()
    #response
    hmuonresp.Write()
    hmuonresptest.Write()
    hRelErrPtvsptTrk.Write()

    hGenPtvsResp.Write()
    hGenPtvsRespS.Write()
    hGenPtvsRespM.Write()
    hGenPtvsRespL.Write()
    hne.Write()
    print "just created file:", fnew.GetName()
    fnew.Close()


def genMatch(lep):
    for igenm, genm in enumerate(c.GenParticles):
        if not genm.Pt() > 10: continue
        if not abs(c.GenParticles_ParentId[igenm]) == 23: continue
        if not (abs(c.GenParticles_PdgId[igenm]) == 11 and c.GenParticles_Status[igenm] == 1):continue
        drm = genm.DeltaR(lep)
        if drm < .01:
            return genm.Pt()
    return 0
def determileLength(sp_track, sp_track_id):
    S = 0
    M = 0
    L = 0
    if c.tracks_pixelLayersWithMeasurement[sp_track_id] == c.tracks_trackerLayersWithMeasurement[sp_track_id]: S = 1
    if c.tracks_trackerLayersWithMeasurement[sp_track_id] < 7 and c.tracks_pixelLayersWithMeasurement[sp_track_id] < c.tracks_trackerLayersWithMeasurement[sp_track_id]: M = 2
    if c.tracks_trackerLayersWithMeasurement[sp_track_id] > 6 and c.tracks_pixelLayersWithMeasurement[sp_track_id] < c.tracks_trackerLayersWithMeasurement[sp_track_id]: L = 3
    return S+M+L


def nJets_adj(muon):
    
    j = c.NJets
    for ijet, jet in enumerate(c.Jets):
        if (c.NJets == ijet): break
        print "Jet number ", ijet+1, " Pt: ", jet.Pt()
        dr = muon.DeltaR(jet)
        if (dr < 0.5): j = j-1
    return j
            

def getSF(Eta, Pt, Draw = False):
    for histkey in  dResponseHist:
        if abs(Eta) > histkey[0][0] and abs(Eta) < histkey[0][1] and Pt > histkey[1][0] and Pt < histkey[1][1]:
            SF_trk = 10**(dResponseHist[histkey].GetRandom())
            return SF_trk #/SF_ele
        
    return 1

def fillIMreco(Eta, Pt, InvM):

    for histkey in  dInvMassRECOHist:
        if abs(Eta) > histkey[0][0] and abs(Eta) < histkey[0][1] and Pt > histkey[1][0] and Pt < histkey[1][1]:
            fillth1(dInvMassRECOHist[histkey],InvM,weight)
            return 1
    return 1

def fillIMdt(Eta, Pt, InvM):

    for histkey in  dInvMassDTHist:
        if abs(Eta) > histkey[0][0] and abs(Eta) < histkey[0][1] and Pt > histkey[1][0] and Pt < histkey[1][1]:
            fillth1(dInvMassDTHist[histkey],InvM,weight)
            return 1
    return 1

def fillResponse(Eta, SmearedPt, GenPt, discisionPt, dictionary):
    for histkey in  dictionary:
        if abs(Eta) > histkey[0][0] and abs(Eta) < histkey[0][1] and discisionPt > histkey[1][0] and discisionPt < histkey[1][1]:
            fillth1(dictionary[histkey],math.log10(SmearedPt/GenPt),weight)
            return 1
    return 1

main()
