from ROOT import *
from array import array

r'''
of the barrel (|eta| < 1.4442). The outer circumferences of the endcaps are obscured by services passing between the barrel and the endcaps, and this area is removed from the fiducial region by excluding the first ring of trigger towers of the endcaps (|eta| > 1.566). The fiducial region terminates at |eta| = 2.5 where the tracker coverage ends.
'''

PtBinEdges = [15, 30, 50, 70, 90, 120, 200, 300, 310]#for Akshansh
EtaBinEdges = [0,1.4442,1.566,2.4]# for Akshansh

PtBinEdges = [15, 30, 60, 120, 130]#try squat little bins
EtaBinEdges = [0,1.4442,1.566,2.4]

PtBinEdges = [0,20, 30,40, 50, 70, 90, 120, 200, 300, 310]
EtaBinEdges = [0,1.4442,1.566,2.4]

tl = TLatex()
tl.SetNDC()
cmsTextFont = 61
extraTextFont = 52
lumiTextSize = 0.6
lumiTextOffset = 0.2
cmsTextSize = 0.75
cmsTextOffset = 0.1
regularfont = 42
originalfont = tl.GetTextFont()
epsi = "#scale[1.3]{#font[122]{e}}"
epsilon = 0.0001

#ptbins = [(15, 30), (30,60), (60,90),(90,9999)]
#etabins = [(0,1.1), (1.1,2.5)]

#ptbins = [(15, 9999)]
#etabins = [(0, 2.5)]


binning = {}
binning['Met']=[0,20,50,100,150,200,300,600,900]
binning['Mht']=binning['Met']
#binning['TrkPt']=[15,30,50,100,300]
#binning['TrkPt']=[15,30,50,70,90,120,200,300,400,410]#good for gen check, and two eta bins
#binning['TrkPt']=[15,30,50,70,90,120,200,300,310]
binning['TrkPt']=PtBinEdges#[15, 30, 60, 120, 130]#just seemed to work very well
#binning['TrkEta']=[0,1.4442,1.566,2.4]
binning['TrkEta']=EtaBinEdges
binning['TrkLen']=[2, 1, 3]
binning['NJets']=[10,0,10]
binning['NLeptons']=[5,0,5]
binning['BTags']=[0,1,2,3,4,5,6,7]
binning['Ht']=[10,0,2000]
binning['MinDeltaPhiMhtJets'] = [8,0,3.2]

#ptbins = [(15, 30),(30,50),(50,90),(90,9999)]
#etabins = [(0,1.1), (1.1,1.9), (1.9,2.4)]

#ptbins = [(15, 30),(30,50),(50,70),(70,90),(90,120),(120,300)]
#etabins = [(0,0.2),(0.2,0.4),(0.4,0.6),(0.6,0.8),(0.8,1.0),(1.0,1.2),(1.2,1.4),(1.4,1.6),(1.6,1.8),(1.8,2.0),(2.0,2.2),(2.2,2.4)]

def findbin(thebins, value):
	for bin in thebins:
		if value>=bin[0] and value<=bin[1]:
			return bin
	if value>thebins[-1]: return thebins[-1]
	if value<thebins[0]: return thebins[0]	




selectionsets = {}
inf = 9999
#selectionsets order: HT,MET,NJets,DeltaPhi1,DeltaPhi2
selectionsets['nocuts'] = [(0,inf),(0,inf),(0,inf),(0,inf),(0,inf)]
selectionsets['highmet'] = [(0,inf),(250,inf),(0,inf),(0,inf),(0,inf)]
CutStages = {}
CutStages[1] = 'All tracks'
CutStages[2] = 'pt>15, |eta|<2.4'
CutStages[3] = 'd(xy)<0.02/0.01'#0.02 if pixel-only
CutStages[4] = 'd(z)<0.05'
CutStages[5] = 'Neut. PF sum (#DeltaR<0.05)'
CutStages[6] = 'Ch. PF sum (DeltaR,0.01)'
CutStages[7] = 'PF lepton overlap'
CutStages[8] = 'PF relIso < 0.2'
CutStages[9] = 'PF absIso < 10.0'
CutStages[10] = '#geq2 hits, #geq2 layers'
CutStages[11] = 'NO lost inner hits'
CutStages[12] = '#geq2 lost outer hits'
CutStages[13] = 'pT resolution'
CutStages[14] = 'High purity'


def histoStyler(h,color):
	h.SetLineWidth(2)
	h.SetLineColor(color)
	h.SetMarkerColor(color)
	#h.SetFillColor(color)
	size = 0.059
	font = 132
	h.GetXaxis().SetLabelFont(font)
	h.GetYaxis().SetLabelFont(font)
	h.GetXaxis().SetTitleFont(font)
	h.GetYaxis().SetTitleFont(font)
	h.GetYaxis().SetTitleSize(size)
	h.GetXaxis().SetTitleSize(size)
	h.GetXaxis().SetLabelSize(size)   
	h.GetYaxis().SetLabelSize(size)
	h.GetXaxis().SetTitleOffset(1.0)
	h.GetYaxis().SetTitleOffset(1.05)
	if not h.GetSumw2N(): h.Sumw2()
	
def makeHist(name, title, nb, low, high, color):
	h = TH1F(name,title,nb,low,high)
	histoStyler(h,color)
	return h

def makeTh1(name, title, nbins, low, high, color=kBlack): 
	h = TH1F(name, title, nbins, low, high)
	histoStyler(h, color)
	return h
	
	
def makeTh1VB(name, title, nbins, arrayOfBins): 
	h = TH1F(name, title, nbins, np.asarray(arrayOfBins, 'd'))
	histoStyler(h, 1)
	return h
	
	
def graphStyler(g,color):
	g.SetLineWidth(2)
	g.SetLineColor(color)
	g.SetMarkerColor(color)
	#g.SetFillColor(color)
	size = 0.055
	font = 132
	g.GetXaxis().SetLabelFont(font)
	g.GetYaxis().SetLabelFont(font)
	g.GetXaxis().SetTitleFont(font)
	g.GetYaxis().SetTitleFont(font)
	g.GetYaxis().SetTitleSize(size)
	g.GetXaxis().SetTitleSize(size)
	g.GetXaxis().SetLabelSize(size)   
	g.GetYaxis().SetLabelSize(size)
	g.GetXaxis().SetTitleOffset(1.0)
	g.GetYaxis().SetTitleOffset(1.05)

def mkcanvas(name='c1'):
	c1 = TCanvas(name,name,750,630)
	c1.SetBottomMargin(.15)
	c1.SetLeftMargin(.14)
	#c1.SetTopMargin(.13)
	#c1.SetRightMargin(.04)
	return c1

def mkcanvas_wide(name):
	c1 = TCanvas(name,name,1200,700)
	c1.Divide(2,1)
	c1.GetPad(1).SetBottomMargin(.14)
	c1.GetPad(1).SetLeftMargin(.14)
	c1.GetPad(2).SetBottomMargin(.14)
	c1.GetPad(2).SetLeftMargin(.14)    
	c1.GetPad(1).SetGridx()
	c1.GetPad(1).SetGridy()
	c1.GetPad(2).SetGridx()
	c1.GetPad(2).SetGridy()    
	#c1.SetTopMargin(.13)
	#c1.SetRightMargin(.04)
	return c1

def mklegend(x1=.22, y1=.66, x2=.69, y2=.82, color=kWhite):
	lg = TLegend(x1, y1, x2, y2)
	lg.SetFillColor(color)
	lg.SetTextFont(42)
	lg.SetBorderSize(0)
	lg.SetShadowColor(kWhite)
	lg.SetFillStyle(0)
	return lg
	
def mklegend_(x1=.22, y1=.66, x2=.69, y2=.82, color=kWhite):
	lg = TLegend(x1, y1, x2, y2)
	lg.SetFillColor(color)
	lg.SetTextFont(42)
	lg.SetBorderSize(0)
	lg.SetShadowColor(kWhite)
	lg.SetFillStyle(0)
	return lg

def fillth1(h,x,weight=1):
	h.Fill(min(max(x,h.GetXaxis().GetBinLowEdge(1)+epsilon),h.GetXaxis().GetBinLowEdge(h.GetXaxis().GetNbins()+1)-epsilon),weight)

def fillth2(h,x,y,weight=1):
	h.Fill(min(max(x,h.GetXaxis().GetBinLowEdge(1)+epsilon),h.GetXaxis().GetBinLowEdge(h.GetXaxis().GetNbins()+1)-epsilon), min(max(y,h.GetYaxis().GetBinLowEdge(1)+epsilon),h.GetYaxis().GetBinLowEdge(h.GetYaxis().GetNbins()+1)-epsilon),weight)


def namewizard(name):
	if 'Mht' == name:
		return r'H_{T}^{miss} [GeV]'
	if 'Met' == name:
		return r'E_{T}^{miss} [GeV]'
	if 'Ht' == name:
		return r'H_{T} [GeV]'
	if 'NJets' == name:
		return r'n_{j}'        
	if 'BTags' == name:
		return r'n_{b}'                
	if 'MinDeltaPhiMetJets' == name:
		return r'#Delta#phi_{min}'                        
	if 'NLeptons' == name:
		return r'n_{#ell}'
	if 'NMuons' == name:
		return r'n(#mu)'
	if 'NTags' == name:
		return r'n_{DT}'
	if 'SumTagPtOverMet' == name:
		return r'R^{*}'
	if 'DPhiMetSumTags' == name:
		return r'#Delta#phi^{*}'
	return name

def mkEfficiencies(hPassList, hAllList):
	gEffList = []
	for i in range(len(hPassList)):
		hPassList[i].Sumw2()
		hAllList[i].Sumw2()
		g = TGraphAsymmErrors(hPassList[i],hAllList[i],'cp')
		FixEfficiency(g,hPassList[i])
		g.SetMarkerSize(3)
		gEffList.append(g)
	return gEffList

def Struct(*args, **kwargs):
	def init(self, *iargs, **ikwargs):
		for k,v in kwargs.items():
			setattr(self, k, v)
		for i in range(len(iargs)):
			setattr(self, args[i], iargs[i])
		for k,v in ikwargs.items():
			setattr(self, k, v)

	name = kwargs.pop("name", "MyStruct")
	kwargs.update(dict((k, None) for k in args))
	return type(name, (object,), {'__init__': init, '__slots__': kwargs.keys()})


def mkHistoStruct(hname):
	if '_' in hname: var = hname[hname.find('_')+1:]
	else: var =  hname
	histoStruct = Struct('Truth','Control','Method')
	if len(binning[var])==3:
		nbins = binning[var][0]
		low = binning[var][1]
		high = binning[var][2]
		histoStruct.Truth = TH1F('h'+hname+'Truth',hname+'Truth',nbins,low,high)
		histoStruct.Control = TH1F('h'+hname+'Control',hname+'Control',nbins,low,high)
		histoStruct.Method = TH1F('h'+hname+'Method',hname+'Method',nbins,low,high)
	
	else:
		nBin = len(binning[var])-1
		binArr = array('d',binning[var])
		histoStruct.Truth = TH1F('h'+hname+'Truth',hname+'Truth',nBin,binArr)
		histoStruct.Control = TH1F('h'+hname+'Control',hname+'Control',nBin,binArr)
		histoStruct.Method = TH1F('h'+hname+'Method',hname+'Method',nBin,binArr)
	histoStyler(histoStruct.Truth,kBlack)
	histoStyler(histoStruct.Control,kTeal-1)
	histoStyler(histoStruct.Method,kAzure-2)
	histoStruct.Method.SetFillStyle(1001)
	histoStruct.Method.SetFillColor(histoStruct.Method.GetLineColor()+1)
	return histoStruct


def writeHistoStruct(hStructDict):
	for key in hStructDict:
		#print 'writing histogram structure:', key
		hStructDict[key].Truth.Write()
		hStructDict[key].Control.Write()
		hStructDict[key].Method.Write()
	
def mkEfficiencyRatio(hPassList, hAllList,hName = 'hRatio'):#for weighted MC, you need TEfficiency!
	hEffList = []
	for i in range(len(hPassList)):
		hPassList[i].Sumw2()
		hAllList[i].Sumw2()    
		g = TGraphAsymmErrors(hPassList[i],hAllList[i],'cp')
		print 'RATIO........'
		FixEfficiency(g,hPassList[i])
		hEffList.append(hPassList[i].Clone('hEff'+str(i)))
		hEffList[-1].Divide(hAllList[i])
		cSam1 = TCanvas('cSam1')
		print 'this is the simply divided histogram:'
		hEffList[-1].Draw()
		cSam1.Update()

		print 'now putting in the uncertainties under ratio'
		for ibin in range(1,hEffList[-1].GetXaxis().GetNbins()+1):
			print 'setting errory(ibin)=',ibin,g.GetX()[ibin],g.GetErrorY(ibin)
			print 'compared with histo',ibin,
			hEffList[-1].SetBinError(ibin,1*g.GetErrorY(ibin-1))
			print 'errory(ibin)=',g.GetX()[ibin],g.GetErrorY(ibin-1)
		#histoStyler(hEffList[-1],hPassList[i].GetLineColor())

		cSam2 = TCanvas('cSam2')
		print 'this is the after divided histogram:'
		hEffList[-1].Draw()
		cSam2.Update()


		hEffList[-1].Draw()
	hRatio = hEffList[0].Clone(hName)
	hRatio.Divide(hEffList[1])
	hRatio.GetYaxis().SetRangeUser(0.95,1.05)
	c3 = TCanvas()
	hRatio.Draw()
	c3.Update()
	return hRatio


def pause(str_='push enter key when ready'):
		import sys
		print str_
		sys.stdout.flush() 
		raw_input('')

datamc = 'MC'
def stamp(lumi='35.9', showlumi = False):    
	tl.SetTextFont(cmsTextFont)
	tl.SetTextSize(0.98*tl.GetTextSize())
	tl.DrawLatex(0.135,0.915, 'CMS')
	tl.SetTextFont(extraTextFont)
	tl.SetTextSize(1.0/0.98*tl.GetTextSize())
	xlab = 0.213
	tl.DrawLatex(xlab,0.915, ('MC' in datamc)*' simulation '+'preliminary')
	tl.SetTextFont(regularfont)
	tl.SetTextSize(0.81*tl.GetTextSize())    
	thingy = ''
	if showlumi: thingy+='#sqrt{s}=13 TeV, L = '+str(lumi)+' fb^{-1}'
	xthing = 0.6202
	if not showlumi: xthing+=0.13
	tl.DrawLatex(xthing,0.915,thingy)
	tl.SetTextSize(1.0/0.81*tl.GetTextSize())  
	
	
def stamp2(lumi='35.9', showlumi = False):    
	tl.SetTextFont(cmsTextFont)
	tl.SetTextSize(0.98*tl.GetTextSize())
	tl.DrawLatex(0.1,0.91, 'CMS')
	tl.SetTextFont(extraTextFont)
	tl.SetTextSize(1.0/0.98*tl.GetTextSize())
	xlab = 0.213
	tl.DrawLatex(xlab,0.91, ('MC' in datamc)*' simulation '+'preliminary')
	tl.SetTextFont(regularfont)
	tl.SetTextSize(0.81*tl.GetTextSize())    
	thingy = ''
	if showlumi: thingy+='#sqrt{s}=13 TeV, L = '+str(lumi)+' fb^{-1}'
	xthing = 0.6202
	if not showlumi: xthing+=0.13
	tl.DrawLatex(xthing,0.91,thingy)
	tl.SetTextSize(1.0/0.81*tl.GetTextSize()) 


#------------------------------------------------------------------------------
def mkcdf(hist, minbin=1):
	hist.Scale(1.0/hist.Integral(1,hist.GetXaxis().GetNbins()))
	c = [0.0]*(hist.GetNbinsX()-minbin+2+1)
	j=1
	for ibin in xrange(minbin, hist.GetNbinsX()+1):
		c[j] = c[j-1] + hist.GetBinContent(ibin)
		j += 1
	c[j] = hist.Integral()
	return c

def mkroc(name, hsig, hbkg, lcolor=kBlue, lwidth=2, ndivx=505, ndivy=505):
	from array import array
	csig = mkcdf(hsig)
	cbkg = mkcdf(hbkg)
	npts = len(csig)
	esig = array('d')
	ebkg = array('d')
	for i in xrange(npts):
		esig.append(1 - csig[npts-1-i])
		ebkg.append(1 - cbkg[npts-1-i])
	g = TGraph(npts,esig,ebkg)
	g.SetName(name)
	g.SetLineColor(lcolor)
	g.SetLineWidth(lwidth)

	g.GetXaxis().SetTitle("#epsilon_{s}")
	g.GetXaxis().SetLimits(0,1)

	g.GetYaxis().SetTitle("#epsilon_{b}")
	g.GetHistogram().SetAxisRange(0,1, "Y")

	g.GetHistogram().SetNdivisions(ndivx, "X")
	g.GetHistogram().SetNdivisions(ndivy, "Y")
	return g



def calcTrackIso(trk, tracks):
	ptsum =  -trk.pt()
	for track in tracks:
		dR = TMath.Sqrt( (trk.eta()-track.eta())**2 + (trk.phi()-track.phi())**2)
		if dR<0.3: ptsum+=track.pt()
	return ptsum/trk.pt()

def calcTrackJetIso(trk, jets):
	for jet in jets:
		if not jet.pt()>30: continue
		if  TMath.Sqrt( (trk.eta()-jet.eta())**2 + (trk.phi()-jet.phi())**2)<0.5: return False
	return True

def calcMiniIso(trk, tracks):
	pt = trk.pt()
	ptsum = -pt
	if pt<=50: R = 0.2
	elif pt<=200: R = 10.0/pt
	else: R = 0.05
	for track in tracks:
		dR = TMath.Sqrt( (trk.eta()-track.eta())**2 + (trk.phi()-track.phi())**2)
		if dR<R: ptsum+=track.pt()
	return ptsum/trk.pt()

def isMatched_(obj, col, dR=0.02, verbose = False):
	matchedIdx = -1
	bigDR = inf
	for ic, thing in enumerate(col):
		dr = thing[0].DeltaR(obj[0])
		if verbose: print 'dr=',dr
		if dr<dR:
			ismatched = True
			matchedIdx = ic
			break
	if matchedIdx<0: return False
	else: return col[matchedIdx]

def FabDraw(cGold,leg,hTruth,hComponents,datamc='mc',lumi=35.9, title = '', LinearScale=False, fractionthing='(bkg-obs)/obs'):
	cGold.cd()
	pad1 = TPad("pad1", "pad1", 0, 0.4, 1, 1.0)
	pad1.SetBottomMargin(0.0)
	pad1.SetLeftMargin(0.12)
	if not LinearScale:
		pad1.SetLogy()
	pad1.SetGridx()
	#pad1.SetGridy()
	pad1.Draw()
	pad1.cd()
	for ih in range(1,len(hComponents[1:])+1):
		print 'entry inventory', hComponents[ih].Integral(), hComponents[ih-1].Integral()
		print 'adding',hComponents[ih-1],'to', hComponents[ih]
		hComponents[ih].Add(hComponents[ih-1])
		print 'entry inventory', hComponents[ih].Integral(), hComponents[ih-1].Integral()        
	hComponents.reverse()        
	if abs(hComponents[0].Integral(-1,999)-1)<0.001:
		hComponents[0].GetYaxis().SetTitle('Normalized')
	else: hComponents[0].GetYaxis().SetTitle('#rho(Events)')
	cGold.Update()
	hTruth.GetYaxis().SetTitle('Normalized')
	hTruth.GetYaxis().SetTitleOffset(1.15)
	hTruth.SetMarkerStyle(20)
	histheight = 1.5*max(hComponents[0].GetMaximum(),hTruth.GetMaximum())
	if LinearScale: low, high = 0, histheight
	else: low, high = max(0.001,max(hComponents[0].GetMinimum(),hTruth.GetMinimum())), 1000*histheight
	
	title0 = hTruth.GetTitle()
	if datamc=='MC':
		leg.AddEntry(hComponents[0],hComponents[0].GetTitle(),'lf')
		leg.AddEntry(hTruth,hTruth.GetTitle(),'lpf')        
	else:
		for ihComp, hComp in enumerate(hComponents):
			leg.AddEntry(hComp, hComp.GetTitle(),'lpf')      
		leg.AddEntry(hTruth,title0,'lp')    
	hTruth.SetTitle('')
	hComponents[0].SetTitle('')	
	hComponents[0].Draw('hist')
	for h in hComponents[1:]: 
		h.Draw('hist same')
		cGold.Update()
		print 'updating stack', h
	hComponents[0].Draw('same') 
	hTruth.Draw('p same')
	hTruth.Draw('e same')    
	cGold.Update()
	#hTruth.Draw('E1 same')
	hComponents[0].Draw('axis same')                    
	leg.Draw()        
	cGold.Update()
	stampFab(lumi,datamc)
	cGold.Update()
	cGold.cd()
	pad2 = TPad("pad2", "pad2", 0, 0.05, 1, 0.4)
	pad2.SetTopMargin(0.0)
	pad2.SetBottomMargin(0.3)
	pad2.SetLeftMargin(0.12)
	pad2.SetGridx()
	pad2.SetGridy()
	pad2.Draw()
	pad2.cd()
	hTruthCopy = hTruth.Clone()
	hRatio = hComponents[0].Clone('hRatio')
	hRatio.SetMarkerStyle(20)
	#hFracDiff = hComponents[0].Clone('hFracDiff')
	#hFracDiff.SetMarkerStyle(20)
	hTruthCopy.SetMarkerStyle(20)
	hTruthCopy.SetMarkerColor(1)    
	#histoStyler(hFracDiff, 1)
	histoStyler(hTruthCopy, 1)
	#hFracDiff.Add(hTruthCopy,-1)
	#hFracDiff.Divide(hTruthCopy)
	hRatio.Divide(hTruthCopy)

	hRatio.GetYaxis().SetRangeUser(0.0,.1)###
	hRatio.SetTitle('')
	if 'prediction' in title0: hFracDiff.GetYaxis().SetTitle('(RS-#Delta#phi)/#Delta#phi')
	else: hRatio.GetYaxis().SetTitle(fractionthing)
	hRatio.GetXaxis().SetTitleSize(0.12)
	hRatio.GetXaxis().SetLabelSize(0.11)
	hRatio.GetYaxis().SetTitleSize(0.12)
	hRatio.GetYaxis().SetLabelSize(0.12)
	hRatio.GetYaxis().SetNdivisions(5)
	hRatio.GetXaxis().SetNdivisions(10)
	hRatio.GetYaxis().SetTitleOffset(0.5)
	hRatio.GetXaxis().SetTitleOffset(1.0)
	hRatio.GetXaxis().SetTitle(hTruth.GetXaxis().GetTitle())
	hRatio.Draw()
	hRatio.Draw('e0')    
	pad1.cd()
	hComponents.reverse()
	hTruth.SetTitle(title0)
	return hRatio



def stampFab(lumi,datamc='MC'):
	tl.SetTextFont(cmsTextFont)
	tl.SetTextSize(1.6*tl.GetTextSize())
	tl.DrawLatex(0.15,0.82, 'CMS')
	tl.SetTextFont(extraTextFont)
	tl.DrawLatex(0.23,0.82, ('MC' in datamc)*' simulation '+'preliminary')
	tl.SetTextFont(regularfont)
	#tl.DrawLatex(0.57,0.82,'#sqrt{s} = 13 TeV, L = '+str(lumi)+' fb^{-1}')
	tl.SetTextSize(tl.GetTextSize()/1.6)
	

def stampE(energy):
    tl.SetTextFont(cmsTextFont)
    tl.SetTextSize(.8*tl.GetTextSize())
    tl.SetTextFont(regularfont)
    tl.DrawLatex(0.68,.91,'#sqrt{s} = 13 TeV')#(L = '+str(lumi)+' '#fb^{-1}')##from Akshansh
    

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
    
    
def isBasicTrack(tree,itrack):		
	if not abs(track.Eta())<2.4: return False
	if not (abs(track.Eta())<1.4442 or abs(track.Eta())>1.566): return False		
	if not tree.tracks_trkRelIso[itrack]<0.2: return False		
	if not abs(tree.tracks_dxyVtx[itrack])<0.02: return False						
	if not abs(tree.tracks_dzVtx[itrack])<0.05: return False
	if not bool(tree.tracks_trackQualityHighPurity[itrack]): return False	
	if not (tree.tracks_nMissingInnerHits[itrack]==0): return False 		
	if not track.Pt()*tree.tracks_trkRelIso[itrack]<10: return False
	return True

	
def isDisappearingTrack_(track, itrack, c, readerPixelOnly, readerPixelStrips):###from Akshansh
        moh_ = c.tracks_nMissingOuterHits[itrack]
        phits = c.tracks_nValidPixelHits[itrack]
        thits = c.tracks_nValidTrackerHits[itrack]
        tlayers = c.tracks_trackerLayersWithMeasurement[itrack]
        pixelOnly = phits>0 and thits==phits
        medium = tlayers< 7 and (thits-phits)>0
        long   = tlayers>=7 and (thits-phits)>0
        pixelStrips = medium or long
        if pixelStrips:
                if not moh_>=2: return False
        if not (c.tracks_nMissingInnerHits[itrack]==0): return False
        if not (pixelOnly or pixelStrips): return False                                                                                                         
        if not c.tracks_passPFCandVeto[itrack]: return False
        pterr = c.tracks_ptError[itrack]/(track.Pt()*track.Pt())        
        dxyVtx = abs(c.tracks_dxyVtx[itrack])
        dzVtx = abs(c.tracks_dzVtx[itrack])        
        if not (c.tracks_trkRelIso[itrack]<0.2 and dzVtx<0.1 and pterr<10 and c.tracks_nMissingMiddleHits[itrack]==0): return False
        if not (c.tracks_trackQualityHighPurity[itrack]): return False
        nhits = c.tracks_nValidTrackerHits[itrack]
        nlayers = c.tracks_trackerLayersWithMeasurement[itrack]
        if not (nlayers>=2 and nhits>=2): return False
        matchedCalo = c.tracks_matchedCaloEnergy[itrack]
        if not c.tracks_chi2perNdof[itrack]<2.88: return False#
        if not dxyVtx < 0.1: return False#  
        trackfv = [dxyVtx, dzVtx, matchedCalo, c.tracks_trkRelIso[itrack], phits, thits, moh_, pterr]
        if pixelOnly:
                mva_ = evaluateBDT(readerPixelOnly, trackfv)
                if not mva_ > 0.4: return False###.4
                else: return mva_
        elif pixelStrips:
                mva_ = evaluateBDT(readerPixelStrips, trackfv)
                if not mva_ > 0.25:return False###.2
                else: return mva_
        else:
                return False
                
def isBaselineTrack(track, track_id, c):
	if not abs(track.Eta())< 2.4 : return False
	if (abs(track.Eta()) > 1.4442 and abs(track.Eta()) < 1.566): return False
	if not bool(c.tracks_trackQualityHighPurity[track_id]) : return False
	if not (c.tracks_ptError[track_id]/(track.Pt()*track.Pt()) < 10): return False
	if not abs(c.tracks_dxyVtx[track_id]) < 0.02: return False
	if not abs(c.tracks_dzVtx[track_id]) < 0.01 : return False
	if not c.tracks_trkRelIso[track_id] < 0.2: return False
	if not (c.tracks_trackerLayersWithMeasurement[track_id] >= 2 and c.tracks_nValidTrackerHits[track_id] >= 2): return False
	if not c.tracks_nMissingInnerHits[track_id]==0: return False
	return True
	                
def overflow(h):
    bin = h.GetNbinsX()+1
    c = h.GetBinContent(bin)
    h.AddBinContent((bin-1),c)
	
