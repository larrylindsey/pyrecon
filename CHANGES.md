Changes are structured (in reverse-chronological order) as follows:
=============
MAJOR RELEASE
=============
	+++++++++++++
	MINOR RELEASE
	+++++++++++++
		-------------
		MICRO RELEASE
		-------------

***********************************************************************
** Visit  https://github.com/wtrdrnkr/pyrecon  for additional detail **
***********************************************************************
=============
Version 2.0.0
=============
*New project structure:
	- overarching code (handleXML.py and main.py) in main pyrecon folder
	- each tool has its own folder (calibrationTool, curationTool, excelTool, mergeTool)
	- projects in development go in ./.dev/
	- classes have individual files in ./classes/

*pyRECONSTRUCT is now compatible with GitHub: see README.txt for more details
	- mergeToolG has been altered to work with 'git merge' command

*Classes have been changed:.
	- now each class has its own file in pyrecon/classes/
	- all xml handling has been moved to ./handleXML.py

		-------------
		Version 1.4.3
		-------------
		*moved dev files and/or programs to their own folder. bethBellMerge.py, excelTool-dev.py, mergeTool-dev.py

		-------------
		Version 1.4.2
		-------------
		*tools.classes
			-Series.locateDuplicateTraces() no longer considers different named objects to be duplicates
		*tools.curationTool
			-No longer pauses after each curation check

		-------------
		Version 1.4.1
		-------------
		*tools.curationTool
			-fixed adding empty lists in find duplicates
			-fixed extra verbosity

	+++++++++++++
	Version 1.4.0
	+++++++++++++
	*tools.curationTool is now ready for use
		-prints location of duplicate traces, traces separated by a given number of sections, and reverse traces
	*tools.renameFRI
		-removed and no longer developing
	*tools.classes
		-renameObject() added to Series and Section
		-getObject(regex) added to Series and Section
		-locateDistantTraces(), locateReverseTraces(), and locateDuplicates() added to Series
		-isReverse() added to Contour
		
		-------------
		Version 1.3.3
		-------------
		*tools.excelTool
			-fixed error with not recognizing correct trace types/children
		*tools.renameFRI
			-still in dev, full of errors :D
		
		-------------
		Version 1.3.2
		-------------
		*tools.classes.Contour
			-self.overlaps()
				-moved threshold variable to parameter, with default 1+2**(-17)
				-added a checker for Contour._shape population
		*tools.classes.rObject
			-created self.getDendNumber(), self.getProtNumber() to get numbers greater than 2 digits
			-added verbose parameter
		*removed wild-card imports, removed unused imports
		*new renameFRI.py (project for FRI students)
		*tools.mergeTool:
			-added sameName parameter to checkOverlappingContours() and separateOverlappingContours(), with default True
		*tools.excelTool:
			-will now make a save directory if does not exist
			-fixed problem with not recognizing dendrites with more than 2 number digits
			
		-------------
		Version 1.3.1
		-------------
		*tools.findCalFactor
			- rmt.getSeries() -> classes.loadSeries()
	
	+++++++++++++
	Version 1.3.0
	+++++++++++++
	*tools.classes:
		- Implemented a new rObject class w/ specific data depending on trace type
	*tools.excelTool:
		- Implemented more robust excelTool
	*tools.reScale:
		- getSeries -> loadSeries
			
		-------------
		Version 1.2.2
		-------------
		*Removed pause in toosl.excelTool.getDendriteDict()
		*Removed some extra verbose code
		*Added some comments
		
		-------------
		Version 1.2.1
		-------------
		*tools.excelTool will now name sheets based on the 5 first characters of the .ser file name (openpyxl module doesnt allow creation of pages with a name >~30 characters)
		
	+++++++++++++
	Version 1.2.0
	+++++++++++++
	*tools.classes.Series.getObjectLists()
		- removed $ cap from d## matching -> makes a sheet for d## even if it contains no protrusions
	*tools.classes.Series.getObjectHierarchy()
		- added output to show ignored objects
	*tools.excelTool.getDendriteDict()
		- implemented a filter to filter regex in self.filters
		- added regex to filter objects containing a space+word after the conventional name
			- (e.g. 'd17sp09 copy' and 'd19rh37 total' are filtered)
	*tools.excelTool.getProtrusionSpacing()
		- NEEDS A BETTER METHOD FOR IDENTIFYING PROTRUSION CHILDREN, soon
		- Removed tools.excelTool.excelWorkbook.getProtrusionSpacingCount(); redundant
	*LICENSE.txt
		- Added GNU General Public License
	*CHANGES.txt 
		- Indentation to reflect major/minor/micro hierarchy
		- Replaced * with +
	
		-------------
		Version 1.1.2
		-------------
		*Problem with excelTool(tools) where deleting the sheet names 'Sheet' caused an index error when saving; unfortunately, this seems to be a problem with the openpyxl library and thus I can not remove the empty 'Sheet' in the workbook
		*Updated how version changes are displayed in CHANGES.txt to reflect major/minor/micro (===,***,--- respectively)
		
		-------------
		Version 1.1.1
		-------------
		*Removed QMessageBox at mergeTool(toolsgui).mergeEverything() that states backslashes replaced with forward slashes

	+++++++++++++
	Version 1.1.0
	+++++++++++++
	*mergeTool(toolsgui) Should now properly output in windows: added a .replace('\\', '/') to mergeEverything function
	*Removed getSeries/getSeriesXML from mergeTool, now using loadSeries/loadSeriesXML from classes

		-------------
		Version 1.0.4
		-------------
		*Replaced os.sep with '/' in the loadSeries functions (found in classes and mergeTool)
		*Working on Windows 7 (have not tested other Windows versions)
		*Removed template option in excelTool (it was not functional)
		*Added excelTool-dev (in development, more sophisticated GUI)
		
		-------------
		Version 1.0.3
		-------------
		*Removed some unnecessary files from distribution
		
		-------------
		Version 1.0.2
		-------------
		*Updated README
		
		-------------
		Version 1.0.1
		-------------
		*Reorganized and updated README.txt with installation instructions

=============
Version 1.0.0
=============
*mergeTool(toolsgui) is fully functional