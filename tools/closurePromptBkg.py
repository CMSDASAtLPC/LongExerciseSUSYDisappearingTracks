from ROOT import *
from utils import *
#from utilsII import *
import os, sys
from glob import glob
gStyle.SetOptStat(0)
gROOT.SetBatch(1)
from time import sleep
lumi = 135 #just for labeling. this weightw as already applied
#must agree with lumi in merged...py!

fCentralMC = 'output/totalweightedbkgsDataDrivenMC.root'


listOfVariationFilenames = []#['output/totalweightedbkgsTrueFit.root']
listOfVariationFiles = []
for variationFileName in listOfVariationFilenames: listOfVariationFiles.append(TFile(variationFileName))
variationColors = [kBlue-1, kBlue, kBlue+1]

drawVariations = False
usePredictionWithClosureCorrection = False
CombineLeptons_ = False
			





infile = TFile(fCentralMC)
infile.ls()

fout = 'closure.root'

fnew = TFile(fout,'recreate')
c1 = mkcanvas('c1')

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
print 'len(keys)', len(keys)
for key in sorted(keys):#[:241]:
	infile.cd()
	name = key.GetName()
	if 'LowHt' in name or 'HighHt' in name: continue
	if CombineLeptons_: 
		if not ('Control' in name.split('_')[-1] and 'hEl'==name[:3]): continue
		lepname = 'lepton (el or #mu)'
	else: 
		if not ('Control' in name.split('_')[-1]): continue
		if 'hEl'==name[:3]: lepname = 'el'
		if 'hMu'==name[:3]: lepname = '#mu'
	#if 'Ttbar' in name: continue
	hVarControl = infile.Get(name)
	if CombineLeptons_: hVarControl.Add(infile.Get(name.replace('hEl','hMu')))
	hVarControl.SetTitle('single '+lepname)	
	truthname = name.replace('barControl','barBarf')
	truthname = truthname.replace('Control','Truth')
	truthname = truthname.replace('barBarf','barControl')
	hVarTruth = infile.Get(truthname)
	hVarTruth.SetTitle('MC observed (truth)')
	if CombineLeptons_: hVarTruth.Add(infile.Get(truthname.replace('hEl','hMu')))
			
	methodname = name.replace('barControl','barBarf')
	methodname = methodname.replace('Control','Method')
	methodname = methodname.replace('barBarf','barControl')
			
	hVarMethod = infile.Get(methodname)
	if 'hMu'==name[:3]: 
		hVarMethod.SetLineColor(kViolet+1)
		hVarControl.SetLineColor(kRed+2)
	else:
		hVarMethod.SetLineColor(kGreen+2)
	if CombineLeptons_: hVarMethod.Add(infile.Get(methodname.replace('hEl','hMu')))
	hVarMethod.SetTitle('weighted single '+lepname)
	shortname = name[1:].replace('Control','').replace('Truth','').replace('Method','')
	varname = shortname.split('_')[-1]
	xax = hVarMethod.GetXaxis()
	hVarControl.GetXaxis().SetTitle(namewizard(varname))
	hVarTruth.GetXaxis().SetTitle(namewizard(varname))
	hVarMethod.GetXaxis().SetTitle(namewizard(varname))
		
	#if not isdata:
	#	hVarControl.Scale(1.0,'width') #lumi*1.0/hHt.Integral(-1,9999))
	#	hVarTruth.Scale(1.0,'width') #lumi*1.0/hHt.Integral(-1,9999))
	#	hVarMethod.Scale(1.0,'width') #lumi*1.0/hHt.Integral(-1,9999))

	
	leg = mklegend(x1=.52, y1=.54, x2=.99, y2=.76, color=kWhite)
	legname = 'single-lep'
	if 'hEl' in name: legname = legname.replace('lep','electron')
	if 'hMu' in name: legname = legname.replace('lep','muon')
	leg.AddEntry(hVarControl,'single-'+lepname,'l')
	#hVarMethod.Scale()
	themax = 1000*max([hVarControl.GetMaximum(),hVarMethod.GetMaximum(),hVarTruth.GetMaximum()])
	hVarMethod.GetYaxis().SetRangeUser(0.00001,themax)
	hVarMethod.SetFillStyle(1001)
	hVarMethod.SetFillColor(hVarMethod.GetLineColor())	
	hVarTruth.GetYaxis().SetRangeUser(0.01,themax)
	hVarControl.GetYaxis().SetRangeUser(0.01,themax)
	hVarMethod.SetLineColor(kGray+2)
	fnew.cd()
	plotname = shortname.replace('_','')
	c1 = mkcanvas('c_'+plotname)
	fnew.mkdir(shortname.replace('_',''))
	if 'Bin' in name: 
		hVarMethodCorrected, hVarCorrectionFactor = makeClosureCorrectionAndUncertainty(hVarMethod, hVarTruth)
		fnew.cd()
		hVarMethodCorrected.Write()
		if usePredictionWithClosureCorrection:
			fnew.cd(plotname) 
			hVarCorrectionFactor.Write()		
			fnew.cd('../')				
			#for ibin in range(1, xax.GetNbins()+1): print 'after', ibin, hVarCorrectionFactor.GetBinContent(ibin)
			hVarMethod = hVarMethodCorrected
			
	hvariations = []
	for f in listOfVariationFiles:
		hAlt = f.Get(methodname)
		hAlt.SetDirectory(0)
		hAlt.SetLineColor(kAzure)
		hAlt.SetTitle('')
		hAlt.Draw('same hist')
		hRatioVariation = hAlt.Clone()
		hRatioVariation.Divide(hVarMethod)
		fnew.cd()
		fnew.cd(plotname)
		hAlt.Write(methodname+'variation')
		hRatioVariation.Write(methodname+'varyRatio')
		fnew.cd('../')
		hvariations.append(hAlt)
		for ibin in range(1, xax.GetNbins()+1): 
			olderr = hVarMethod.GetBinError(ibin)
			syst = abs(hVarMethod.GetBinContent(ibin)-hAlt.GetBinContent(ibin))
			hVarMethod.SetBinError(ibin, TMath.Sqrt(pow(olderr,2)+pow(syst,2)))
			
	hratio = FabDraw(c1,leg,hVarTruth,[hVarMethod],datamc='MC',lumi=lumi, title = '', LinearScale=False, fractionthing='method / truth')
	#hratio.GetYaxis().SetRangeUser(0.0,2.5)
	hratio.GetYaxis().SetRangeUser(0.001,5.001)	
	#hratio.GetYaxis().SetRangeUser(-3,3)		
	hratio.SetLineColor(kBlack)
	hratio.SetMarkerColor(kBlack)
	hratio.SetDirectory(0)
	c1.cd(2)
	c1.SetLogy()
	c1.Update()
	c1.cd(1)
	hVarMethod.SetTitle('')
	hVarTruth.SetTitle('')	
	hVarControl.SetTitle('')		
	hVarControl.Draw('same p')
	if drawVariations:
		for hvari in hvariations: hvari.Draw('same')
			
	c1.Update()
	fnew.cd()
	c1.Write()
	c1.Print('pdfs/closure/prompt-bkg/'+shortname.replace('_','')+'.pdf')
	clist.append(c1)
	#c1.Delete()
	hratios.append(hratio)
	c1.Update()
	#pause()

print 'test a'
	
import os, sys
print 'test b'
print 'just created', os.getcwd()+'/'+fnew.GetName()
fnew.Close()
print 'test c'

	
	
