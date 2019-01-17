#!/bin/env python
from __future__ import division
from ROOT import *
from array import array
from optparse import OptionParser
import os
import numpy as np
import os.path

def prepareReader(xmlfilename, vars_training, vars_spectator, tmva_variables):

    # import BDT from TMVA, add training and spectator variables

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


def get_tmva_info(path):

    # get BDT configuration details from tmva.cxx

    training_variables = []
    spectator_variables = []
    preselection = ""
    method = ""
    configuration = ""
    count_mycutb = 0
    
    with open(path + "/tmva.cxx", 'r') as tmva_macro:
        for line in tmva_macro.readlines():
            if "AddVariable" in line and "//" not in line.split()[0]:
                variable = line.split('"')[1]
                training_variables.append(variable)
            elif "AddSpectator" in line and "//" not in line.split()[0]:
                spectator_variables.append(line.split('"')[1])
            elif 'mycutb=("' in line and "Entry" not in line and "//" not in line.split()[0]:
                preselection = line.split('"')[1]
            elif "BookMethod" in line and "//" not in line.split()[0]:
                method = line.split('"')[1]
                configuration = line.split('"')[3]
                configuration = configuration.replace(":", ", ")

    return {"method": method, "configuration": configuration, "variables": training_variables, "spectators": spectator_variables, "preselection": preselection}


def loop(event_tree_filenames, track_tree_output, bdt_folders, nevents = -1, treename = "TreeMaker2/PreSelection", zmass_matching = True):

    # contains main event loop

    tree = TChain(treename)
    for iFile in event_tree_filenames:
        tree.Add(iFile)
    
    fout = TFile(track_tree_output, "recreate")

    # write number of events to histogram:
    nev = tree.GetEntries()
    h_nev = TH1F("nev", "nev", 1, 0, 1)
    h_nev.Fill(0, nev)
    h_nev.Write()

    tout = TTree("Events", "tout")
 
    # get variables of tree
    variables = []
    for i in range(len(tree.GetListOfBranches())):
        label = tree.GetListOfBranches()[i].GetName()
        if "tracks_" in label:
            label = label.replace("tracks_", "")
            variables.append(label)

    # prepare variables for output tree
    tree_branch_values = {}
    for variable in [
                      "MET",
                      "MHT",
                      "MHT_cleaned",
                      "HT",
                      "HT_cleaned",
                      "MinDeltaPhiMhtJets",
                      "MinDeltaPhiMhtJets_cleaned",
                      "zmass",
                      "PFCaloMETRatio",
                      "CrossSection",
                    ]:
        tree_branch_values[variable] = array( 'f', [ -1000 ] )
        tout.Branch( variable, tree_branch_values[variable], '%s/F' % variable )

    for variable in [
                      "n_DT",
                      "n_DT_realfake",
                      "n_jets",
                      "n_jets_cleaned",
                      "n_btags",
                      "n_btags_cleaned",
                      "n_leptons",
                      "n_allvertices",
                      "n_NVtx",
                      "n_gen_particles_in_cone",
                      "n_gen_taus_in_cone",
                      "n_leading_tracks_in_cone",
                      "EvtNumEven",
                      "lepton_type",
                    ]:
        tree_branch_values[variable] = array( 'i', [ -1000 ] )
        tout.Branch( variable, tree_branch_values[variable], '%s/I' % variable )
        
    # BDT configuration:
    readerPixelOnly = 0
    readerPixelStrips = 0
    preselection_pixelonly = ""
    preselection_pixelstrips = ""

    tmva_variables = {}

    for i_category, category in enumerate(["pixelonly", "pixelstrips"]):

        bdt_infos = get_tmva_info(bdt_folders[i_category])

        if category == "pixelonly":
            readerPixelOnly = prepareReader(bdt_folders[i_category] + '/weights/TMVAClassification_BDT.weights.xml', bdt_infos["variables"], bdt_infos["spectators"], tmva_variables)
            preselection_pixelonly = bdt_infos["preselection"]
            bdt_cut_pixelonly = 0.1
            
        elif category == "pixelstrips":
            readerPixelStrips = prepareReader(bdt_folders[i_category] + '/weights/TMVAClassification_BDT.weights.xml', bdt_infos["variables"], bdt_infos["spectators"], tmva_variables)
            preselection_pixelstrips = bdt_infos["preselection"]
            bdt_cut_pixelstrips = 0.25

    # some loop variables:
    nevents_total = 0
    nevents_tagged = 0
    nevents_tagged_realfake = 0

    # loop over events:
    for iEv, event in enumerate(tree):

        if nevents > 0 and iEv > nevents: break
        
        if (iEv+1) % 500 == 0:
            print "Processing event %s / %s" % (iEv + 1, nev)

        # do HT-binned background stitching:
        current_file_name = tree.GetFile().GetName()
        if tree.GetBranch("madHT"):
            madHT = event.madHT
            if (madHT>0) and \
               ("DYJetsToLL_M-50_Tune" in current_file_name and madHT>100) or \
               ("TTJets_Tune" in current_file_name and madHT>600) or \
               ("100to200_" in current_file_name and (madHT<100 or madHT>200)) or \
               ("100To200_" in current_file_name and (madHT<100 or madHT>200)) or \
               ("200to400_" in current_file_name and (madHT<200 or madHT>400)) or \
               ("200To400_" in current_file_name and (madHT<200 or madHT>400)) or \
               ("400to600_" in current_file_name and (madHT<400 or madHT>600)) or \
               ("400To600_" in current_file_name and (madHT<400 or madHT>600)) or \
               ("600to800_" in current_file_name and (madHT<600 or madHT>800)) or \
               ("600To800_" in current_file_name and (madHT<600 or madHT>800)) or \
               ("800to1200_" in current_file_name and (madHT<800 or madHT>1200)) or \
               ("800To1200_" in current_file_name and (madHT<800 or madHT>1200)) or \
               ("1200to2500_" in current_file_name and (madHT<1200 or madHT>2500)) or \
               ("1200To2500_" in current_file_name and (madHT<1200 or madHT>2500)) or \
               ("2500toInf_" in current_file_name and madHT<2500) or \
               ("2500ToInf_" in current_file_name and madHT<2500):
                continue
                    
        # reset all branch values
        for label in tree_branch_values:
            tree_branch_values[label][0] = -1000

        if zmass_matching:
            # only two oppositely charged leptons matched to Z mass:
            min_lepton_pt = 30.0        
            invariant_mass = 0
            
            if (len(event.Electrons) == 2 and len(event.Muons) == 0):
                if (event.Electrons[0].Pt() > min_lepton_pt):
                    if (bool(event.Electrons_mediumID[0]) and bool(event.Electrons_mediumID[1])):
                        if (event.Electrons_charge[0] * event.Electrons_charge[1] < 0):
                            if (bool(event.Electrons_passIso[0]) * bool(event.Electrons_passIso[1]) == 1):
                                invariant_mass = (event.Electrons[0] + event.Electrons[1]).M()
                                if invariant_mass > (91.19 - 10.0) and invariant_mass < (91.19 + 10.0):
                                    tree_branch_values["zmass"][0] = invariant_mass
                                    tree_branch_values["lepton_type"][0] = 11
            
            elif (len(event.Muons) == 2 and len(event.Electrons) == 0):
                if (event.Muons[0].Pt() > min_lepton_pt):
                    if (bool(event.Muons_tightID[0]) and bool(event.Muons_tightID[1])):
                        if (event.Muons_charge[0] * event.Muons_charge[1] < 0):
                            if (bool(event.Muons_passIso[0]) * bool(event.Muons_passIso[1]) == 1):
                                invariant_mass = (event.Muons[0] + event.Muons[1]).M()            
                                if invariant_mass > (91.19 - 10.0) and invariant_mass < (91.19 + 10.0):
                                    tree_branch_values["zmass"][0] = invariant_mass
                                    tree_branch_values["lepton_type"][0] = 13
                                
            # veto events with incompatible Z mass
            if tree_branch_values["zmass"][0] < 0:
                continue
                
        # clean event (recalculate HT, MHT, n_Jets without the two leptons):
        csv_b = 0.8838
        metvec = TLorentzVector()
        metvec.SetPtEtaPhiE(event.MET, 0, event.METPhi, event.MET)
        mhtvec = TLorentzVector()
        mhtvec.SetPtEtaPhiE(0, 0, 0, 0)
        jets = []
        nb = 0
        HT_cleaned = 0
        
        for ijet, jet in enumerate(event.Jets):
            
            if not (abs(jet.Eta()) < 5 and jet.Pt() > 30): continue
            
            # check if lepton is in jet, and veto jet if that is the case
            lepton_is_in_jet = False
            for leptons in [event.Electrons, event.Muons]:
                for lepton in leptons:
                    if jet.DeltaR(lepton) < 0.05:
                        lepton_is_in_jet = True
            if lepton_is_in_jet: continue
            
            mhtvec-=jet
            jets.append(jet)
            HT_cleaned+=jet.Pt()        
            if event.Jets_bDiscriminatorCSV[ijet] > csv_b: nb+=1
            
        n_btags_cleaned = nb        
        n_jets_cleaned = len(jets)
        MHT_cleaned = mhtvec.Pt()

        MinDeltaPhiMhtJets_cleaned = 9999   
        for jet in jets: 
            if abs(jet.DeltaPhi(mhtvec)) < MinDeltaPhiMhtJets_cleaned:
                MinDeltaPhiMhtJets_cleaned = abs(jet.DeltaPhi(mhtvec))
                
       
        # calculate MinDeltaPhiMhtJets:
        csv_b = 0.8838
        mhtvec = TLorentzVector()
        mhtvec.SetPtEtaPhiE(event.MHT, 0, event.MHTPhi, event.MHT)
        MinDeltaPhiMhtJets = 9999
        nj = 0
        nb = 0
        for ijet, jet in enumerate(event.Jets):
            if not (abs(jet.Eta())<2.4 and jet.Pt()>30): continue
            nj+=1
            if event.Jets_bDiscriminatorCSV[ijet]>csv_b: nb+=1
            if abs(jet.DeltaPhi(mhtvec))<MinDeltaPhiMhtJets:
                MinDeltaPhiMhtJets = abs(jet.DeltaPhi(mhtvec))
     
        nevents_total += 1
        n_DT = 0
        n_DT_realfake = 0

        gen_track_cone_pdgid = -1000
        gen_track_cone_taucorrected = -1000
        n_gen_particles_in_cone = 0

        n_gen_taus_in_cone = 0
        n_leading_tracks_in_cone = 0

        # loop over tracks (tracks)
        for i_iCand, iCand in enumerate(xrange(len(event.tracks))):

            # set up booleans
            is_pixel_track = False
            is_tracker_track = False
            genparticle_in_track_cone = False
            tau_leadtrk_in_track_cone = False
            is_disappearing_track = False
            is_a_PF_lepton = False

            # re-check PF lepton veto:
            for k in range(len(event.Muons)):
                deltaR = event.tracks[iCand].DeltaR(event.Muons[k])
                if deltaR < 0.01:
                    is_a_PF_lepton = True
            for k in range(len(event.Electrons)):
                deltaR = event.tracks[iCand].DeltaR(event.Electrons[k])
                if deltaR < 0.01:
                    is_a_PF_lepton = True

            if is_a_PF_lepton: continue

            # fill custom variables:
            ptErrOverPt2 = event.tracks_ptError[iCand] / (event.tracks[iCand].Pt()**2)

            # check for category:
            if event.tracks_trackerLayersWithMeasurement[iCand] == event.tracks_pixelLayersWithMeasurement[iCand]:
                is_pixel_track = True
            if event.tracks_trackerLayersWithMeasurement[iCand] > event.tracks_pixelLayersWithMeasurement[iCand]:
                is_tracker_track = True

            # apply TMVA preselection:
            if is_pixel_track and not (event.tracks[iCand].Pt() > 15 and \
                abs(event.tracks[iCand].Eta()) < 2.4 and \
                event.tracks_trkRelIso[iCand] < 0.2 and \
                event.tracks_dxyVtx[iCand] < 0.1 and \
                event.tracks_dzVtx[iCand] < 0.1 and \
                ptErrOverPt2 < 10 and \
                event.tracks_nMissingMiddleHits[iCand] == 0 and \
                bool(event.tracks_trackQualityHighPurity[iCand]) == 1 and \
                bool(event.tracks_passPFCandVeto[iCand]) == 1):
                    continue

            if is_tracker_track and not (event.tracks[iCand].Pt() > 15 and \
                abs(event.tracks[iCand].Eta()) < 2.4 and \
                event.tracks_trkRelIso[iCand] < 0.2 and \
                event.tracks_dxyVtx[iCand] < 0.1 and \
                event.tracks_dzVtx[iCand] < 0.1 and \
                ptErrOverPt2 < 10 and \
                event.tracks_nMissingOuterHits[iCand] >= 2 and \
                event.tracks_nMissingMiddleHits[iCand] == 0 and \
                bool(event.tracks_trackQualityHighPurity[iCand]) == 1 and \
                bool(event.tracks_passPFCandVeto[iCand]) == 1):
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
            
            # final categorization:
            if is_pixel_track:
                mva = readerPixelOnly.EvaluateMVA("BDT")
                if mva>bdt_cut_pixelonly:
                    is_disappearing_track = True
            elif is_tracker_track:
                mva = readerPixelStrips.EvaluateMVA("BDT")
                if mva>bdt_cut_pixelstrips:
                    is_disappearing_track = True

            # check if track is really a fake track (track has no charged genparticles in cone around track):            
            if is_disappearing_track and tree.GetBranch("GenParticles"):
                for k in range(len(event.GenParticles)):
                    deltaR = event.tracks[iCand].DeltaR(event.GenParticles[k])
                    if deltaR < 0.01:

                        # we only need genparticles with status 1:
                        if event.GenParticles_Status[k] != 1:
                            continue

                        # ignore certain non-charged genparticles (neutrinos, gluons and photons):
                        gen_track_cone_pdgid = event.GenParticles_PdgId[k]
                        if abs(gen_track_cone_pdgid) == 12 or abs(gen_track_cone_pdgid) == 14 or abs(gen_track_cone_pdgid) == 16 or abs(gen_track_cone_pdgid) == 21 or abs(gen_track_cone_pdgid) == 22:
                            continue

                        genparticle_in_track_cone = True
                
            if is_disappearing_track:
                n_DT += 1
                if not genparticle_in_track_cone:
                    n_DT_realfake += 1
 
        # fill tree branches:
        if tree.GetBranch("CrossSection"):
            tree_branch_values["CrossSection"][0] = event.CrossSection
        tree_branch_values["n_leptons"][0] = len(event.Electrons) + len(event.Muons)
        tree_branch_values["n_btags"][0] = event.BTags
        tree_branch_values["n_btags_cleaned"][0] = n_btags_cleaned
        tree_branch_values["n_DT"][0] = n_DT
        tree_branch_values["n_DT_realfake"][0] = n_DT_realfake
        tree_branch_values["n_jets"][0] = len(event.Jets)
        tree_branch_values["n_jets_cleaned"][0] = n_jets_cleaned
        tree_branch_values["n_allvertices"][0] = event.nAllVertices
        tree_branch_values["PFCaloMETRatio"][0] = event.PFCaloMETRatio
        tree_branch_values["MET"][0] = event.MET
        tree_branch_values["MHT"][0] = event.MHT
        tree_branch_values["MHT_cleaned"][0] = MHT_cleaned
        tree_branch_values["HT"][0] = event.HT
        tree_branch_values["HT_cleaned"][0] = HT_cleaned
        tree_branch_values["MinDeltaPhiMhtJets"][0] = MinDeltaPhiMhtJets
        tree_branch_values["MinDeltaPhiMhtJets_cleaned"][0] = MinDeltaPhiMhtJets_cleaned
        tree_branch_values["n_NVtx"][0] = event.NVtx
        
        if event.EvtNum % 2 == 0:
            tree_branch_values["EvtNumEven"][0] = 1
        else:
            tree_branch_values["EvtNumEven"][0] = 0

        tree_branch_values["n_gen_particles_in_cone"][0] = n_gen_particles_in_cone
        tree_branch_values["n_gen_taus_in_cone"][0] = n_gen_taus_in_cone
        tree_branch_values["n_leading_tracks_in_cone"][0] = n_leading_tracks_in_cone
      
        tout.Fill()
        
    fout.Write()
    fout.Close()


if __name__ == "__main__":

    parser = OptionParser()
    (options, args) = parser.parse_args()
    
    iFile = args[0].split(",")
    out_tree = args[1]
    if len(args)>2 and args[2]>0:
        nev = int(args[2])
    else:
        nev = -1

    if len(args)>3:
        zmass_matching = int(args[3])
    else:
        zmass_matching = True

    if os.path.exists("CMSSW_10_1_0"):
        # this is for gridpacks:
        loop(iFile, out_tree, ["CMSSW_10_1_0/src/cmsdas2019/track-tag/cmssw8-newpresel3-200-4-short", "CMSSW_10_1_0/src/cmsdas2019/track-tag/cmssw8-newpresel2-200-4-medium"], nevents=nev, zmass_matching = zmass_matching )
    else:
        # we're in tools:
        loop(iFile, out_tree, ["../track-tag/cmssw8-newpresel3-200-4-short", "../track-tag/cmssw8-newpresel2-200-4-medium"], nevents=nev, zmass_matching = zmass_matching )
    
    


