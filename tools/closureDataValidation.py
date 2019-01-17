from ROOT import *
from utils import *
#from utilsII import *
import os, sys
from glob import glob
gStyle.SetOptStat(0)
gROOT.SetBatch(1)
from time import sleep

lumi = 135000.
istest = False

snatchFakesFromMC = True

isdata = True

try: infname = sys.argv[1]
except: infname = 'mergedRoots/mergedRun2016SingleEl_Split.root'

#do: python tools/closureDataValidation.py mergedRoots/mergedRun2016SingleEl_Split.root && python tools/closureDataValidation.py mergedRoots/mergedRun2016SingleMu_Split.root 

skipifnot = {}
skipifnot['mergedRoots/mergedRun2016SingleEl.root'] = 'CtrEl'
skipifnot['mergedRoots/mergedRun2016SingleMu.root'] = 'CtrMu'
skipifnot['mergedRoots/mergedRun2016SingleEl_Split.root'] = 'CtrEl'
skipifnot['mergedRoots/mergedRun2016SingleMu_Split.root'] = 'CtrMu'


infile = TFile(infname)
infile.ls()
if snatchFakesFromMC:
	fFakes = TFile('output/totalweightedbkgsDataDrivenMC.root')

fnameOut = skipifnot[infname]+'_'+infname.split('/')[-1].replace('merged','')
fnew2 = TFile(fnameOut,'recreate')


applyClosureCorrection = False
def makeClosureCorrectionAndUncertainty(hMethod, hTruth):
	hCorrectedPrediction = hMethod.Clone('hCorrectedPrediction_'+hMethod.GetName())
	hCorrectionFactor = hMethod.Clone('hCorrectionFactor_'+hMethod.GetName())
	hCorrectedPrediction.Reset()
	hCorrectionFactor.Reset()	
	xax = hTruth.GetXaxis()
	for ibin in range(1, xax.GetNbins()+1):
		nmeth = hMethod.GetBinContent(ibin)
		ntrut = hTruth.GetBinContent(ibin)
		newcv = (nmeth+ntrut)/2.0
		hCorrectedPrediction.SetBinContent(ibin, newcv)
		hCorrectedPrediction.SetBinError(ibin, TMath.Sqrt(pow(hMethod.GetBinError(ibin),2)+pow(abs(newcv-ntrut),2)))
		if (nmeth>0 and ntrut>0): 
			hCorrectionFactor.SetBinContent(ibin, 1.0*newcv/nmeth)
			print 'before ibin', ibin, 1.0*newcv/nmeth
			hCorrectionFactor.SetBinError(ibin, 1.0*abs(newcv-ntrut)/newcv)
		else: 
			hCorrectionFactor.SetBinContent(ibin, 1.0)
			hCorrectionFactor.SetBinError(ibin, 0.0)
	return hCorrectedPrediction, hCorrectionFactor
		
keys = infile.GetListOfKeys()

hratios = []
clist = []
for key in sorted(keys):
	infile.cd()
	name = key.GetName()
	if 'LowHt' in name or 'HighHt' in name: continue
	if not ('Control' in name.split('_')[-1]): continue
		
	if not skipifnot[infname] in name: continue
	if not 'hEl' in name: continue #this applies to single-muon channel as well	
	
	if 'PixOnly' in name: dtmode = 'short tracks'
	elif 'PixAndStrips' in name: dtmode = 'long tracks'	
	else: dtmode = 'short/long merged'
	
	hElControl = infile.Get(name)
	hMuControl = infile.Get(name.replace('hEl','hMu'))
	hMuControl.SetLineColor(kRed+1)
	
	methodname = name.replace('Control','Method')
	hElMethod = infile.Get(methodname)	
	hElMethod.SetLineColor(kGreen+2)
	
	hMuMethod = infile.Get(methodname.replace('hEl','hMu'))	
	hMuMethod.SetLineColor(kViolet)	
	
	truthname = name.replace('Control','Truth')
	hTruth = infile.Get(truthname)	
	
	if skipifnot[infname] == 'CtrEl':
		hElControl.SetTitle('Run2016 double-e')	
		hMuControl.SetTitle('Run2016 1-e, 1-#mu')	
		hElMethod.SetTitle('Run2016 wtd. double-e')
		hMuMethod.SetTitle('Run2016 wtd. 1-e, 1-#mu')
		hTruth.SetTitle('Run2016 1-e, 1-dis. trk')
	if skipifnot[infname] == 'CtrMu':
		hElControl.SetTitle('Run2016 double-#mu')	
		hMuControl.SetTitle('Run2016 1-#mu, 1-e')	
		hElMethod.SetTitle('Run2016 wtd double-#mu')
		hMuMethod.SetTitle('Run2016 wtd 1-#mu, 1-e')
		hTruth.SetTitle('Run2016 1-#mu, 1-dis. trk')	
			


	
	if 'TrkPt' in name:
		hElControl.Scale(1.0,'width') #lumi*1.0/hHt.Integral(-1,9999))
		hTruth.Scale(1.0,'width') #lumi*1.0/hHt.Integral(-1,9999))
		hElMethod.Scale(1.0,'width') #lumi*1.0/hHt.Integral(-1,9999))	
		hMuControl.Scale(1.0,'width') #lumi*1.0/hHt.Integral(-1,9999))
		hMuMethod.Scale(1.0,'width') #lumi*1.0/hHt.Integral(-1,9999))		
	
			
	shortname = name[1:].replace('Control','').replace('Truth','').replace('Method','')
	varname = shortname.split('_')[-1]
	hElControl.GetXaxis().SetTitle(namewizard(varname))
	hElMethod.GetXaxis().SetTitle(namewizard(varname))
	hMuControl.GetXaxis().SetTitle(namewizard(varname))
	hMuMethod.GetXaxis().SetTitle(namewizard(varname))	
	hTruth.GetXaxis().SetTitle(namewizard(varname))	
	

	leg = mklegend(x1=.52, y1=.5, x2=.99, y2=.76, color=kWhite)
	legname = 'single-lep'
	ename = legname.replace('lep','electron')
	muname = legname.replace('lep','muon')
	leg.AddEntry(hElControl,hElControl.GetTitle(),'l')
	leg.AddEntry(hMuControl,hMuControl.GetTitle(),'l')	
	
	hElMethod.SetFillStyle(1001)
	hElMethod.SetFillColor(hElMethod.GetLineColor())
	hMuMethod.SetFillStyle(1001)
	hMuMethod.SetFillColor(hMuMethod.GetLineColor())
	hMuMethod.SetLineColor(kGray+2)					
	hElMethod.SetLineColor(kGray+2)
	c1 = mkcanvas('c_'+shortname.replace('_',''))
	
	if snatchFakesFromMC:
		fakename = name.replace('hEl','hFake').replace('Control','Truth')
		hFakes = fFakes.Get(fakename)
		hFakes.SetTitle('fakes (TT+Jets MC) x f')
		hFakes.SetLineColor(kOrange)
		hFakes.SetFillColor(kOrange)
		hFakes.SetFillStyle(1001)		
		if 'PixOnly' in name: fudgefactor = 4.0
		else: fudgefactor = 3.0		
		hFakes.Scale(fudgefactor)
		hratio = FabDraw(c1,leg,hTruth,[hFakes,hElMethod,hMuMethod],datamc='data',lumi=lumi/1000, title = '', LinearScale=False, fractionthing='pred. / obs')
	else:
		hratio = FabDraw(c1,leg,hTruth,[hElMethod,hMuMethod],datamc='data',lumi=lumi, title = '', LinearScale=False, fractionthing='pred. / obs.')
	#hratio.GetYaxis().SetRangeUser(0.0,2.5)
	hratio.GetYaxis().SetRangeUser(0.001,3.1)	
	hratio.SetLineColor(kBlack)
	hratio.SetMarkerColor(kBlack)
	hratio.SetDirectory(0)
	themax = 100000*max([2*hElControl.GetMaximum(),2*hMuControl.GetMaximum(),2*hTruth.GetMaximum()])	
	hElMethod.GetYaxis().SetRangeUser(0.005,themax)
	hElControl.GetYaxis().SetRangeUser(0.005,themax)					
	hMuMethod.GetYaxis().SetRangeUser(0.005,themax)
	hMuControl.GetYaxis().SetRangeUser(0.005,themax)		
	hTruth.GetYaxis().SetRangeUser(0.005,themax)	
	c1.cd(2)
	c1.SetLogy()
	c1.Update()
	c1.cd(1)
	hElControl.Draw('same p')
	hMuControl.Draw('same p')	
	hTruth.Draw('same')
	tl.DrawLatex(.2,.69,dtmode)	
	c1.Update()
	fnew2.cd()
	c1.Write()
	c1.Print('pdfs/closure/prompt-bkg-validation/'+shortname.replace('_','')+'.pdf')
	hratios.append(hratio)
	clist.append(c1)

print 'test a'
	
import os, sys
print 'test b'
print 'just created', os.getcwd()+'/'+fnew2.GetName()
fnew2.Close()
print 'test c'

	
	
