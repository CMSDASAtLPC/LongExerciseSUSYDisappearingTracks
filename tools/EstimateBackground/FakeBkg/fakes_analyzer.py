#!/bin/env python
from __future__ import division
from array import array
from ROOT import *
import os, sys, glob
import numpy as np
import math
from optparse import OptionParser
import best_tmva_significance
import multiprocessing 

# fakes analyzer by Viktor Kutzner
# TMVA parts adapted from SkimTreeMaker.py by Sam Bein

# backgrounds are HT-binned, do stitching
def pass_background_stitching(file_name, madHT):
    passed = True
    if "DYJetsToLL_M-50_Tune" in file_name and madHT>100 or \
       "TTJets_Tune" in file_name and madHT>600 or \
       "_HT-100to200_" in file_name and (madHT<100 or madHT>200) or \
       "_HT-200to400_" in file_name and (madHT<200 or madHT>400) or \
       "_HT-400to600_" in file_name and (madHT<400 or madHT>600) or \
       "_HT-600to800_" in file_name and (madHT<600 or madHT>800) or \
       "_HT-800to1200_" in file_name and (madHT<800 or madHT>1200) or \
       "_HT-1200to2500_" in file_name and (madHT<1200 or madHT>2500) or \
       "_HT-2500toInf_" in file_name and madHT<2500:
            passed = False

    return passed


# general set up training/spectator variables for TMVA
tmva_variables = {}
def prepareReader(xmlfilename, vars_training, vars_spectator):

    reader = TMVA.Reader()
    for label in vars_training + vars_spectator:
        if label not in tmva_variables:
            tmva_variables[label] = array('f',[0])

    for label in vars_training:
        reader.AddVariable(label, tmva_variables[label])
    for label in vars_spectator:
        reader.AddSpectator(label, tmva_variables[label])
    reader.BookMVA("BDT", xmlfilename)

    return reader


def set_to_zero(tout_output_values):

    for item in tout_output_values:
        if not "pass" in item:
            tout_output_values[item][0] = -10
    return tout_output_values


def loop(args):

    event_tree_filenames = args[0]
    track_tree_output = args[1]
    nevents = args[2]
    choose_bdt = args[3]
    treename = "TreeMaker2/PreSelection"
    
    if choose_bdt == "complete":
        bdt_folder_pixelonly = "newpresel3-200-4-short"
        bdt_folder_pixelstrips = "newpresel2-200-4-medium"
        vars_training = ["dxyVtx", "dzVtx", "matchedCaloEnergy", "trkRelIso", "nValidPixelHits", "nValidTrackerHits", "nMissingOuterHits", "ptErrOverPt2"]
        vars_spectator = ["trkRelIso*pt",  "neutralPtSum", "chargedPtSum", "pixelLayersWithMeasurement", "trackerLayersWithMeasurement", "pt", "eta", "phi", "nMissingMiddleHits", "deDxHarmonic2", "trkMiniRelIso", "passExo16044JetIso", "passExo16044LepIso", "passExo16044Tag", "trackJetIso", "trackLeptonIso", "madHT", "MET", "HT", "nCandPerEevent"]
    elif choose_bdt == "noVtx":
        bdt_folder_pixelonly = "newpresel3-200-4-short-noVtx"
        bdt_folder_pixelstrips = "newpresel2-200-4-medium-noVtx"
        vars_training = ["matchedCaloEnergy", "trkRelIso", "nValidPixelHits", "nValidTrackerHits", "nMissingOuterHits", "ptErrOverPt2"]
        vars_spectator = ["trkRelIso*pt",  "neutralPtSum", "chargedPtSum", "pixelLayersWithMeasurement", "trackerLayersWithMeasurement", "pt", "eta", "phi", "nMissingMiddleHits", "deDxHarmonic2", "trkMiniRelIso", "passExo16044JetIso", "passExo16044LepIso", "passExo16044Tag", "trackJetIso", "trackLeptonIso", "madHT", "MET", "HT", "nCandPerEevent"]        
    elif choose_bdt == "nodxyVtx":
        bdt_folder_pixelonly = "newpresel3-200-4-short-nodxyVtx"
        bdt_folder_pixelstrips = "newpresel2-200-4-medium-nodxyVtx"
        vars_training = ["dzVtx", "matchedCaloEnergy", "trkRelIso", "nValidPixelHits", "nValidTrackerHits", "nMissingOuterHits", "ptErrOverPt2"]
        vars_spectator = ["trkRelIso*pt",  "neutralPtSum", "chargedPtSum", "pixelLayersWithMeasurement", "trackerLayersWithMeasurement", "pt", "eta", "phi", "nMissingMiddleHits", "deDxHarmonic2", "trkMiniRelIso", "passExo16044JetIso", "passExo16044LepIso", "passExo16044Tag", "trackJetIso", "trackLeptonIso", "madHT", "MET", "HT", "nCandPerEevent"]        

    print "Input:\t\t", event_tree_filenames
    print "Tree:\t\t", treename
    print "Output:\t\t", track_tree_output

    # get best BDT cut value:
    bdt_bestcut_pixelonly = best_tmva_significance.get_get_bdt_cut_value(bdt_folder_pixelonly + '/output.root')["best_cut_value"]
    bdt_bestcut_pixelstrips = best_tmva_significance.get_get_bdt_cut_value(bdt_folder_pixelstrips + '/output.root')["best_cut_value"]
    print "Using BDT cut values:"
    print "pixel-only:", bdt_bestcut_pixelonly
    print "pixel+strips:", bdt_bestcut_pixelstrips

    tree = TChain(treename)
    for iFile in event_tree_filenames:
        tree.Add(iFile)
    
    fout = TFile(track_tree_output, "recreate")
    tout = TTree("Events", "tout")
 
    # get variables of tree
    variables = []
    for i in range(len(tree.GetListOfBranches())):
        label = tree.GetListOfBranches()[i].GetName()
        if "tracks_" in label:
            label = label.replace("tracks_", "")
            variables.append(label)

    # prepare variables for output tree
    tout_output_values = {}
    for variable in [
                      "MET",
                      "MHT",
                      "HT",
                      "MinDeltaPhiMhtJets",
                      "tagged_track_highest_bdt",
                      "tagged_track_pt",
                      "tagged_track_eta",
                      "tagged_track_chi2perNdof",
                      "tagged_track_trkRelIso",
                      "tagged_track_dxyVtx",
                      "tagged_track_dzVtx",
                    ]:
        tout_output_values[variable] = array( 'f', [ -10 ] )

    for variable in [
                      "pass_sr",
                      "n_DT",
                      "n_DT_realfake",
                      "n_jets",
                      "n_btags",
                      "n_leptons",
                      "n_allvertices",
                      "tagged_track_trackerlayers",
                      "tagged_track_pixellayers",
                    ]:
        tout_output_values[variable] = array( 'i', [ -10 ] )

    tout.Branch( "MET", tout_output_values["MET"], 'MET/F' )
    tout.Branch( "MHT", tout_output_values["MHT"], 'MHT/F' )
    tout.Branch( "HT", tout_output_values["HT"], 'HT/F' )
    tout.Branch( "MinDeltaPhiMhtJets", tout_output_values["MinDeltaPhiMhtJets"], 'MinDeltaPhiMhtJets/F' )
    tout.Branch( "pass_sr", tout_output_values["pass_sr"], 'pass_sr/I' )
    tout.Branch( "n_DT", tout_output_values["n_DT"], 'n_DT/I' )
    tout.Branch( "n_DT_realfake", tout_output_values["n_DT_realfake"], 'n_DT_realfake/I' )
    tout.Branch( "n_jets", tout_output_values["n_jets"], 'n_jets/I' )
    tout.Branch( "n_btags", tout_output_values["n_btags"], 'n_btags/I' )
    tout.Branch( "n_leptons", tout_output_values["n_leptons"], 'n_leptons/I' )
    tout.Branch( "n_allvertices", tout_output_values["n_allvertices"], 'n_allvertices/I' )
    tout.Branch( "tagged_track_highest_bdt", tout_output_values["tagged_track_highest_bdt"], 'tagged_track_highest_bdt/F' )
    tout.Branch( "tagged_track_pt", tout_output_values["tagged_track_pt"], 'tagged_track_pt/F' )
    tout.Branch( "tagged_track_eta", tout_output_values["tagged_track_eta"], 'tagged_track_eta/F' )
    tout.Branch( "tagged_track_trackerlayers", tout_output_values["tagged_track_trackerlayers"], 'tagged_track_trackerlayers/I' )
    tout.Branch( "tagged_track_pixellayers", tout_output_values["tagged_track_pixellayers"], 'tagged_track_pixellayers/I' )
    tout.Branch( "tagged_track_chi2perNdof", tout_output_values["tagged_track_chi2perNdof"], 'tagged_track_chi2perNdof/F' )
    tout.Branch( "tagged_track_trkRelIso", tout_output_values["tagged_track_trkRelIso"], 'tagged_track_trkRelIso/F' )
    tout.Branch( "tagged_track_dxyVtx", tout_output_values["tagged_track_dxyVtx"], 'tagged_track_dxyVtx/F' )
    tout.Branch( "tagged_track_dzVtx", tout_output_values["tagged_track_dzVtx"], 'tagged_track_dzVtx/F' )

    nevents_total = 0
    nevents_tagged = 0
    nevents_tagged_realfake = 0

    # Configure BDTs with training/spectator variables:
    readerPixelOnly = prepareReader(bdt_folder_pixelonly + '/weights/TMVAClassification_BDT.weights.xml', vars_training, vars_spectator)
    readerPixelStrips = prepareReader(bdt_folder_pixelstrips + '/weights/TMVAClassification_BDT.weights.xml', vars_training, vars_spectator)

    nev = tree.GetEntries()

    # loop over events
    # ****************
    for iEv, event in enumerate(tree):

        # don't include prompt background: ignore events with gen electrons or muons
        veto_event = False
        if tree.GetBranch("GenParticles_PdgId"):
            for k in range(len(event.GenParticles)):
                if abs( event.GenParticles_PdgId[k] ) == 11 or abs( event.GenParticles_PdgId[k] ) == 13:
                    veto_event = True
                    break
        if veto_event:
            continue

        if nevents > 0 and (iEv+1) > nevents:
            break
        if (iEv+1) % 500 == 0:
            print "Processing event %s / %s" % (iEv + 1, nev)

        #if not pass_background_stitching(event_tree_filename, event.madHT): continue        
        
        # event selection:
        # ================

        # as defined in https://indico.desy.de/indico/event/20437/contribution/2/material/slides/0.pdf
        if event.MHT<200 or event.MET<200 or event.HT<100:
            tout_output_values["pass_sr"][0] = 0
        elif event.MHT>=200 and event.MHT<300:
            if len(event.Jets)==1:
                tout_output_values["pass_sr"][0] = 1
            elif len(event.Jets)>=2 and len(event.Jets)<=3:
                tout_output_values["pass_sr"][0] = 2
            elif len(event.Jets)>=4:
                tout_output_values["pass_sr"][0] = 3
        elif event.MHT>=300 and event.MHT<600:
            if len(event.Jets)==1:
                tout_output_values["pass_sr"][0] = 4
            elif len(event.Jets)>=2 and len(event.Jets)<=3:
                tout_output_values["pass_sr"][0] = 5
            elif len(event.Jets)>=4:
                tout_output_values["pass_sr"][0] = 6
        elif event.MHT>=600:
            if len(event.Jets)==1:
                tout_output_values["pass_sr"][0] = 7
            elif len(event.Jets)>=2 and len(event.Jets)<=3:
                tout_output_values["pass_sr"][0] = 8
            elif len(event.Jets)>=4:
                tout_output_values["pass_sr"][0] = 9
        else:
            tout_output_values["pass_sr"][0] = 0

        # set everything to zero:
        tout_output_values = set_to_zero(tout_output_values)

        # MinDeltaPhiMhtJets:
        csv_b = 0.8484
        metvec = TLorentzVector()
        metvec.SetPtEtaPhiE(event.MET, 0, event.METPhi, event.MET)
        mhtvec = TLorentzVector()
        mhtvec.SetPtEtaPhiE(event.MHT, 0, event.MHTPhi, event.MHT)
        mindphi = 9999
        nj = 0
        nb = 0
        for ijet, jet in enumerate(event.Jets):
                if not (abs(jet.Eta())<5.0 and jet.Pt()>30): continue
                nj+=1
                if event.Jets_bDiscriminatorCSV[ijet]>csv_b: nb+=1
                if abs(jet.DeltaPhi(mhtvec))<mindphi:
                        mindphi = abs(jet.DeltaPhi(mhtvec))
        MinDeltaPhiMhtJets = mindphi
        
        nevents_total += 1

        n_DT = 0
        n_DT_realfake = 0

        highest_bdt_value = -1
        highest_bdt_index = -1

        # loop over tracks (tracks)
        # ***************************
        number_of_tracks = len(event.tracks)

        for iCand in xrange(number_of_tracks):

            # event / track selection:
            passed = False
            if event.HT>100 and event.MHT>322 and len(event.Jets)>6 and tracks[iCand].Pt()>15 and abs(tracks[iCand].Eta())<2.4 and (len(event.Electrons)+len(event.Muons)+len(event.BTags))==0 and MinDeltaPhiMhtJets>0.28:
                passed = True
            
            if not passed:
                continue

            # fill custom variables:
            ptErrOverPt2 = event.tracks_ptError[iCand] / event.tracks[iCand].Pt()**2

            # set up booleans
            is_pixel_track = False
            is_tracker_track = False
            is_present_after_preselection = False
            is_a_real_fake = True
            is_a_PF_lepton = False
            is_disappearing_track = False

            # check for category:
            if event.tracks_trackerLayersWithMeasurement[iCand] == event.tracks_pixelLayersWithMeasurement[iCand]:
                is_pixel_track = True
            if event.tracks_trackerLayersWithMeasurement[iCand] > event.tracks_pixelLayersWithMeasurement[iCand]:
                is_tracker_track = True

            if choose_bdt == "complete":
                # apply TMVA preselection with modified pt (30 instead of 15 GeV):
                if event.tracks[iCand].Pt() > 30 and \
                    abs(event.tracks[iCand].Eta()) < 2.4 and \
                    event.tracks_trkRelIso[iCand] < 0.2 and \
                    event.tracks_dxyVtx[iCand] < 0.1 and \
                    event.tracks_dzVtx[iCand] < 0.1 and \
                    ptErrOverPt2 < 10 and \
                    event.tracks_nMissingMiddleHits[iCand] == 0 and \
                    bool(event.tracks_trackQualityHighPurity[iCand]) == 1 and \
                    bool(event.tracks_passPFCandVeto[iCand]) == 1:
                        is_present_after_preselection = True
                else:
                    continue

                # evalulate BDT:
                tmva_variables["dxyVtx"][0] = event.tracks_dxyVtx[iCand]
                tmva_variables["dzVtx"][0] = event.tracks_dzVtx[iCand]
                tmva_variables["matchedCaloEnergy"][0] = event.tracks_matchedCaloEnergy[iCand]
                tmva_variables["trkRelIso"][0] = event.tracks_trkRelIso[iCand]
                tmva_variables["nValidPixelHits"][0] = event.tracks_nValidPixelHits[iCand]
                tmva_variables["nValidTrackerHits"][0] = event.tracks_nValidTrackerHits[iCand]
                tmva_variables["nMissingOuterHits"][0] = event.tracks_nMissingOuterHits[iCand]
                tmva_variables["ptErrOverPt2"][0] = ptErrOverPt2

            elif choose_bdt == "noVtx":
                # apply TMVA preselection with modified pt (30 instead of 15 GeV):
                if event.tracks[iCand].Pt() > 30 and \
                    abs(event.tracks[iCand].Eta()) < 2.4 and \
                    event.tracks_trkRelIso[iCand] < 0.2 and \
                    ptErrOverPt2 < 10 and \
                    event.tracks_nMissingMiddleHits[iCand] == 0 and \
                    bool(event.tracks_trackQualityHighPurity[iCand]) == 1 and \
                    bool(event.tracks_passPFCandVeto[iCand]) == 1:
                        is_present_after_preselection = True
                else:
                    continue

                # evalulate BDT:
                tmva_variables["matchedCaloEnergy"][0] = event.tracks_matchedCaloEnergy[iCand]
                tmva_variables["trkRelIso"][0] = event.tracks_trkRelIso[iCand]
                tmva_variables["nValidPixelHits"][0] = event.tracks_nValidPixelHits[iCand]
                tmva_variables["nValidTrackerHits"][0] = event.tracks_nValidTrackerHits[iCand]
                tmva_variables["nMissingOuterHits"][0] = event.tracks_nMissingOuterHits[iCand]
                tmva_variables["ptErrOverPt2"][0] = ptErrOverPt2

            elif choose_bdt == "nodxyVtx":
                # apply TMVA preselection with modified pt (30 instead of 15 GeV):
                if event.tracks[iCand].Pt() > 30 and \
                    abs(event.tracks[iCand].Eta()) < 2.4 and \
                    event.tracks_trkRelIso[iCand] < 0.2 and \
                    event.tracks_dzVtx[iCand] < 0.1 and \
                    ptErrOverPt2 < 10 and \
                    event.tracks_nMissingMiddleHits[iCand] == 0 and \
                    bool(event.tracks_trackQualityHighPurity[iCand]) == 1 and \
                    bool(event.tracks_passPFCandVeto[iCand]) == 1:
                        is_present_after_preselection = True
                else:
                    continue

                # evalulate BDT:
                tmva_variables["dzVtx"][0] = event.tracks_dzVtx[iCand]
                tmva_variables["matchedCaloEnergy"][0] = event.tracks_matchedCaloEnergy[iCand]
                tmva_variables["trkRelIso"][0] = event.tracks_trkRelIso[iCand]
                tmva_variables["nValidPixelHits"][0] = event.tracks_nValidPixelHits[iCand]
                tmva_variables["nValidTrackerHits"][0] = event.tracks_nValidTrackerHits[iCand]
                tmva_variables["nMissingOuterHits"][0] = event.tracks_nMissingOuterHits[iCand]
                tmva_variables["ptErrOverPt2"][0] = ptErrOverPt2

            # re-check PF lepton veto:
            for k in range(len(event.Muons)):
                deltaR = event.tracks[iCand].DeltaR(event.Muons[k])
                if deltaR < 0.001:
                    is_a_PF_lepton = True
            for k in range(len(event.Electrons)):
                deltaR = event.tracks[iCand].DeltaR(event.Electrons[k])
                if deltaR < 0.001:
                    is_a_PF_lepton = True

            # check if real fake (no genparticle around track):
            if tree.GetBranch("GenParticles"):
                for k in range(len(event.GenParticles)):
                    deltaR = event.tracks[iCand].DeltaR(event.GenParticles[k])
                    if deltaR < 0.001:
                        is_a_real_fake = False
            
            mva = -1
            # final categorization:
            if is_pixel_track:
                mva = readerPixelOnly.EvaluateMVA("BDT")
                if mva>bdt_bestcut_pixelonly and is_present_after_preselection and not is_a_PF_lepton and is_a_real_fake:
                    is_disappearing_track = True
            elif is_tracker_track:
                mva = readerPixelStrips.EvaluateMVA("BDT")
                if mva>bdt_bestcut_pixelstrips and is_present_after_preselection and not is_a_PF_lepton and is_a_real_fake:
                    is_disappearing_track = True

            if is_present_after_preselection and not is_a_PF_lepton:

                if mva > highest_bdt_value:
                    highest_bdt_value = mva
                    highest_bdt_index = iCand

                if is_disappearing_track:
                    n_DT += 1
                    if is_a_real_fake:
                        n_DT_realfake += 1
                                    
        # veto event if no track survives preselection:
        if highest_bdt_index == -1: continue

        # fill track info for highest BDT score track
        tout_output_values["tagged_track_pt"][0] = event.tracks[highest_bdt_index].Pt()
        tout_output_values["tagged_track_eta"][0] = event.tracks[highest_bdt_index].Eta()
        tout_output_values["tagged_track_trackerlayers"][0] = event.tracks_trackerLayersWithMeasurement[highest_bdt_index]
        tout_output_values["tagged_track_pixellayers"][0] = event.tracks_pixelLayersWithMeasurement[highest_bdt_index]
        tout_output_values["tagged_track_chi2perNdof"][0] = event.tracks_chi2perNdof[highest_bdt_index]
        tout_output_values["tagged_track_trkRelIso"][0] = event.tracks_trkRelIso[highest_bdt_index]
        tout_output_values["tagged_track_dxyVtx"][0] = event.tracks_dxyVtx[highest_bdt_index]
        tout_output_values["tagged_track_dzVtx"][0] = event.tracks_dzVtx[highest_bdt_index]

        # other event info
        tout_output_values["n_leptons"][0] = len(event.Electrons) + len(event.Muons)
        tout_output_values["n_btags"][0] = event.BTags
        tout_output_values["n_DT"][0] = n_DT
        tout_output_values["n_DT_realfake"][0] = n_DT_realfake
        tout_output_values["n_jets"][0] = len(event.Jets)
        tout_output_values["n_allvertices"][0] = event.nAllVertices
        tout_output_values["MET"][0] = event.MET
        tout_output_values["MHT"][0] = event.MHT
        tout_output_values["HT"][0] = event.HT
        tout_output_values["tagged_track_highest_bdt"][0] = highest_bdt_value
        tout_output_values["MinDeltaPhiMhtJets"][0] = MinDeltaPhiMhtJets#
        
        print "ok"

        tout.Fill()
        
    fout.Write()
    fout.Close()


def do_abcd_chi2(tree_file):

    # define regions:
    region_dxy = 0.005
    region_chi2 = 3.0

    #fin = TFile(tree_file)
    #tree = fin.Get("Events")
    tree = TChain("Events")
    tree.Add(" /nfs/dust/cms/user/kutznerv/shorttrack/fake-tracks/output/*root")

    canvas = TCanvas("c1", "c1", 800, 800)
    canvas.SetLeftMargin(1.2 * canvas.GetLeftMargin())
    canvas.SetRightMargin(1.4 * canvas.GetRightMargin())
    canvas.SetTopMargin(0.7 * canvas.GetTopMargin())

    morecuts = " && n_DT>0"

    tree.Draw("tagged_track_dxyVtx:tagged_track_chi2perNdof", "tagged_track_dxyVtx<%s && tagged_track_chi2perNdof<%s %s" % (region_dxy, region_chi2, morecuts), "COLZ")
    count_TT = int(tree.GetHistogram().GetEntries())
    tree.Draw("tagged_track_dxyVtx:tagged_track_chi2perNdof", "tagged_track_dxyVtx>%s && tagged_track_chi2perNdof>%s %s" % (region_dxy, region_chi2, morecuts), "COLZ")
    count_LL = int(tree.GetHistogram().GetEntries())
    tree.Draw("tagged_track_dxyVtx:tagged_track_chi2perNdof", "tagged_track_dxyVtx<%s && tagged_track_chi2perNdof>%s %s" % (region_dxy, region_chi2, morecuts), "COLZ")
    count_TL = int(tree.GetHistogram().GetEntries())
    tree.Draw("tagged_track_dxyVtx:tagged_track_chi2perNdof", "tagged_track_dxyVtx>%s && tagged_track_chi2perNdof<%s %s" % (region_dxy, region_chi2, morecuts), "COLZ")
    count_LT = int(tree.GetHistogram().GetEntries())

    print "count_TT, count_LL, count_LT, count_TL", count_TT, count_LL, count_LT, count_TL

    tree.Draw("tagged_track_dxyVtx:tagged_track_chi2perNdof", "tagged_track_dxyVtx<0.1 && tagged_track_chi2perNdof<6 %s" % (morecuts), "COLZ")
    h_abcd = tree.GetHistogram().Clone()
    h_abcd.SetDirectory(0)
    h_abcd.SetTitle(";chi2ndof;dxyVtx")
    h_abcd.Draw("COLZ")
    print "#h_abcd", h_abcd.GetEntries()

    xmin = h_abcd.GetXaxis().GetXmin()
    xmax = h_abcd.GetXaxis().GetXmax()
    ymin = h_abcd.GetYaxis().GetXmin()
    ymax = h_abcd.GetYaxis().GetXmax()

    line = TLine(xmin, region_dxy, xmax, region_dxy)
    line.SetLineColor(kRed)
    line.SetLineWidth(2)
    line.Draw("same")
    line2 = TLine(region_chi2, ymin, region_chi2, ymax)
    line2.SetLineColor(kRed)
    line2.SetLineWidth(2)
    line2.Draw("same")

    text = TLatex()
    text.SetNDC()
    text.SetTextColor(kRed)
    text.DrawLatex(0.65, 0.12, "TL: " + str(count_TL))
    text.DrawLatex(0.65, 0.6, "LL: " + str(count_LL))
    text.DrawLatex(0.15, 0.6, "LT: " + str(count_LT))
    text.DrawLatex(0.15, 0.12, "TT: " + str(count_TT))
    
    result = 0
    if count_LL>0:
        result = count_LT*count_TL/count_LL
    
    text.DrawLatex(0.15, 0.87, "TT = LT x #frac{TL}{LL} = %0.2f" % (result))
    
    canvas.Print("abcd_chi2.pdf")

    #fin.Close()


def do_abcd_chi2_more_regions(tree_file):

    # define regions:
    region_dxy = 0.005
    region_chi2 = 1.2
    region_chi2_ext = 3.0

    tree = TChain("Events")
    tree.Add("/nfs/dust/cms/user/kutznerv/shorttrack/fake-tracks/output/*root")

    canvas = TCanvas("c1", "c1", 1200, 800)
    canvas.SetLeftMargin(1.2 * canvas.GetLeftMargin())
    canvas.SetRightMargin(1.4 * canvas.GetRightMargin())
    canvas.SetTopMargin(0.7 * canvas.GetTopMargin())

    morecuts = " && n_DT>0 "

    tree.Draw("tagged_track_dxyVtx:tagged_track_chi2perNdof", "tagged_track_dxyVtx<%s && tagged_track_chi2perNdof<%s %s" % (region_dxy, region_chi2, morecuts), "COLZ")
    count_TT = int(tree.GetHistogram().GetEntries())
    tree.Draw("tagged_track_dxyVtx:tagged_track_chi2perNdof", "tagged_track_dxyVtx>%s && tagged_track_chi2perNdof>%s && tagged_track_chi2perNdof<%s %s" % (region_dxy, region_chi2, region_chi2_ext, morecuts), "COLZ")
    count_LL = int(tree.GetHistogram().GetEntries())
    tree.Draw("tagged_track_dxyVtx:tagged_track_chi2perNdof", "tagged_track_dxyVtx<%s && tagged_track_chi2perNdof>%s && tagged_track_chi2perNdof<%s %s" % (region_dxy, region_chi2, region_chi2_ext, morecuts), "COLZ")
    count_TL = int(tree.GetHistogram().GetEntries())
    tree.Draw("tagged_track_dxyVtx:tagged_track_chi2perNdof", "tagged_track_dxyVtx>%s && tagged_track_chi2perNdof<%s %s" % (region_dxy, region_chi2, morecuts), "COLZ")
    count_LT = int(tree.GetHistogram().GetEntries())

    tree.Draw("tagged_track_dxyVtx:tagged_track_chi2perNdof", "tagged_track_dxyVtx<%s && tagged_track_chi2perNdof>%s %s" % (region_dxy, region_chi2_ext, morecuts), "COLZ")
    count_TL_ext = int(tree.GetHistogram().GetEntries())
    tree.Draw("tagged_track_dxyVtx:tagged_track_chi2perNdof", "tagged_track_dxyVtx>%s && tagged_track_chi2perNdof>%s %s" % (region_dxy, region_chi2_ext, morecuts), "COLZ")
    count_LL_ext = int(tree.GetHistogram().GetEntries())

    print "count_TT, count_LL, count_LT, count_TL", count_TT, count_LL, count_LT, count_TL, count_TL_ext, count_LL_ext

    tree.Draw("tagged_track_dxyVtx:tagged_track_chi2perNdof", "tagged_track_dxyVtx<0.05 && tagged_track_chi2perNdof<6 %s" % (morecuts), "COLZ")
    h_abcd = tree.GetHistogram().Clone()
    h_abcd.SetDirectory(0)
    h_abcd.SetTitle(";chi2ndof;dxyVtx")
    h_abcd.Draw("COLZ")
    print "#h_abcd", h_abcd.GetEntries()

    xmin = h_abcd.GetXaxis().GetXmin()
    xmax = h_abcd.GetXaxis().GetXmax()
    ymin = h_abcd.GetYaxis().GetXmin()
    ymax = h_abcd.GetYaxis().GetXmax()

    line = TLine(xmin, region_dxy, xmax, region_dxy)
    line.SetLineColor(kRed)
    line.SetLineWidth(2)
    line.Draw("same")
    line2 = TLine(region_chi2, ymin, region_chi2, ymax)
    line2.SetLineColor(kRed)
    line2.SetLineWidth(2)
    line2.Draw("same")
    line3 = TLine(region_chi2_ext, ymin, region_chi2_ext, ymax)
    line3.SetLineColor(kRed)
    line3.SetLineWidth(2)
    line3.Draw("same")
    
    text = TLatex()
    text.SetNDC()
    text.SetTextColor(kRed)
    text.DrawLatex(0.3, 0.12, "TL: " + str(count_TL))
    text.DrawLatex(0.3, 0.6, "LL: " + str(count_LL))
    text.DrawLatex(0.125, 0.6, "LT: " + str(count_LT))
    text.DrawLatex(0.125, 0.12, "TT: " + str(count_TT))
    text.DrawLatex(0.70, 0.12, "TL-ext: " + str(count_TL_ext))
    text.DrawLatex(0.70, 0.6, "LL-ext: " + str(count_LL_ext))
    
    result = 0
    if count_LL>0:
        result = count_LT*count_TL/count_LL
        result_ext = count_LT*count_TL_ext/count_LL_ext
    
    text.SetTextColor(kBlack)
    text.DrawLatex(0.15, 0.87, "TT = LT x #frac{TL}{LL} = %0.2f" % (result))
    text.DrawLatex(0.15, 0.75, "TT = LT x #frac{TL_ext}{LL_ext} = %0.2f" % (result_ext))
    
    canvas.Print("abcd_chi2.pdf")


if __name__ == "__main__":

    parser = OptionParser()
    (options, args) = parser.parse_args()
    
    if len(args)>0:
        iFile = eval(args[0].replace("[", "['").replace(",", "','").replace("]", "']"))
        out_tree = args[1]
        loop([iFile, out_tree, -1, "nodxyVtx"])
    else:
        # if no arguments are given, do plot
        #do_abcd_chi2("fakes_nodxyVtx.root")
        do_abcd_chi2_more_regions("")
    
