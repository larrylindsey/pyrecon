from pyrecon.tools import handleXML as xml

class MergeSet: #===
	'''This object contains MergeSeries and MergeSection objects. This can then be passed into mergeTool functions.'''
	def __init__(self, *args, **kwargs):
		self.seriesMerge = None # MergeSeries object
		self.sectionMerge = None # List of MergeSection objects
		self.output_directory = None
		self.processArguments(args, kwargs)
	# Argument processing
	def processArguments(self, args, kwargs):
		self.processArgs(*args)
		self.processKwargs(**kwargs)
		self.checkAttributes()
	def processArgs(self, *args): #===
		return
	def processKwargs(self, **kwargs): #===
		return
	def checkAttributes(self): #===
		return
	# Class methods
	def run(self):
		'''Performs merge for <series> and <sections>'''
		self.seriesMerge.run()
		for sectionMerge in self.sectionMerges:
			sectionMerge.run()
	def save(self):
		if self.output_directory is None:
			# Ask for output_directory #===
			return
		# Create mergedSeries from MergeSeries object
		mergedSeries = self.series.output()
		# For each MergeSection, create section and add to mergedSeries' sections
		for section in self.sections:
			mergedSeries.sections.append( section.output() )
		# Write series/sections
		xml.writeSeries(mergedSeries, self.output_directory, sections=True)

class MergeSection:
	'''This class manages data about two Section objects that are undergoing a merge.'''
	def __init__(self, *args, **kwargs):
		# Sections to be merged
		self.section1 = None
		self.section2 = None

		# Merged stuff
		self.attributes = None
		self.images = None
		self.contours = None

		# Process arguments
		self.processArguments(args, kwargs)

	# Argument processing
	def processArguments(self, args, kwargs):
		'''Process given arguments.'''
		for arg in args:
			print arg #===
			# Section object
			if arg.__class__.__name__ == 'Section':
				if not self.section1:
					self.section1 = arg
				elif not self.section2:
					self.section2 = arg
				else:
					print 'MergeSection already contains two Sections...'
		for kwarg in kwargs:
			print kwarg+':',kwargs[kwarg] #===

	def isDone(self):
		'''Boolean indicating status of merge.'''
		return (self.attributes is not None and
				self.images is not None and
				self.contours is not None)
		
	# mergeTool functions
	def getUniqueContours(self):
		ovlpsA, ovlpsB = self.getOverlappingContours()
		uniqueA = [cont for cont in self.section1.contours if cont not in ovlpsA]
		uniqueB = [cont for cont in self.section2.contours if cont not in ovlpsB]
		return uniqueA, uniqueB
	def getOverlappingContours(self, threshold=(1+2**(-17)), sameName=True, separate=False):
		'''Returns lists of mutually overlapping contours between two Section objects.'''
		OvlpsA = [] # Section1 contours that have ovlps in section2
		OvlpsB = [] # Section2 contours that have ovlps in section1
		for contA in self.section1.contours:
			ovlpA = []
			ovlpB = []
			for contB in self.section2.contours:
				# If sameName: only check contours with the same name
				if sameName and contA.name == contB.name and contA.overlaps(contB, threshold) != 0:
					ovlpA.append(contA)
					ovlpB.append(contB)
				# If not sameName: check all contours, regardless of same name
				elif not sameName and contA.overlaps(contB, threshold) != 0:
					ovlpA.append(contA)
					ovlpB.append(contB)
			OvlpsA.extend(ovlpA)
			OvlpsB.extend(ovlpB)
		if not separate:
			return OvlpsA, OvlpsB
		else:
			return MergeSection.separateOverlappingContours(OvlpsA, OvlpsB, threshold, sameName) #===

	def separateOverlappingContours(ovlpsA, ovlpsB, threshold=(1+2**(-17)), sameName=True):
		'''Returns a list of completely overlapping pairs and a list of conflicting overlapping pairs.'''
		compOvlps = [] # list of completely overlapping contour pairs
		confOvlps = [] # list of conflicting overlapping contour pairs
		for contA in ovlpsA:
			for contB in ovlpsB:
				overlap = contA.overlaps(contB, threshold)
				if sameName and contA.name == contB.name:
					if overlap == 1:
						compOvlps.append([contA, contB])
					elif overlap != 0 and overlap != 1:
						confOvlps.append([contA, contB])
				elif not sameName:
					if overlap == 1:
						compOvlps.append([contA, contB])
					elif overlap != 0 and overlap != 1:
						confOvlps.append([contA, contB])
		return compOvlps, confOvlps
		

class MergeSeries:
	'''MergeSeries contains the two series to be merged, handlers for how to merge the series, and functions for manipulating class data.'''
	def __init__(self, *args, **kwargs):
		# Series to be merged
		self.series1 = None
		self.series2 = None

		# Merged stuff
		self.attributes = None
		self.contours = None
		self.zcontours = None

		# Process arguments
		self.processArguments(args, kwargs)

	# Argument processing
	def processArguments(self, args, kwargs):
		'''Process given arguments.'''
		for arg in args:
			print arg #===
			if arg.__class__.__name__ == 'Series':
				if not self.series1:
					self.series1 = arg
				elif not self.series2:
					self.series2 = arg
				else:
					print 'MergeSeries already contains two Series...'
		for kwarg in kwargs:
			print kwarg+':',kwargs[kwarg]
	
	def isDone(self):
		'''Boolean indicating status of merge.'''
		return (self.attributes is not None and
				self.contours is not None and
				self.zcontours is not None)

	# mergeTool functions
	def getZContours(self):
		'''Returns unique series1 zcontours, unique series2 zcontours, and overlapping contours.'''
		copyConts1 = [cont for cont in self.series1.zcontours]
		copyConts2 = [cont for cont in self.series2.zcontours]
		overlaps = []
		for contA in copyConts1:
			for contB in copyConts2:
				if contA.name == contB.name and contA.overlaps(contB, threshold):
					# If overlaps, append to overlap list and remove from unique lists
					overlaps.append(contA)
					copyConts1.remove(contA)
					copyConts2.remove(contB)
		return copyConts1, copyConts2, overlaps
