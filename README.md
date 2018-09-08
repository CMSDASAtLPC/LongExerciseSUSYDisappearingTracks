# CMSDAS @ DESY 2018


The following are a set of guidelines for running the 2018 DESY 
CMSDAS Exercise on the search for SUSY with disappearing tracks

## Introduction

Long-lived (LL) charged particles are featured in many models of physics beyond the standard model, e.g., hidden valley theories. In particular, R-parity conserving SUSY models with a wino-like LSP usually feature charginos with proper decay lengths between 1 nm and several meters, after which point the chargino would decay into a neutralino and a very soft pion or lepton. SUSY models with a light higgsino but with particularly heavy bino and wino parameters can also give rise to charginos with similar lifetimes. The known particles do not have similar lifetimes, so the potential signal events are quite distinct from the standard model background. 

The most recent public result of the search for long-lived particles with disappearing tracks at sqrt(s)=13 TeV is available [here](https://cds.cern.ch/record/2306201). This PAS (Physics Analysis Summary) gives a good overview of the general search approach and the characteristics and difficulties one encounters when looking at this particular signature. 

The exercise is organized in sections as follows: After setting up the working area, you will start on the track-level analysis and identify the relevant properties of disappearing tracks (DT). This DT identification is then used on event level where you study the event topology and the background contributions, which are estimated with data-driven methods.

## 1.) Set up a working area

First, login to a NAF machine using the details you received via email: 

```
ssh USERNAME@naf-schoolXX.desy.de
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
git clone https://github.com/ShortTrackSusy/cmsdas.git cmsdas2018
cd cmsdas2018
```

## 2.) Track-level analysis

In this section, you will take a closer look at the tracking properies and develop a method to identify disappearing tracks in events.

### Short introduction to tracking variables

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

### Plot signal and background

TODO: use plotting script to make plots with weighted signal+bg.

<b style='color:black'>Exercise: Create plots of more variables to familiarize yourself with the tracking properties.</b>

### Constructing a DT tag (training a BDT)

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

![](https://i.imgur.com/nAlEGrx.png)

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

## 3.) A look at background events

Let's make some distributions of various event-level quantities, 
comparing signal and background events. 

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

## 4.) Skimming events 

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

## 5.) Performing an optimization

Let's get systematic with the optimization. Many tools exist that help to select events with a good sensitivity. The main challenge is that an exaustive scan over all possible cut values on all observables in an n-dimensional space of observables becomes computationally prohibitive for n>3. 

One interesting tool that seeks to overcome this curse of dimensionality is called a random grid search (RGS), which is documented in the publication, "Optimizing Event Selection with the Random Grid Search" https://arxiv.org/abs/1706.09907. RGS performs a scan over the observable hyperplane, using a set of available simulated signal (or background) events to define steps in the scan. For each step in the scan (each simulated event), a proposed selection is defined taking the cut values to be the values of the observables of the event. We are going to run RGS on the signal/background samples, and compare the sensitivity of the selection to the hand-picked cuts you obtained previously.  


```
git clone https://github.com/sbein/RGS.git
cd RGS/
make
source setup.sh #whenever intending to use RGS
cd ../
pwd
```

The first script to run is tools/rgs_train.py. Open this script up, edit the lumi appropriately (to 35900/pb), give the path to the signal event file you just created, and tweak anything else as you see fit. Then open tools/LLSUSY.cuts. This file specifies the observables you want RGS to scan over and cut on, as well as the type of cut to apply (greater than, less than, equal to...). Run the first RGS script:

```
python tools/rgs_train.py
```
This creates the file LLSUSY.root which contains signal and background counts for each possible selection set in the scan. Now run the second RGS script:

```
python tools/rgs_analyze.py
```
This will print the optimum set of thresholds to the screen, as well as the signal and background count corresponding to each set of cuts. It will also print the approximate signal significance, z.  How does the RGS optimal selection compare to your hand-picked selection? Hopefully better - if not, you are pretty darn good at eyeball optimization!

You'll have noticed the script also draws a canvase. The scatter plot shows the ROC cloud, defined as the set of signal and background efficiencies corresponding to each step of the scan. The color map in the background indicates the highest value of the significance falling into a given bin. 

Open up tools/rgs_analyze.py and have a look. You'll notice the significance measure is the simplified z = s/sqrt(b+db^2), where the user can specify the systematic uncertainty (SU) db. The fractional SU is currently set to 0.05. Try changing this value to something larger and rerunning rgs_analyze.py script. 

<b style='color:black'>Question 5. What happened to the optimum thresholds after doubling the SU? How about the expected significance? </b>

<b style='color:black'>Question 6. What value of the systematic uncertainty would correspond to a significance of 2 sigma, which is the worst case scenario that would allow us to exclude this signal model? </b>

## 6.) Background estimation

   * explain main backgrounds
   * explain why we need a data-diven method here. 
   * nice introduction to data-diven methods [here](http://www.desy.de/~csander/Talks/120223_SFB_DataDrivenBackgrounds.pdf)

### Prompt background

   * estimation method

### Fake tracks

Another source of background are fake tracks, which are not from a real particle but originate from pattern recognition errors in the tracking algorithm. Such tracks are also expected to have higher impact parameters (dxy, dz) as they do not necessarily seem to originate from the primary vertex. A general strategy to estimate this background is to loosen the disappearing track tag by removing the impact parameter from the training and preselection.

#### Identifying fake tracks

   * provide some sketches how fake tracks can contribute to the background

#### ABCD method

   * you will use an ABCD method to determine the fake tracks contribution
   * need two uncorrelated variables. Check correlation for dxy, dz, chi2ndof, track isolation
   * variables used for the region definitions must not be included in the BDT training. we provide loose BDTs.
   * create 2D plot of two uncorrelated variables after applying TMVA preselection + BDT + PF lepton veto
   * need to define regions -> use RGS for this. use trees with applied loosened BDT
   * create 2D plot with region cuts, count events in each region
   * discuss ratio formula

