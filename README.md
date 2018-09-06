# CMSDAS @ DESY 2018


The following are a set of guidelines for running the 2018 DESY 
CMSDAS Exercise on the search for SUSY with disappearing tracks

## Set up a working area

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

## A look at tracks

*Tracks of long-lived charginos*

*Events with long-lived charginos*

## A look at events

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

After clicking through a few plots, can you identify which are the main backgrounds? 

```rust
Question 1: What is the main background in events with low missing transverse momentum, MHT?
```
```
Question 2: What is the main background in events with at least 2 b-tagged jets?
```rust

Hint: the most useful observables have distributions that are different in shape between signal and background.

We can edit tools/CharacterizeEvents.py. Try adding a few sets of selection you think might help the signal/background estimation and re-run the code. Afterwards, open up canvases.root and have another look at the distributions.


Time to get systematic with the optimization. Many tools exist that help in choosing a set of event selection that gives the highest sensitivity. 

## Performing an optimization
```
git clone https://github.com/hbprosper/RGS.git
cd RGS
make
source setup.sh
```
