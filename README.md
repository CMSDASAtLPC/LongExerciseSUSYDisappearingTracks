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

*Tracks of long-lived charginos*

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

## 3.) Skimming events (with signal)

We'd like to overlay some signal distributions onto these plots, 
but there are currently no skims for the signal. Have a look 
in the pre-made pyroot script to skim signal events, 
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

## 4.) Performing an optimization

Now it's time to get systematic with the optimization. Many tools exist that help to select events so as to give a good sensitivity. The main challenge is that an exaustive scan over all possible cut values of all observables in an n-dimensional space of observables becomes computationally prohibitive if n(observables) is larger than X. 

One interesting tool that seeks to overcome this curse of dimensionality is called a random grid search (RGS), which is documented in the publication, "Optimizing Event Selection with the Random Grid Search" https://arxiv.org/abs/1706.09907. RGS performs a scan over the observable hyperplane, using a set of available simulated signal (or background) events to define steps in the scan. For each step in the scan, the cut values defining the event selection are taken to be the values of the observables of the event. We are going to run RGS on the signal/background samples, and compare the sensitivity of the selection to the hand-picked cuts you obtained previously.  


```
git clone https://github.com/hbprosper/RGS.git
cd RGS
make
source setup.sh
```
