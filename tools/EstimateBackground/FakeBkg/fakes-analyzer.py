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

# contains variables used for TMVA
tmva_variables = {}

# general set up training/spectator variables for TMVA
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

    event_tree_filename = args[0]
    track_tree_output = args[1]
    nevents = args[2]
    choose_bdt = args[3]
    treename = "TreeMaker2/PreSelection"
    
    if choose_bdt == "complete":
        bdt_folder_pixelonly = "newpresel3-200-4-short"
        bdt_folder_pixelstrips = "newpresel2-200-4-medium"
        vars_training = ["dxyVtx", "dzVtx", "matchedCaloEnergy", "trkRelIso", "nValidPixelHits", "nValidTrackerHits", "nMissingOuterHits", "ptErrOverPt2"]
        vars_spectator = ["trkRelIso*pt",  "neutralPtSum", "chargedPtSum", "pixelLayersWithMeasurement", "trackerLayersWithMeasurement", "pt", "eta", "phi", "nMissingMiddleHits", "deDxHarmonic2", "trkMiniRelIso", "passExo16044JetIso", "passExo16044LepIso", "passExo16044Tag", "trackJetIso", "trackLeptonIso", "madHT", "MET", "HT", "nCandPerEevent"]
    elif choose_bdt == "nodxyVtx":
        bdt_folder_pixelonly = "newpresel3-200-4-short-nodxyVtx"
        bdt_folder_pixelstrips = "newpresel2-200-4-medium-nodxyVtx"
        vars_training = ["dzVtx", "matchedCaloEnergy", "trkRelIso", "nValidPixelHits", "nValidTrackerHits", "nMissingOuterHits", "ptErrOverPt2"]
        vars_spectator = ["trkRelIso*pt",  "neutralPtSum", "chargedPtSum", "pixelLayersWithMeasurement", "trackerLayersWithMeasurement", "pt", "eta", "phi", "nMissingMiddleHits", "deDxHarmonic2", "trkMiniRelIso", "passExo16044JetIso", "passExo16044LepIso", "passExo16044Tag", "trackJetIso", "trackLeptonIso", "madHT", "MET", "HT", "nCandPerEevent"]        

    print "Input:\t\t", event_tree_filename
    print "Tree:\t\t", treename
    print "Output:\t\t", track_tree_output

    # get best BDT cut value:
    bdt_bestcut_pixelonly = best_tmva_significance.get_get_bdt_cut_value(bdt_folder_pixelonly + '/output.root')["best_cut_value"]
    bdt_bestcut_pixelstrips = best_tmva_significance.get_get_bdt_cut_value(bdt_folder_pixelstrips + '/output.root')["best_cut_value"]
    print "Using BDT cut values:"
    print "pixel-only:", bdt_bestcut_pixelonly
    print "pixel+strips:", bdt_bestcut_pixelstrips

    fin = TFile(event_tree_filename)
    tree = fin.Get(treename)
    fout = TFile(track_tree_output, "recreate")
    tout = TTree("Events", "tout")

    # check input file
    if fin.IsZombie(): # or fin.TestBit(TFile.kRecovered):
        print "input not properly closed:", fin
        fin.Close()
        return fin

    # check if tracks are available in tree
    for branch in tree:
        try:
            temp = branch.tracks
        except:
            print "input does not contain tracks:", fin
            fin.Close()
        break
 
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
                      "n_allvertices",
                      "tagged_track_trackerlayers",
                      "tagged_track_pixellayers",
                    ]:
        tout_output_values[variable] = array( 'i', [ -10 ] )

    tout.Branch( "MET", tout_output_values["MET"], 'MET/F' )
    tout.Branch( "MHT", tout_output_values["MHT"], 'MHT/F' )
    tout.Branch( "HT", tout_output_values["HT"], 'HT/F' )
    tout.Branch( "pass_sr", tout_output_values["pass_sr"], 'pass_sr/I' )
    tout.Branch( "n_DT", tout_output_values["n_DT"], 'n_DT/I' )
    tout.Branch( "n_DT_realfake", tout_output_values["n_DT_realfake"], 'n_DT_realfake/I' )
    tout.Branch( "n_jets", tout_output_values["n_jets"], 'n_jets/I' )
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

    # loop over events
    # ****************
    for iEv, event in enumerate(tree):

        if nevents > 0 and (iEv+1) > nevents:
            break
        if (iEv+1) % 100 == 0:
            print "Processing event %s" % (iEv+1)

       
        # signal regions
        # ==============

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

        nevents_total += 1

        n_DT = 0
        n_DT_realfake = 0

        highest_bdt_value = -1
        highest_bdt_index = -1

        # loop over tracks (tracks)
        # ***************************
        number_of_tracks = len(event.tracks)

        for iCand in xrange(number_of_tracks):

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

            elif choose_bdt == "nodxyVtx":
                # TODO:
                # check if event passes the TMVA preselection

                # TODO:
                # store all event variables in the tmva_variables dictionary
                # to evaluate the BDT classifier for each event, you need to get all variables which were used in the training
                tmva_variables["dxyVtx"][0] = event.tracks_dxyVtx[iCand]

            # TODO:
            # check if real fake (no genparticle around track)

            # finally, you can evaluate the BDT classifier like this:
            # mva = readerPixelOnly.EvaluateMVA("BDT")
            # 
            # before, check if you are looking at pixel-only or pixel+strips tracks (see category definition)

            # TODO:
            # For each event, we want to determine the track with the highest BDT value and save its properties.
            # Update the variables highest_bdt_value and highest_bdt_index (the track index).
            # Also, update the number of disappearing tracks (n_DT) and if the track is "real" fake track (n_DT_realfake).

            



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
        tout_output_values["n_DT"][0] = n_DT
        tout_output_values["n_DT_realfake"][0] = n_DT_realfake
        tout_output_values["n_jets"][0] = len(event.Jets)
        tout_output_values["n_allvertices"][0] = event.nAllVertices
        tout_output_values["MET"][0] = event.MET
        tout_output_values["MHT"][0] = event.MHT
        tout_output_values["HT"][0] = event.HT
        tout_output_values["tagged_track_highest_bdt"][0] = highest_bdt_value

        tout.Fill()
        
    fout.Write()
    fout.Close()
    fin.Close()


def do_abcd_chi2(tree_file):

    # define regions:
    # TODO:
    # Get region definiton from RGS
    region_dxy = 0
    region_chi2 = 0

    fin = TFile(tree_file)
    tree = fin.Get("Events")

    canvas = TCanvas("c1", "c1", 800, 800)
    canvas.SetLeftMargin(1.2 * canvas.GetLeftMargin())
    canvas.SetRightMargin(1.4 * canvas.GetRightMargin())
    canvas.SetTopMargin(0.7 * canvas.GetTopMargin())

    morecuts = " && n_DT>0 && tagged_track_dzVtx<0.5"

    tree.Draw("tagged_track_dxyVtx:tagged_track_chi2perNdof", "tagged_track_dxyVtx<%s && tagged_track_chi2perNdof<%s %s" % (region_dxy, region_chi2, morecuts), "COLZ")
    count_TT = int(tree.GetHistogram().GetEntries())
    tree.Draw("tagged_track_dxyVtx:tagged_track_chi2perNdof", "tagged_track_dxyVtx>%s && tagged_track_chi2perNdof>%s %s" % (region_dxy, region_chi2, morecuts), "COLZ")
    count_LL = int(tree.GetHistogram().GetEntries())
    tree.Draw("tagged_track_dxyVtx:tagged_track_chi2perNdof", "tagged_track_dxyVtx<%s && tagged_track_chi2perNdof>%s %s" % (region_dxy, region_chi2, morecuts), "COLZ")
    count_TL = int(tree.GetHistogram().GetEntries())
    tree.Draw("tagged_track_dxyVtx:tagged_track_chi2perNdof", "tagged_track_dxyVtx>%s && tagged_track_chi2perNdof<%s %s" % (region_dxy, region_chi2, morecuts), "COLZ")
    count_LT = int(tree.GetHistogram().GetEntries())

    print "count_TT, count_LL, count_LT, count_TL", count_TT, count_LL, count_LT, count_TL

    tree.Draw("tagged_track_dxyVtx:tagged_track_chi2perNdof", "tagged_track_dxyVtx<0.1 && tagged_track_chi2perNdof<3 %s" % (morecuts), "COLZ")
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
    text.DrawLatex(0.15, 0.87, "TT = LT x #frac{TL}{LL} = %0.2f" % (count_LT*count_TL/count_LL))
    
    canvas.Print("abcd_chi2.pdf")

    fin.Close()


def do_tree(choose_bdt, nevents):

    parameters = []
    filelist = glob.glob("/pnfs/desy.de/cms/tier2/store/user/sbein/NtupleHub/Production2016v2/Summer16.ZJetsToNuNu_HT-*_13TeV-madgraph_1_*")

    for iFile in filelist:
        out_tree = "output_%s/" % choose_bdt + iFile.split("/")[-1].split(".root")[0] + "_fakes.root"
        os.system("mkdir -p output_%s" % choose_bdt)
        parameters.append( [iFile, out_tree, nevents, choose_bdt] )

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    pool.map(loop, parameters)

    print "running hadd..."
    os.system("hadd -f fakes_%s.root output_%s/Summer*.root" % (choose_bdt, choose_bdt))



if __name__ == "__main__":

    # TODO: Adjust number of events, can select low number for testing
    nevents = 1000

    do_tree("nodxyVtx", nevents)
    do_abcd_chi2("fakes_nodxyVtx.root")

