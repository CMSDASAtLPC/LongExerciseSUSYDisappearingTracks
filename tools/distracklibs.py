from utils import *

def isDisappearingTrack_(track, itrack, c, readerPixelOnly, readerPixelStrips):###from Akshansh
        moh_ = c.tracks_nMissingOuterHits[itrack]
        phits = c.tracks_nValidPixelHits[itrack]
        thits = c.tracks_nValidTrackerHits[itrack]
        tlayers = c.tracks_trackerLayersWithMeasurement[itrack]
        pixelOnly = phits>0 and thits==phits
        medium = tlayers< 7 and (thits-phits)>0
        long   = tlayers>=7 and (thits-phits)>0
        pixelStrips = medium or long
        if pixelStrips:
                if not moh_>=2: return 0
        if not (c.tracks_nMissingInnerHits[itrack]==0): return 0
        if not (pixelOnly or pixelStrips): return 0                                                                                                         
        if not c.tracks_passPFCandVeto[itrack]: return 0
        pterr = c.tracks_ptError[itrack]/(track.Pt()*track.Pt())        
        dxyVtx = abs(c.tracks_dxyVtx[itrack])
        dzVtx = abs(c.tracks_dzVtx[itrack])        
        if not (c.tracks_trkRelIso[itrack]<0.2 and dzVtx<0.1 and pterr<10): return 0
        if not (c.tracks_trackQualityHighPurity[itrack]): return 0
        nhits = c.tracks_nValidTrackerHits[itrack]
        nlayers = c.tracks_trackerLayersWithMeasurement[itrack]
        if not (nlayers>=2 and nhits>=2): return 0
        matchedCalo = c.tracks_matchedCaloEnergy[itrack]        
        if not dxyVtx < 0.1: return 0
        #if not c.tracks_trackJetIso[itrack]>0.45: return False
        #if not c.tracks_minDrLetpons[itrack]>0.01: return False	        
        trackfv = [dxyVtx, dzVtx, matchedCalo, c.tracks_trkRelIso[itrack], phits, thits, moh_, pterr]
        if pixelOnly:
                mva_ = evaluateBDT(readerPixelOnly, trackfv)
                if not mva_ > 0.1: return 0###.1
                else: return 1
        elif pixelStrips:
                mva_ = evaluateBDT(readerPixelStrips, trackfv)             
                if not mva_ > 0.25:return 0###.25
                else: return 2
        else:
                return 0

def isBaselineTrack(track, itrack, c, hMask):
	if not abs(track.Eta())< 2.4 : return False
	if not (abs(track.Eta()) < 1.4442 or abs(track.Eta()) > 1.566): return False
	if not bool(c.tracks_trackQualityHighPurity[itrack]) : return False
	if not (c.tracks_ptError[itrack]/(track.Pt()*track.Pt()) < 10): return False
	if not abs(c.tracks_dxyVtx[itrack]) < 0.1: return False
	if not abs(c.tracks_dzVtx[itrack]) < 0.1 : return False
	if not c.tracks_trkRelIso[itrack] < 0.2: return False
	if not (c.tracks_trackerLayersWithMeasurement[itrack] >= 2 and c.tracks_nValidTrackerHits[itrack] >= 2): return False
	if not c.tracks_nMissingInnerHits[itrack]==0: return False
	if not c.tracks_nMissingMiddleHits[itrack]==0: return False	
	if hMask!='':
		xax, yax = hMask.GetXaxis(), hMask.GetYaxis()
		ibinx, ibiny = xax.FindBin(track.Phi()), yax.FindBin(track.Eta())
		if hMask.GetBinContent(ibinx, ibiny)==0: return False
	return True
	              
