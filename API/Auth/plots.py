import matplotlib 
import matplotlib.pyplot as plt, mpld3
import numpy as np
import matplotlib.cbook as cbook
import requests
from markupsafe import Markup

matplotlib.use('Agg')

class PlotWeatherData():

	def __init__(self, width, height, _dpi):
		self.marker = '*'
		self.fig, self.ax = plt.subplots()
		self.fig.set_size_inches(width/_dpi, height/_dpi)		

	def createHtmlObject(self):
		self.ax.set(xlabel = self.xLabel, ylabel = self.yLabel)

		data = mpld3.fig_to_html(self.fig)

		return data

	def setData(self, x, y, xLabel, yLabel):
		self.xData = x
		self.yData = y
		self.xLabel = xLabel
		self.yLabel = yLabel
		self.ax.plot(self.xData, self.yData, self.marker)

	def setMarker(self, marker):

		self.marker = marker
	

def getPlotFromURL(url):
	plotData = requests.get(url).content
	plotData = plotData.decode('UTF_8')
	plotData = Markup(plotData)
	return plotData