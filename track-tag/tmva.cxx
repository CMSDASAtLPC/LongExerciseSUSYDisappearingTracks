int tmva() {

    // short tracks:
    std::string path = "root://cmseos.fnal.gov//store/user/cmsdas/2019/long_exercises/DisappearingTracks/track-tag/tracks-pixelonly";

    // long tracks (uncomment to use path):
    // std::string path = "root://cmseos.fnal.gov//store/user/cmsdas/2019/long_exercises/DisappearingTracks/track-tag/tracks-pixelstrips";

    const char* treename = "PreSelection";

    TMVA::Tools::Instance();

    TFile* outputFile = TFile::Open("output.root", "RECREATE");

    TMVA::Factory *factory = new TMVA::Factory("TMVAClassification",outputFile,"V:!Silent:Color:Transformations=I:DrawProgressBar:AnalysisType=Classification"); 

    Double_t weight;
    Double_t lumi = 150000;       // 1/pb
    TH1D* Nev;

    TFile* fsignal = TFile::Open((path + "/signal.root").c_str());
    TTree* sgTree = (TTree*)(fsignal->Get(treename));
    Nev = (TH1D*)(fsignal->Get("Nev"));
    weight = 0.00276133 * lumi / Nev->GetBinContent(1);
    factory->AddSignalTree(sgTree, weight);
    
    TFile* fbackground_wjets_100To200 = TFile::Open((path + "/Summer16.WJetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_wjets_100To200 = (TTree*)(fbackground_wjets_100To200->Get(treename));
    Nev = (TH1D*)(fbackground_wjets_100To200->Get("Nev"));
    weight = 1627 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_wjets_100To200, weight);

    TFile* fbackground_wjets_200To400 = TFile::Open((path + "/Summer16.WJetsToLNu_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_wjets_200To400 = (TTree*)(fbackground_wjets_200To400->Get(treename));
    Nev = (TH1D*)(fbackground_wjets_200To400->Get("Nev"));
    weight = 435.2 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_wjets_200To400, weight);

    TFile* fbackground_wjets_400To600 = TFile::Open((path + "/Summer16.WJetsToLNu_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_wjets_400To600 = (TTree*)(fbackground_wjets_400To600->Get(treename));
    Nev = (TH1D*)(fbackground_wjets_400To600->Get("Nev"));
    weight = 59.18 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_wjets_400To600, weight);

    TFile* fbackground_wjets_800To1200 = TFile::Open((path + "/Summer16.WJetsToLNu_HT-800To1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_wjets_800To1200 = (TTree*)(fbackground_wjets_800To1200->Get(treename));
    Nev = (TH1D*)(fbackground_wjets_800To1200->Get("Nev"));
    weight = 6.66 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_wjets_800To1200, weight);

    TFile* fbackground_wjets_1200To2500 = TFile::Open((path + "/Summer16.WJetsToLNu_HT-1200To2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_wjets_1200To2500 = (TTree*)(fbackground_wjets_1200To2500->Get(treename));
    Nev = (TH1D*)(fbackground_wjets_1200To2500->Get("Nev"));
    weight = 1.608 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_wjets_1200To2500, weight);

    TFile* fbackground_wjets_2500ToInf = TFile::Open((path + "/Summer16.WJetsToLNu_HT-2500ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_wjets_2500ToInf = (TTree*)(fbackground_wjets_2500ToInf->Get(treename));
    Nev = (TH1D*)(fbackground_wjets_2500ToInf->Get("Nev"));
    weight = 0.03891 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_wjets_2500ToInf, weight);

    TFile* fbackground_ttjets = TFile::Open((path + "/Summer16.TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_ttjets = (TTree*)(fbackground_ttjets->Get(treename));
    Nev = (TH1D*)(fbackground_ttjets->Get("Nev"));
    weight = 831.8 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_ttjets, weight);

    TFile* fbackground_ttjets_600To800 = TFile::Open((path + "/Summer16.TTJets_HT-600to800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_RA2AnalysisTree.root").c_str());
    TTree* bgTree_ttjets_600To800 = (TTree*)(fbackground_ttjets_600To800->Get(treename));
    Nev = (TH1D*)(fbackground_ttjets_600To800->Get("Nev"));
    weight = 2.734 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_ttjets_600To800, weight);

    TFile* fbackground_ttjets_1200To2500 = TFile::Open((path + "/Summer16.TTJets_HT-1200to2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_RA2AnalysisTree.root").c_str());
    TTree* bgTree_ttjets_1200To2500 = (TTree*)(fbackground_ttjets_1200To2500->Get(treename));
    Nev = (TH1D*)(fbackground_ttjets_1200To2500->Get("Nev"));
    weight = 0.1979 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_ttjets_1200To2500, weight);

    TFile* fbackground_ttjets_2500ToInf = TFile::Open((path + "/Summer16.TTJets_HT-2500toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_RA2AnalysisTree.root").c_str());
    TTree* bgTree_ttjets_2500ToInf = (TTree*)(fbackground_ttjets_2500ToInf->Get(treename));
    Nev = (TH1D*)(fbackground_ttjets_2500ToInf->Get("Nev"));
    weight = 0.002368 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_ttjets_2500ToInf, weight);

    TFile* fbackground_dyjets = TFile::Open((path + "/Summer16.DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_RA2AnalysisTree.root").c_str());
    TTree* bgTree_dyjets = (TTree*)(fbackground_dyjets->Get(treename));
    Nev = (TH1D*)(fbackground_dyjets->Get("Nev"));
    weight = 6025.0 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_dyjets, weight);

    TFile* fbackground_dyjets_100To200 = TFile::Open((path + "/Summer16.DYJetsToLL_M-50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_dyjets_100To200 = (TTree*)(fbackground_dyjets_100To200->Get(treename));
    Nev = (TH1D*)(fbackground_dyjets_100To200->Get("Nev"));
    weight = 181.3 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_dyjets_100To200, weight);

    TFile* fbackground_dyjets_200To400 = TFile::Open((path + "/Summer16.DYJetsToLL_M-50_HT-200to400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_dyjets_200To400 = (TTree*)(fbackground_dyjets_200To400->Get(treename));
    Nev = (TH1D*)(fbackground_dyjets_200To400->Get("Nev"));
    weight = 50.42 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_dyjets_200To400, weight);

    TFile* fbackground_dyjets_400To600 = TFile::Open((path + "/Summer16.DYJetsToLL_M-50_HT-400to600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_dyjets_400To600 = (TTree*)(fbackground_dyjets_400To600->Get(treename));
    Nev = (TH1D*)(fbackground_dyjets_400To600->Get("Nev"));
    weight = 6.984 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_dyjets_400To600, weight);

    TFile* fbackground_dyjets_800To1200 = TFile::Open((path + "/Summer16.DYJetsToLL_M-50_HT-800to1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_dyjets_800To1200 = (TTree*)(fbackground_dyjets_800To1200->Get(treename));
    Nev = (TH1D*)(fbackground_dyjets_800To1200->Get("Nev"));
    weight = 0.7754 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_dyjets_800To1200, weight);

    TFile* fbackground_dyjets_1200To2500 = TFile::Open((path + "/Summer16.DYJetsToLL_M-50_HT-1200to2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_dyjets_1200To2500 = (TTree*)(fbackground_dyjets_1200To2500->Get(treename));
    Nev = (TH1D*)(fbackground_dyjets_1200To2500->Get("Nev"));
    weight = 0.1862 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_dyjets_1200To2500, weight);

    TFile* fbackground_dyjets_2500ToInf = TFile::Open((path + "/Summer16.DYJetsToLL_M-50_HT-2500toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_dyjets_2500ToInf = (TTree*)(fbackground_dyjets_2500ToInf->Get(treename));
    Nev = (TH1D*)(fbackground_dyjets_2500ToInf->Get("Nev"));
    weight = 0.004385 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_dyjets_2500ToInf, weight);

    // training variables:
    factory->AddVariable("dzVtx",'F');
    factory->AddVariable("nValidTrackerHits",'I');
   
    // If no numbers of events are given, half of the events in the tree are used for training, and the other half for testing:
    TCut mycuts = ("");
    TCut mycutb = ("");

    factory->PrepareTrainingAndTestTree(mycuts, mycutb, "SplitMode=random:!V");
    factory->BookMethod(TMVA::Types::kBDT, "BDT", "NTrees=200:MaxDepth=4");
    factory->TrainAllMethods();
    factory->TestAllMethods();
    factory->EvaluateAllMethods();
    outputFile->Close();

    if (!gROOT->IsBatch()) TMVA::TMVAGui("output.root");

    return 0;

}

