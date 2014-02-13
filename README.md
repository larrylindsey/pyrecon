PyRECONSTRUCT
=============
Date Created: 3/7/2013<br>
Authors: Michael Musslewhite, Larry Lindsey<br>

# Overview
PyRECONSTRUCT provides easy access to data in XML files associated with the program [RECONSTRUCT](http://synapses.clm.utexas.edu/tools/reconstruct/reconstruct.stm).
This package also contains several tools for managing this data:
*mergeTool - merge series together with built-in conflict resolution
*excelTool - output data into excel workbooks (.xlsx)
*calibrationTool - rescale contours representing images in a section
*curationTool - check for various properties of objects in a series
The functions/tools already in place can be used to develop solutions to a wide range of problems associated with RECONSTRUCT data.

# Install Instructions
*Linux*
---
1) Install the following dependencies:
    python-dev
    python-setuptools
    libgeos-dev
    libblas-dev
    liblapack-dev
    libfreetype6-dev
    libpng-dev
    gfortran
    libxml2-dev
    libxslt-dev
    cmake
    libshiboken-dev
2) Install PySide
3) Install PyRECONSTRUCT by running 'python setup.py install' from the parent folder

*Windows* (strongly discouraged)
---
PyRECONSTRUCT for Windows has only been tested using the following method:
1. Download and install Python2.7:
	http://www.python.org/download/releases/2.7.5/
2. Download and install python-setuptools (setup.py install):
	http://python-distribute.org/distribute_setup.py
3. Download PyRECONSTRUCT code from pypi:
	https://pypi.python.org/pypi/PyRECONSTRUCT
4. Run 'setup.py install' after cding into parent folder
	*This will be unsuccessful due to missing dependencies, but it will tell you why.
	 This will most likely be resolved in the following steps, but rerun this command after every step to determine if problems are being resolved successfully 

5. Download and install lxml (includes libxml2/libxslt):
	https://pypi.python.org/packages/2.7/l/lxml/lxml-3.2.3.win-amd64-py2.7.exe#md5=3720e7d124275b728f553eb93831869c
6. Download and install Cython:
	http://www.lfd.uci.edu/~gohlke/pythonlibs/#cython
7. Download and install Scipy-stack:
	http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy-stack
8. Download and install scikit-image:
	http://www.lfd.uci.edu/~gohlke/pythonlibs/#scikit-image
9. Download and install scipy (fixes missing scipy.special package):
	http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy
10. ...Should work now?*
	*email me (address located in setup.py) if there are problems!



---------------------------------------------------------------------------
IMPORTING INTO PYTHON
---------------------------------------------------------------------------
PyRECONSTRUCT should be imported with the name 'pyrecon' (i.e. import pyrecon)

To import only the XML-parse portion of PyRECONSTRUCT:
	
	from pyrecon.tools import classes
		or
	from pyrecon.tool.classes import * 



---------------------------------------------------------------------------
More Information
---------------------------------------------------------------------------

More info on RECONSTRUCT can be found here:
	http://synapses.clm.utexas.edu/tools/index.stm

