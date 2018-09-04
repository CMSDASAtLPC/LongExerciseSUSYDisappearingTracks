# cmsdas


Tracks of long-lived charginos



Events with long-lived charginos

Let's make some distributions of various event-level quantities, comparing signal and background events. 

python tools/CharacterizeEvents.py

Open up canvases.root and have a look at the canvases stored there. Can you identify any potentially useful observables? Hint: the most useful observables have distributions that are different in shape between signal and background.

We can edit tools/CharacterizeEvents.py. Try adding a few sets of selection you think might help the signal/background estimation and re-run the code. Afterwards, open up canvases.root and have another look at the distributions.


Time to get systematic with the optimization. Many tools exist that help in choosing a set of event selection that gives the highest sensitivity. 

git clone https://github.com/hbprosper/RGS.git
cd RGS
make
source setup.sh
