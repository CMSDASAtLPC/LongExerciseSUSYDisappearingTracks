#include "TApplication.h"
#include <cstdlib>
#include <iostream>
#include <map>
#include <stdio.h>
#include <string>
#include "TApplication.h"
#include "TChain.h"
#include "TFile.h"
#include "TH1D.h"
#include "TTree.h"
#include "TString.h"
#include "TObjString.h"
#include "TSystem.h"
#include "TROOT.h"
#include "TMVA/Factory.h"
#include "TMVA/Tools.h"
#include "TMVA/TMVAGui.h"
#include "TMVA/TMVARegGui.h"

int tmva(const char* signalFileName, const char* outFileName, const char* backgroundPath, const char* maxTreeEntries) {

    std::string path = backgroundPath;
    std::string maxTreeEntriesString = maxTreeEntries;
    std::cout << "Background path: " << path << std::endl;

    const char* treename = "PreSelection";

    gROOT->SetBatch(kTRUE);

    TMVA::Tools::Instance();

    TFile* outputFile = TFile::Open(outFileName, "RECREATE");

    TMVA::Factory *factory = new TMVA::Factory("TMVAClassification",outputFile,"V:!Silent:Color:Transformations=I:DrawProgressBar:AnalysisType=Classification"); 

    Double_t weight;
    Double_t lumi = 35900;  // 1/pb
    TH1D* Nev;

    TFile* fsignal = new TFile(signalFileName);
    TTree* sgTree = (TTree*)(fsignal->Get(treename));
    Nev = (TH1D*)(fsignal->Get("Nev"));
    weight = 0.00276133 * lumi / Nev->GetBinContent(1);
    factory->AddSignalTree(sgTree, weight);
    
    TFile* fbackground_wjets_100To200 = new TFile((path + "/Summer16.WJetsToLNu_HT-100To200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_wjets_100To200 = (TTree*)(fbackground_wjets_100To200->Get(treename));
    Nev = (TH1D*)(fbackground_wjets_100To200->Get("Nev"));
    weight = 1627 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_wjets_100To200, weight);

    TFile* fbackground_wjets_200To400 = new TFile((path + "/Summer16.WJetsToLNu_HT-200To400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_wjets_200To400 = (TTree*)(fbackground_wjets_200To400->Get(treename));
    Nev = (TH1D*)(fbackground_wjets_200To400->Get("Nev"));
    weight = 435.2 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_wjets_200To400, weight);

    TFile* fbackground_wjets_400To600 = new TFile((path + "/Summer16.WJetsToLNu_HT-400To600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_wjets_400To600 = (TTree*)(fbackground_wjets_400To600->Get(treename));
    Nev = (TH1D*)(fbackground_wjets_400To600->Get("Nev"));
    weight = 59.18 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_wjets_400To600, weight);

    //TFile* fbackground_wjets_600To800 = new TFile((path + "/Summer16.WJetsToLNu_HT-600To800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    //TTree* bgTree_wjets_600To800 = (TTree*)(fbackground_wjets_600To800->Get(treename));
    //Nev = (TH1D*)(fbackground_wjets_600To800->Get("Nev"));
    //weight = 14.58 * lumi / Nev->GetBinContent(1);
    //factory->AddBackgroundTree(bgTree_wjets_600To800, weight);

    TFile* fbackground_wjets_800To1200 = new TFile((path + "/Summer16.WJetsToLNu_HT-800To1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_wjets_800To1200 = (TTree*)(fbackground_wjets_800To1200->Get(treename));
    Nev = (TH1D*)(fbackground_wjets_800To1200->Get("Nev"));
    weight = 6.66 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_wjets_800To1200, weight);

    TFile* fbackground_wjets_1200To2500 = new TFile((path + "/Summer16.WJetsToLNu_HT-1200To2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_wjets_1200To2500 = (TTree*)(fbackground_wjets_1200To2500->Get(treename));
    Nev = (TH1D*)(fbackground_wjets_1200To2500->Get("Nev"));
    weight = 1.608 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_wjets_1200To2500, weight);

    TFile* fbackground_wjets_2500ToInf = new TFile((path + "/Summer16.WJetsToLNu_HT-2500ToInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_wjets_2500ToInf = (TTree*)(fbackground_wjets_2500ToInf->Get(treename));
    Nev = (TH1D*)(fbackground_wjets_2500ToInf->Get("Nev"));
    weight = 0.03891 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_wjets_2500ToInf, weight);

    TFile* fbackground_ttjets = new TFile((path + "/Summer16.TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_ttjets = (TTree*)(fbackground_ttjets->Get(treename));
    Nev = (TH1D*)(fbackground_ttjets->Get("Nev"));
    weight = 831.8 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_ttjets, weight);

    TFile* fbackground_ttjets_600To800 = new TFile((path + "/Summer16.TTJets_HT-600to800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_RA2AnalysisTree.root").c_str());
    TTree* bgTree_ttjets_600To800 = (TTree*)(fbackground_ttjets_600To800->Get(treename));
    Nev = (TH1D*)(fbackground_ttjets_600To800->Get("Nev"));
    weight = 2.734 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_ttjets_600To800, weight);

    //TFile* fbackground_ttjets_800To1200 = new TFile((path + "/Summer16.TTJets_HT-800to1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_RA2AnalysisTree.root").c_str());
    //TTree* bgTree_ttjets_800To1200 = (TTree*)(fbackground_ttjets_800To1200->Get(treename));
    //Nev = (TH1D*)(fbackground_ttjets_800To1200->Get("Nev"));
    //weight = 1.121 * lumi / Nev->GetBinContent(1);
    //factory->AddBackgroundTree(bgTree_ttjets_800To1200, weight);

    TFile* fbackground_ttjets_1200To2500 = new TFile((path + "/Summer16.TTJets_HT-1200to2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_RA2AnalysisTree.root").c_str());
    TTree* bgTree_ttjets_1200To2500 = (TTree*)(fbackground_ttjets_1200To2500->Get(treename));
    Nev = (TH1D*)(fbackground_ttjets_1200To2500->Get("Nev"));
    weight = 0.1979 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_ttjets_1200To2500, weight);

    TFile* fbackground_ttjets_2500ToInf = new TFile((path + "/Summer16.TTJets_HT-2500toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_RA2AnalysisTree.root").c_str());
    TTree* bgTree_ttjets_2500ToInf = (TTree*)(fbackground_ttjets_2500ToInf->Get(treename));
    Nev = (TH1D*)(fbackground_ttjets_2500ToInf->Get("Nev"));
    weight = 0.002368 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_ttjets_2500ToInf, weight);

    TFile* fbackground_dyjets = new TFile((path + "/Summer16.DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_RA2AnalysisTree.root").c_str());
    TTree* bgTree_dyjets = (TTree*)(fbackground_dyjets->Get(treename));
    Nev = (TH1D*)(fbackground_dyjets->Get("Nev"));
    weight = 6025.0 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_dyjets, weight);

    TFile* fbackground_dyjets_100To200 = new TFile((path + "/Summer16.DYJetsToLL_M-50_HT-100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_dyjets_100To200 = (TTree*)(fbackground_dyjets_100To200->Get(treename));
    Nev = (TH1D*)(fbackground_dyjets_100To200->Get("Nev"));
    weight = 181.3 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_dyjets_100To200, weight);

    TFile* fbackground_dyjets_200To400 = new TFile((path + "/Summer16.DYJetsToLL_M-50_HT-200to400_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_dyjets_200To400 = (TTree*)(fbackground_dyjets_200To400->Get(treename));
    Nev = (TH1D*)(fbackground_dyjets_200To400->Get("Nev"));
    weight = 50.42 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_dyjets_200To400, weight);

    TFile* fbackground_dyjets_400To600 = new TFile((path + "/Summer16.DYJetsToLL_M-50_HT-400to600_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_dyjets_400To600 = (TTree*)(fbackground_dyjets_400To600->Get(treename));
    Nev = (TH1D*)(fbackground_dyjets_400To600->Get("Nev"));
    weight = 6.984 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_dyjets_400To600, weight);

    //TFile* fbackground_dyjets_600To800 = new TFile((path + "/Summer16.DYJetsToLL_M-50_HT-600to800_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    //TTree* bgTree_dyjets_600To800 = (TTree*)(fbackground_dyjets_600To800->Get(treename));
    //Nev = (TH1D*)(fbackground_dyjets_600To800->Get("Nev"));
    //weight = 1.681 * lumi / Nev->GetBinContent(1);
    //factory->AddBackgroundTree(bgTree_dyjets_600To800, weight);

    TFile* fbackground_dyjets_800To1200 = new TFile((path + "/Summer16.DYJetsToLL_M-50_HT-800to1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_dyjets_800To1200 = (TTree*)(fbackground_dyjets_800To1200->Get(treename));
    Nev = (TH1D*)(fbackground_dyjets_800To1200->Get("Nev"));
    weight = 0.7754 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_dyjets_800To1200, weight);

    TFile* fbackground_dyjets_1200To2500 = new TFile((path + "/Summer16.DYJetsToLL_M-50_HT-1200to2500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_dyjets_1200To2500 = (TTree*)(fbackground_dyjets_1200To2500->Get(treename));
    Nev = (TH1D*)(fbackground_dyjets_1200To2500->Get("Nev"));
    weight = 0.1862 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_dyjets_1200To2500, weight);

    TFile* fbackground_dyjets_2500ToInf = new TFile((path + "/Summer16.DYJetsToLL_M-50_HT-2500toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RA2AnalysisTree.root").c_str());
    TTree* bgTree_dyjets_2500ToInf = (TTree*)(fbackground_dyjets_2500ToInf->Get(treename));
    Nev = (TH1D*)(fbackground_dyjets_2500ToInf->Get("Nev"));
    weight = 0.004385 * lumi / Nev->GetBinContent(1);
    factory->AddBackgroundTree(bgTree_dyjets_2500ToInf, weight);

    // track-related variables:
    factory->AddVariable("dxyVtx",'F');
    factory->AddVariable("dzVtx",'F');
    factory->AddVariable("matchedCaloEnergy",'F');
    factory->AddVariable("trkRelIso",'F');
    factory->AddVariable("nValidPixelHits",'I');
    factory->AddVariable("nValidTrackerHits",'I');
    factory->AddVariable("nMissingOuterHits",'I');
    factory->AddVariable("ptErrOverPt2",'F');
   
    // spectator variables:
    factory->AddSpectator("trkRelIso*pt",'F');
    factory->AddSpectator("neutralPtSum",'F');
    factory->AddSpectator("chargedPtSum",'F');
    factory->AddSpectator("pixelLayersWithMeasurement",'I');
    factory->AddSpectator("trackerLayersWithMeasurement",'I');
    factory->AddSpectator("pt",'F');
    factory->AddSpectator("eta",'F');
    factory->AddSpectator("phi",'F');
    factory->AddSpectator("nMissingMiddleHits",'I');
    factory->AddSpectator("deDxHarmonic2",'F');
    factory->AddSpectator("trkMiniRelIso",'F');
    factory->AddSpectator("passExo16044JetIso",'I');
    factory->AddSpectator("passExo16044LepIso",'I');
    factory->AddSpectator("passExo16044Tag",'I');
    factory->AddSpectator("trackJetIso",'F');
    factory->AddSpectator("trackLeptonIso",'F');
    factory->AddSpectator("madHT",'F');
    factory->AddSpectator("MET",'F');
    factory->AddSpectator("HT",'F');
    factory->AddSpectator("nCandPerEevent",'F');

    // If no numbers of events are given, half of the events in the tree are used 
    // for training, and the other half for testing:
    TCut mycuts;
    TCut mycutb;
    if (strcmp(maxTreeEntriesString.c_str(), "-1")) {
        // maxTreeEntriesString is set to a different value than -1
        mycuts=("pt>15 && abs(eta)<2.4 && passPFCandVeto==1 && trkRelIso<0.2 && dxyVtx<0.1 && dzVtx<0.1 && ptErrOverPt2<10 && nMissingMiddleHits==0 && nMissingOuterHits>=2 && trackQualityHighPurity==1 && Entry$<" + maxTreeEntriesString).c_str();
        mycutb=("pt>15 && abs(eta)<2.4 && passPFCandVeto==1 && trkRelIso<0.2 && dxyVtx<0.1 && dzVtx<0.1 && ptErrOverPt2<10 && nMissingMiddleHits==0 && nMissingOuterHits>=2 && trackQualityHighPurity==1 && Entry$<" + maxTreeEntriesString).c_str();
    } else {
        mycuts=("pt>15 && abs(eta)<2.4 && passPFCandVeto==1 && trkRelIso<0.2 && dxyVtx<0.1 && dzVtx<0.1 && ptErrOverPt2<10 && nMissingMiddleHits==0 && nMissingOuterHits>=2 && trackQualityHighPurity==1");
        mycutb=("pt>15 && abs(eta)<2.4 && passPFCandVeto==1 && trkRelIso<0.2 && dxyVtx<0.1 && dzVtx<0.1 && ptErrOverPt2<10 && nMissingMiddleHits==0 && nMissingOuterHits>=2 && trackQualityHighPurity==1");
    }

    factory->PrepareTrainingAndTestTree(mycuts, mycutb, "SplitMode=random:!V");

    factory->BookMethod(TMVA::Types::kBDT, "BDT", "NTrees=200:MaxDepth=4");

    factory->TrainAllMethods();
    factory->TestAllMethods();
    factory->EvaluateAllMethods();
    outputFile->Close();

    if (!gROOT->IsBatch()) TMVA::TMVAGui( outFileName );

    return 0;

}


int main( int argc, char** argv )
{
   return tmva(argv[1], argv[2], argv[3], argv[4]);
}

