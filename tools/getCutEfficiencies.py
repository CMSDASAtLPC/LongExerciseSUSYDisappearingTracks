#!/usr/bin/env python
from __future__ import division
from ROOT import *
import os, sys, glob
import math
import numpy as np
import uuid
from glob import glob
import multiprocessing
from CfgUtils import readSamplesConfig

gROOT.SetBatch(True)
gStyle.SetOptStat(0)
canvas = TCanvas()
number_of_cores = 20

# script to apply cuts on signal / background trees. Output: Weighted number of tracks and efficiencies w.r.t. to a "no cuts" scenario

def apply_cuts_on_tree(tfile, treename, var, cutstring, samples, lumi):
    
    fin = TFile(tfile)
    tree = fin.Get(treename)

    # get number of tracks for given cutstring:
    tree.Draw(var, cutstring)
    histo = tree.GetHistogram().Clone()
    histo.SetDirectory(0)
    n_tracks = histo.GetEntries()

    # normalization:
    label = tfile.split("/")[-1].split(".root")[0]
    xsec = samples[label]["xsec"]

    # get number of events:
    h_nev = fin.Get("Nev")
    n_ev = h_nev.GetBinContent(1)

    n_tracks_weighted = 1.0 * xsec * n_tracks * lumi / n_ev

    fin.Close()

    return {"label": label, "type": samples[label]["type"], "n_tracks_weighted": n_tracks_weighted, "n_tracks": n_tracks, "histogram": histo}
   

def start_apply_cuts_on_tree(args):
   return apply_cuts_on_tree(*args)


def get_number_of_tracks_for_cut(tree_files, cutstring, configuration_file):

    samples = readSamplesConfig(configuration_file)

    lumi = samples["global"]["lumi"]

    # get weighted number of tracks for all trees:
    parameters = []
    for iFile in glob(tree_files):
        label = iFile.split("/")[-1].split(".root")[0]
        if label not in samples: continue
        parameters.append([iFile, "PreSelection", "pt", cutstring, samples, lumi])
  
    pool = multiprocessing.Pool(number_of_cores)
    output = pool.map(start_apply_cuts_on_tree, parameters)

    # calculate efficiencies:

    n_sg = [0, 0]
    n_bg = [0, 0]

    for sample in output:
        if sample["type"] == 's':
            n_sg[0] += sample["n_tracks_weighted"]
            n_sg[1] += sample["n_tracks"]
        if sample["type"] == 'b':
            n_bg[0] += sample["n_tracks_weighted"]
            n_bg[1] += sample["n_tracks"]

    return {"sg": n_sg, "bg": n_bg}


def get_efficiency_for_cut(tree_files, cutstring_nominator, configuration_file = "samples.cfg", cutstring_denominator = ""):

    print "Getting efficiencies for cut...", cutstring_nominator

    nominator = get_number_of_tracks_for_cut(tree_files, cutstring_nominator, configuration_file)
    denominator = get_number_of_tracks_for_cut(tree_files, cutstring_denominator, configuration_file)

    if denominator["sg"][0] > 0:
        eff_sg = nominator["sg"][0] / denominator["sg"][0]
    else:
        eff_sg = -1
    if denominator["bg"][0] > 0:
        eff_bg = nominator["bg"][0] / denominator["bg"][0]
    else:
        eff_bg = -1

    output = {"eff_sg": eff_sg, "eff_bg": eff_bg, "n_tracks_sg_nominator": nominator["sg"][0], "n_tracks_sg_nominator_unweighted": nominator["sg"][1], "n_tracks_bg_nominator": nominator["bg"][0], "n_tracks_bg_nominator_unweighted": nominator["bg"][1], "n_tracks_sg_denominator": denominator["sg"][0], "n_tracks_sg_denominator_unweighted": denominator["sg"][1], "n_tracks_bg_denominator": denominator["bg"][0], "n_tracks_bg_denominator_unweighted": denominator["bg"][1]}
    print output
    return output


if __name__ == "__main__":
    
    cutstring = ""
    print "Testing:", get_efficiency_for_cut("/eos/uscms/store/user/cmsdas/2019/long_exercises/DisappearingTracks/track-tag/tracks-pixelonly/*.root", cutstring)




