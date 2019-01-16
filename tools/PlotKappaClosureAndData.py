from ROOT import *
from utils import *
import sys

gStyle.SetOptStat(0)
gROOT.SetBatch(1)


try: dtmode = sys.argv[1]
except:	dtmode = 'PixOrStrips'

print 'dtmode', dtmode
if dtmode == 'PixOnly': 
	PixMode = True
	PixStripsMode = False
	CombineMode = False
elif dtmode == 'PixAndStrips': 
	PixMode = False
	PixStripsMode = True
	CombineMode = False	
else:
	PixMode = False
	PixStripsMode = False
	CombineMode = True	
	
if CombineMode:
	fTTJets = TFile('usefulthings/KappaTTJets_PixOrStrips.root')
	fWJetsToLL = TFile('usefulthings/KappaWJets_PixOrStrips.root')
	fMethodMC = TFile('usefulthings/KappaAllMC_PixOrStrips.root')
	fMethodDataList = [TFile('usefulthings/KappaRun2016_PixOrStrips.root')]
	#fMethodDataList = [TFile('usefulthings/KappaRun2016B.root'), TFile('usefulthings/KappaRun2016D.root'), TFile('usefulthings/KappaRun2016G.root'), TFile('usefulthings/KappaRun2016H.root')]
if PixMode:
	fTTJets = TFile('usefulthings/KappaTTJets_PixOnly.root')
	fWJetsToLL = TFile('usefulthings/KappaWJets_PixOnly.root')
	fMethodMC = TFile('usefulthings/KappaAllMC_PixOnly.root')
	fMethodDataList = [TFile('usefulthings/KappaRun2016_PixOnly.root')]
	#fMethodDataList = [TFile('usefulthings/KappaRun2016B.root'), TFile('usefulthings/KappaRun2016D.root'), TFile('usefulthings/KappaRun2016G.root'), TFile('usefulthings/KappaRun2016H.root')]
if PixStripsMode:
	fTTJets = TFile('usefulthings/KappaTTJets_PixAndStrips.root')
	fWJetsToLL = TFile('usefulthings/KappaWJets_PixAndStrips.root')
	fMethodMC = TFile('usefulthings/KappaAllMC_PixAndStrips.root')
	fMethodDataList = [TFile('usefulthings/KappaRun2016_PixAndStrips.root')]
	#fMethodDataList = [TFile('usefulthings/KappaRun2016B.root'), TFile('usefulthings/KappaRun2016D.root'), TFile('usefulthings/KappaRun2016G.root'), TFile('usefulthings/KappaRun2016H.root')]	


fWJetsToLL.ls()
names_ = []
for key in fWJetsToLL.GetListOfKeys():
	names_.append(key.GetName())
	
fnew = TFile('ClosureKappaWithData_'+dtmode+'.root', 'recreate')

c1 = mkcanvas('c1')
c1.SetLogy()
#c1.SetLogx()
for name in names_:
	if not 'hGen' in name: continue
	if name[0]=='c' or name[0]=='f': continue
	print name
	'''
	hWJetsToLL = fWJetsToLL.Get('hGenElProbePtKappa_eta0to1.4442')
	funcWJetsToLL = fWJetsToLL.Get('f1hGenElProbePtKappa_eta0to1.4442')
	MethodMC = fMethodMC.Get('hElProbePtKappa_eta0to1.4442')
	funcMethodMC = fMethodMC.Get('f1hElProbePtKappa_eta0to1.4442')
	MethodData = fMethodData.Get('hElProbePtKappa_eta0to1.4442')
	funcMethodData = fMethodData.Get('f1hElProbePtKappa_eta0to1.4442')
	'''
	hWJetsToLL = fWJetsToLL.Get(name)
	funcWJetsToLL = fWJetsToLL.Get('f1'+name)
	
	hTTJets = fTTJets.Get(name)
	funcTTJets = fTTJets.Get('f1'+name)
	hTTJets.SetLineColor(kGreen+2)
	funcTTJets.SetLineColor(kGreen+2)	
	
	mname = name.replace('Gen','')	
	MethodMC = fMethodMC.Get(mname)
	funcMethodMC = fMethodMC.Get('f1'+mname)

	xrangemax = 250
	leg = mklegend(x1=.41, y1=.69, x2=.89, y2=.87)
	hWJetsToLL.GetXaxis().SetRangeUser(0,xrangemax)
	hWJetsToLL.GetYaxis().SetRangeUser(0.000001,1.5)
	hWJetsToLL.Draw()	
	hTTJets.GetXaxis().SetRangeUser(0,xrangemax)
	hTTJets.GetYaxis().SetRangeUser(0.000001,2)
	hTTJets.Draw('same')
		
	funcWJetsToLL.Draw('same')
	leg.AddEntry(hWJetsToLL, 'MC Truth (W+Jets)')
	
	funcTTJets.Draw('same')
	leg.AddEntry(hTTJets, 'MC Truth (t#bar{t}+Jets)')
		
	MethodMC.Draw('same')
	funcMethodMC.Draw('same')
	leg.AddEntry(MethodMC, 'MC Tag and Probe')
	
	for iFile, fMethodData in enumerate(fMethodDataList):
		MethodData = fMethodData.Get(mname)
		funcMethodData = fMethodData.Get('f1'+mname)	
		MethodData.Draw('same')
		funcMethodData.Draw('same')
		MethodData.SetLineColor(kBlack+iFile)
		MethodData.SetMarkerColor(kBlack+iFile)
		funcMethodData.SetLineColor(kBlack+iFile)
		yearstr = fMethodData.GetName().split('/')[-1].split('.root')[0].replace('Kappa','').split('_')[0]
		if 'El' in name: leg.AddEntry(MethodData, yearstr+' Tag and Probe')
		if 'Mu' in name: leg.AddEntry(MethodData, yearstr+' Tag and Probe')	

	leg.Draw()
	stamp()	
	tl.DrawLatex(.2,.8,name.split('_')[-1].replace('eta','#eta=').replace('to','-'))
	if 'hMu' in name: 
		tl.DrawLatex(.2,.74,'muons')	
	if 'hEl' in name: 
		tl.DrawLatex(.2,.74,'electrons')
	tl.DrawLatex(.2,.69,dtmode.replace('And','+').replace('Only','-only').replace('Pix','pix').replace('Strips','strips'))
	
	c1.Update()
	fnew.cd()
	c1.Write(name.replace('hGen','c_').replace('.','p'))
	namypoo = 'pdfs/closure/tpkappa/'+name.replace('hGen','kappa').replace('.','p')+'_'+dtmode+'.pdf'
	c1.Print(namypoo)


print 'just created'
import os
print os.getcwd()+'/'+fnew.GetName()
fnew.Close()
