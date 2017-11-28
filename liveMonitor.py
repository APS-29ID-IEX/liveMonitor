import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import matplotlib.dates as mdates
plt.ion()

# Make plots live-update while scans run.
from bluesky.utils import install_qt_kicker
install_qt_kicker()
 
#Start BlueSky
from bluesky.plans import count
from ophyd.sim import noisy_det, det, motor, det1, det2
from bluesky.callbacks import LivePlot, LiveTable
from bluesky import RunEngine
from ophyd.signal import EpicsSignalRO, EpicsSignal

import datetime

import sys

def curr_doc(name, doc):
    print(name)

class LivePlot2(LivePlot):
	def event(self, doc):
		# Unpack data from the event and call self.update().
		# This outer try/except block is needed because multiple event
		# streams will be emitted by the RunEngine and not all event
		# streams will have the keys we want.
		try:
			# This inner try/except block handles seq_num and time, which could
			# be keys in the data or accessing the standard entries in every
			# event.
			try:
				new_x = doc['data'][self.x]
			except KeyError:
				if self.x in ('time', 'seq_num'):
					new_x = doc[self.x]
				else:
					raise
				new_y = doc['data'][self.y]
		except KeyError:
			# wrong event stream, skip it
			return

		new_t = datetime.datetime.fromtimestamp(new_x)

		self.update_caches(new_t, new_y)
		self.update_plot()


RE = RunEngine({})

class DataFlowControl(object):
	def quitMon(self, event):
		RE.stop()

def liveMonitor(sigList = ['29idd:tc1:setVal_SP.VAL', 
						  '29idd:tc1:getVal_B' ], 
				displayList = ['TC1 setpoint',
							   'TC1 readback'], 
				delay = 1, 
				points = None,
				testPlot = False,
				liveTab = False,
				ylab = True,
				verbose = False):
	'''	liveMonitor plots (with live updates) PVs. 

	Inputs:

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
	'''

	if not verbose: 
		sys.tracebacklimit = 0
	else:
		sys.tracebacklimit = 1000

	#setup PVs to be monitored
	pvList = []
	if not testPlot:
		for j in range(len(sigList)):
			sig = EpicsSignal(sigList[j], name = displayList[j])
			pvList.append(sig)
			if j == 0:
				ylabel = 'EGU' 	#need to add code to use value of EGU field of
								#first PV as y-axis label
	else:
		pvList = [noisy_det, det1, det2]
		displayList = ['noisy_det', 'det1', 'det2']
		ylabel = 'Arb. units'

	#create plot object
	fig, ax = plt.subplots()

	#Rescaling operation -- needs to be here to get ax object
	class AutoScaleAxes(object):
		def resetAxes(self, event):
			ax.set_xlim(auto=True)
			ax.set_ylim(auto=True)
	
	#Rescale button
	ASA = AutoScaleAxes()
	axreset = plt.axes([0.62, 0.91, 0.14, 0.07])
	breset = Button(axreset, 'Reset Axes')
	breset.on_clicked(ASA.resetAxes)

	#Quit button
	DFC = DataFlowControl()
	axquit = plt.axes([0.79, 0.91, 0.18, 0.07])
	bquit = Button(axquit, 'Quit Monitor')
	bquit.on_clicked(DFC.quitMon)

	lm_callbacks = []

	#Define LiveTable callback
	if liveTab:
		lm_callbacks.append(LiveTable(pvList))
	
	#Define multi-plot callback
	for i in pvList:
		lm_callbacks.append(LivePlot2(i, x='time', ax = ax, label=i.name))

	#set axis labels
	ax.set_xlabel('Time') 
	if ylab:
		ax.set_ylabel(ylabel)
	else:
		ax.set_ylabel(' ')
		
	#reformat axis tick labels and data
	lmformat = mdates.DateFormatter('%m/%d %H:%M:%S')
	ax.xaxis.set_major_formatter(lmformat)
	ax.format_xdata = lmformat
	labels = ax.get_xticklabels()
	plt.setp(labels, rotation=30, ha='right')
	plt.subplots_adjust(bottom=0.20)

	#start Run Engine
	RE(count(pvList, delay = delay, num = points), lm_callbacks)
		
	return

