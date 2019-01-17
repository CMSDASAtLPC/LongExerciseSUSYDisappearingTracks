# Take a root file a make the corresponding datacard

#/usr/bin/env python
import os,sys
from string import *
from ROOT import *

frn = sys.argv[1]
fdn = frn.split('.')[0]+'.txt'
print frn, fdn

fr = TFile(frn)
fd = open(fdn, 'w')

# Physics processes
procs = [
    'Signal',
    'PrEle',
    'PrMu',
    'Fake'
    ]

# Yields for processes
yields = []
for p in procs:
    yields.append(fr.Get(p).Integral())
print yields

# Shape systematics
syst = [
    'Closure'
    ]

# Write the datacard
cnt = '''imax 1 number of channels
jmax %s number of backgrounds
kmax * number of nuisance parameters
------------------------------------------------------------
observation     %s
------------------------------------------------------------
shapes * * %s $PROCESS $PROCESS_$SYSTEMATIC
------------------------------------------------------------
'''
# Number of background processes and number of data events
nbg = str(len(procs) - 1)
ndata = str(fr.Get('data_obs').Integral())

fd.write(cnt % (nbg, ndata, frn))

# Write processes and rates
row = '%-15s ' % 'bin'
for i in procs:
    row = row+'%-9s ' % 'DT'
fd.write(row+'\n')
row = '%-15s ' % 'process'
for i in procs:
    row = row+'%-9s ' % i
fd.write(row+'\n')
row = '%-15s ' % 'process'
for i in range(len(procs)):
    row = row+'%-9i ' % i
fd.write(row+'\n')
row = '%-15s ' % 'rate'
for y in yields:
    row = row+'%9.3f ' % y
fd.write(row+'\n')

# Add random systematics
cnt = ''''------------------------------------------------------------
Lumi     lnN    1.025     1.025     1.025     1.025
jes      lnN    0.98/1.03 -         -         -
btag     lnN    1.02      -         -         -
Closure  shape  -         1.0       1.0       1.0
'''
fd.write(cnt)

