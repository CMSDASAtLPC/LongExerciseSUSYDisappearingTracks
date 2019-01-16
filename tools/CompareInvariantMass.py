from ROOT import *
from utils import *
gStyle.SetOptStat(0)
gROOT.SetBatch(1)

drawttbar = True
files = [TFile('RawKappaMaps/RawKapps_AllMC_PixAndStrips.root'),TFile('RawKappaMaps/RawKapps_AllMC_PixOnly.root'),TFile('RawKappaMaps/RawKapps_Run2016_PixAndStrips.root'), TFile('RawKappaMaps/RawKapps_Run2016_PixOnly.root')]

labels = {}
files[0].ls()

c1 = mkcanvas('c1')
#c1.SetLogy()

newkeys = files[0].GetListOfKeys()
for file in files:
  lilbit = file.GetName().split('RawKapps_')[1].replace('.root','')
  fnew_ = TFile('InvMass'+lilbit+'.root','recreate')
  for key_ in newkeys:
	key = key_.GetName()
	if not ('hInvMass' in key): continue
	if not ('_RECOden' in key): continue
	if 'eta1.4442to1.566' in key: continue
	etarange, ptrange = key.split('_')[1], key.split('_')[2]
	leg = mklegend(x1=.12, y1=.54, x2=.59, y2=.68, color=kWhite)
	print 'getting', key
	shortbit = file.GetName().split('_')[1].replace('.root','').replace('Run ','Run')
	#h1.Rebin()
	h1 = file.Get(key)	
	h2 = file.Get(key.replace('_RECOden','_DTnum'))
	#h2.Rebin()	
	if 'El' in key: 
		h1.SetFillColor(kTeal)		
		h2.SetMarkerColor(kGreen+3)
		h2.SetLineColor(kGreen+3)		
		lepname = '#e'
		h1.SetTitle('DY Z#rightarrow ee')
	if 'Mu' in key: 
		lepname = '#mu'		
		h1.SetFillColor(kViolet)
		h1.SetFillColor(kViolet)		
		h2.SetMarkerColor(kMagenta+3)
		h2.SetLineColor(kMagenta+3)		
		
	h1.SetTitle(shortbit+ ' Tag + smeared '+lepname)		
	h1.SetLineColor(kGray+2)
	h2.SetTitle(shortbit+ ' Tag + dis. trk')
	h1.SetFillStyle(1001)
	
	int1 = h1.Integral(-1,9999)
	int2 = h2.Integral(-1,9999)	
	if int1>0: h1.Scale(1.0/int1)
	if int2>0: h2.Scale(1.0/int2)
	h1.GetYaxis().SetRangeUser(0.0001+0.1*min(h1.GetMinimum(0.001),h2.GetMinimum(0.001)), 0.0002+2*max(h1.GetMaximum(), h2.GetMaximum()))
	
	hratio = FabDraw(c1,leg,h2,[h1],datamc='Data',lumi='', title = '', LinearScale=True, fractionthing='(mc-data)/data')
	h2.GetYaxis().SetRangeUser(0.0001+0.1*min(h1.GetMinimum(0.001),h2.GetMinimum(0.001)), 0.0002+2*max(h1.GetMaximum(), h2.GetMaximum()))
	hratio.GetYaxis().SetRangeUser(0.001,4.99)
	hratio.GetXaxis().SetTitle('m(tag, probe) [GeV]')
	range = (etarange+' '+ptrange).replace('to','-').replace('eta', '|eta|=').replace('pt', 'p_{T}=')
	tl.DrawLatex(0.6,0.7,range)
	if 'AllMC' in file.GetName():
		fCompanion = TFile(file.GetName().replace('AllMC','TTJets'))
		hCompanion = fCompanion.Get(key.replace('_RECOden','_DTnum'))
		hCompanion.SetLineColor(kOrange)
		hCompanion.SetMarkerColor(kOrange)
		hCompanion.SetMarkerStyle(h2.GetMarkerStyle())		
		#hCompanion.SetFillStyle(1001)
		if int2>0: hCompanion.Scale(1.0/int2)
		hCompanion.Draw('same')
		leg.AddEntry(hCompanion,'t#bar{t} MC','p')
		
	c1.Update()
	#pause()	
	fnew_.cd()
	c1.Write(shortbit.replace(' ','')+key)
	print 'making pdf associated with', file	
	c1.Print(('pdfs/tagandprobe/'+lilbit+key.replace('_RECOden','')).replace('.','p')+'.pdf')
print 'just created', fnew_.GetName()
fnew_.Close()
exit(0)
