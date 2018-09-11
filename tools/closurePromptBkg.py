from ROOT import *
from utils import *
from utilsII import *
import os, sys
from glob import glob
gStyle.SetOptStat(0)
gROOT.SetBatch(1)

try: fname = sys.argv[1]
except: fname = 'test.root'

try: fnameOut = sys.argv[2]
except: fnameOut = 'closure.root'

lumi = 35900

BkgComponents = {}
BkgComponents['TTJets'] = ['TTJets_TuneCUETP8M1','TTJets_HT-600to800','TTJets_HT-1200to2500','TTJets_HT-2500toInf']
hBkgComponents = {}
#for bkgkey in BkgComponents:
#	fStarter = TFile('Output/closureLumiXsec/'+bkgkey)

infile = TFile(fname)
infile.ls()

fnew = TFile(fnameOut,'recreate')

keys = infile.GetListOfKeys()
for key in keys:
	infile.cd()
	name = key.GetName()
	print name
	if not 'Control' in name: continue
	hVarControl = infile.Get(name)
	hVarControl.SetTitle('single el.')	
	hVarTruth = infile.Get(name.replace('Control','Truth'))
	hVarTruth.SetTitle('dis track (truth)')		
	hVarMethod = infile.Get(name.replace('Control','Method'))	
	hVarMethod.SetTitle('weighted single el.')
	shortname = name[1:].replace('Control','').replace('Truth','').replace('Method','')
	varname = shortname.split('_')[-1]
	hVarControl.GetXaxis().SetTitle(namewizard(varname))
	hVarTruth.GetXaxis().SetTitle(namewizard(varname))
	hVarMethod.GetXaxis().SetTitle(namewizard(varname))
		
	hVarControl.Scale(1) #lumi*1.0/hHt.Integral(-1,9999))
	hVarTruth.Scale(1) #lumi*1.0/hHt.Integral(-1,9999))
	hVarMethod.Scale(1) #lumi*1.0/hHt.Integral(-1,9999))

	c1 = mkcanvas('c_'+shortname.replace('_',''))
	print 'name, canvname = ', name, c1.GetName()
	leg = mklegend(x1=.52, y1=.54, x2=.99, y2=.76, color=kWhite)
	leg.AddEntry(hVarControl,'single e','l')
	#hVarMethod.Scale()
	themax = 1000*max([hVarControl.GetMaximum(),hVarMethod.GetMaximum(),hVarTruth.GetMaximum()])
	hVarMethod.GetYaxis().SetRangeUser(0.01,themax)
	hVarMethod.SetFillStyle(1001)
	hVarMethod.SetFillColor(hVarMethod.GetLineColor())	
	hVarTruth.GetYaxis().SetRangeUser(0.01,themax)
	hVarControl.GetYaxis().SetRangeUser(0.01,themax)
	hratio = FabDraw(c1,leg,hVarTruth,[hVarMethod],datamc='MC',lumi=35.9, title = '', LinearScale=False, fractionthing='method / truth')
	hratio.GetYaxis().SetRangeUser(0.0,2.5)
	hratio.SetLineColor(kBlack)
	hratio.SetMarkerColor(kBlack)
	c1.Update()
	c1.cd(1)
	hVarControl.Draw('same p')
	c1.Update()
	#c1.Print('pdfs/closureTests/'+shortname.replace('_','')+'.pdf')
	#pause()
	fnew.cd()
	c1.Write()
	
print 'just created', fnew.GetName()
fnew.Close()
	
	
