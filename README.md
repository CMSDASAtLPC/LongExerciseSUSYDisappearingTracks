# CMSDAS @ DESY 2018


The following are a set of guidelines for running the 2018 DESY 
CMSDAS Exercise on the search for SUSY with disappearing tracks

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

## 2.) A look at tracks

In this section, you will develop a method to identify disappearing tracks in events.

### Short introduction to tracking variables

For an introduction to CMS tracking, see the [tracking short exercise](https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideCMSDataAnalysisSchoolHamburg2018TrackingAndVertexingExercise).

Generally, CMS analyses operate on AOD datasets, of which smaller datasets (miniAOD, nanoAOD) exist as well. Datasets contain several collections of track objects which contain the trajectories produced by the tracking algorithm. A collection of detector-level information is also retained for each trajectory. A reference of which track variables you can access is given [here](http://cmsdoxygen.web.cern.ch/cmsdoxygen/CMSSW_7_5_2/doc/html/d8/df2/classreco_1_1TrackBase.html).

The detector-level information for each track is stored in the hitpattern. It contains among others the number of hits per track, the number of tracker layers with or without measurement as well as missing hit information. A reference can be found [here](http://cmsdoxygen.web.cern.ch/cmsdoxygen/CMSSW_7_5_2/doc/html/d3/dcb/classreco_1_1HitPattern.html).

In this exercise, we will be working with ntuples created from AOD and minAOD datasets, which contain a selection of useful tracking variables. For this section in particular, ntuples which only contain tracks are used. From each event in the considered datasets, tracks with pT>10 GeV were stored in the ntuple.

Let's start by having a look at some of the tracking variables of signal tracks:
```
$ cd /nfs/dust/cms/user/kutznerv/cmsdas/ntuple-tracks/tracks
$ root signal.root
root [0] new TBrowser
```
With TBrowser, open the "PreSelection" tree and take a look at the variables. The tree contains variables from the track objets such as pT, eta and phi as well as variables from the hitpattern, such as nValidPixelHits or nMissingOuterHits. Also, for each track a selection of corresponding event-level properties as MET and HT are also stored.

Take some time to think about which variables could be relevant for tagging disappearing tracks. The track length is connected to the amount of hits and layers with measurement. Missing inner, middle and outer hits indicate missing hits on the track trajectory before, during and after a certain sequence of hits of the track. DxyVtx and dzVtx indicate the impact parameter with respect to the primary vertex.

One aspect of disappearing tracks is that such tracks contain a certain number of missing outer hits. You can correlate this property with other variables, such as the impact parameter:
```
root [0] PreSelection->Draw("nMissingOuterHits:dxyVtx", "dxyVtx<0.1", "COLZ")
root [0] PreSelection->Draw("nMissingOuterHits:dxyVtx", "dxyVtx<0.01", "COLZ")
```
This already indicates two possible selection criteria for disappearing tracks. Create plots of more variables to familiarize yourself with the tracking properties.

### Constructing a DT tag

After having looked at some of the tracking variables, you now have to develop a set of criteria on how to select disappearing tracks and to discriminate such tracks from Standard Model (SM) background. One approach is to put cuts on each relevant track property by hand. By applying this set of cuts to signal and SM background, you can evaluate the efficiency of the cuts. With the large number of tracking variables available, it is worthwhile to consider other approaches as well, such as a random grid search (RGS) or boosted decision trees (BDT). In the following, we will concentrate on training a BDT for the track selection. The random grid search will be used later in the exercise as well for a different aspect.

#### Track categorization

   * use a basic categorization: very short tracks (pixel-only) and long tracks (pixel+strips)
   * basic approach: put cuts on a selection of tracking variables
   * many variables, large phase space: can use advanced methods such as a BDT. RGS also possible to deal with large phase space
   * introduce BDTs, RGS will be used later in exercise
   * set up TMVA with a small tmva.cxx example macro, look at TMVA GUI output
   * train BDT with selectecd variables
   * evaluate and compare different BDT results by plotting ROC curves. These plots will later be included in the final presentation
   * we are providing BDTs for both pixel-only and pixel+strips categories. Compare your performance to provided BDTs
   * you have now learned how to train a BDT with signal and background samples and to come up with a tag for disppearing tracks
   * in the following, you will use skims which we provided with our BDT results

*Events with long-lived charginos*

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

<b style='color:red'>Question 1: What is the main background in 
  events with low missing transverse momentum, MHT?</b>

<b style='color:red'>Question 2: What is the main background in 
  events with at least 2 b-tagged jets?</b>

## 4.) Skimming events (with signal)

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


<b style='color:red'>Question 3: How many skimmed events are there?</b>
  
Create a directory called Signal for the new file, move the new file into Signal/ 
and re-run the plot maker:

```
mkdir Signal
mv skim_g1800_chi1400_27_200970_step4_30.root Signal/
python tools/CharacterizeEvents.py
root -l canvases.root
```

Clicking around on the canvases, you will now be able to see the signal overlaid (not stacked). Can you identify any observables/kinematic regions where the signal-to-background ratio looks more favorable? Look at several observables and try to come up with a set of cuts that improves the sensitivity. Your selection can be tested by adding elements to the python dictionary called ```cutsets``` in ```tools/CharacterizeEvents.py.``` Hint: the most useful observables have distributions that are different in shape between signal and background.

<b style='color:red'>When you have a decent set of selection and nice looking plots, you can save the canvases as pdfs for the record. </b>

You just performed a so-called eyeball optimization. Can you count the total weighted signal and background events that pass your selection? Write these numbers down in a safe place; we can use them later.

<b style='color:red'>Question 4: How many weighted signal and background events were there passing your selection? What was the expected significance, in terms of s/sqrt(s+b)</b>

## 5.) Performing an optimization

Now it's time to get systematic with the optimization. Many tools exist that help to select events with a good sensitivity. The main challenge is that an exaustive scan over all possible cut values on all observables in an n-dimensional space of observables becomes computationally prohibitive for n>4. 

One interesting tool that seeks to overcome this curse of dimensionality is called a random grid search (RGS), which is documented in the publication, "Optimizing Event Selection with the Random Grid Search" https://arxiv.org/abs/1706.09907. RGS performs a scan over the observable hyperplane, using a set of available simulated signal (or background) events to define steps in the scan. For each step in the scan (each simulated event), a proposed selection is defined taking the cut values to be the values of the observables of the event. We are going to run RGS on the signal/background samples, and compare the sensitivity of the selection to the hand-picked cuts you obtained previously.  


```
git clone https://github.com/hbprosper/RGS.git
cd RGS
make
source setup.sh
```

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

