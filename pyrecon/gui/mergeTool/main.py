from PySide.QtCore import *
from PySide.QtGui import *

from pyrecon.main import openSeries
from pyrecon.tools.mergeTool.main import MergeSet, MergeSeries, MergeSection

from pyrecon.gui.main import BrowseOutputDirectory, DoubleSeriesLoad
from pyrecon.gui.mergeTool.sectionHandlers import SectionMergeWrapper
from pyrecon.gui.mergeTool.seriesHandlers import SeriesMergeWrapper

class MergeSetWrapper(QWidget):
    '''This class is a single widget that contains all necessary widgets for resolving conflicts in a MergeSet and handles the signal/slots between them.'''
    def __init__(self, MergeSet):
        QWidget.__init__(self)
        self.setWindowTitle('PyRECONSTRUCT mergeTool')
        self.merge = MergeSet
        self.loadObjects()
        self.loadFunctions()
        self.loadLayout()
        self.loadResolutions()
    def loadObjects(self):
        self.navigator = MergeSetNavigator(self.merge) # Buttons and list of MergeObjects
        self.resolutionStack = QStackedWidget() # Contains all of the resolution wrappers
    def loadFunctions(self):
        # QStackedWidget needs to respond to setList.itemClicked
        self.navigator.setList.itemClicked.connect( self.updateCurrent )
    def loadLayout(self):
        container = QHBoxLayout()
        container.addWidget(self.navigator)
        container.addWidget(self.resolutionStack)
        self.setLayout(container)
    def loadResolutions(self):
        if self.merge is not None:
            for itemIndex in range( self.navigator.setList.count() ):
                self.resolutionStack.addWidget( self.navigator.setList.item(itemIndex).resolution )
            self.navigator.setList.item(0).clicked() # Show MergeSeries
    def updateCurrent(self, item):
        '''Updates currently shown resolution based on an item received from self.navigator.setList'''
        self.resolutionStack.setCurrentIndex( self.navigator.setList.indexFromItem(item).row() ) # Get row that the item belongs to

class MergeSetNavigator(QWidget):
    '''This class provides buttons for loading and saving MergeSets as well as a list for choosing current conflict to manage.'''
    def __init__(self, MergeSet):
        QWidget.__init__(self)
        self.merge = MergeSet
        self.loadObjects()
        self.loadFunctions()
        self.loadLayout()
    def loadObjects(self):
        self.loadButton = QPushButton('&Change MergeSet')
        self.loadButton.setMinimumHeight(50)
        self.setList = MergeSetList(self.merge)
        self.saveButton = QPushButton('&Save')
        self.saveButton.setMinimumHeight(50)
    def loadFunctions(self):
        self.loadButton.clicked.connect( self.load )
        self.saveButton.clicked.connect( self.save )
    def loadLayout(self):
        container = QVBoxLayout()
        container.addWidget( self.loadButton )
        container.addWidget( self.setList )
        container.addWidget( self.saveButton )
        self.setLayout(container)
    def load(self):
        # Load DoubleSeriesBrowse widget
        loadDialog = DoubleSeriesLoad()
        s1,s2 = openSeries(loadDialog.output[0]), openSeries(loadDialog.output[1]) # Create Series objects from path
        # Make MergeSeries, MergeSection objects
        mSeries = MergeSeries(s1,s2)
        mSections = []
        for i in range(len(s1.sections)):
            mSections.append( MergeSection(s1.sections[i],s2.sections[i]) )
        # Clear setList
        self.setList.clear()
        # Create setList with new MergeSet
        self.setList.merge = MergeSet(mSeries, mSections)
        #=== Could not figure out how to make new one from class, use functions instead
        self.setList.loadObjects()
        self.setList.loadFunctions()
        self.setList.loadLayout()
    def save(self):
        # Check for conflicts
        if self.checkConflicts():
            a = BrowseOutputDirectory()
            outpath = a.output
            # Go through all setList items and save to outputdir
            self.writeMergeObjects(outpath)
    def checkConflicts(self):
        unresolved_list = [] # list of unresolved conflict names
        for i in range(self.setList.count()):
            item = self.setList.item(i)
            if item.isResolved():
                continue
            else:
                unresolved_list.append(item.merge.name)
        # Bring up dialog for unresolved conflicts
        if len(unresolved_list) > 0:
            msg = QMessageBox()
            msg.setText('Not all conflicts were resolved (red/yellow):\n'+'\n'.join(unresolved_list))
            msg.setInformativeText('Would you like to default unresolved conflicts to the first (left) series for these conflicts?')
            msg.setStandardButtons( QMessageBox.Ok | QMessageBox.Cancel)
            ret = msg.exec_()
            return (ret == QMessageBox.Ok)
        else:
            return True
    def writeMergeObjects(self, outpath):
        self.merge.writeMergeSet(outpath)

class MergeSetList(QListWidget):
    '''This class is a specialized QListWidget that contains MergeSetListItems.'''
    def __init__(self, MergeSet):
        QListWidget.__init__(self)
        self.merge = MergeSet
        self.loadObjects()
        self.loadFunctions()
        self.loadLayout()
    def loadObjects(self):
        # Load MergeObjects into list
        self.addItem( MergeSetListItem(self.merge.seriesMerge) ) # Load MergeSeries
        for MergeSection in self.merge.sectionMerges: # Load MergeSections
            self.addItem( MergeSetListItem(MergeSection) )
    def loadFunctions(self):
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # What to do when item clicked?
        self.itemClicked.connect( self.clicked )
        # What to do when item doubleClicked?
        self.itemDoubleClicked.connect( self.doubleClicked )
    def loadLayout(self):
        return
    def clicked(self, item):
        item.clicked()
    #=== COPY/PASTE FROM PREVIOUS
    def itemDoubleClicked(self, item):
        '''double-clicking a mergeItem displays a small menu allowing the user to use quick merge options.'''
        items = self.mergeSelect.selectedItems()
        # Make menu
        dcMenu = QMenu()
        # - Options for when doubleClicked
        selAAction = QAction(QIcon(), 'select A all', self) # Select the A versions of all
        selBAction = QAction(QIcon(), 'select B all', self) # Select the B versions of all
        selABContsActionA = QAction(QIcon(), 'select both contours, rest A', self) # Select both for contour conflicts, A for rest
        selABContsActionB = QAction(QIcon(), 'select both contours, rest B', self) # Select both for contour conflicts, B for rest
        # - ToolTips
        selAAction.setToolTip('Select the A version of everything for this item(s)')
        selBAction.setToolTip('Select the B version of everything for this item(s)')
        selABContsActionA.setToolTip('Select A&&B contours, A for everything else')
        selABContsActionB.setToolTip('Select A&&B contours, B for everything else')
        # - Add options to menu
        dcMenu.addAction(selAAction)
        dcMenu.addAction(selBAction)
        dcMenu.addAction(selABContsActionA)
        dcMenu.addAction(selABContsActionB)

        # Pop open menu for user selection
        action = dcMenu.exec_( QCursor.pos() )

        # Perform selected action
        if action == selAAction:
            self.quickMergeA(items)
        elif action == selBAction:
            self.quickMergeB(items)
        elif action == selABContsActionA:
            self.quickMergeABContsA(items)
        elif action == selABContsActionB:
            self.quickMergeABContsB(items)
    def quickMergeA(self, items):
        '''Selects A version for all conflicts in items.'''
        for item in items:
            if item.object1.__class__.__name__ == 'Section':
                # Select section A's attributes/image
                item.resolution.attributes.pick1.click()
                item.resolution.images.pick1.click()
                # Contours
                # - Select & Move uniqueA contours to output
                item.resolution.contours.inUniqueA.selectAll()
                item.resolution.contours.moveSelectedA.click()
                # - Resolve conflicts (choose A)
                item.resolution.contours.inOvlp.selectAll()
                conflicts = item.resolution.contours.inOvlp.selectedItems()
                for conflict in conflicts:
                    conflict.forceResolution(1) # Choose contour A
                # - - Move to output
                item.resolution.contours.moveSelectedO.click()
                # Move any uniqueB's in output back to input
                item.resolution.contours.outUniqueB.selectAll()
                item.resolution.contours.moveSelectedB.click()
                # Resolve conflicts that may be in output as A
                item.resolution.contours.outOvlp.selectAll()
                outConflicts = item.resolution.contours.outOvlp.selectedItems()
                for conflict in outConflicts:
                    if conflict.background() == QColor('red') or conflict.background() == QColor('lightgreen'):
                        conflict.forceResolution(1)
                item.resolution.contours.outOvlp.clearSelection()
                # Click merge button (conflicts resolved)
                item.resolution.contours.finish()
            elif item.object1.__class__.__name__ == 'Series':
                item.resolution.attributes.pick1.click()
                item.resolution.contours.pick1.click()
                # ZContours
                item.resolution.zcontours.output = item.resolution.zcontours.uniqueA+item.resolution.zcontours.merged
                # - update lab
                item.resolution.zcontours.lab.setText('Only section A\'s zcontours were kept, as per the quickmerge option.')
    def quickMergeB(self, items):
        '''Selects B version for all conflicts in items.'''
        for item in items:
            if item.object1.__class__.__name__ == 'Section':
                # Select section B's attributes/image
                item.resolution.attributes.pick2.click()
                item.resolution.images.pick2.click() 
                # Contours
                # - Select & Move uniqueB contours to output
                item.resolution.contours.inUniqueB.selectAll()
                item.resolution.contours.moveSelectedB.click()
                # - Resolve conflicts (choose B)
                item.resolution.contours.inOvlp.selectAll()
                conflicts = item.resolution.contours.inOvlp.selectedItems()
                for conflict in conflicts:
                    conflict.forceResolution(2) # Choose contour B
                # - - Move to output
                item.resolution.contours.moveSelectedO.click()
                # Move any uniqueA's in output back to input
                item.resolution.contours.outUniqueA.selectAll()
                item.resolution.contours.moveSelectedA.click()
                # Resolve conflicts that may be in output as B
                item.resolution.contours.outOvlp.selectAll()
                outConflicts = item.resolution.contours.outOvlp.selectedItems()
                for conflict in outConflicts:
                    if conflict.background() == QColor('red') or conflict.background() == QColor('lightgreen'):
                        conflict.forceResolution(2)
                item.resolution.contours.outOvlp.clearSelection()
                # Click merge button (conflicts resolved)
                item.resolution.contours.finish()
            elif item.object1.__class__.__name__ == 'Series':
                item.resolution.attributes.pick2.click()
                item.resolution.contours.pick2.click()
                # ZContours... all but A
                item.resolution.zcontours.output = item.resolution.zcontours.uniqueA+item.resolution.zcontours.merged
                # - update lab
                item.resolution.zcontours.lab.setText('Only section B\'s zcontours were kept, as per the quickmerge option.')
    def quickMergeABContsA(self, items):
        '''This completes the merge resolution by selecting the A version of non-contour conflicts. For contour conflicts, this selects BOTH for overlaps and also includes uniques from A and B.'''
        for item in items:
            if item.object1.__class__.__name__ == 'Section':
                # Select section A's attributes/image
                item.resolution.attributes.pick1.click()
                item.resolution.images.pick1.click() 
                # Contours
                # - Select & Move uniqueA contours to output
                item.resolution.contours.inUniqueA.selectAll()
                item.resolution.contours.moveSelectedA.click()
                # - Select & Move uniqueB contours to output
                item.resolution.contours.inUniqueB.selectAll()
                item.resolution.contours.moveSelectedB.click()
                # - Resolve conflicts (choose BOTH)
                item.resolution.contours.inOvlp.selectAll()
                conflicts = item.resolution.contours.inOvlp.selectedItems()
                for conflict in conflicts:
                    conflict.forceResolution(3) # Choose BOTH contours
                # - - Move to output
                item.resolution.contours.moveSelectedO.click()
                # Resolve conflicts that may be in output as BOTH
                item.resolution.contours.outOvlp.selectAll()
                outConflicts = item.resolution.contours.outOvlp.selectedItems()
                for conflict in outConflicts:
                    if conflict.background() == QColor('red') or conflict.background() == QColor('lightgreen'):
                        conflict.forceResolution(3)
                item.resolution.contours.outOvlp.clearSelection()
                # Click merge button (conflicts resolved)
                item.resolution.contours.finish()
            elif item.object1.__class__.__name__ == 'Series':
                item.resolution.attributes.pick1.click()
                item.resolution.contours.pick1.click()
                # ZContours are default
    def quickMergeABContsB(self, items):
        '''This completes the merge resolution by selection the B version of non-contour conflicts. For contour conflicts, this selects BOTH for overlaps and also includes uniques from A and B.'''
        for item in items:
            if item.object1.__class__.__name__ == 'Section':
                item.resolution.attributes.pick2.click()
                item.resolution.images.pick2.click() 
                # Contours
                # - Select & Move uniqueA contours to output
                item.resolution.contours.inUniqueA.selectAll()
                item.resolution.contours.moveSelectedA.click()
                # - Select & Move uniqueB contours to output
                item.resolution.contours.inUniqueB.selectAll()
                item.resolution.contours.moveSelectedB.click()
                # - Resolve conflicts (choose BOTH)
                item.resolution.contours.inOvlp.selectAll()
                conflicts = item.resolution.contours.inOvlp.selectedItems()
                for conflict in conflicts:
                    conflict.forceResolution(3) # Choose BOTH contours
                # - - Move to output
                item.resolution.contours.moveSelectedO.click()
                # Resolve conflicts that may be in output as BOTH
                item.resolution.contours.outOvlp.selectAll()
                outConflicts = item.resolution.contours.outOvlp.selectedItems()
                for conflict in outConflicts:
                    if conflict.background() == QColor('red') or conflict.background() == QColor('lightgreen'):
                        conflict.forceResolution(3)
                item.resolution.contours.outOvlp.clearSelection()
                # Click merge button (conflicts resolved)
                item.resolution.contours.finish()
            elif item.object1.__class__.__name__ == 'Series':
                item.resolution.attributes.pick2.click()
                item.resolution.contours.pick2.click()
                # ZContours are default
    #=== END COPY/PASTE

class MergeSetListItem(QListWidgetItem):
    '''This is a specialized QListWidgetItem that contains either a MergeSection or MergeSeries object and the widget used for its resolution'''
    def __init__(self, MergeObject):
        QListWidgetItem.__init__(self)
        self.merge = MergeObject
        self.resolution = None
        self.loadDetails()
    def loadDetails(self):
        self.setText(self.merge.name)
        self.setFont(QFont("Arial", 14))
        # Resolution (type specific MergeWrapper)
        if self.merge.__class__.__name__ == 'MergeSection':
            self.resolution = SectionMergeWrapper(self.merge)
        elif self.merge.__class__.__name__ == 'MergeSeries':
            self.resolution = SeriesMergeWrapper(self.merge)
        else:
            print 'Unknown resolution type, could not make wrapper'
        # Check status, choose color
        if not self.merge.isDone():
            self.setBackground(QColor('red'))
        else:
            self.setBackground(QColor('lightgreen'))
    def clicked(self):
        if self.merge.isDone():
            self.setBackground(QColor('lightgreen'))
        else:
            self.setBackground(QColor('yellow'))
    def doubleClicked(self):
        print 'MergeSetListItem.doubleClicked()'
        # Necessary? #===
    def isResolved(self):
        '''Returns true if merge conflicts are resolved.'''
        return self.resolution.merge.isDone()
    def refresh(self): #===
        '''Update colors'''
        if self.isResolved():
            self.setBackground(QColor('lightgreen'))