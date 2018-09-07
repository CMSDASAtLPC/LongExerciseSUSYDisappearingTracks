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
from utilsII import *
import random

options = VarParsing ('python')
options.parseArguments()
weight = 1 #################################WEIGHT
gROOT.SetBatch()
gROOT.SetStyle('Plain')
inputFiles = options.inputFiles
verbose = False
if inputFiles ==  []:
	print 'running on small default DYtoLL sample'
	inputFiles = ["/pnfs/desy.de/cms/tier2/store/user/sbein/NtupleHub/Production2016v2/Summer16.DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_391_RA2AnalysisTree.root"]
x_ = len(inputFiles)

c = TChain("TreeMaker2/PreSelection")

fname = '/nfs/dust/cms/user/singha/LLCh/BACKGROUNDII/CMSSW_8_0_20/src/MCTemplatesBinned/BinnedTemplatesIIDY_WJ_TT.root'
fSmear  = TFile(fname)

dResponseHist = {}
for iPtBin, PtBin in enumerate(PtBinEdges[:-1]):
        for iEtaBin, EtaBin in enumerate(EtaBinEdges[:-1]):
                newHistKey = ((EtaBin,EtaBinEdges[iEtaBin + 1]),(PtBin,PtBinEdges[iPtBin + 1]))
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
                dSmearedEleResponseHist[newHistKey] = TH1D("hsmearedeleresp"+str(newHistKey),"hsmearedeleresp"+str(newHistKey), 100,-2,2)
                histoStyler(dSmearedEleResponseHist[newHistKey], 1)

dProbeTrkResponseHist_ = {}
for iPtBin, PtBin in enumerate(PtBinEdges[:-1]):
        for iEtaBin, EtaBin in enumerate(EtaBinEdges[:-1]):
                newHistKey = ((EtaBin,EtaBinEdges[iEtaBin + 1]),(PtBin,PtBinEdges[iPtBin + 1]))
                dProbeTrkResponseHist_[newHistKey] = TH1D("hProbeTrkresp"+str(newHistKey),"hProbeTrkresp"+str(newHistKey), 100,-2,2)
                histoStyler(dProbeTrkResponseHist_[newHistKey], 1)


dInvMassRECOHist = {}
for iPtBin, PtBin in enumerate(PtBinEdges[:-1]):
        for iEtaBin, EtaBin in enumerate(EtaBinEdges[:-1]):
                newHistKey = ((EtaBin,EtaBinEdges[iEtaBin + 1]),(PtBin,PtBinEdges[iPtBin + 1]))
                dInvMassRECOHist[newHistKey] = TH1D("hInvMass"+str(newHistKey)+"RECOeff"  , "hInvMass"+str(newHistKey)+"RECOeff", 40, 60, 120)
		histoStyler(dInvMassRECOHist[newHistKey], 1)

dInvMassDTHist = {}
for iPtBin, PtBin in enumerate(PtBinEdges[:-1]):
        for iEtaBin, EtaBin in enumerate(EtaBinEdges[:-1]):
                newHistKey = ((EtaBin,EtaBinEdges[iEtaBin + 1]),(PtBin,PtBinEdges[iPtBin + 1]))
                dInvMassDTHist[newHistKey] = TH1D("hInvMass"+str(newHistKey)+"DTeff"  , "hInvMass"+str(newHistKey)+"DTeff", 40, 60, 120)
		histoStyler(dInvMassDTHist[newHistKey], 1)

##adapt script for BDT disappearing track

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
pixelXml = '/nfs/dust/cms/user/kutznerv/shorttrack/CMSSW_10_1_7/src/shorttrack/cutoptimization/tmva/newpresel3-200-4-short/weights/TMVAClassification_BDT.weights.xml'
prepareReader(readerPixelOnly, pixelXml)
readerPixelStrips = TMVA.Reader()
trackerXml = '/nfs/dust/cms/user/kutznerv/shorttrack/CMSSW_10_1_7/src/shorttrack/cutoptimization/tmva/newpresel2-200-4-medium/weights/TMVAClassification_BDT.weights.xml'
prepareReader(readerPixelStrips, trackerXml)



def main():
	
        for f in range(0,x_):
		print 'file number:', f, ':',inputFiles[f]
		c.Add(inputFiles[f])
	nentries = c.GetEntries()
	print nentries, ' events to be analyzed'
	verbosity = 1000
	identifier = inputFiles[0][inputFiles[0].rfind('/')+1:].replace('.root','').replace('Summer16.','').replace('RA2AnalysisTree','')
	identifier+='nFiles'+str(len(inputFiles))

	hHTnum                = TH1D("hHTnum","HT for number of events", 150,40,2500)
	histoStyler(hHTnum,1)
	hne                  = TH1F("hne", "number of electrons", 4, 0, 4)
	histoStyler(hne,1)	
	hIMcheck                  = TH1D("hIMcheck"  , "IM  ", 60, 20, 180)
	histoStyler(hIMcheck,1)	
	hEleGenPt             = TH1D("hEleGenPt", ";m [GeV] ;pt of the gen Ele;;", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
	histoStyler(hEleGenPt,1)	
	hEleGenPtRECOeff      = TH1D("hEleGenPtRECOeff", ";m [GeV] ;pt of the RECO Ele;;", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
	histoStyler(hEleGenPtRECOeff,1)
	hEleGenChargeRECOeff      = TH1D("hEleGenChargeRECOeff", ";m [GeV] ;charge of the RECO Ele;;", 9,-4,4)
        histoStyler(hEleGenChargeRECOeff,1)

	hEleGenPtDTeff        = TH1D("hEleGenPtDTeff", "pt of the DT Ele", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
	histoStyler(hEleGenPtDTeff,1)
	hEleGenChargeDTeff        = TH1D("hEleGenChargeDTeff", "pt of the DT Ele", 9,-4,4)
        histoStyler(hEleGenChargeDTeff,1)

        hEleGenPtbarrelRECOeff      = TH1D("hEleGenPtbarrelRECOeff", ";m [GeV] ;pt of the RECO Ele;;", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
        histoStyler(hEleGenPtbarrelRECOeff,1)
        hEleGenPtbarrelDTeff        = TH1D("hEleGenPtbarrelDTeff", "pt of the DT Ele", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
        histoStyler(hEleGenPtbarrelDTeff,1)
        hEleGenPtECRECOeff      = TH1D("hEleGenPtECRECOeff", ";m [GeV] ;pt of the RECO Ele;;", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
        histoStyler(hEleGenPtECRECOeff,1)
        hEleGenPtECDTeff        = TH1D("hEleGenPtECDTeff", "pt of the DT Ele", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
        histoStyler(hEleGenPtECDTeff,1)




	hEleGenPtSDTeff        = TH1D("hEleGenPtSDTeff", "pt of the SDT Ele", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
	histoStyler(hEleGenPtSDTeff,1)
	hEleGenPtMDTeff        = TH1D("hEleGenPtMDTeff", "pt of the MDT Ele", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
	histoStyler(hEleGenPtMDTeff,1)
	hEleGenPtLDTeff        = TH1D("hEleGenPtLDTeff", "pt of the LDT Ele", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
	histoStyler(hEleGenPtLDTeff,1)
	hEleGenEta            = TH1D("hEleGenEta", "Eta of the gen Ele", len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
	histoStyler(hEleGenEta,1)
	hEleGenEtaRECOeff     = TH1D("hEleGenEtaRECOeff", "Eta of the gen Ele", len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
	histoStyler(hEleGenEtaRECOeff,1)
	hEleGenEtaDTeff       = TH1D("hEleGenEtaDTeff", "Eta of the reco Ele", len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
	histoStyler(hEleGenEtaDTeff,1)
	hEleGenEtaSDTeff       = TH1D("hEleGenEtaSDTeff", "Eta of the SDT", len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
	histoStyler(hEleGenEtaSDTeff,1)
	hEleGenEtaMDTeff       = TH1D("hEleGenEtaMDTeff", "Eta of the MDT", len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
	histoStyler(hEleGenEtaMDTeff,1)
	hEleGenEtaLDTeff       = TH1D("hEleGenEtaLDTeff", "Eta of the LDT", len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
	histoStyler(hEleGenEtaLDTeff,1)
	hEleProbePt           = TH1D("hEleProbePt", "pt of the EleProbes", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
	hEleProbePtDTeff      = TH1D("hEleProbePtDTeff", "pt of the EleProbes", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
	hEleProbeChargeDTeff      = TH1D("hEleProbeChargeDTeff", "charge of the EleProbes", 9,-4,4)
        hEleProbePtbarrelDTeff      = TH1D("hEleProbePtbarrelDTeff", "pt of the EleProbes", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
        hEleProbePtECDTeff      = TH1D("hEleProbePtECDTeff", "pt of the EleProbes", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
	hEleProbePtSDTeff      = TH1D("hEleProbePtSDTeff", "pt of the EleProbes", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
	hEleProbePtMDTeff      = TH1D("hEleProbePtMDTeff", "pt of the EleProbes", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
	hEleProbePtLDTeff      = TH1D("hEleProbePtLDTeff", "pt of the EleProbes", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
	hEleProbePtRECOeff    = TH1D("hEleProbePtRECOeff", "pt of the EleProbes", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
	hEleProbeChargeRECOeff    = TH1D("hEleProbeChargeRECOeff", "pt of the EleProbes", 9,-4,4)
        hEleProbePtbarrelRECOeff    = TH1D("hEleProbePtbarrelRECOeff", "pt of the EleProbes", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
        hEleProbePtECRECOeff    = TH1D("hEleProbePtECRECOeff", "pt of the EleProbes", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
	#hEleProbePtDTmeff      = TH1D("hEleProbePtDTmeff", "pt of the EleProbes", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
	histoStyler(hEleProbePt,1)
	histoStyler(hEleProbePtDTeff,1)
	histoStyler(hEleProbeChargeDTeff,1)
        histoStyler(hEleProbePtbarrelDTeff,1)
        histoStyler(hEleProbePtECDTeff,1)
	histoStyler(hEleProbePtSDTeff,1)
	histoStyler(hEleProbePtMDTeff,1)
	histoStyler(hEleProbePtLDTeff,1)
	histoStyler(hEleProbePtRECOeff,1)
	histoStyler(hEleProbeChargeRECOeff,1)
        histoStyler(hEleProbePtbarrelRECOeff,1)
        histoStyler(hEleProbePtECRECOeff,1)
	hEleProbeEta          = TH1D("hEleProbeEta", "Eta of the EleProbes", len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
	hEleProbeEtaDTeff     = TH1D("hEleProbeEtaDTeff", "Eta of the EleProbes", len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
	hEleProbeEtaSDTeff     = TH1D("hEleProbeEtaSDTeff", "Eta of the EleProbes", len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
	hEleProbeEtaMDTeff     = TH1D("hEleProbeEtaMDTeff", "Eta of the EleProbes", len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
	hEleProbeEtaLDTeff     = TH1D("hEleProbeEtaLDTeff", "Eta of the EleProbes", len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
	hEleProbeEtaDTmeff     = TH1D("hEleProbeEtaDTmeff", "Eta of the EleProbes", len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
	hEleProbeEtaRECOeff   = TH1D("hEleProbeEtaRECOeff", "Eta of the EleProbes", len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
	histoStyler(hEleProbeEta,1)
	histoStyler(hEleProbeEtaDTeff,1)
	histoStyler(hEleProbeEtaSDTeff,1)
	histoStyler(hEleProbeEtaMDTeff,1)
	histoStyler(hEleProbeEtaLDTeff,1)
	histoStyler(hEleProbeEtaDTmeff,1)
	histoStyler(hEleProbeEtaRECOeff,1)
	hEleTagPt             = TH1D("hEleTagPt"  , "pt of the EleTags", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
	hEleTagEta            = TH1D("hEleTagEta"  , "Eta of the EleTags", len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
	histoStyler(hEleTagPt,1)
	histoStyler(hEleTagEta,1)
	hbkgID                          = TH1F("hbkgID", "background pdgID", 100, -25, 25)
	histoStyler(hbkgID,1)
	hEleControlPt             = TH1D("hEleControlPt"  , "hEleControlPt", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
	hEleSmearedControlPt             = TH1D("hEleSmearedControlPt"  , "hEleSmearedControlPt", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
	histoStyler(hEleControlPt,1)
	histoStyler(hEleSmearedControlPt,1)
	hprobe                = TH1D("hprobe"  , "probe status", 2, 0, 2)
	histoStyler(hprobe,1)
	hIMmuZ                = TH1D("hIMmuZ"  , "IM z ", 60, 20, 150)
	histoStyler(hIMmuZ,1)
	hIMmuZsmear           = TH1D("hIMmuZsmear"  , "IM z smeared ", 60, 20, 150)
	histoStyler(hIMmuZsmear,1)
	hIMZ                  = TH1D("hIMZ"  , "IM z ", 40, 60, 120)
	histoStyler(hIMZ,1)

	hIMZRECOeff           = TH1D("hIMZRECOeff"  , "IM tag + RECOing probe ", 40, 60, 120)
	histoStyler(hIMZRECOeff,1)
	hIMZDTeff             = TH1D("hIMZDTeff"  , "IM tag + DTing probe ", 40, 60, 120)
	histoStyler(hIMZDTeff,1)

	hIMZDTmeff            = TH1D("hIMZDTmeff"  , "IM tag + DTing probe ", 40, 60, 120)

	histoStyler(hIMZDTmeff,1)


	hmuonresp             =TH1D("hmuonresp","muon response", 50,-3,3.2)
	histoStyler(hmuonresp,1)
	hmuonresptest         =TH1D("hmuonresptest","muon response test", 50,-3,3.2)
	histoStyler(hmuonresptest,1)

	#####
	hRelErrPtvsptMu        = TH2D("hRelErrPtvsptMu","hRelErrPtvsptMu",50, 10, 400, 20, 0 ,2)
	hRelErrPtvsptTrk       = TH2D("hRelErrPtvsptTrk","hRelErrPtvsptTrk",50, 10, 400, 20, 0 ,2)


	hEleGenEtaSDTeff       = TH1D("hEleGenEtaSDTeff", "Eta of the SDT", len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
	histoStyler(hEleGenEtaSDTeff,1)
	#####
	hGenPtvsResp        = TH2D("hGenPtvsResp","hGenPtvsResp",50, 10, 400, 20, -2 ,3)         
	histoStyler(hGenPtvsResp,1)

	hGenPtvsRespS        = TH2D("hGenPtvsRespS","hGenPtvsRespS",50, 10, 400, 20, -2 ,3)
	histoStyler(hGenPtvsRespS,1)
	hGenPtvsRespM        = TH2D("hGenPtvsRespM","hGenPtvsRespM",50, 10, 400, 20, -2 ,3)
	histoStyler(hGenPtvsRespM,1)
	hGenPtvsRespL        = TH2D("hGenPtvsRespL","hGenPtvsRespL",50, 10, 400, 20, -2 ,3)
	histoStyler(hGenPtvsRespL,1)

	hPtvsEtaRECOeff        = TH2D("hPtvsEtaRECOeff","hPtvsEtaRECOeff",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
        histoStyler(hPtvsEtaRECOeff,1)
	hPtvsEtaDTeff        = TH2D("hPtvsEtaDTeff","hPtvsEtaDTeff",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
        histoStyler(hPtvsEtaDTeff,1)
	hGenPtvsEtaRECOeff        = TH2D("hGenPtvsEtaRECOeff","hGenPtvsEtaRECOeff",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
        histoStyler(hGenPtvsEtaRECOeff,1)
        hGenPtvsEtaDTeff        = TH2D("hGenPtvsEtaDTeff","hGenPtvsEtaDTeff",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
        histoStyler(hGenPtvsEtaDTeff,1)

        hPtvsEtaPlusRECOeff        = TH2D("hPtvsEtaPlusRECOeff","hPtvsEtaPlusRECOeff",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
        histoStyler(hPtvsEtaPlusRECOeff,1)
        hPtvsEtaPlusDTeff        = TH2D("hPtvsEtaPlusDTeff","hPtvsEtaPlusDTeff",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
        histoStyler(hPtvsEtaPlusDTeff,1)
        hGenPtvsEtaPlusRECOeff        = TH2D("hGenPtvsEtaPlusRECOeff","hGenPtvsEtaPlusRECOeff",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
        histoStyler(hGenPtvsEtaPlusRECOeff,1)
        hGenPtvsEtaPlusDTeff        = TH2D("hGenPtvsEtaPlusDTeff","hGenPtvsEtaPlusDTeff",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
        histoStyler(hGenPtvsEtaPlusDTeff,1)

        hPtvsEtaMinusRECOeff        = TH2D("hPtvsEtaMinusRECOeff","hPtvsEtaMinusRECOeff",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
        histoStyler(hPtvsEtaMinusRECOeff,1)
        hPtvsEtaMinusDTeff        = TH2D("hPtvsEtaMinusDTeff","hPtvsEtaMinusDTeff",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
        histoStyler(hPtvsEtaMinusDTeff,1)
        hGenPtvsEtaMinusRECOeff        = TH2D("hGenPtvsEtaMinusRECOeff","hGenPtvsEtaMinusRECOeff",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
        histoStyler(hGenPtvsEtaMinusRECOeff,1)
        hGenPtvsEtaMinusDTeff        = TH2D("hGenPtvsEtaMinusDTeff","hGenPtvsEtaMinusDTeff",len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'), len(EtaBinEdges)-1,np.asarray(EtaBinEdges, 'd'))
        histoStyler(hGenPtvsEtaMinusDTeff,1)

	hEleProbePtDTmeff      = TH1D("hEleProbePtDTmeff", "pt of the EleProbes", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
	histoStyler(hEleProbePtDTmeff,1)	
	

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
			print 'now processing event number', ientry
		if verbose:
			if not ientry in [15385]: continue
#		print 'getting entry', ientry
		c.GetEntry(ientry)
#		print 'getting entry', ientry
#		if not (c.HT > 100): continue
		full = 2.4 
		weight = 1 #(c.CrossSection*35.9)/(1*.001)
		deemedgen_elePt = 0
		discisionPtele = 0
		SmearedelePt = 0
		fillth1(hHTnum, c.madHT)
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
#		if not (c.HT > 100): continue
#		if not (c.MHT > 150): continue
#		if not (c.NJets > 0): continue
		for imu, muon in enumerate(c.Muons):
			if not muon.Pt()>15: continue
			if not (abs(muon.Eta()) < 2.4): continue
			if abs(muon.Eta()) < 1.566 and abs(muon.Eta()) > 1.4442: continue
			muons.append(muon)
		if not len(muons)==0: continue
		genels = []
		for igp, gp in enumerate(c.GenParticles):
                        if not gp.Pt()>10: continue
                        if not abs(gp.Eta())<2.4: continue
                        if not abs(c.GenParticles_ParentId[igp]) == 23: continue # 24 for Wpm 23 for DY
                        if not (abs(c.GenParticles_PdgId[igp])==11 and c.GenParticles_Status[igp] == 1) : continue
                        genels.append([gp,igp])
#                if not len(genels)==1: continue  #uncomment for Gen WJ kappa
#		if not len(genels) <3: continue  #uncomment for Gen DY kappa

		basicTracks = []
		for itrack, track in enumerate(c.tracks):
			if not track.Pt() > 15 : continue
			if not abs(track.Eta()) < 2.4: continue
			if abs(abs(track.Eta()) < 1.566) and abs(track.Eta()) > 1.4442: continue
			if not isBaselineTrk(track, itrack): continue
			basicTracks.append([track,itrack])
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
			for trk in basicTracks:
				drTrk = trk[0].DeltaR(c.Electrons[iel])
				if drTrk<drBig4Trk:
					drBig4Trk = drTrk
					if drTrk<0.01: break
			if not drBig4Trk<0.01: continue
			if verbose: print 'passed baseline track'
			RecoElectrons.append([ele,iel])
			#sf = 1
			sf = getSF(abs(c.Electrons[iel].Eta()), min(c.Electrons[iel].Pt(),309.999))
			smearedEle.SetPtEtaPhiE(sf*c.Electrons[iel].Pt(),c.Electrons[iel].Eta(),c.Electrons[iel].Phi(),sf*c.Electrons[iel].E())
		#	if not (smearedEle.Pt()>15): continue
			SmearedElectrons.append([smearedEle,iel])

		#if not (len(disappearingTracks)==1 or len(SmearedElectrons)==1): continue  #uncomment for WJ gen kappa

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
				fillth2(hGenPtvsEtaRECOeff, e[0].Pt(), abs(e[0].Eta()), weight )
	                       #replace gen[0].Pt() with # e[0].Pt() for reco kappa
	                       #if (gen[0].Pt() > 70 and gen[0].Pt() < 90): print ientry, 'found electron, pT=', gen[0].Pt()
			       #print ientry, '***********Just filled with RECO elec Pt', gen[0].Pt()
				if c.Electrons_charge[idlep] == 1:fillth2(hGenPtvsEtaPlusRECOeff, e[0].Pt(), abs(e[0].Eta()), weight )
				if c.Electrons_charge[idlep] == -1:fillth2(hGenPtvsEtaMinusRECOeff, e[0].Pt(), abs(e[0].Eta()), weight )
				fillth1(hEleGenPtRECOeff, e[0].Pt(), weight)
				fillth1(hEleGenChargeRECOeff, c.GenParticles_PdgId[gen[1]]/11, weight)
				fillth1(hEleGenEtaRECOeff, abs(c.Electrons[idlep].Eta()), weight)
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
				fillth2(hGenPtvsEtaDTeff, dtTlvsum[0].Pt(),abs(dtTlvsum[0].Eta()), weight)
#			if gen[0].Pt()>300:
#			print ientry, 'found disappearing track, pT=', gen[0].Pt()
				if c.tracks_charge[idtrk] == 1:fillth2(hGenPtvsEtaPlusDTeff, dtTlvsum[0].Pt(),abs(dtTlvsum[0].Eta()), weight)
				if c.tracks_charge[idtrk] ==-1:fillth2(hGenPtvsEtaMinusDTeff, dtTlvsum[0].Pt(),abs(dtTlvsum[0].Eta()), weight)
				fillth1(hEleGenPtDTeff, dtTlvsum[0].Pt(), weight)
				fillth1(hbkgID, c.GenParticles_PdgId[gen[1]], weight)
				fillth1(hEleGenChargeDTeff, c.GenParticles_PdgId[gen[1]]/11, weight)
				fillth1(hEleGenEtaDTeff, abs(dtTlvsum[0].Eta()), weight)
				fillth2(hGenPtvsResp, math.log10(dtTlvsum[0].Pt()/gen[0].Pt()),gen[0].Pt(),weight)
				length = determileLength(dtTlvsum, idtrk)
				if (length == 1):
					fillth1(hEleGenPtSDTeff, dtTlvsum[0].Pt(), weight)
					fillth1(hEleGenEtaSDTeff, abs(dtTlvsum[0].Eta()), weight)
					fillth2(hGenPtvsRespS, gen[0].Pt(),math.log10(dtTlvsum[0].Pt()/gen[0].Pt()),weight)
				if (length == 2):
					fillth1(hEleGenPtMDTeff, dtTlvsum[0].Pt(), weight)
					fillth1(hEleGenEtaMDTeff, abs(dtTlvsum[0].Eta()), weight)
					fillth2(hGenPtvsRespM, gen[0].Pt(),math.log10(dtTlvsum[0].Pt()/gen[0].Pt()),weight)
				if (length == 3):
					fillth1(hEleGenPtLDTeff, dtTlvsum[0].Pt(), weight)
					fillth1(hEleGenEtaLDTeff, abs(dtTlvsum[0].Eta()), weight)
					fillth2(hGenPtvsRespL, gen[0].Pt(),math.log10(dtTlvsum[0].Pt()/gen[0].Pt()),weight)
		
#		continue # uncomment to calculate Kappa only from Gen Information
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
				#	if not (bool(c.Electrons_tightID[smearE[1]]) ==1): continue ## NOT sure about this criteria
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
					#	probeTlv =  smearE
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
						gm  = genMatch(probeTlv)
#						if gm == 0: continue #uncomment to skip genMatching of Probes
						fillth2(hPtvsEtaDTeff, P2, Eta2, weight)
						if C2 == 1:fillth2(hPtvsEtaPlusDTeff, P2, Eta2, weight)
						if C2 == -1:fillth2(hPtvsEtaMinusDTeff, P2, Eta2, weight)
						fillth1(hIMZDTeff, IM, weight)
						fillIMdt(Eta2, P2,IM)
						fillth1(hEleProbePtDTeff, P2, weight)
						fillth1(hEleProbeChargeDTeff, C2, weight)
						fillth1(hEleProbeChargeRECOeff, C2, weight)
						fillResponse(Eta2, P2, gm,min(gm, 309.99), dProbeTrkResponseHist_)
						if Eta2 < 1.4442: fillth1(hEleProbePtbarrelDTeff, P2, weight)
						if Eta2 > 1.4442: fillth1(hEleProbePtECDTeff, P2, weight)
						fillth1(hEleProbeEtaDTeff, Eta2, weight)
						fillth2(hRelErrPtvsptTrk, P2,c.tracks_ptError[track_id]/(P2*P2),weight)
						length = determileLength(probeTlv, track_id)
						if (length == 1):
							fillth1(hEleProbePtSDTeff, P2, weight)
							fillth1(hEleProbeEtaSDTeff, Eta2, weight)
						if (length == 2):
							fillth1(hEleProbePtMDTeff, P2, weight)
							fillth1(hEleProbeEtaMDTeff, Eta2, weight)
						if (length == 3):
							fillth1(hEleProbePtLDTeff, P2, weight)
							fillth1(hEleProbeEtaLDTeff, Eta2, weight)
					if probeIsEl:
						gm  = genMatch(probeTlv)
						fillth1(hEleControlPt, ControlPt, weight)
						fillth1(hEleSmearedControlPt, P2, weight)
#						if gm == 0: continue #uncomment to skip genMatching of Probes
						fillth1(hIMZ, IM, weight)  ##try to use this to get counts
						P2   = probeTlv.Pt()
						Eta2 = abs(probeTlv.Eta())
						fillth2(hPtvsEtaRECOeff, P2, Eta2, weight)	
						if C2 == 1:fillth2(hPtvsEtaPlusRECOeff, P2, Eta2, weight)
						if C2 == -1:fillth2(hPtvsEtaMinusRECOeff, P2, Eta2, weight)
						fillth1(hEleTagPt, P1, weight)
						#fillth1(hEleProbePt, P2, weight)
						fillth1(hEleTagEta, Eta1, weight)
						fillth1(hEleProbeEta, Eta2, weight)
						fillth1(hIMZRECOeff, IM, weight)
						fillIMreco(Eta2, P2, IM)
						fillth1(hEleProbePtRECOeff, P2, weight)
						fillth1(hEleProbeChargeRECOeff, C2, weight)
						fillResponse(Eta2, SmearedelePt, deemedgen_elePt, min(discisionPtele,309.999), dSmearedEleResponseHist)
						if Eta2 < 1.4442 : fillth1(hEleProbePtbarrelRECOeff, P2, weight)
						if Eta2 > 1.4442 : fillth1(hEleProbePtECRECOeff, P2, weight)
						fillth1(hEleProbeEtaRECOeff, Eta2, weight)
						recof = 1				

	print "RECOing probe", f , "DTing probes", n

	fnew = TFile('BDT_TagnProbeEleHists_'+identifier+'.root','recreate')
        print 'making', 'TagnProbeEleHists_'+identifier+'.root'
        fnew.cd()
	hbkgID.Write()
	hEleSmearedControlPt.Write()
	hEleControlPt.Write()
        hGenPtvsEtaRECOeff.Write()
        hGenPtvsEtaDTeff.Write()
	hPtvsEtaRECOeff.Write()
	hPtvsEtaDTeff.Write()

        hGenPtvsEtaPlusRECOeff.Write()
        hGenPtvsEtaPlusDTeff.Write()
        hPtvsEtaPlusRECOeff.Write()
        hPtvsEtaPlusDTeff.Write()

        hGenPtvsEtaMinusRECOeff.Write()
        hGenPtvsEtaMinusDTeff.Write()
        hPtvsEtaMinusRECOeff.Write()
        hPtvsEtaMinusDTeff.Write()

	hEleProbeChargeRECOeff.Write()
	hEleProbeChargeDTeff.Write()
	hIMcheck.Write()
	hHTnum.Write()

	hEleGenPt.Write()
	hEleGenEta.Write()

	hEleGenPtRECOeff.Write()
	hEleGenChargeRECOeff.Write()
        hEleGenPtbarrelRECOeff.Write()
        hEleGenPtECRECOeff.Write()
	hEleGenEtaRECOeff.Write()

	hEleGenPtDTeff.Write()
	hEleGenChargeDTeff.Write()
        hEleGenPtbarrelDTeff.Write()
        hEleGenPtECDTeff.Write()
	hEleGenEtaDTeff.Write()
	hEleGenPtSDTeff.Write()
	hEleGenEtaSDTeff.Write()
	hEleGenPtMDTeff.Write()
	hEleGenEtaMDTeff.Write()
	hEleGenPtLDTeff.Write()
	hEleGenEtaLDTeff.Write()
	hEleTagPt.Write()
	hEleTagEta.Write()

	hEleProbePt.Write()
	hEleProbeEta.Write()
	hIMZ.Write()
	hIMmuZsmear.Write()
	hIMmuZ.Write()
	hprobe.Write()

	hIMZRECOeff.Write()
	hEleProbePtRECOeff.Write()
	hEleProbePtbarrelRECOeff.Write()
        hEleProbePtECRECOeff.Write()
	hEleProbeEtaRECOeff.Write()
	hIMZDTeff.Write()
	hEleProbePtDTeff.Write()
        hEleProbePtbarrelDTeff.Write()
        hEleProbePtECDTeff.Write()
	hEleProbeEtaDTeff.Write()
	hEleProbePtSDTeff.Write()
	hEleProbeEtaSDTeff.Write()
	hEleProbePtMDTeff.Write()
	hEleProbeEtaMDTeff.Write()
	hEleProbePtLDTeff.Write()
	hEleProbeEtaLDTeff.Write()

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
		
def isBaselineTrk(track, track_id):
	etaMax = 2.4
	flag = 1
	if not abs(track.Eta())< etaMax: return 0
	if (abs(track.Eta()) > 1.4442 and abs(track.Eta()) < 1.566): return 0
#		if not (track.Pt() > 15 and abs(track.Eta())< etaMax): return 0
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
