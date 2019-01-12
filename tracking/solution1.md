The total energy is the sum in quadrature of mass and momentum magnitude,

```
print math.sqrt(0.140**2 + track.p()**2)
```

and the total energy is the linear sum of mass and kinetic energy. Since we're interested in kinetic energy, subtract off the mass:

```
print math.sqrt(0.140**2 + track.p()**2) - 0.140
```

The exact numerical value depends on which track you're looking at, and that depends on how many you're looped through. You can go back to the first event and track using this trick:

```
events.toBegin()   # go back to the first event
for event in events:
    event.getByLabel("generalTracks", tracks)
    for track in tracks.product():
        break   # get out of this loop while you're still on the first track
    break   # get out of this loop while you're still on the first event
```

Now the numerical value should be
```
print math.sqrt(0.140**2 + track.p()**2) - 0.140
```
```
0.635611846351
```
