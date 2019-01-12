The solution combines several of the techniques introduced above.

```
import math
import DataFormats.FWLite as fwlite
import ROOT

events = fwlite.Events("tracks_and_vertices.root")
tracks = fwlite.Handle("std::vector<reco::Track>")
mass_histogram = ROOT.TH1F("mass", "mass", 100, 0.0, 5.0)

events.toBegin()
for event in events:
    event.getByLabel("globalMuons", tracks)
    product = tracks.product()
    if product.size() == 2:
        one = product[0]
        two = product[1]
        energy = (math.sqrt(0.106**2 + one.p()**2) +
                  math.sqrt(0.106**2 + two.p()**2))
        px = one.px() + two.px()
        py = one.py() + two.py()
        pz = one.pz() + two.pz()
        mass = math.sqrt(energy**2 - px**2 - py**2 - pz**2)
        mass_histogram.Fill(mass)

c = ROOT.TCanvas ("c", "c", 800, 800)
mass_histogram.Draw()
c.SaveAs("mass.png")
```

The histogram should look like this:

![](/mass.png&raw=true)

If so, congratulations! You've discovered the J/ψ! 
