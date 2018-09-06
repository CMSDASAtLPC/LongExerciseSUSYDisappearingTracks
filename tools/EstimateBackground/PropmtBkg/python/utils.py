from ROOT import *

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

PtBinEdges = [15, 20, 30, 40, 50, 70, 90, 120, 200, 300, 310]
EtaBinEdges = [0,1.4442,1.566,2.4]

def histoStyler(h,color):
    h.SetLineWidth(2)
    h.SetLineColor(color)
    h.SetMarkerColor(color)
    #h.SetFillColor(color)
    size = 0.055
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
    h.Sumw2()

def fillth1(h,x,weight=1):
        h.Fill(min(max(x,h.GetXaxis().GetBinLowEdge(1)+epsilon),h.GetXaxis().GetBinLowEdge(h.GetXaxis().GetNbins()+1)-epsilon),weight)

def fillth2(h,x,y,weight=1):
        h.Fill(min(max(x,h.GetXaxis().GetBinLowEdge(1)+epsilon),h.GetXaxis().GetBinLowEdge(h.GetXaxis().GetNbins()+1)-epsilon), min(max(y,h.GetYaxis().GetBinLowEdge(1)+epsilon),h.GetYaxis().GetBinLowEdge(h.GetYaxis().GetNbins()+1)-epsilon),weight)

def overflow(h):
    bin = h.GetNbinsX()+1
    c = h.GetBinContent(bin)
    h.AddBinContent((bin-1),c)
#.GetXaxis()
def histoStylerDPS(h):
        h.SetLineWidth(2)
        size = 0.055
        font = 132
        #h.SetTitleFont(font)
        h.GetXaxis().SetLabelFont(font)
        h.GetYaxis().SetLabelFont(font)
        #h.GetXaxis().SetTitleFont(font)
        #h.GetYaxis().SetTitleFont(font)
        h.GetYaxis().SetTitleSize(size)
        h.GetXaxis().SetTitleSize(size)
        h.GetXaxis().SetLabelSize(size)   
        h.GetYaxis().SetLabelSize(size)
        h.GetXaxis().SetTitleOffset(0.95)
        h.GetYaxis().SetTitleOffset(0.8)

#def mkcanvas(name):
#    c1 = TCanvas(name)
#    c1.SetBottomMargin(.125)
#    c1.SetLeftMargin(.12)
#    c1.SetTopMargin(.13)
#    c1.SetRightMargin(.04)
#    return c1    

def mkcanvas(name):
    c1 = TCanvas(name,name,700,630)
    c1.SetBottomMargin(.15)
    c1.SetLeftMargin(.14)
    #c1.SetTopMargin(.13)
    #c1.SetRightMargin(.04)
    return c1

def mklegend(x1=.4105, y1=.423, x2=.8805, y2=.58, color=kWhite):
    lg = TLegend(x1, y1, x2, y2)
    lg.SetFillColor(color)
    lg.SetTextFont(42)
    lg.SetBorderSize(0)
    lg.SetShadowColor(kWhite)
    lg.SetFillStyle(0)
    return lg


def namewizard(name):
    if 'Mht' in name:
        return 'Offline H_{T}^{miss} [GeV]'
    if 'Met' in name:
        return 'Offline E_{T}^{miss} [GeV]'
    if 'Ht' in name:
        return 'Offline HT [GeV]'
    return name

def prephisto(hLil,color):
    hLil.SetLineColor(color)
    hLil.SetMarkerColor(color)
    hLil.SetLineWidth(1)
    hLil.SetFillColor(color)
    return 0



def specialDraw(h,c1, scale, options=''):
    shpings = ['']
    t = TLatex()
    t.SetTextSize(0.025)
    t.SetTextAlign(22)
    nbins = h.GetXaxis().GetNbins()
    binsize = ( h.GetXaxis().GetBinLowEdge(1)+h.GetXaxis().GetBinLowEdge(nbins))/nbins
    hNorm = h.Clone('hNorm')
    hNorm.Scale(scale)
    #hNorm.UseCurrentStyle()
    #h.UseCurrentStyle()
    for ibin in range(1,nbins+1):
        x = h.GetXaxis().GetBinCenter(ibin)
        y = hNorm.GetBinContent(ibin)+0.022
        thing = str(h.GetBinContent(ibin))
        thing = thing[:thing.rfind('.')]
        shpings.append([x,y,thing])   
    if 'noline' not in options:
        hNorm.Draw('same')
    c1.Update()
    for ibin in range(1,nbins+1):
        print '0,1,2=',shpings[ibin][0],shpings[ibin][1],shpings[ibin][2]
        t.DrawLatex(shpings[ibin][0],shpings[ibin][1],shpings[ibin][2])


def getscale(key, lumi):
    if lumi=='3InvFb':
        if key == 'Qcd_Pt120To170':
            return 409.0
        if key == 'Qcd_Pt300To470':
            return 8.0
        if key == 'Qcd_Pt600To800':
            return 2.0
    if lumi=='1InvFb':
        if key == 'Qcd_Pt120To170':
            return 409.0
        if key == 'Qcd_Pt300To470':
            return 8.0
        if key == 'Qcd_Pt600To800':
            return 2.0
    return 1

def mkTriggerName(key):
    if key=="Met":
        return "HLT_PFMET170_NoiseCleaned"
    if key=="EleHT":
        return "HLT_Ele15_IsoVVVL_PFHT600"
    if key=="MuHT":
        return "HLT_Mu15_IsoVVVL_PFHT600"
    if key=="SingleEleHT":
        return "HLT_Ele15_IsoVVVL_PFHT600"
    if key=="EleHTBTag":
        return "HLT_Ele15_IsoVVVL_PFHT600 || HLT_Ele15_IsoVVVL_BTagCSV0p72_PFHT400"
    if key=="MuHTBTag":
        return "HLT_Mu15_IsoVVVL_PFHT600 || HLT_Mu15_IsoVVVL_BTagCSV0p72_PFHT400"
    if key=='SingleEleDoubleEG':
        return "(Single || Double) e"
    if key=='SingleMuDoubleMu':
        return "SingleMu || DoubleMu"
    if key=='SingleEleDoubleEGSingleMuDoubleMu':
        return 'SingleEle || DoubleEG || SingleMu || DoubleMu'
    if key=='SingleEle_DoubleEG':
        return 'SingleE27 || DoubleE24_22'
    return key

def FixEfficiency(gEff,hPass):
    for ibin in range(1,hPass.GetXaxis().GetNbins()+1):
        cv = gEff.GetY()[ibin]
        if abs(gEff.GetX()[ibin]-750)<1:
            print 'first errory(ibin)=',gEff.GetX()[ibin],gEff.GetErrorY(ibin)
        try:
            cvmo = gEff.GetY()[ibin-1]
            #print 'cv, cvmo=',cv,cvmo
            if cv-gEff.GetErrorYlow(ibin)<cvmo-gEff.GetErrorYlow(ibin-1) and cv-(cvmo-gEff.GetErrorYlow(ibin-1))>0:
                print 'changing'
                gEff.SetPointError(ibin, gEff.GetErrorXlow(ibin), gEff.GetErrorXhigh(ibin), cv-(cvmo-gEff.GetErrorYlow(ibin-1)), gEff.GetErrorYhigh(ibin))
        except: 
            pass
        if abs(gEff.GetX()[ibin]-750)<1:
            print 'then errory(ibin)=',gEff.GetX()[ibin],gEff.GetErrorY(ibin)


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
def stamp(lumi):
    tl.SetTextFont(cmsTextFont)
    tl.SetTextSize(.94*tl.GetTextSize())
    tl.DrawLatex(0.155,.905, 'CMS')
    tl.SetTextFont(extraTextFont)
    tl.SetTextSize(1.0/1.04*tl.GetTextSize())
    xlab = 0.24
    tl.DrawLatex(xlab,.905, ('MC' in datamc)*' simulation '+'preliminary')
    tl.SetTextFont(regularfont)
#    tl.DrawLatex(0.68,.92,'#sqrt{s} = 13 TeV')#(L = '+str(lumi)+' '#fb^{-1}')

def stampE(energy):
    tl.SetTextFont(cmsTextFont)
    tl.SetTextSize(.81*tl.GetTextSize())
    tl.SetTextFont(regularfont)
    tl.DrawLatex(0.61,.905,'L = 35.9fb^{-1}(#sqrt{s} = 13 TeV)')#(L = '+str(lumi)+' '#fb^{-1}')        


