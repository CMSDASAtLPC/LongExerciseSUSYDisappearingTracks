from ROOT import *
from utils import *
from random import shuffle
gROOT.SetBatch(1)
gStyle.SetOptStat(0)
execfile('tools/EventCategories.py')
UseOptimizedCuts = True
dolog = True
lumi = 35900

fnew = TFile('canvases.root','recreate')

#this code combines events stored in trees in many files such as
#/nfs/dust/cms/user/beinsam/CMSDAS2018b/Skims/Signal/skim_pMSSM12_MCMC1_44_855871.root
#and
#/nfs/dust/cms/user/beinsam/CMSDAS2018b/Skims/Background/skim_TTJets_HT-600to800.root 
#the list of braches can be shown by opening a file and using the TTree::Show(0) method


cutsets = {}
cutsets['NoCuts'] = 'Mht>0'

histframes = {}
histframes['Met'] = TH1F('Met','',14,100,800)
histframes['Ht'] = TH1F('Ht','',15,100,3100)
histframes['NJets'] = TH1F('Ht','',10,0,10)
histframes['BTags'] = TH1F('BTags','',5,0,5)
histframes['NTags'] = TH1F('NTags','',4,0,4)
histframes['MinDeltaPhiMetJets'] = TH1F('DPhiMetSumTags','',16,0,3.2)
histframes['SumTagPtOverMht'] = TH1F('SumTagPtOverMht','',11,0,2.2)

for selectionkey in cutsets:
 hists = {}
 histsStack = {}
 for histkey in histframes:
	cwaste = TCanvas('cwaste')
	growinghist = histframes[histkey].Clone(histkey)
	histframes[histkey].GetXaxis().SetTitle(namewizard(histframes[histkey].GetName()))
	growinghist.GetXaxis().SetTitle(namewizard(histkey))	
	histoStyler(growinghist, kGray+1)
	growinghist.SetFillStyle(1001)	
	nbins = histframes[histkey].GetXaxis().GetNbins()
	xlow, xhigh = histframes[histkey].GetXaxis().GetBinLowEdge(1), histframes[histkey].GetXaxis().GetBinUpEdge(nbins)
	drawarg = 'max(%f+0.001,min(%f-0.001,%s))>>hadc(%d,%f,%f)'%(xlow,xhigh,histkey,nbins,xlow,xhigh)
	weightstring = '('+cutsets[selectionkey]+')*weight*'+str(lumi)	
	if UseOptimizedCuts: weightstring+='*('+'1'+')'		
	for category in CategoryKeysSmallToBig:
		hCategory = histframes[histkey].Clone(histkey+'_cat')
		histoStyler(hCategory,ColorsByCategory[category])
		hCategory.SetFillColor(ColorsByCategory[category])
		hCategory.SetFillStyle(1001)
		histoStyler(growinghist,ColorsByCategory[category])
		growinghist.SetFillColor(ColorsByCategory[category])
		growinghist.SetFillStyle(1001)			
		for subcategory in SubcategoryChainDictsByCategoryDict[category]:
			SubcategoryChainDictsByCategoryDict[category][subcategory].Draw(drawarg,weightstring)
			h = SubcategoryChainDictsByCategoryDict[category][subcategory].GetHistogram()
			hCategory.Add(h)
		growinghist.Add(hCategory)			
		hists[category] = hCategory.Clone(category)
		histsStack[category] = growinghist.Clone(category+'_stack')
	sighists = []
	for key in SignalChainDict:
		print 'drawing', key
		SignalChainDict[key].Draw(drawarg,weightstring)
		hsig = SignalChainDict[key].GetHistogram()
		hsig.SetDirectory(0)
		hsig.SetTitle(key)
		sighists.append(hsig)
		histoStyler(sighists[-1],ColorsBySignal[key])
		sighists[-1].SetLineStyle(kDashed)		
		sighists[-1].SetLineColor(sighists[-1].GetMarkerColor())				
	c1 = mkcanvas('c_'+histkey)
	if dolog: c1.SetLogy()
	histsStack[CategoryKeysBigToSmall[0]].SetLineColor(kGray+1)		
	if dolog:
		histsStack[CategoryKeysBigToSmall[0]].GetYaxis().SetRangeUser(0.1,300*histsStack[CategoryKeysBigToSmall[0]].GetMaximum())
	else:
		histsStack[CategoryKeysBigToSmall[0]].GetYaxis().SetRangeUser(0,1.3*histsStack[CategoryKeysBigToSmall[0]].GetMaximum())
	legBkg = mklegend(x1=.61, y1=.56, x2=.95, y2=.88, color=kWhite)
	arg = ''
	for category in CategoryKeysBigToSmall:
		histsStack[category].Draw('hist '+arg)
		legBkg.AddEntry(histsStack[category],category,'f')
		arg = 'same'
	histsStack[CategoryKeysBigToSmall[0]].Draw('same E0')
	legSig = mklegend(x1=.16, y1=.7, x2=.6, y2=.88, color=kWhite)	
	for sighist in sighists:
		sighist.Draw('hist same')
		legSig.AddEntry(sighist,sighist.GetTitle().replace('_MCMC1',''),'l')
	histsStack[CategoryKeysBigToSmall[0]].Draw('axis same')	
	legBkg.Draw()
	legSig.Draw()
	stamp(round(1.0*lumi/1000,1))
	c1.Update()
	fnew.cd()	
	c1.Write('c_'+histkey+'_'+selectionkey)
print 'just created', fnew.GetName()
fnew.Close()
			
			
