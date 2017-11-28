# liveMonitor
Monitor multiple signals utilizing BlueSky's LivePlot but without saving data to database (doesn't use databroker)

## liveMonitor.py

	liveMonitor plots (with live updates) PVs. 

### Inputs:

	sigList: 		List of PVs to plot. Defaults are two signals from 29ID.
	displayList: 	Display names for the plots for each PV. Defaults are two 
					signals from 29ID.
	delay: 			delay in seconds between data acquisitions. Defaults 
					to 1 second
	points: 		number of points to acquire, Defaults to infinite
	testPlot:       boolean set to True for using bluesky test signals (det1, 
					noisy_det). Defaults to False
	liveTab			boolean for adding a LiveTable callback during plan. 
					Defaults to False (no LiveTable).
	ylab:			boolean for using EGU field of 1st PV as y-label of plot.  
					Defaults to True (use EGU field)
	verbose:		boolean for showing tracebacks. Default is false which
					suppresses traceback listing
### Usage:


## Multi-LivePlot.ipynb

	This Jupyter notebook was used for prototyping aspects of the liveMonitor project
