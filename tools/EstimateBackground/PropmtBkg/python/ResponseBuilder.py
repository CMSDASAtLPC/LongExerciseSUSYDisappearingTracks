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

gROOT.SetBatch()
gROOT.SetStyle('Plain')


hHTnum                          = TH1F("hHTnum","HT for number of events", 150,40,2500)
histoStyler(hHTnum,1)
hnJets                          = TH1F("hnJets", "Jet multiplicity", 8, 0, 8)
histoStyler(hnJets,1)
hHT                             = TH1F("hHT","HT", 150,40,2500)
histoStyler(hHT,1)
hMETpf                          = TH1F("hMETpf","pfMET", 150,30,1000)
histoStyler(hMETpf,1)
hnGenE                            = TH1F("hnGenE", "number of generated electrons", 4, 0, 4)
histoStyler(hnGenE,1)

hnDT                            = TH1F("hnDT", "number of disappearing tracks", 4, 0, 4)
histoStyler(hnDT,1)
hSnDT                            = TH1F("hSnDT", "number of disappearing tracks", 4, 0, 4)
histoStyler(hSnDT,1)
hMnDT                            = TH1F("hMnDT", "number of disappearing tracks", 4, 0, 4)
histoStyler(hMnDT,1)
hLnDT                            = TH1F("hLnDT", "number of disappearing tracks", 4, 0, 4)
histoStyler(hLnDT,1)
hMHT                            = TH1F("hMHT","MHT",100,40,1500)
histoStyler(hMHT,1)

hMHT                            = TH1F("hMHT","MHT",100,40,1500)
histoStyler(hMHT,1)
####
hEleGenPtRECOeff      = TH1D("hEleGenPtRECOeff", ";m [GeV] ;pt of the RECO Ele;;", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
histoStyler(hEleGenPtRECOeff,1)
hEleGenPtDTeff        = TH1D("hEleGenPtDTeff", "pt of the DT Ele", len(PtBinEdges)-1,np.asarray(PtBinEdges, 'd'))
histoStyler(hEleGenPtDTeff,1)
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


htrkrespS              = TH1D("htrkrespS","small track response", 50,-3,3.2)
histoStyler(htrkrespS,1)
htrkrespSEta1P1              = TH1D("htrkrespSEta1P1","track response", 50,-3,3.2)
histoStyler(htrkrespSEta1P1,1)
htrkrespSEta1P2              = TH1D("htrkrespSEta1P2","track response", 50,-3,3.2)
histoStyler(htrkrespSEta1P2,1)
htrkrespSEta2P1              = TH1D("htrkrespSEta2P1","track response", 50,-3,3.2)
histoStyler(htrkrespSEta2P1,1)
htrkrespSEta2P2              = TH1D("htrkrespSEta2P2","track response", 50,-3,3.2)
histoStyler(htrkrespSEta2P2,1)
htrkrespM              = TH1D("htrkrespM","medium track response", 50,-3,3.2)
histoStyler(htrkrespM,1)
htrkrespMEta1P1              = TH1D("htrkrespMEta1P1","track response", 50,-3,3.2)
histoStyler(htrkrespMEta1P1,1)
htrkrespMEta1P2              = TH1D("htrkrespMEta1P2","track response", 50,-3,3.2)
histoStyler(htrkrespMEta1P2,1)
htrkrespMEta2P1              = TH1D("htrkrespMEta2P1","track response", 50,-3,3.2)
histoStyler(htrkrespMEta2P1,1)
htrkrespMEta2P2              = TH1D("htrkrespMEta2P2","track response", 50,-3,3.2)
histoStyler(htrkrespMEta2P2,1)
htrkrespL              = TH1D("htrkrespL","long track response", 50,-3,3.2)
histoStyler(htrkrespL,1)
htrkrespLEta1P1              = TH1D("htrkrespLEta1P1","track response", 50,-3,3.2)
histoStyler(htrkrespLEta1P1,1)
htrkrespLEta1P2              = TH1D("htrkrespLEta1P2","track response", 50,-3,3.2)
histoStyler(htrkrespLEta1P2,1)
htrkrespLEta2P1              = TH1D("htrkrespLEta2P1","track response", 50,-3,3.2)
histoStyler(htrkrespLEta2P1,1)
htrkrespLEta2P2              = TH1D("htrkrespLEta2P2","track response", 50,-3,3.2)
histoStyler(htrkrespLEta2P2,1)
hmuonresp             =TH1D("hmuonresp","muon response", 50,-3,3.2)
histoStyler(hmuonresp,1)


dResponseHist = {}
for iPtBin, PtBin in enumerate(PtBinEdges[:-1]):
	for iEtaBin, EtaBin in enumerate(EtaBinEdges[:-1]):
		newHistKey = ((EtaBin,EtaBinEdges[iEtaBin + 1]),(PtBin,PtBinEdges[iPtBin + 1]))
		dResponseHist[newHistKey] = TH1D("htrkresp"+str(newHistKey),"htrkresp"+str(newHistKey), 200,-2,2)
		histoStyler(dResponseHist[newHistKey], 1)

dEleResponseHist = {}
for iPtBin, PtBin in enumerate(PtBinEdges[:-1]):
        for iEtaBin, EtaBin in enumerate(EtaBinEdges[:-1]):
                newHistKey = ((EtaBin,EtaBinEdges[iEtaBin + 1]),(PtBin,PtBinEdges[iPtBin + 1]))
                dEleResponseHist[newHistKey] = TH1D("heleresp"+str(newHistKey),"heleresp"+str(newHistKey), 200,-2,2)
                histoStyler(dEleResponseHist[newHistKey], 1)


####
options = VarParsing ('python')
options.parseArguments()

#Input File    
inputFiles = options.inputFiles
if inputFiles == []:
    print 'running on the default'
    inputFiles = ["/pnfs/desy.de/cms/tier2/store/user/sbein/NtupleHub/Production2016v2/Summer16.DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_391_RA2AnalysisTree.root"]

c=TChain("TreeMaker2/PreSelection")
x = len(inputFiles)
#c.Add(inputFiles[0])

nentries = c.GetEntries()
print "will process", nentries, "events"

#Output file   
verbosity = 1000
identifier = inputFiles[0][inputFiles[0].rfind('/')+1:].replace('.root','').replace('pMSSM12_MCMC1_','pMSSMid').replace('_step4','').replace('_miniAODSIM','').replace('nFiles1_RA2AnalysisTree','').replace('_*','').replace('*','')

identifier+='nFiles'+str(len(inputFiles))

def main():

    for f in range(0,x):
        print 'file number:', f, ':',inputFiles[f]
        c.Add(inputFiles[f])

    nentries = c.GetEntries()
    print "will process", nentries, "events"
    for ientry in range(nentries):
        if ientry%verbosity ==0:
            print 'Now processing event number', ientry
        c.GetEntry(ientry)
        weight = 1
        hHTnum.Fill(c.madHT)
#	if not (c.HT > 100): continue
#        if not(c.NJets > 1 and c.NJets < 4): continue
        flag_probe = -1
        nGenE = 0
        nDT = 0
        SnDT = 0
        MnDT = 0
        LnDT = 0
        trkTlvsum = TLorentzVector()
        trkTlvsum.SetPxPyPzE(0, 0, 0, 0)
        dtTlvsum = TLorentzVector()
        dtTlvsum.SetPxPyPzE(0, 0, 0, 0)
        
        muons = []
        for imu, muon in enumerate(c.Muons):
            if not muon.Pt() > 15: continue
            if not (abs(muon.Eta()) < 2.4): continue
            if  abs(muon.Eta()) > 1.4442 and abs(muon.Eta()) < 1.566: continue
            muons.append(muon)
        if not len(muons)==0: continue

        basicTracks = []
        for itrack, track in enumerate(c.tracks):
            if not isBaselineTrack(track, itrack): continue
            basicTracks.append(track)
        
        for igen, gen in enumerate(c.GenParticles):
            drsmall = 0.2
            drsmal  = 0.2
            idtrk   = -1
            idlep   = -1

            if not (gen.Pt() > 3 and abs(gen.Eta()) < 2.4): continue
            if not (abs(c.GenParticles_PdgId[igen]) == 11 and c.GenParticles_Status[igen] == 1): continue
            if (abs(gen.Eta()) > 1.4442 and abs(gen.Eta()) < 1.566) : continue
            nGenE += 1

            for im, m in enumerate(c.Electrons):
                if (abs(m.Eta()) < 1.566 and abs(m.Eta()) > 1.4442): continue        
                if not (m.Pt() > 10 and abs(m.Eta()) < 2.4): continue
		if not c.Electrons_passIso[im]: continue
                drBig4Trk = 9999
                for trk in basicTracks:
                    drTrk = trk.DeltaR(c.Electrons[im])
                    if drTrk<drBig4Trk:
                        drBig4Trk = drTrk
                        if drTrk<0.01: break
                if not drBig4Trk<0.01: continue
                
                dr = gen.DeltaR(m)

                if dr < drsmall:
                    drsmall = dr
                    idlep   = im
#            print gen.Eta()
            if drsmall < .005:
                hEleGenPtRECOeff.Fill(c.Electrons[idlep].Pt(), weight)
                hEleGenEtaRECOeff.Fill(abs(c.Electrons[idlep].Eta()), weight)
                hmuonresp.Fill(math.log10(c.Electrons[idlep].Pt()/gen.Pt()),weight)
                for histkey in  dEleResponseHist:
                    if abs(c.Electrons[idlep].Eta()) > histkey[0][0] and abs(c.Electrons[idlep].Eta()) < histkey[0][1] and gen.Pt() > histkey[1][0] and min(gen.Pt(),309.999) < histkey[1][1]:
                            fillth1(dEleResponseHist[histkey],math.log10(c.Electrons[idlep].Pt()/gen.Pt()),weight)




            for itrk, trk in enumerate(c.tracks):
                if (abs(trk.Eta()) < 1.566 and abs(trk.Eta()) > 1.4442): continue            
                if not (trk.Pt() > 3 and abs(trk.Eta()) < 2.4): continue
                if not isBaselineTrack(trk, itrk): continue
                if not isDisappearingTrack(trk, itrk): continue
                dr = gen.DeltaR(trk)
                if dr < drsmal:
                    drsmal = dr
                    idtrk   = itrk
                    trkTlvsum = trk
            PtDivision = 250
            if drsmal < 0.005:
                dtTlvsum = trkTlvsum
                nDT +=1
                hEleGenPtDTeff.Fill(c.tracks[idtrk].Pt(), weight)
                hEleGenEtaDTeff.Fill(abs(c.tracks[idtrk].Eta()), weight)
   #             htrkresp.Fill(math.log10(c.tracks[idtrk].Pt()/gen.Pt()),weight)
                
                for histkey in  dResponseHist:
                    if abs(c.tracks[idtrk].Eta()) > histkey[0][0] and abs(c.tracks[idtrk].Eta()) < histkey[0][1] and gen.Pt() > histkey[1][0] and min(gen.Pt(),309.999) < histkey[1][1]:
			    fillth1(dResponseHist[histkey],math.log10(c.tracks[idtrk].Pt()/gen.Pt()),weight)                

                length = determineSML(dtTlvsum, idtrk)
                if (length == 1):
                    SnDT += 1
                    htrkrespS.Fill(math.log10(c.tracks[idtrk].Pt()/gen.Pt()),weight)
                    hEleGenPtSDTeff.Fill(c.tracks[idtrk].Pt(), weight)
                    hEleGenEtaSDTeff.Fill(abs(c.tracks[idtrk].Eta()), weight)

                    if abs(c.tracks[idtrk].Eta()) < 1.4442:
                        if gen.Pt() < PtDivision:
                            htrkrespSEta1P1.Fill(math.log10(c.tracks[idtrk].Pt()/gen.Pt()),weight)
                        elif gen.Pt() > PtDivision:
                            htrkrespSEta1P2.Fill(math.log10(c.tracks[idtrk].Pt()/gen.Pt()),weight)
                    if abs(c.tracks[idtrk].Eta()) > 1.566:
                        if gen.Pt() < PtDivision:
                            htrkrespSEta2P1.Fill(math.log10(c.tracks[idtrk].Pt()/gen.Pt()),weight)
                        elif gen.Pt() > PtDivision:
                            htrkrespSEta2P2.Fill(math.log10(c.tracks[idtrk].Pt()/gen.Pt()),weight)

                if (length == 2):
                    MnDT += 1
                    htrkrespM.Fill(math.log10(c.tracks[idtrk].Pt()/gen.Pt()),weight)
                    hEleGenPtMDTeff.Fill(c.tracks[idtrk].Pt(), weight)
                    hEleGenEtaMDTeff.Fill(abs(c.tracks[idtrk].Eta()), weight)

                    if abs(c.tracks[idtrk].Eta()) < 1.4442:
                        if gen.Pt() < PtDivision:
                            htrkrespMEta1P1.Fill(math.log10(c.tracks[idtrk].Pt()/gen.Pt()),weight)
                        elif gen.Pt() > PtDivision:
                            htrkrespMEta1P2.Fill(math.log10(c.tracks[idtrk].Pt()/gen.Pt()),weight)
                    if abs(c.tracks[idtrk].Eta()) > 1.566:
                        if gen.Pt() < PtDivision:
                            htrkrespMEta2P1.Fill(math.log10(c.tracks[idtrk].Pt()/gen.Pt()),weight)
                        elif gen.Pt() > PtDivision:
                            htrkrespMEta2P2.Fill(math.log10(c.tracks[idtrk].Pt()/gen.Pt()),weight)

                if (length == 3):
                    LnDT += 1
                    htrkrespL.Fill(math.log10(c.tracks[idtrk].Pt()/gen.Pt()),weight)
                    hEleGenPtLDTeff.Fill(c.tracks[idtrk].Pt(), weight)
                    hEleGenEtaLDTeff.Fill(abs(c.tracks[idtrk].Eta()), weight)

                    if abs(c.tracks[idtrk].Eta()) < 1.4442:
                        if gen.Pt() < PtDivision:
                            htrkrespLEta1P1.Fill(math.log10(c.tracks[idtrk].Pt()/gen.Pt()),weight)
                        elif gen.Pt() > PtDivision:
                            htrkrespLEta1P2.Fill(math.log10(c.tracks[idtrk].Pt()/gen.Pt()),weight)
                    if abs(c.tracks[idtrk].Eta()) > 1.566:
                        if gen.Pt() < PtDivision:
                            htrkrespLEta2P1.Fill(math.log10(c.tracks[idtrk].Pt()/gen.Pt()),weight)
                        elif gen.Pt() > PtDivision:
                            htrkrespLEta2P2.Fill(math.log10(c.tracks[idtrk].Pt()/gen.Pt()),weight)

        hnGenE.Fill(nGenE, weight)
        hnDT.Fill(nDT, weight)
        #print nDT
        if (nDT > 0):
            #print 'after if', nDT
            hSnDT.Fill(SnDT, weight)
            hMnDT.Fill(MnDT, weight)
            hLnDT.Fill(LnDT, weight)
            hHT.Fill(c.HT, weight)
            hnJets.Fill(c.NJets, weight)
            hMETpf.Fill(c.MET, weight)
            hMHT.Fill(c.MHT, weight)

    ftem = TFile('BinnedTemplate_Hists'+identifier+'.root','recreate')
    ftem.cd()

    for histkey in  dResponseHist: dResponseHist[histkey].Write()
    for histkey in  dEleResponseHist: dEleResponseHist[histkey].Write()
    htrkrespS.Write()
    htrkrespSEta1P1.Write()
    htrkrespSEta1P2.Write()
    htrkrespSEta2P1.Write()
    htrkrespSEta2P2.Write()
    htrkrespM.Write()
    htrkrespMEta1P1.Write()
    htrkrespMEta1P2.Write()
    htrkrespMEta2P1.Write()
    htrkrespMEta2P2.Write()
    htrkrespL.Write()
    htrkrespLEta1P1.Write()
    htrkrespLEta1P2.Write()
    htrkrespLEta2P1.Write()
    htrkrespLEta2P2.Write()
    hmuonresp.Write()
    ftem.Close()
    print "file:", ftem, "created."
    


def determineSML(sp_chi, sp_chi_id):
    S = 0
    M = 0
    L = 0
    if c.tracks_pixelLayersWithMeasurement[sp_chi_id] == c.tracks_trackerLayersWithMeasurement[sp_chi_id]: S = 1
    if c.tracks_trackerLayersWithMeasurement[sp_chi_id] < 7 and c.tracks_pixelLayersWithMeasurement[sp_chi_id] < c.tracks_trackerLayersWithMeasurement[sp_chi_id]: M = 2
    if c.tracks_trackerLayersWithMeasurement[sp_chi_id] > 6 and c.tracks_pixelLayersWithMeasurement[sp_chi_id] < c.tracks_trackerLayersWithMeasurement[sp_chi_id]: L = 3
    return S+M+L

def isBaselineTrack(track, track_id):
    flag = 1
#    if not (track.Pt()> 10 and abs(track.Eta())<2.4): return 0
    if abs(track.Eta()) < 1.566 and abs(track.Eta()) > 1.4442: return 0
    if not bool(c.tracks_trackQualityHighPurity[track_id]) : return 0
    if not (c.tracks_ptError[track_id]/(track.Pt()*track.Pt()) < 0.2): return 0
    if not c.tracks_dxyVtx[track_id] < 0.02: return 0
    if not c.tracks_dzVtx[track_id] < 0.05 : return 0
    if not c.tracks_trkRelIso[track_id] < 0.2: return 0
    if not c.tracks_trkRelIso[track_id]*track.Pt() < 10: return 0
    if not (c.tracks_trackerLayersWithMeasurement[track_id] >= 2 and c.tracks_nValidTrackerHits[track_id] >= 2): return 0
    if not c.tracks_nMissingInnerHits[track_id]==0: return 0
    return flag

def isDisappearingTrack(track, track_id):
    S = 0
    M = 0
    L = 0
    flag = 1
    if c.tracks_pixelLayersWithMeasurement[track_id] == c.tracks_trackerLayersWithMeasurement[track_id]: S = 1
    if c.tracks_trackerLayersWithMeasurement[track_id] < 7 and c.tracks_pixelLayersWithMeasurement[track_id] < c.tracks_trackerLayersWithMeasurement[track_id] : M = 2
    if c.tracks_trackerLayersWithMeasurement[track_id] > 6 and c.tracks_pixelLayersWithMeasurement[track_id] < c.tracks_trackerLayersWithMeasurement[track_id]: L = 3
#    if track.Pt() < 15: return 0
    if c.tracks_dxyVtx[track_id] > 0.02 and S == 1: return 0
    if c.tracks_dxyVtx[track_id] > 0.01 and S == 0: return 0
    if c.tracks_neutralPtSum[track_id] > 10 or ((c.tracks_neutralPtSum[track_id]/track.Pt()) > 0.1): return 0
    if c.tracks_chargedPtSum[track_id] > 10 or ((c.tracks_chargedPtSum[track_id]/track.Pt()) > 0.1): return 0
    if not c.tracks_passPFCandVeto[track_id]:return 0
    if c.tracks_nMissingOuterHits[track_id] < 2 and S == 0: return 0
    if c.tracks_ptError[track_id]/(track.Pt()*track.Pt()) > 0.2 and S == 1: return 0
    if c.tracks_ptError[track_id]/(track.Pt()*track.Pt()) > 0.05 and M == 2: return 0
    if c.tracks_ptError[track_id]/(track.Pt()*track.Pt()) > 0.005 and L == 3: return 0
    return flag

main()
