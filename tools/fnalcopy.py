import glob

path = "/pnfs/desy.de/cms/tier2/store/user/sbein/NtupleHub/Production2016v2/"

with open("commands", "w") as fo:
    
    for iFile in glob.glob(path + "/*root"):
    
        #for sample in ["Summer16.TTJets", "Run2016C", "Summer16.DYJets", "Summer16.ZJets"]:
        for sample in ["Summer16.QCD_HT", "Summer16.WJets", "Summer16.ZJets", "Summer16.WZ", "Summer16.WW", "Summer16.ZZ"]:

            if sample not in iFile: continue
    
            filename = iFile.split("/")[-1]
            command = "xrdcp root://dcache-cms-xrootd.desy.de/%s root://cmseos.fnal.gov//store/user/lpcsusyhad/sbein/cmsdas19/Ntuples/%s" % (iFile, filename)
            fo.write(command + "\n")
