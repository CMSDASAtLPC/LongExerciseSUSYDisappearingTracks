from ROOT import *
from random import shuffle
from glob import glob

skimDirectory = '/eos/uscms///store/user/cmsdas/2019/long_exercises/DisappearingTracks/Skims/'
sigfilelist = glob('Signal/*.root')
print 'sigfilelist', sigfilelist

SubcategoryChainDictsByCategoryDict= {}
WJetsToLNu_SubcategoryChainDict = {}
WJetsToLNu_SubcategoryChainDict['WJetsToLNu_HT-100To200'] = TChain('tEvent')
WJetsToLNu_SubcategoryChainDict['WJetsToLNu_HT-200To400'] = TChain('tEvent')
WJetsToLNu_SubcategoryChainDict['WJetsToLNu_HT-400To600'] = TChain('tEvent')
#WJetsToLNu_SubcategoryChainDict['WJetsToLNu_HT-600To800'] = TChain('tEvent')
WJetsToLNu_SubcategoryChainDict['WJetsToLNu_HT-800To1200'] = TChain('tEvent')
WJetsToLNu_SubcategoryChainDict['WJetsToLNu_HT-1200To2500'] = TChain('tEvent')#WJetsToLNuSubcategoryChainDict['HT-2500ToInf'] = TChain('tEvent')
WJetsToLNu_SubcategoryChainDict['WJetsToLNu_HT-2500ToInf'] = TChain('tEvent')
SubcategoryChainDictsByCategoryDict['WJetsToLNu'] = WJetsToLNu_SubcategoryChainDict
TTJets_SubcategoryChainDict = {}
TTJets_SubcategoryChainDict['TTJets_TuneCUETP8M1'] = TChain('tEvent')
TTJets_SubcategoryChainDict['TTJets_HT-600to800'] = TChain('tEvent')
#TTJets_SubcategoryChainDict['TTJets_HT-800to1200'] = TChain('tEvent')
TTJets_SubcategoryChainDict['TTJets_HT-1200to2500'] = TChain('tEvent')
TTJets_SubcategoryChainDict['TTJets_HT-2500toInf'] = TChain('tEvent')
SubcategoryChainDictsByCategoryDict['TTJets'] = TTJets_SubcategoryChainDict
ZJetsToNuNu_SubcategoryChainDict = {}
ZJetsToNuNu_SubcategoryChainDict['ZJetsToNuNu_HT-200To400'] = TChain('tEvent')
ZJetsToNuNu_SubcategoryChainDict['ZJetsToNuNu_HT-400To600'] = TChain('tEvent')
ZJetsToNuNu_SubcategoryChainDict['ZJetsToNuNu_HT-600To800'] = TChain('tEvent')#ZJetsToNuNuSubcategoryChainDict['HT-800To1200'] = TChain('tEvent')#ZJetsToNuNuSubcategoryChainDict['HT-1200To2500'] = TChain('tEvent')#ZJetsToNuNuSubcategoryChainDict['HT-2500ToInf'] = TChain('tEvent')
SubcategoryChainDictsByCategoryDict['ZJetsToNuNu'] = ZJetsToNuNu_SubcategoryChainDict
VV_SubcategoryChainDict = {}
VV_SubcategoryChainDict['WWTo1L1Nu2Q_13TeV'] = TChain('tEvent')
VV_SubcategoryChainDict['WZTo1L1Nu2Q_13TeV'] = TChain('tEvent')
VV_SubcategoryChainDict['WZTo1L3Nu_13TeV'] = TChain('tEvent')
VV_SubcategoryChainDict['ZZTo2L2Q_13TeV'] = TChain('tEvent')
VV_SubcategoryChainDict['ZZTo2Q2Nu_13TeV'] = TChain('tEvent')
#VV_SubcategoryChainDict['WWTo2L2Nu_13TeV'] = TChain('tEvent')
SubcategoryChainDictsByCategoryDict['Diboson'] = VV_SubcategoryChainDict
DYJets_SubcategoryChainDict = {}
DYJets_SubcategoryChainDict['DYJetsToLL_M-50_HT-100to200'] = TChain('tEvent')
DYJets_SubcategoryChainDict['DYJetsToLL_M-50_HT-200to400'] = TChain('tEvent')
DYJets_SubcategoryChainDict['DYJetsToLL_M-50_HT-400to600'] = TChain('tEvent')
DYJets_SubcategoryChainDict['DYJetsToLL_M-50_HT-600to800'] = TChain('tEvent')
DYJets_SubcategoryChainDict['DYJetsToLL_M-50_HT-800to1200'] = TChain('tEvent')
DYJets_SubcategoryChainDict['DYJetsToLL_M-50_HT-1200to2500'] = TChain('tEvent')
DYJets_SubcategoryChainDict['DYJetsToLL_M-50_HT-2500toInf'] = TChain('tEvent')
SubcategoryChainDictsByCategoryDict['DYJets'] = DYJets_SubcategoryChainDict
QCD_SubcategoryChainDict = {}
QCD_SubcategoryChainDict['QCD_HT200to300'] = TChain('tEvent')
QCD_SubcategoryChainDict['QCD_HT300to500'] = TChain('tEvent')
QCD_SubcategoryChainDict['QCD_HT500to700'] = TChain('tEvent')
QCD_SubcategoryChainDict['QCD_HT700to1000'] = TChain('tEvent')
QCD_SubcategoryChainDict['QCD_HT1000to1500'] = TChain('tEvent')
QCD_SubcategoryChainDict['QCD_HT1500to2000'] = TChain('tEvent')
QCD_SubcategoryChainDict['QCD_HT2000toInf'] = TChain('tEvent')
SubcategoryChainDictsByCategoryDict['QCD'] = QCD_SubcategoryChainDict
Rare_SubcategoryChainDict = {}
#Rare_SubcategoryChainDict['WWZ_TuneCUETP8M1'] = TChain('tEvent')
SubcategoryChainDictsByCategoryDict['Rare'] = Rare_SubcategoryChainDict

ColorsByCategory = {'WJetsToLNu':kGreen+1,'TTJets':kOrange+1,'ZJetsToNuNu':kViolet,'Diboson':kTeal-4,'DYJets':kBlue+1,'QCD':kYellow,'Rare':kBlack}
CategoryKeysBigToSmall = ['WJetsToLNu','TTJets','QCD','ZJetsToNuNu','Diboson','DYJets','Rare']
#CategoryKeysBigToSmall = ['DYJets']
CategoryKeysSmallToBig = list(CategoryKeysBigToSmall)
CategoryKeysSmallToBig.reverse()
for category in CategoryKeysSmallToBig:
		for subcategory in SubcategoryChainDictsByCategoryDict[category]:
			fname = skimDirectory+'/Background/skim_'+subcategory+'.root'
			print 'processing', fname
			SubcategoryChainDictsByCategoryDict[category][subcategory].Add(fname)

#sigfilelist = glob(skimDirectory+'/Signal/*.root')
smallsigfilelist = list(sigfilelist)
colors = [kRed-1,kRed-0,kRed+1,kRed+2,kPink-1,kPink+0,kPink+1,kPink+2,kAzure-1,kAzure+0,kAzure+1,kAzure+2, kBlack, kGray]
shuffle(colors)
ColorsBySignal = {}
SignalChainDict = {}
for isig, sigfile in enumerate(smallsigfilelist):
	stem = sigfile.split('/')[-1].replace('.root','')
	SignalChainDict[stem] = TChain('tEvent')
	SignalChainDict[stem].Add(sigfile)
	ColorsBySignal[stem] = colors[isig]
