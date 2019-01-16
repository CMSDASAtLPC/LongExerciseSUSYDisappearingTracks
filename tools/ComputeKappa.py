from ROOT import *
from utils import *
from namelib import *
import sys
from random import shuffle
gROOT.SetBatch(1)

gStyle.SetOptStat(0)
gStyle.SetFrameBorderMode(0)
gStyle.SetLegendBorderSize(0)
gStyle.SetLegendTextSize(0.026)
try:fname =sys.argv[1]
except:
    fname = 'TagnProbe_DYJetsToLL.root'
    print 'Histogram file not specified, will run default file:',fname

try:foname =sys.argv[2]
except:
    foname = 'Kappa.root'
    print 'Output file not specified, will create output as: Kappa.root'
file  = TFile(fname)
file.ls()

funcs = {}

keys = file.GetListOfKeys()

c1 = mkcanvas('c1')
fnew = TFile(foname,'recreate')
fnew.cd()

for key in keys:
    name = key.GetName()
    if not 'ProbePtDT_eta' in name: continue
    hnum   = file.Get(name)
    if 'Gen' in name: hnum.SetLineColor(kAzure)
    else: hnum.SetLineColor(kViolet)
    if 'Run' in fname: 
    	hnum.SetLineColor(kBlack)
    	hnum.SetMarkerStyle(20)
    	hnum.SetMarkerSize(.85*hnum.GetMarkerSize())
    hden    = file.Get(name.replace('_num','_den').replace('DT','RECO'))
    ratname = name.replace('_num','').replace('DT','Kappa')
    print 'ratname', ratname
    hratio = hnum.Clone(ratname)
    hratio.Divide(hden)

    
    hratio.SetTitle('')
    hratio.GetXaxis().SetTitle('p_{T}[GeV]')
    hratio.GetYaxis().SetTitle('#kappa = n(DT)/n(reco-lep)')    
    hratio.GetYaxis().SetLabelSize(0.05)
    hratio.GetXaxis().SetLabelSize(0.05)    
    hratio.GetYaxis().SetTitleOffset(1.25)
    hratio.Draw()
    #if 'El' in name: funcs['f1'+ratname] = TF1('f1'+ratname,'[0]+[1]/pow(x,.5)+[2]*exp(-[3]*pow(x-[4],2))',20,2000)
    #if 'Mu' in name: funcs['f1'+ratname] = TF1('f1'+ratname,'[0]+([1]/pow(x,2)+[2]/x)*exp(-[3]*pow(x-[4],2))',20,2000)
	#funcs['f1'+ratname] = TF1('f1'+ratname,'[0]+([1]/pow(x,1)+[2]/pow(x,2))+[3]*exp(-[4]*pow(x-350,2))',20,2000)
    #funcs['f1'+ratname] = TF1('f1'+ratname,'0.001*[0]+([1]/pow(x,1)+[2]/pow(x,2)+[5]/pow(x,3))+0.0002*exp(-[3]*pow(x-325,2))',20,2000)
    #funcs['f1'+ratname] = TF1('f1'+ratname,'0.001*[0] + [1]/pow(x,1) + [2]/pow(x,2)+[5]/pow(x,0.5) + 0.0002*exp(-[3]*pow(x-325,2))',20,2000)
    #funcs['f1'+ratname] = TF1('f1'+ratname,'0.001*[0] + [1]/pow(x,1) + [2]*x +[3]*exp(-[4]*(x-325)) ',20,2000)
    #funcs['f1'+ratname] = TF1('f1'+ratname,'0.01*[0] + 0.01*[1]/x + 0.01*[2]/x/x + [3]*exp(-[4]*x)',20,2500)
    funcs['f1'+ratname] = TF1('f1'+ratname,'0.1*[0] + 0.1*[1]/(pow(x,0.5)) + 0.1*[5]/(pow(x,1)) + 0.1*[2]/pow(x,2) + [3]*exp(-[4]*x)',30,2500)
    funcs['f1'+ratname].SetParLimits(0,0, 1.9)
    #funcs['f1'+ratname].SetParLimits(1,0, 9999)
    #funcs['f1'+ratname].SetParLimits(2,0, 9999)
    #funcs['f1'+ratname].SetParLimits(3,0, 0.999)
    #funcs['f1'+ratname].SetParLimits(4,200, 400)
            
    hratio.Fit('f1'+ratname,'','SN',30,2500)
    funcs['f1'+ratname].SetLineColor(hratio.GetLineColor())
    leg = mklegend(x1=.22, y1=.66, x2=.79, y2=.82)
    legname = ratname.split('_')[-1].replace('eta','eta ')
    if 'Gen' in name: legname+=' (W+Jets MC, 2016 geom)'
    leg.AddEntry(hratio,legname)
    leg.Draw()
    c1.Update()
    fnew.cd()
    hratio.Write(hratio.GetName())
    c1.Write('c_'+hratio.GetName())
    #hratio.Write()
    funcs['f1'+ratname].Write()


print 'just made', fnew.GetName()
fnew.Close()
exit(0)
