import sys
import time
import numpy as np
from ROOT import *
from utils import *
from distracklibs import *
from glob import glob
from random import shuffle
import random
BTAG_CSV = 0.8838#2017
BTAG_CSV = 0.8484#2016
 
gROOT.SetBatch()
gROOT.SetStyle('Plain')
SmearLeps = False

verbose = False
defaultInfile = "/eos/uscms//store/user/lpcsusyhad/sbein/cmsdas19/Ntuples/Summer16.WJetsToLNu_HT-800To1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_25_RA2AnalysisTree.root"
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


############VARIATIONS
useGenKappa = False #aka TrueFit


#####################

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

mZ = 91
genMatchEverything = False
RelaxGenKin = True
ClosureMode = True #false means run as if real data

isdata = 'Run20' in fnamekeyword
if 'Run2016' in fnamekeyword or 'Summer16' in fnamekeyword:
    phase = 0
else:
    phase = 1


if isdata: ClosureMode = False


identifier = fnamekeyword
print 'Identifier', identifier


newfname = 'PromptBkgHists_'+identifier+'.root'

if genMatchEverything: newfname = newfname.replace('.root','Truth.root')
fnew_ = TFile(newfname,'recreate')
print 'Will write results to', newfname

hHt = TH1F('hHt','hHt',100,0,3000)
hHtWeighted = TH1F('hHtWeighted','hHtWeighted',100,0,3000)


lepPtCut = 30

inf = 999999

regionCuts = {}
varlist_                         = ['Ht',    'Mht',     'NJets', 'BTags', 'NTags', 'NPix', 'NPixStrips', 'MinDPhiMhtJets', 'NElectrons', 'NMuons', 'TrkPt',       'TrkEta','BinNumber']
regionCuts['NoCuts']             = [(0,inf), (0.0,inf), (0,inf), (0,inf), (1,inf), (0,inf), (0,inf),     (0.0,inf),        (0,inf),     (0,inf),  (lepPtCut,inf), (0,2.4), (-1,inf)]
#regionCuts['LowMhtBaseline']     = [(0,inf), (150,inf), (1,inf), (0,inf), (1,inf), (0,inf), (0,inf),     (0.3,inf),        (0,0  ),     (0,0),    (lepPtCut,inf), (0,2.4), (-1,inf)]
regionCuts['Baseline']           = [(0,inf), (250,inf), (1,inf), (0,inf), (1,inf), (0,inf), (0,inf),     (0.3,inf),        (0,0  ),     (0,0),    (lepPtCut,inf), (0,2.4), (-1,inf)]
regionCuts['TtbarCtrEl']         = [(0,inf), (100,300), (2,inf), (1,5),   (1,1),   (0,inf), (0,inf),     (0.3,inf),        (1,1),       (0,0),    (lepPtCut,inf), (0,2.4), (-1,inf)]
regionCuts['TtbarCtrMu']         = [(0,inf), (100,300), (2,inf), (1,5),   (1,1),   (0,inf), (0,inf),     (0.3,inf),        (0,0),       (1,1),    (lepPtCut,inf), (0,2.4), (-1,inf)]

#regionCuts['LowMhtBasePixOnly']  = [(0,inf), (150,inf), (1,inf), (0,inf), (1,inf), (1,inf), (0,inf),     (0.3,inf),        (0,0  ),     (0,0),    (lepPtCut,inf), (0,2.4), (-1,inf)]
regionCuts['BaselinePixOnly']    = [(0,inf), (250,inf), (1,inf), (0,inf), (1,inf), (1,inf), (0,inf),     (0.3,inf),        (0,0  ),     (0,0),    (lepPtCut,inf), (0,2.4), (-1,inf)]
regionCuts['TtbarCtrElPixOnly']  = [(0,inf), (100,300), (2,inf), (1,5),   (1,1),   (1,inf), (0,inf),     (0.3,inf),        (1,1),       (0,0),    (lepPtCut,inf), (0,2.4), (-1,inf)]
regionCuts['TtbarCtrMuPixOnly']  = [(0,inf), (100,300), (2,inf), (1,5),   (1,1),   (1,inf), (0,inf),     (0.3,inf),        (0,0),       (1,1),    (lepPtCut,inf), (0,2.4), (-1,inf)]

#regionCuts['LowMhtBasePixAndStrips']=[(0,inf),(150,inf),(1,inf), (0,inf), (1,inf), (0,inf), (1,inf),     (0.3,inf),        (0,0  ),     (0,0),    (lepPtCut,inf), (0,2.4), (-1,inf)]
regionCuts['BaselinePixAndStrips']  =[(0,inf),(250,inf),(1,inf), (0,inf), (1,inf), (0,inf), (1,inf),     (0.3,inf),        (0,0  ),     (0,0),    (lepPtCut,inf), (0,2.4), (-1,inf)]
regionCuts['TtbarCtrElPixAndStrips']=[(0,inf),(100,300),(2,inf), (1,5),   (1,1),   (0,inf), (1,inf),     (0.3,inf),        (1,1),       (0,0),    (lepPtCut,inf), (0,2.4), (-1,inf)]
regionCuts['TtbarCtrMuPixAndStrips']=[(0,inf),(100,300),(2,inf), (1,5),   (1,1),   (0,inf), (1,inf),     (0.3,inf),        (0,0),       (1,1),    (lepPtCut,inf), (0,2.4), (-1,inf)]


indexVar = {}
for ivar, var in enumerate(varlist_): indexVar[var] = ivar
histoStructDict = {}
for region in regionCuts:
    for var in varlist_:
        histname = 'El'+region+'_'+var
        histoStructDict[histname] = mkHistoStruct(histname)
        histname = 'Mu'+region+'_'+var
        histoStructDict[histname] = mkHistoStruct(histname)        
        histname = 'Fake'+region+'_'+var
        histoStructDict[histname] = mkHistoStruct(histname)  
                   
                
binnumbers = {}
listagain = ['Ht',  'Mht',    'NJets','BTags','NTags','NPix', 'NPixStrips', 'MinDPhiMhtJets', 'NElectrons', 'NMuons', 'TrkPt','TrkEta','BinNumber']
binnumbers[((0,inf),(250,400),(1,1),  (0,inf),(1,1),  (0,0),  (1,1))] = 1
binnumbers[((0,inf),(250,400),(2,5),  (0,0),  (1,1),  (0,0),  (1,1))] = 2
binnumbers[((0,inf),(250,400),(2,5),  (1,5),  (1,1),  (0,0),  (1,1))] = 3
binnumbers[((0,inf),(250,400),(6,inf),(0,0),  (1,1),  (0,0),  (1,1))] = 4
binnumbers[((0,inf),(250,400),(6,inf),(1,inf),(1,1),  (0,0),  (1,1))] = 5
binnumbers[((0,inf),(400,700),(1,1),  (0,inf),(1,1),  (0,0),  (1,1))] = 6
binnumbers[((0,inf),(400,700),(2,5),  (0,0),  (1,1),  (0,0),  (1,1))] = 7
binnumbers[((0,inf),(400,700),(2,5),  (1,5),  (1,1),  (0,0),  (1,1))] = 8
binnumbers[((0,inf),(400,700),(6,inf),(0,0),  (1,1),  (0,0),  (1,1))] = 9
binnumbers[((0,inf),(400,700),(6,inf),(1,inf),(1,1),  (0,0),  (1,1))] = 10
binnumbers[((0,inf),(700,inf),(1,1),  (0,inf),(1,1),  (0,0),  (1,1))] = 11
binnumbers[((0,inf),(700,inf),(2,5),  (0,0),  (1,1),  (0,0),  (1,1))] = 12
binnumbers[((0,inf),(700,inf),(2,5),  (1,5),  (1,1),  (0,0),  (1,1))] = 13
binnumbers[((0,inf),(700,inf),(6,inf),(0,0),  (1,1),  (0,0),  (1,1))] = 14
binnumbers[((0,inf),(700,inf),(6,inf),(1,inf),(1,1),  (0,0),  (1,1))] = 15
binnumbers[((0,inf),(250,400),(1,1),  (0,inf),(1,1),  (1,1),  (0,0))] = 16
binnumbers[((0,inf),(250,400),(2,5),  (0,0),  (1,1),  (1,1),  (0,0))] = 17
binnumbers[((0,inf),(250,400),(2,5),  (1,5),  (1,1),  (1,1),  (0,0))] = 18
binnumbers[((0,inf),(250,400),(6,inf),(0,0),  (1,1),  (1,1),  (0,0))] = 19
binnumbers[((0,inf),(250,400),(6,inf),(1,inf),(1,1),  (1,1),  (0,0))] = 20
binnumbers[((0,inf),(400,700),(1,1),  (0,inf),(1,1),  (1,1),  (0,0))] = 21
binnumbers[((0,inf),(400,700),(2,5),  (0,0),  (1,1),  (1,1),  (0,0))] = 22
binnumbers[((0,inf),(400,700),(2,5),  (1,5),  (1,1),  (1,1),  (0,0))] = 23
binnumbers[((0,inf),(400,700),(6,inf),(0,0),  (1,1),  (1,1),  (0,0))] = 24
binnumbers[((0,inf),(400,700),(6,inf),(1,inf),(1,1),  (1,1),  (0,0))] = 25
binnumbers[((0,inf),(700,inf),(1,1),  (0,inf),(1,1),  (1,1),  (0,0))] = 26
binnumbers[((0,inf),(700,inf),(2,5),  (0,0),  (1,1),  (1,1),  (0,0))] = 27
binnumbers[((0,inf),(700,inf),(2,5),  (1,5),  (1,1),  (1,1),  (0,0))] = 28
binnumbers[((0,inf),(700,inf),(6,inf),(0,0),  (1,1),  (1,1),  (0,0))] = 29
binnumbers[((0,inf),(700,inf),(6,inf),(1,inf),(1,1),  (1,1),  (0,0))] = 30
binnumbers[((0,inf),(250,400),(1,inf),(0,inf),(2,inf),(0,inf),(0,inf))]=31
binnumbers[((0,inf),(400,inf),(1,inf),(0,inf),(2,inf),(0,inf),(0,inf))]=32

def getBinNumber(fv):
    for binkey in binnumbers:
        foundbin = True
        for iwindow, window in enumerate(binkey):
            if not (fv[iwindow]>=window[0] and fv[iwindow]<=window[1]): foundbin = False
        if foundbin: return binnumbers[binkey]
    return -1

nentries = c.GetEntries()
#nentries = 100

c.Show(0)
#nentries = 5

def selectionFeatureVector(fvector, regionkey='', omitcuts=''):
    iomits = []
    for cut in omitcuts.split('Vs'): iomits.append(indexVar[cut])
    for i, feature in enumerate(fvector):
        if i in iomits: continue
        if not (feature>=regionCuts[regionkey][i][0] and feature<=regionCuts[regionkey][i][1]):
            return False
    return True


if 'TTJets_TuneCUET' in fnamekeyword:  madranges = [(0,600)]
elif 'TTJets_HT' in fnamekeyword: madranges = [(600,inf)]
elif 'WJetsToLNu_TuneCUET' in fnamekeyword: madranges = [(0, 100), (600,800)]
elif 'WJetsToLNu_HT' in fnamekeyword: madranges = [(100, inf)]
else: madranges = [(0, inf)]


#pause()
#fname = '/nfs/dust/cms/user/singha/LLCh/BACKGROUNDII/CMSSW_8_0_20/src/MCTemplatesBinned/BinnedTemplatesIIDY_WJ_TT.root'
if isdata: fsmearname = 'usefulthings/DataDrivenSmear_2016Data.root'
else: fsmearname = 'usefulthings/DataDrivenSmear_2016MC.root'
fSmear  = TFile(fsmearname)
fMask = TFile('usefulthings/Masks.root')
if 'Run2016' in fnamekeyword: hMask = fMask.Get('hEtaVsPhiDT_maskRun2016')
else: hMask = fMask.Get('hEtaVsPhiDTRun2016')

dResponseHist = {}
for iPtBinEdge, PtBinEdge in enumerate(PtBinEdgesForSmearing[:-1]):
    for iEtaBinEdge, EtaBinEdge_ in enumerate(EtaBinEdgesForSmearing[:-1]):
        newHistKey = ((EtaBinEdge_,EtaBinEdgesForSmearing[iEtaBinEdge + 1]),(PtBinEdge,PtBinEdgesForSmearing[iPtBinEdge + 1]))
        dResponseHist[newHistKey] = fSmear.Get("htrkresp"+str(newHistKey))

print 'dResponseHist', dResponseHist
def getSmearFactor(Eta, Pt, Draw = False):
    for histkey in  dResponseHist:
        if abs(Eta) > histkey[0][0] and abs(Eta) < histkey[0][1] and Pt > histkey[1][0] and Pt < histkey[1][1]:
            if SmearLeps: return 10**(dResponseHist[histkey].GetRandom())
            else: return 1.0
    print 'returning 1', Eta, Pt, dResponseHist
    return 1


readerShort = TMVA.Reader()
pixelXml = 'usefulthings/cmssw8-newpresel3-200-4-short-updated/weights/TMVAClassification_BDT.weights.xml'
prepareReaderShort(readerShort, pixelXml)
readerLong = TMVA.Reader()
trackerXml = 'usefulthings/cmssw8-newpresel2-200-4-medium-updated/weights/TMVAClassification_BDT.weights.xml'
prepareReaderLong(readerLong, trackerXml)


if isdata: 
    fileKappaPixOnly = 'usefulthings/KappaRun2016_PixOnly.root'
    fileKappaPixAndStrips = 'usefulthings/KappaRun2016_PixAndStrips.root'    
else: 
    fileKappaPixOnly = 'usefulthings/KappaDYJets_PixOnly.root'
    fileKappaPixAndStrips = 'usefulthings/KappaDYJets_PixAndStrips.root'  
    fileKappaPixOnlyGen = 'usefulthings/KappaWJets_PixOnly.root'
    fileKappaPixAndStripsGen = 'usefulthings/KappaWJets_PixAndStrips.root' 
    fKappaPixOnlyGen  = TFile(fileKappaPixOnly)
    fKappaPixAndStripsGen  = TFile(fileKappaPixAndStrips)     
      

print 'using file', fileKappaPixOnly
fKappaPixOnly  = TFile(fileKappaPixOnly)
fKappaPixAndStrips  = TFile(fileKappaPixAndStrips)
#KappaMap = fKappaPixOnly.Get("kappaGenPtvsEta")##kappaPtvsEta

fElProbePt_KappasPixOnly = {}
fGenElProbePt_KappasPixOnly = {}
fMuProbePt_KappasPixOnly = {}
fGenMuProbePt_KappasPixOnly = {}

fElProbePt_KappasPixAndStrips = {}
fGenElProbePt_KappasPixAndStrips = {}
fMuProbePt_KappasPixAndStrips = {}
fGenMuProbePt_KappasPixAndStrips = {}


for iEtaBin, EtaBin in enumerate(EtaBinEdges[:-1]):
    etakey = (EtaBin,EtaBinEdges[iEtaBin + 1])
    specialpart = '_eta'+str(etakey).replace('(','').replace(')','').replace(', ','to')
    oldNumName = "hElProbePtDT"+specialpart+"_num"
    newKappaName = oldNumName.replace('_num','').replace('DT','Kappa')
    newKappaFuncName = 'f1'+newKappaName
    fElProbePt_KappasPixOnly[etakey] = fKappaPixOnly.Get(newKappaFuncName).Clone()
    fElProbePt_KappasPixAndStrips[etakey] = fKappaPixAndStrips.Get(newKappaFuncName).Clone()    
    oldGenNumName = "hGenElProbePtDT"+specialpart+"_num"
    newGenKappaName = oldGenNumName.replace('_num','').replace('DT','Kappa')
    newGenKappaFuncName = 'f1'+newGenKappaName
    fGenElProbePt_KappasPixOnly[etakey] = fKappaPixOnlyGen.Get(newGenKappaFuncName).Clone()
    fGenElProbePt_KappasPixAndStrips[etakey] = fKappaPixAndStripsGen.Get(newGenKappaFuncName).Clone()    
    oldNumName = "hMuProbePtDT"+specialpart+"_num"
    newKappaName = oldNumName.replace('_num','').replace('DT','Kappa')
    newKappaFuncName = 'f1'+newKappaName
    fMuProbePt_KappasPixOnly[etakey] = fKappaPixOnly.Get(newKappaFuncName).Clone()
    fMuProbePt_KappasPixAndStrips[etakey] = fKappaPixAndStrips.Get(newKappaFuncName).Clone()    
    oldGenNumName = "hGenMuProbePtDT"+specialpart+"_num"
    newGenKappaName = oldGenNumName.replace('_num','').replace('DT','Kappa')
    newGenKappaFuncName = 'f1'+newGenKappaName
    fGenMuProbePt_KappasPixOnly[etakey] = fKappaPixOnlyGen.Get(newGenKappaFuncName).Clone()
    fGenMuProbePt_KappasPixAndStrips[etakey] = fKappaPixAndStripsGen.Get(newGenKappaFuncName).Clone()    
        
if useGenKappa: 
    kappadictElPixOnly = fGenElProbePt_KappasPixOnly
    kappadictMuPixOnly = fGenMuProbePt_KappasPixOnly    
    
    kappadictElPixAndStrips = fGenElProbePt_KappasPixAndStrips
    kappadictMuPixAndStrips = fGenMuProbePt_KappasPixAndStrips        
else: 
    kappadictElPixOnly = fElProbePt_KappasPixOnly
    kappadictMuPixOnly = fMuProbePt_KappasPixOnly  
    
    kappadictElPixAndStrips = fElProbePt_KappasPixAndStrips
    kappadictMuPixAndStrips = fMuProbePt_KappasPixAndStrips        


dKappaBinList = {}
for iPtBinEdge, PtBinEdge in enumerate(PtBinEdges[:-1]):
        for iEtaBinEdge, EtaBinEdge in enumerate(EtaBinEdges[:-1]):
                newHistKey = ((EtaBinEdge,EtaBinEdges[iEtaBinEdge + 1]),(PtBinEdge,PtBinEdges[iPtBinEdge + 1]))
                dKappaBinList[newHistKey] = [iPtBinEdge+1,iEtaBinEdge+1]
                
                
def fetchKappa(Eta, Pt, KappaDict=fGenElProbePt_KappasPixOnly):
    for iEtaBin, EtaBin in enumerate(EtaBinEdges[:-1]):
        etakey = (EtaBin,EtaBinEdges[iEtaBin + 1])
        if abs(Eta) >= etakey[0] and abs(Eta) <= etakey[1]:
            #return 1
            kappa = KappaDict[etakey].Eval(Pt)
            #print 'got an', kappa
            return kappa
    print etakey, Eta
    print 'didnt get anything meaningful', Eta, Pt
    return 1
    
    
import time
t1 = time.time()
i0=0

triggerIndecesV2 = {}
#triggerIndecesV2['SingleEl'] = [36,39]
#triggerIndecesV2['SingleEl45'] = [41]
triggerIndecesV2['SingleElCocktail'] = [14, 15, 16, 17, 18, 19, 20, 21]
#triggerIndecesV2['MhtMet6pack'] = [108,110,114,123,124,125,126,128,129,130,131,132,133,122,134]#123
#triggerIndecesV2["SingleMu"] = [48,50,52,55,63]
triggerIndecesV2["SingleMuCocktail"] = [24,25,26,27,28,30,31,32]
#triggerIndecesV2["SinglePho"] = [139]
#triggerIndecesV2["SinglePhoWithHt"] = [138, 139,141,142,143]
#triggerIndecesV2['HtTrain'] = [67,68,69,72,73,74,80,84,88,91,92,93,95,96,99,102,103,104]

triggerIndeces = triggerIndecesV2

def PassTrig(c,trigname):
    for trigidx in triggerIndeces[trigname]: 
        if c.TriggerPass[trigidx]==1: 
            return True
    return False
    
verbosity = 10000
print nentries, 'evets to be analyzed'
for ientry in range(nentries):
    if verbose:
        if not ientry in [8841]: continue
    if ientry%verbosity==0:
        print 'now processing event number', ientry, 'of', nentries
        if ientry==0: 
            for itrig, trigname in enumerate(c.TriggerNames):
                print itrig, trigname, c.TriggerPass[itrig], c.TriggerPrescales[itrig]
        
    if verbose: print 'getting entry', ientry
    c.GetEntry(ientry) 
    hHt.Fill(c.HT)
    if isdata: weight = 1
    else: weight = c.CrossSection
    hHtWeighted.Fill(c.HT,weight)
    
    
    if not isdata:
      isValidHtRange = False
      for madrange in madranges:
        if (c.madHT>madrange[0] and c.madHT<madrange[1]):
            isValidHtRange = True
            break 
      if not isValidHtRange: continue
    
    
    if ClosureMode:
        genels = []
        genmus = []
        for igp, gp in enumerate(c.GenParticles):
            if not gp.Pt()>5: continue
            if not abs(gp.Eta())<2.4: continue
            if not (abs(gp.Eta())<1.445 or abs(gp.Eta())>1.56): continue    
            if not c.GenParticles_Status[igp] == 1: continue        
            #if not abs(c.GenParticles_ParentId[igp]) == 24: continue
            if abs(c.GenParticles_PdgId[igp])==11: genels.append(gp)
            if abs(c.GenParticles_PdgId[igp])==13: genmus.append(gp)            
        #if genMatchEverything:
        #    if not len(genels)==1: continue
    else: genels, genmus = [], []
        
    if isdata:
        if not (PassTrig(c, 'SingleElCocktail') or PassTrig(c, 'SingleMuCocktail')): continue
        
    if not c.CaloMET/c.MET<5.0: continue
    #if not c.JetID: continue
    
    
    if verbose: "print test gen electron"
    muons = []        
    for imu, muon in enumerate(c.Muons):
        if not muon.Pt()>10: continue
        #if abs(muon.Eta()) < 1.566 and abs(muon.Eta()) > 1.4442: continue
        if not abs(muon.Eta())<2.4: continue    
        muons.append([muon,c.Muons_charge[imu]])
    #if not len(muons)==0: continue    
    if verbose: "print test muon"
    basicTracks = []
    disappearingTracks = []    
    nShort, nLong = 0, 0
    for itrack, track in enumerate(c.tracks):
        if not track.Pt() > 10 : continue
        if not abs(track.Eta()) < 2.4: continue
        if  not (abs(track.Eta()) > 1.566 or abs(track.Eta()) < 1.4442): continue
        if not isBaselineTrack(track, itrack, c, hMask): continue
        basicTracks.append([track,c.tracks_charge[itrack], itrack])
        if not (track.Pt() > lepPtCut and track.Pt()<2499): continue        
        dtstatus = isDisappearingTrack_(track, itrack, c, readerShort, readerLong)
        if dtstatus==0: continue
        drlep = 99
        passeslep = True
        for ilep, lep in enumerate(list(c.Electrons)+list(c.Muons)): 
            drlep = min(drlep, lep.DeltaR(track))
            if drlep<0.01: 
                passeslep = False
                break            
        if not passeslep: continue        
        if verbose: "we be here"
        #print 'found disappearing track w pT =', track.Pt() 
        if dtstatus==1: nShort+=1
        if dtstatus==2: nLong+=1         
        disappearingTracks.append([track,dtstatus])
        
    
    SmearedElectrons = []
    RecoElectrons = []
    for iel, ele in enumerate(c.Electrons):
        if verbose: print ientry, iel,'ele with Pt' , ele.Pt()
        if (abs(ele.Eta()) < 1.566 and abs(ele.Eta()) > 1.4442): continue
        if not abs(ele.Eta())<2.4: continue
        if verbose: print 'passed eta and Pt'
        if not c.Electrons_passIso[iel]: continue
        if not c.Electrons_mediumID[iel]: continue
        drmin = inf
        matchedTrk = TLorentzVector()
        for trk in basicTracks:
            drTrk = trk[0].DeltaR(ele)
            if drTrk<drmin:
                if not c.tracks_nMissingOuterHits[trk[2]]==0: continue
                drmin = drTrk
                matchedTrk = trk
                if drTrk<0.01: 
                    break
        if not drmin<0.01: continue
        if ele.Pt()>lepPtCut: RecoElectrons.append([ele, c.Electrons_charge[iel]])
        smear = getSmearFactor(abs(matchedTrk[0].Eta()), min(matchedTrk[0].Pt(),299.999))
        smearedEl = TLorentzVector()
        smearedEl.SetPtEtaPhiE(0, 0, 0, 0)        
        smearedEl.SetPtEtaPhiE(smear*matchedTrk[0].Pt(),matchedTrk[0].Eta(),matchedTrk[0].Phi(),smear*matchedTrk[0].E())
        if not (smearedEl.Pt()>lepPtCut and smearedEl.Pt()<2499): continue
        SmearedElectrons.append([smearedEl,c.Electrons_charge[iel]])
        #print 'a lovely ele', ele.Pt(), smearedEle.Pt()
        
        
    SmearedMuons = []
    RecoMuons = []
    for ilep, mu in enumerate(c.Muons):
        if verbose: print ientry, ilep,'mu with Pt' , mu.Pt()
        if (abs(mu.Eta()) < 1.566 and abs(mu.Eta()) > 1.4442): continue
        if not abs(mu.Eta())<2.4: continue
        if verbose: print 'passed eta and Pt'
        if not c.Muons_passIso[ilep]: continue
        drmin = inf
        matchedTrk = TLorentzVector()
        for trk in basicTracks:
            drTrk = trk[0].DeltaR(mu)
            if drTrk<drmin:
                if not c.tracks_nMissingOuterHits[trk[2]]==0: continue
                drmin = drTrk
                matchedTrk = trk
                if drTrk<0.01: 
                    break
        if not drmin<0.01: continue
        if mu.Pt()>lepPtCut: RecoMuons.append([mu,c.Muons_charge[ilep]])    
        smear = getSmearFactor(abs(matchedTrk[0].Eta()), min(matchedTrk[0].Pt(),299.999))
        smearedMu = TLorentzVector()
        smearedMu.SetPtEtaPhiE(0, 0, 0, 0)        
        smearedMu.SetPtEtaPhiE(smear*matchedTrk[0].Pt(),matchedTrk[0].Eta(),matchedTrk[0].Phi(),smear*matchedTrk[0].E())
        if not (smearedMu.Pt()>lepPtCut and smearedMu.Pt()<2499): continue
        SmearedMuons.append([smearedMu,c.Muons_charge[ilep]])    


    singleElEvent_ = len(SmearedElectrons) >=1
    singleMuEvent_ = len(SmearedMuons) >=1    
    presentDisTrkEvent = len(disappearingTracks) >=1# and len(SmearedElectrons) ==0 and len(SmearedMuons)==0 ##try commenting out last two
    
    if not (singleElEvent_ or presentDisTrkEvent or singleMuEvent_): continue
    
    metvec = TLorentzVector()
    metvec.SetPtEtaPhiE(c.MET, 0, c.METPhi, c.MET) #check out feature vector in case of ttbar control region

    if singleElEvent_:
        elec = random.sample(SmearedElectrons,1)[0][0]
        adjustedMht = TLorentzVector()
        adjustedMht.SetPxPyPzE(0,0,0,0)
        adjustedJets = []
        adjustedHt = 0
        adjustedBTags = 0
        if genMatchEverything:
            dr = elec.DeltaR(genels[0])
            if verbose: print dr
            if not dr<0.02: continue
            
        #print ientry, 'found a tawdry se', elec.Pt()            
        for ijet, jet in enumerate(c.Jets):
            if not jet.Pt()>30: continue
            if not jet.DeltaR(elec)>0.4: continue####update 
            if not abs(jet.Eta())<5.0: continue####update to 2.4
            adjustedMht-=jet
            if not abs(jet.Eta())<2.4: continue####update to 2.4
            adjustedJets.append(jet)            
            adjustedHt+=jet.Pt()
            if c.Jets_bDiscriminatorCSV[ijet]>BTAG_CSV: adjustedBTags+=1
        adjustedNJets = len(adjustedJets)
        mindphi = 4
        for jet in adjustedJets: mindphi = min(mindphi, abs(jet.DeltaPhi(adjustedMht)))
        
        if genMatchEverything:
                if RelaxGenKin:
                        pt = elec.Pt()
                        eta = abs(elec.Eta())
                else:
                        pt = genels[0].Pt()
                        eta = abs(genels[0].Eta())
        else:
                pt = elec.Pt()
                eta = abs(elec.Eta())    
        ptForKappa = pt
        #short
        fv = [adjustedHt,adjustedMht.Pt(),adjustedNJets,adjustedBTags, 1+len(disappearingTracks), 1+nShort, nLong, mindphi, len(SmearedElectrons)-1, len(SmearedMuons), pt,eta]
        fv.append(getBinNumber(fv))
        kPixOnly = fetchKappa(abs(eta),min(ptForKappa,9999.99), kappadictElPixOnly)
        for regionkey in regionCuts:
            for ivar, varname in enumerate(varlist_):
                hname = 'El'+regionkey+'_'+varname
                if selectionFeatureVector(fv,regionkey,varname):
                    fillth1(histoStructDict[hname].Control,fv[ivar], weight)
                    fillth1(histoStructDict[hname].Method,fv[ivar], kPixOnly*weight)
                    
        #long        
        fv = [adjustedHt,adjustedMht.Pt(),adjustedNJets,adjustedBTags, 1+len(disappearingTracks), nShort, 1+nLong, mindphi, len(SmearedElectrons)-1, len(SmearedMuons), pt,eta]
        fv.append(getBinNumber(fv))                    
        kPixAndStrips = fetchKappa(abs(eta),min(ptForKappa,9999.99), kappadictElPixAndStrips)
        for regionkey in regionCuts:
            for ivar, varname in enumerate(varlist_):
                hname = 'El'+regionkey+'_'+varname
                if selectionFeatureVector(fv,regionkey,varname):
                    if 'Pix' in regionkey or 'Bin' in varname: fillth1(histoStructDict[hname].Control,fv[ivar], weight)# skip double counting 1-lep region
                    fillth1(histoStructDict[hname].Method,fv[ivar], kPixAndStrips*weight)                                        
                    
                    
    if singleMuEvent_:
        muon = random.sample(SmearedMuons,1)[0][0]
        adjustedMht = TLorentzVector()
        adjustedMht.SetPxPyPzE(0,0,0,0)
        adjustedJets = []
        adjustedHt = 0
        adjustedBTags = 0
        if genMatchEverything:
            dr = muon.DeltaR(genmus[0])
            if verbose: print dr
            if not dr<0.02: continue
        #print ientry, 'found a tawdry se', elec.Pt()            
        for ijet, jet in enumerate(c.Jets):
            if not jet.Pt()>30: continue
            if not jet.DeltaR(muon)>0.4: continue####update 
            if not abs(jet.Eta())<5.0: continue####update to 2.4
            adjustedMht-=jet
            if not abs(jet.Eta())<2.4: continue####update to 2.4
            adjustedJets.append(jet)            
            adjustedHt+=jet.Pt()
            if c.Jets_bDiscriminatorCSV[ijet]>BTAG_CSV: adjustedBTags+=1
        adjustedNJets = len(adjustedJets)
        mindphi = 4
        for jet in adjustedJets: mindphi = min(mindphi, abs(jet.DeltaPhi(adjustedMht)))
        
        if genMatchEverything:
                if RelaxGenKin:
                        pt = muon.Pt()
                        eta = abs(muon.Eta())
                else:
                        pt = genmus[0].Pt()
                        eta = abs(genmus[0].Eta())
        else:
                pt = muon.Pt()
                eta = abs(muon.Eta())    
        ptForKappa = pt
        fv = [adjustedHt,adjustedMht.Pt(),adjustedNJets,adjustedBTags, 1+len(disappearingTracks),1+nShort,nLong, mindphi, len(SmearedElectrons), len(SmearedMuons)-1,pt,eta]
        fv.append(getBinNumber(fv))
        kPixOnly = fetchKappa(abs(eta),min(ptForKappa,9999.99), kappadictMuPixOnly)
        for regionkey in regionCuts:
            for ivar, varname in enumerate(varlist_):
                hname = 'Mu'+regionkey+'_'+varname
                if selectionFeatureVector(fv,regionkey,varname):
                    fillth1(histoStructDict[hname].Control,fv[ivar], weight)
                    fillth1(histoStructDict[hname].Method,fv[ivar], kPixOnly*weight)
                    
        fv = [adjustedHt,adjustedMht.Pt(),adjustedNJets,adjustedBTags, 1+len(disappearingTracks),nShort,nLong+1, mindphi, len(SmearedElectrons), len(SmearedMuons)-1,pt,eta]
        fv.append(getBinNumber(fv))
        kPixAndStrips = fetchKappa(abs(eta),min(ptForKappa,9999.99), kappadictMuPixAndStrips)
        for regionkey in regionCuts:
            for ivar, varname in enumerate(varlist_):
                hname = 'Mu'+regionkey+'_'+varname
                if selectionFeatureVector(fv,regionkey,varname):
                    if 'Pix' in regionkey or 'Bin' in varname: fillth1(histoStructDict[hname].Control,fv[ivar], weight)
                    fillth1(histoStructDict[hname].Method,fv[ivar], kPixAndStrips*weight)                        
                                    
                    
                    
                                        
    if presentDisTrkEvent:
        dt = disappearingTracks[0][0]
        isPromptEl = isMatched(dt, genels, 0.02)
        isPromptMu = isMatched(dt, genmus, 0.02)    
        if isdata:     isPromptEl, isPromptMu = True, True
        
        #if not (isPromptEl or isPromptMu): continue
        
        print ientry, 'found a nice dt', dt.Pt()
        adjustedNJets = 0        
        adjustedBTags = 0        
        adjustedJets = []
        adjustedHt = 0
        adjustedMht = TLorentzVector()
        adjustedMht.SetPxPyPzE(0,0,0,0)
        for ijet, jet in enumerate(c.Jets):
            if not jet.Pt()>30: continue
            if not abs(jet.Eta())<5.0: continue###update to 2.4
            if not jet.DeltaR(dt)>0.4: continue###update to include second disappearing track
            adjustedMht-=jet
            if not abs(jet.Eta())<2.4: continue###update to 2.4            
            if c.Jets_bDiscriminatorCSV[ijet]>BTAG_CSV: adjustedBTags+=1
            adjustedJets.append(jet)
            adjustedHt+=jet.Pt()
        adjustedNJets = len(adjustedJets)
        mindphi = 4
        for jet in adjustedJets: mindphi = min(mindphi, abs(jet.DeltaPhi(adjustedMht)))            
    #    if not adjustedNJets>0: continue                
        if genMatchEverything:
            if RelaxGenKin: 
                pt = dt.Pt()
                eta = abs(dt.Eta())
            else: 
                if isPromptEl: 
                    pt = isPromptEl.Pt()
                    eta = abs(isPromptEl.Eta())
                if isPromptMu:
                    pt = isPromptMu.Pt()
                    eta = abs(isPromptMu.Eta())                
        else: 
            pt = dt.Pt()
            eta = abs(dt.Eta())    
        fv = [adjustedHt,adjustedMht.Pt(),adjustedNJets,adjustedBTags,len(disappearingTracks), nShort, nLong, mindphi,len(RecoElectrons), len(RecoMuons), pt, eta]
        fv.append(getBinNumber(fv))
        for regionkey in regionCuts:
            for ivar, varname in enumerate(varlist_):
                if selectionFeatureVector(fv,regionkey,varname):
                        if isPromptEl: fillth1(histoStructDict['El'+regionkey+'_'+varname].Truth,fv[ivar], weight)                
                        elif isPromptMu: fillth1(histoStructDict['Mu'+regionkey+'_'+varname].Truth,fv[ivar], weight)
                        else: fillth1(histoStructDict['Fake'+regionkey+'_'+varname].Truth,fv[ivar], weight)
                        
                    

fnew_.cd()
hHt.Write()
hHtWeighted.Write()
writeHistoStruct(histoStructDict)
print 'just created', fnew_.GetName()
fnew_.Close()
fKappaPixOnly.Close()
fSmear.Close()
