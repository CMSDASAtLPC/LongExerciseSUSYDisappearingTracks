# CMSDAS @ DESY 2018


Welcome to the 2018 DESY CMSDAS exercise on disappearing tracks! This long exercise will walk students through a number of steps needed to set up and implement an search for new physics at CMS. Enjoy!

## Introduction

Long-lived (LL) charged particles are featured in many models of physics beyond the standard model, e.g., hidden valley theories. In particular, R-parity conserving SUSY models with a wino-like LSP usually feature charginos with proper decay lengths between 1 nm and several meters, after which point the chargino would decay into a neutralino and a very soft pion or lepton. SUSY models with a light higgsino but with particularly heavy bino and wino parameters can also give rise to charginos with similar lifetimes. The known particles do not have similar lifetimes, so the potential signal events are quite distinct from the standard model background. 

The most recent public result of the search for long-lived particles with disappearing tracks at sqrt(s)=13 TeV is available [here](https://cds.cern.ch/record/2306201). This PAS (Physics Analysis Summary) gives a good overview of the general search approach and the characteristics and difficulties one encounters when looking at this particular signature. 

The exercise is organized in sections as follows: First, the recipe for setting up a working area will be described. Then, you'll start on a track-level analysis and identify the relevant properties of disappearing tracks (DT). This DT identification is then used on event level where you study the event topology and the background contributions, which are estimated with data-driven methods.

## 1.) Set up a working area

First, login to a NAF machine using the details you received via email: 

```
ssh -y USERNAME@naf-schoolXX.desy.de
```

Initialize the NAF software environment. This you have to do for every login: 

```
source /etc/profile.d/modules.sh
module use -a /afs/desy.de/group/cms/modulefiles/
module load cmssw
```

Create a CMSSW working environment: 

```
mkdir longlivedLE
cd longlivedLE
cmsrel CMSSW_10_1_0
```

Change to your newly created working environment and initialize the 
CMSSW software environment: 

```
cd CMSSW_10_1_0/src
cmsenv
```

Now you need to clone the git repository which contains the analysis-specific code: 

```
git clone https://github.com/https://github.com/DisappearingTrack/cmsdas.git cmsdas2018
cd cmsdas2018
```

## 2.) Track-level analysis

In this section, you will take a closer look at the tracking properies and develop a method to identify disappearing tracks in events.

### 2.a) Short introduction to tracking variables

For an introduction to CMS tracking, see the [tracking short exercise](https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideCMSDataAnalysisSchoolHamburg2018TrackingAndVertexingExercise).

Generally, CMS analyses operate on AOD datasets, of which smaller datasets (miniAOD, nanoAOD) exist as well. Datasets contain several collections of track objects which contain the trajectories produced by the tracking algorithm. A collection of detector-level information is retained for each trajectory. A reference of accessible track properties is [here](http://cmsdoxygen.web.cern.ch/cmsdoxygen/CMSSW_7_5_2/doc/html/d8/df2/classreco_1_1TrackBase.html).

The detector-level information for each track is stored in the hitpattern. It contains the number of hits per track, the number of tracker layers with or without measurement, the missing hit information, and much much more. A reference can be found [here](http://cmsdoxygen.web.cern.ch/cmsdoxygen/CMSSW_7_5_2/doc/html/d3/dcb/classreco_1_1HitPattern.html).

In this exercise, we will be working with ntuples created from AOD and minAOD datasets, which contain a selection of useful tracking variables. For this section in particular, ntuples which only contain tracks are used. From each event in the considered datasets, tracks with pT>10 GeV were stored in the ntuple.

Let's start by having a look at some of the tracking variables of signal tracks:
```
root -l /nfs/dust/cms/user/kutznerv/cmsdas/tracks-mini-medium/signal.root 
root [0] new TBrowser
```
With TBrowser, open the "PreSelection" tree and take a look at the variables. The tree contains variables from the track objets such as pT, eta and phi as well as variables from the hitpattern, such as nValidPixelHits or nMissingOuterHits. Also, for each track a selection of corresponding event-level properties as MET and HT are also stored.

Take some time to think about which variables could be relevant for tagging disappearing tracks. The track length is connected to the number of hits and layers with a measurement. Missing inner, middle, and outer hits indicate missing hits on the track trajectory adjacent to the interaction point, within the sequence of tracker hits, and adjacent to the ECAL, respectively. DxyVtx and dzVtx indicate the impact parameter with respect to the primary vertex.

One aspect of a disappearing track is that it has some number of missing outer hits. You can correlate this property with other variables, such as the impact parameter:
```
root [0] PreSelection->Draw("nMissingOuterHits")
root [0] PreSelection->Draw("nMissingOuterHits:dxyVtx", "dxyVtx<0.1", "COLZ")
root [0] PreSelection->Draw("nMissingOuterHits:dxyVtx", "dxyVtx<0.01", "COLZ")
```
You are looking at a couple of observables that are key to selecting signal disappearing tracks.

### 2.b) Plot signal and background

We will now plot the signal alongside with the stacked main MC backgrounds on track level. Use the following script to first convert the trees to histograms and then do a complete plot:

```
$ ./plot_track_variables.py
```

<b style='color:black'>Exercise: Create plots of all variables to familiarize yourself with the tracking properties.</b>

You only need to re-create the histograms when you change the cutstring. Open the script and set `recreate_histograms = True` to False. To add your own histogram, you'll also need to edit `treeToHist.py`.

The plots will appear in the `/plots` folder.

Add your own cut (e.g. a higher cut on pT): Set

```
cuts = {"loose": "",
        "mycut": "pt>50"}
```

and

```
stages = ["loose", "mycut"]
```

After that, run the plotting script with re-creating all histograms.

### 2.c) Disappearing track tag (training a BDT)

After having looked at some of the tracking variables, you now have to develop a set of criteria for selecting disappearing tracks that  discriminates between such tracks and the Standard Model (SM) background. One approach is to choose a set of thresholds (cuts) to apply to the relevant track properties by hand/eye. By applying these cuts to simulated signal and background samples, one can evaluate performance of the cuts. With the large number of tracking variables available, however, it is worthwhile to consider other approaches, such as a random grid search (RGS) or a boosted decision tree (BDT). In the following, we will train a BDT for the track selection.

#### Track categorization

We define two basic track categories. Tracks which are reconstructed in the pixel tracker are classified as pixel-only tracks, while tracks in both the pixel and strips tracker are classified as pixel+strips tracks:
   * pixel-only tracks: equal number of pixel and tracker layers with measurement
   * pixel+strips tracks: tracker layers with measurement > pixel layers with measurement

#### Boosted decision trees

The Boosted decision tree is a rather popular type of multivariate classifier. An introduction to boosted decision trees is given [here](http://www.if.ufrj.br/~helder/20070706_hh_bdt.pdf). What most multivariant classifiers have in common, including BDTs, is that they take as input a set of properties (measurable numbers) of a signal event candidate, and output (typically a single) number that indicates how likely it is the event corresponds to true signal. We will train two separate BDTs, one for each track category, using TMVA ([Toolkit for Multivariate Analysis](https://root.cern/tmva)) included in ROOT.

In the exercise repository, change into track-selection and prepare a CMSSW 8.0.28 environment in order to use the correct TMVA version for the exercise:
```
$ cd track-selection
$ cmsrel CMSSW_8_0_28
$ cd CMSSW_8_0_28/src
$ cmsenv
$ cd -
```

Test your TMVA setup by running a minimal example:

```
$ root tmva.cxx
```

The configuration and training of the BDT is set up in a ROOT macro, tmva.cxx. If everything went well, you will see the TMVA GUI which you can use to evaluate the training and how well you did:

<center>

![](https://i.imgur.com/nAlEGrx.png)
</center>

You can find the TMVA documentation [here](https://root.cern.ch/download/doc/tmva/TMVAUsersGuide.pdf). The most imporant functions accessible here are:
  * 1a) View input variables
  * 4a) View BDT response of the test sample
  * 4b) View BDT response of both test & training sample
  * 5a) View ROC curve

You can use button (1a) to take a look at the normalized signal and background plots of the input variables. In the minimal example, only the impact parameter dz with respect to the primary vertex and the number of tracker layers with measurement are used.
For each event, the BDT gives a BDT classifier ranging from -1 to 1 and indicates whether the event is background- or signal-like. A plot showing this classifier is accessible with button (4a). In this plot, we want to aim for a good separation between signal and background, which would allow us to put a cut on the BDT classifier to select disappearing tracks (signal).

By default, TMVA uses half of the input samples for training, the other half for testing. As the training should be general and not specific to one half of the dataset, the testing sample is used to verfiy no overtraining has taken place. Button (4b) shows an overlay of the BDT response plot for both the test sample and training sample, which ideally should look the same.

Button (5a) reveals the "receiver-operator curve", or ROC. For each event, the signal eff(sg) and background efficiencies eff(bg) are calculated. The background rejection efficiency is 1-eff(bg). The ROC curve is used to select a a point with high signal and high background rejection efficiency, which is linked to a cut on the BDT classifier.

Have a look at the tmva.cxx macro. On the top, you can specify whether you want to train using pixel-only or pixel+strips tracks by adjusting the path. After that, the signal and the relevant background files are added:

  * W jets -> lepton + neutrino binned in HT
  * TTbar jets binned in HT
  * Drell-Yan jets -> dilepton binned in HT

Each sample is added to TMVA with the correct weight of cross section * luminosity / number of events.

Below that, you can add/modifiy variables used for the training, with 'F' indicating float and 'I' indicating integer variables:

```
factory->AddVariable("dzVtx",'F');
factory->AddVariable("nValidTrackerHits",'I');
```

The configuration of the BDT is made with

```
factory->BookMethod(TMVA::Types::kBDT, "BDT", "NTrees=200:MaxDepth=4");
```

where we configure a BDT with 200 trees and a maximum depth of 4.

Relevant tracking variables available in the tree are:
  * chargedPtSum, the sum of charged particles around a small cone around the track
  * chi2perNdof, indicating the goodness of the track fit
  * deDxHarmonic2, the deposited energy per distance
  * dxyVtx and dzVtx, the impact parameter indicating the displacement of the track with respect to the primary vertex
  * eta, phi, pt, the kinematic variables
  * matchedCaloEnergy, the deposited energy in the calorimeter for a small cone around the track
  * nMissing*Hits, missing hits on the track trajectory (no hits detected)
  * nValid*Hits, number of hits of the track
  * pixel/trackerLayersWithMeasurement, number of tracker layers with measurement
  * ptErrOverPt2, the error on pT divided by pT^2
  * trackQuality*, a set of track quality criteria. High purity tracks are recommended
  * trkRelIso, the track isolation

<b style='color:black'>Exercise: Find the best combination of input variables and the best BDT configuration. Compare different ROCs and check for overtraining to get the maximum in signal and background rejection efficiency.</b>

##### Some hints:
The TCut variables "mycuts" and "mycutb" can be used to apply cuts before the BDT training. This can be useful to exclude certain ranges of input parameters to improve BDT performance, as well as to set the number of signal and background events used for training and testing. The latter may become necessary when exploring many different TMVA configurations. For example, to consider only tracks with pT>50 GeV and 100 events for training and testing in total, write:

```
TCut mycuts = ("pt>50 && event<100");
TCut mycutb = ("pt>50 && event<100");
```

Note that by changing the number of events, you need to adjust the "Nev" variable for each signal and background sample as well in order to use the correct weighting.

##### Comparing TMVA results

TMVA stores the output by default in "output.root" and a folder containing the weights of the BDT along with a C helper class to apply the weights to a given event. You can use roc_comparison.py to overlay different ROC curves, which you can specify in the last line: 

```
plot_rocs("comparison.pdf", ["./output1.root", "./output2.root", ...])
```

Run it with

```
$ python roc_comparison.py
```

##### Selecting a lower cut on the BDT classifier

After you have decided on a BDT configuration, you need to select a lower cut on the BDT classifier to separate signal tracks. One possible way to do this is to calculate the significance Z = S/sqrt(S+B) for each combination of signal and background efficiency, and then to determine the BDT classifier value with the highest significance:

```
$ python best_tmva_significance.py
```

This script will produce a similar plot as when accessing button (5a), but gives you greater flexibility and considers the total amount of signal and background tracks used in the training.

We will provide two BDTs for pixel-only and pixel+strips tracks which you can compare your performance against. You can later include your best BDTs in the Friday presentation.

You have now learned how to train a BDT with signal and background samples and to come up with a first track tag for disppearing tracks. A similar track tag is used in the skims provided in the following sections.

## 3.) Event-based analysis

Background skim files have been Let's make some distributions of various event-level quantities, 
comparing signal and background events. 

### 3.a) Background events

```
python tools/CharacterizeEvents.py
```

This script created histograms with a minimal set of selection, 
and saved them in a new file called canvases.root. Open up canvases.root 
and have a look at the canvases stored there. 

```
root -l canvases.root
[inside ROOT command prompt]: TBrowser b
```

After clicking through a few plots, can you identify which are the 
main backgrounds? 

<b style='color:black'>Question 1: What is the main background in 
  events with low missing transverse momentum, MHT?</b>

<b style='color:black'>Question 2: What is the main background in 
  events with at least 2 b-tagged jets?</b>

### 3.b) Skimming signal events 

We'd like to overlay some signal distributions onto these plots, 
but there are currently no skims for the signal. We are interested in a wide range of 
signal models, but we will consider the important example of gluino pair production,
with a small mass splitting between the gluino and LSP, called T1qqqqLL(1800,1400,30); 
where 1800 GeV is the gluino mass, 1400 is the LSP mass, and the chargino proper decay 
length is 30 cm. Have a look  in the pre-made pyroot script to skim signal events, 
tools/SkimTreeMaker.py, and after a quick glance, run the script:

```
python tools/SkimTreeMaker.py /nfs/dust/cms/user/beinsam/CMSDAS2018b/Ntuples/g1800_chi1400_27_200970_step4_30.root
```


<b style='color:black'>Question 3: How many skimmed events are there?</b>
  
Create a directory called Signal for the new file, move the new file into Signal/ 
and re-run the plot maker:

```
mkdir Signal
mv skim_g1800_chi1400_27_200970_step4_30.root Signal/
python tools/CharacterizeEvents.py
root -l canvases.root
```

Clicking around on the canvases, you will now be able to see the signal overlaid (not stacked). Can you identify any observables/kinematic regions where the signal-to-background ratio looks more favorable? Look at several observables and try to come up with a set of cuts that improves the sensitivity. Your selection can be tested by adding elements to the python dictionary called ```cutsets``` in ```tools/CharacterizeEvents.py.``` Hint: the most useful observables have distributions that are different in shape between signal and background.

<b style='color:black'>When you have a decent set of selection and nice looking plots, you can save the canvases as pdfs for the record. </b>

You just performed a so-called eyeball optimization. Can you count the total weighted signal and background events that pass your selection? Write these numbers down in a safe place; we can use them later.

<b style='color:black'>Question 4: How many weighted signal and background events were there passing your selection? What was the expected significance, in terms of s/sqrt(s+b)</b>

## 3.c) Cut-based optimization (RGS)

Let's get systematic with the optimization. Many tools exist that help to select events with a good sensitivity. The main challenge is that an exaustive scan over all possible cut values on all observables in an n-dimensional space of observables becomes computationally intensive or prohibitive for n>3. 

One interesting tool that seeks to overcome this curse of dimensionality is called a random grid search (RGS), which is documented in the publication, "Optimizing Event Selection with the Random Grid Search" https://arxiv.org/abs/1706.09907. RGS performs a scan over the observable hyperplane, using a set of available simulated signal (or background) events to define steps in the scan. For each step in the scan (each simulated event), a proposed selection set is defined taking the cut values to be the values of the observables of the event. We are going to run RGS on the signal/background samples, and compare the sensitivity of the selection to the hand-picked cuts you obtained previously.  


```
git clone https://github.com/sbein/RGS.git
cd RGS/
make
source setup.sh #whenever intending to use RGS
cd ../
pwd
```

The first script to run is tools/rgs_train.py. Open this script up, edit the lumi appropriately (to 35900/pb), give the path to the signal event file you just created, and tweak anything else as you see fit. When finished, save and open tools/LLSUSY.cuts. This file specifies the observables you want RGS to scan over and cut on, as well as the type of cut to apply (greater than, less than, equal to, etc.). Run the (first) training RGS script:

```
python tools/rgs_train.py
```
This creates the file LLSUSY.root which contains a tree of signal and background counts for each possible selection set in the scan. To determine the most optimal cut set, run the (second) analysis RGS script:

```
python tools/rgs_analyze.py
```
This will print the optimum set of thresholds to the screen, as well as the signal and background count corresponding to each set of cuts, and an estimate of the signal significance, z.  How does the RGS optimal selection compare to your hand-picked selection? Hopefully better - if not, you are pretty darn good at eyeball optimization!

You'll have noticed the script also draws a canvas. The scatter plot depicts the ROC cloud, which shows the set of signal and background efficiencies corresponding to each step of the scan. The color map in the background indicates the highest value of the significance of the various cut sets falling into each bin. 

Open up tools/rgs_analyze.py and have a look. You'll notice the significance measure is the simplified z = s/sqrt(b+db^2), where the user can specify the systematic uncertainty (SU) db. The fractional SU is currently set to 0.05. Try changing this value to something larger and rerunning rgs_analyze.py script. 

<b style='color:black'>Question 5. What happened to the optimum thresholds after doubling the SU? How about the expected significance? </b>

<b style='color:black'>Question 6. What value of the systematic uncertainty would correspond to a significance of 2 sigma? This is the worst case uncertainty that would allow us to exclude this signal model. </b>

## 4.) Background estimation

There are two main sources of backgrounds contributing to the search, *prompt* and *fake* background. The prompt background is due to charged leptons which failed the lepton reconstruction, but leave a track in the tracker and are thus not included in the ParticleFlow candidates. Fake tracks originate from pattern recogniction errors, which produce tracks not originating from real particles.

A precise determination for these types of backgrounds requires a data-diven method. A general introduction to data-diven methods is given [here](http://www.desy.de/~csander/Talks/120223_SFB_DataDrivenBackgrounds.pdf).
 
### 4.a) Prompt background

The prompt background is the name given to SM events with a disappearing track that arises because of the presence of a true electron. The method for estimating this background is based on a single-lepton control region. Transfer factors (kappa factors) are derived that relate the count in the single lepton control region to the count in the signal region. 

The single-lepton control region is defined as being analogous to the signal region, but where the requirement of there being 1 disappearing track is replaced by the requirement of there being one well-reconstructed lepton:

n(bkg in SR) = kappa * n(single lepton)

Kappa factors are derived using a data-driven tag and probe method. A well-reconstructed lepton is identified as the tag, and the event is checked for an isolated track (probe) that can be paired with the tag such that the invariant mass of the pair falls within 20 GeV of the Z mass, 90 GeV. In such a case, the track is identified as either being a well-reconstructed lepton, a disappearing track, or neither. The ratio of probes that are disappearing tracks to probes that are well-reconstructed leptons is taken as the estimate of kappa. 

#### step 1. Create histograms for deriving kappa factors

The following command will run a script that generates histograms for the numberator (disappearing tracks) and denominator (prompt leptons) that are needed compute kappa:

```

python tools/TagNProbeHistMaker_BDT.py /pnfs/desy.de/cms/tier2/store/user/sbein/NtupleHub/Production2016v2/Summer16.DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_ext1_391_RA2AnalysisTree.root

```

When the script has finished running, open up the file and view a few random histograms. You'll notice that the statistics are very low for the binned pT and eta distributions. 

One of you (not all) can proceed to do a larger submission on the condor batch system, which will generate a higher statistics version of these plots. The script SubmitJobs_condor.py creates one job per input file, running the script specified in the first argument over each respective file. The output file for each job will be delivered to your Output directory. 
```
mkdir Output/
mkdir bird/

python tools/SubmitJobs_condor.py tools/TagNProbeHistMaker_BDT.py "/pnfs/desy.de/cms/tier2/store/user/sbein/NtupleHub/Production2016v2/Summer16.DYJetsToLL*.root"

```
After the jobs are submitted, the status of the jobs can be checked by:
```
condor_q | <your user name> 
#or simply
condor_q 
```

When the jobs are finished, merge the files using an hadd (pronounced like "H"-add) command, After that, we'll proceed to computing the kappa factors from the merged histogram file: 

```
python tools/ahadd.py -f TagnProbe_DYJetsToLL.root Output/BDT_TagnProbeEleHists*.root
```

*note likely for you*: I just realized it is likely that one of your group mates did the submission, so be sure to get the full path to their Output directory, and specify that in the last argument of the above command.

#### step 2. Compute the kappa factors

To compute kappas from the merged histograms, and then proceed to view those kappa factors, run the following two scripts in sequence:
```
python tools/ComputeKappa.py TagnProbe_DYJetsToLL.root
python tools/CompareKappas.py
```
You might find it useful to use a log scale when answering the next question.
<b style='color:black'>Question 7. do you notice anything distinct about the shape of kappa as a function of pT? Eta? What can be said about the charge asymmetry?</b>

#### step 3. peform closure test
Step 3 : Construct a **single lepton CR** and weight each event by the corresponding kappa factor. The result is the **background prediction in the SR** for the prompt electrons. The script called PromptBkgHistMaker_BDT.py creates histograms of these two populations, as well as the **"true" distributions**, which of course consist of events with a disappearing track in the signal region:

```
python tools/PromptBkgHistMaker_BDT.py "/pnfs/desy.de/cms/tier2/store/user/sbein/NtupleHub/Production2016v2/Summer16.WJetsToLNu_HT-800To1200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_25_RA2AnalysisTree.root"
```

If the script runs ok, edit it and add your new signal region from the RGS optimization, and then do another test run to ensure there is no crash. Then, again please just one of you, can proceed to submit a large number of jobs:

```
python tools/SubmitJobs_condor.py tools/PromptBkgHistMaker_BDT.py "/pnfs/desy.de/cms/tier2/store/user/sbein/NtupleHub/Production2016v2/Summer16.WJetsToLNu_*"
```

After a few jobs accrue a bit in the Output directory, an hadd of the output files is in order, as done previously. Again, I realize it is likely that one of your group mates did the submission so be sure to get the full path to their Output directory. 

Step 4: The histograms generated by this script are sufficient to generate a so-called *closure test.* Closure is a consistency check between the data-driven prediction and the truth in the signal region, all performed in simulation. 

```
python tools/closurePromptBkg.py <inputFile.root> <outputFile.root>
```

### 4.b) Fake track background

Another source of background are fake tracks, which are not from real particles but originate from pattern recognition errors in the tracking algorithm. Such tracks are also expected to have higher impact parameters (dxy, dz) as they do not necessarily seem to originate from the primary vertex. A general strategy to estimate this background is to relax the disappearing track tag by removing the impact parameter from the training and preselection.

#### Identifying fake tracks

The following figure shows a (somewhat extreme) example how pattern recognition errors might occur, with hits in the tracking layers indicated as red and valid tracks marked as black. A large number of possible tracks corresponding to hits in the tracker poses a combinatorial problem and can cause fake tracks (violet) to occur:

<center>

![artist's impression](https://i.imgur.com/hKZdG0M.png)
</center>

In addition, the hits marked in red can be valid hits or hits due to detector noise, thus providing another (connected) source of fake tracks.

#### ABCD method

Within the ABCD method, background in the signal region is determined from several control regions. The regions are defined by two uncorrelated variables:

<center>

![](https://i.imgur.com/aQVAzGo.png)
</center>

Let's assume that the signal region A is defined by a small value of both variable 1 and variable 2. Regions B to D are thus control regions. If both variables are uncorrelated, the ration between regions A and C is equal to that of regions B and D:

A/C = B/D

Therefore, contribution to the signal region A can be estimated by A = C‧B/D.

Here, we relax the disappearing track tag by removing dxyVtx from the BDT training. We will then use the ABCD method to determine the fake tracks contribution. A signal and three control regions can be defined by dxyVtx and another uncorrelated variable, chi2Ndof.

<b style='color:black'>Question 7. Evaluate the correlation between the two variables.</b>

Create a 2D plot of the two variables for events which have at least one (loosely) tagged track which is not a PF lepton. First, change to the FakeBkg directory and copy the complete and relaxed BDT to that location:

```
$ cp -r /nfs/dust/cms/user/kutznerv/cmsdas/BDTs/* .
```

Take a look at tmvx.cxx in each directory to see which variables and preselection have been used in the BDT training. We will first test the method on a ZJetsToNuNu MC background sample. You can use the following script:

```
$ python fakes-analyzer.py
```

There are missing parts in the script which you need to complete to get the plot. They are marked with "TODO".

Create the 2D plot for events which pass the relaxed disappearing track tag, the BDT preselection and the ParticleFlow lepton veto. Once you have created the plot, you now have to define a signal region and three control regions by putting cuts on dxyVtx and chi2Ndof. To do this, we will once again use RGS.

Write a RGS configuration file, in which you load the following prepared trees for signal and backgrounds:
```
/nfs/dust/cms/user/kutznerv/cmsdas/tracks-mini-short-bdt
/nfs/dust/cms/user/kutznerv/cmsdas/tracks-mini-medium-bdt
```

Take a look at a signal tree with TBrowser. In each tree, you can find the BDT classifier of the complete and relaxed training for each track. Think about the preselection and the correcting weighting of the samples. Run RGS and determine the best cuts.

Some hints: The cross sections needed for the weights can be found in tmva.cxx. You will also need to include the number of events in the weighting. If you select all tracks from the sample, you can use the "Nev" histogram to get the event count:

```
fin = TFile(filename_of_sample)
h_nev = fin.Get("Nev")
nev = h_nev.GetEntries()
```

When considering pixel+strips tracks, RGS might take a long time to finish. In that case, you can limit the number of rows (= number of tracks). Now you have to get the corresponding event count, for which you can use the "event" branch. It contains the event number for each track. Here is one possibility how to determine the event count:

```
fin = TFile(filename_of_sample)
tree = fin.Get("PreSelection")
tree.Draw("event", "Entry$<%s" % numrows, "COLZ")
h_event = tree.GetHistogram()
maxbin = h_event.GetXaxis().GetLast()
nev = h_event.GetXaxis().GetBinCenter( maxbin )
```

Run RGS for pixel-only and pixel+strips tracks and analyze the output. With the best cuts for dxyVtx and chi2Ndof, you can now extend fakes-analyzer.py in order to count events in each region A, B, C and D.

The contribution of fake tracks  will be eventually determined from the control regions B, C and D. Compare the event count in region A to the result you obtain when considering the ratios.

This method does not rely on MC information and is used especially on data to obtain data-driven background estimations. Since we considered a sample with MC truth information first, you can additionally perform a check whether the tagged track is in close distance of a generator particle. If so, we would not classify that track as a fake track:

```
        for iCand in xrange(number_of_tracks):
        
            ...
        
            # for current track, loop over all generator particles
            # and determine how close the track is to the particle:
            if tree.GetBranch("GenParticles"):
                for k in range(len(event.GenParticles)):
                    ...
                    # perform check if track is close to a generator particle
```

How large is the difference when performing the MC truth check?

What is the systematic uncertainty of this method?

The ABCD method is a simple yet powerful data-driven estimation method which is in particular useful if you cannot rely on MC information. However, it is only applicable when the two variables used are not correlated, which is not trivial to determine.


## 6) Limit 

Congratulations, you've made it! We can now put exlusion limits on the production cross section of the signal process. Since the data is still blinded for this analysis, we will calculate 95% CL expected limits.

First, let's install the [Higgs combine](https://cms-hcomb.gitbooks.io/combine/content/) tool. It is recommended to run ``combine`` in a CMSSW 8.1.0 environment. Change to the parent directory of your CMSSW_10_1_0 folder, then do:

```
export SCRAM_ARCH=slc6_amd64_gcc530
cmsrel CMSSW_8_1_0
cd CMSSW_8_1_0/src 
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v7.0.10
scramv1 b clean; scramv1 b # always make a clean build
```

Prepare an example datacard file called ``test``, which contains a single "tthhad" bin and a single nuisance parameter (an uncertainty of the luminosity measurement of 2.5%). For signal and background, the event count is entered into the datacard:

```
------------------------------------
imax 1 number of bins
jmax 1 number of backgrounds
kmax 1 number of nuisance parameters
------------------------------------
bin          tthhad
observation  368
------------------------------------
bin          tthhad          tthhad
process      SIG             BKG
process      0               1
rate         0.6562          368
------------------------------------
lumi  lnN    1.025       1.025
```

Save this example datacard and run:

```
combine test
```

Now, let's calculate an expected limit for our analysis. Modify the datacard with the event counts you have determined and add the systematic uncertainties.
