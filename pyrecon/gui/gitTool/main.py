import pyrecon, time, subprocess, os, sys
from git import *
from PySide.QtCore import *
from PySide.QtGui import *
from dialogs import *

class RepositoryViewer(QWidget):
    '''Provides a GUI for interacting with a GitPython repository'''
    def __init__(self, repository):
        QWidget.__init__(self)
        self.repository = repository # The repository being used
        self.setWindowTitle('Repository - '+str(self.repository.working_dir))
        os.chdir(self.repository.working_dir) # For console to retrieve status from correct repository
        self.loadObjects()
        self.loadFunctions()
        self.loadLayout()
    def loadObjects(self):
        # List of branches in the repository
        self.branches = BranchList( self.repository )
        # List of commits for the currently selected branch
        self.commits = CommitList( self.repository )
        self.refreshBut = QPushButton('Refresh')
        self.refreshBut.setToolTip('Click this if you\'ve made changes in the repository outside of this tool')
        self.pickBranch = QPushButton('Checkout this branch')
        self.pickBranch.setMinimumHeight(50)
        self.pickCommit = QPushButton('Checkout this commit')
        self.pickCommit.setMinimumHeight(50)
        self.functions = FunctionsBar( self.repository, viewer=self )
        self.view = QStackedWidget() #===
    def loadFunctions(self):
        self.pickBranch.clicked.connect( self.checkoutBranch )
        self.pickCommit.clicked.connect( self.checkoutCommit )
        self.refreshBut.clicked.connect( self.refresh )
    def refresh(self): 
        '''Refresh lists to match current repository status'''
        self.branches.refresh()
        self.commits.refresh() # will remove commits more recent than the one currently checkedout commit
    def checkoutBranch(self, lastTry=False, new=False):
        '''Checkout branch and refresh() lists'''
        # Called from functionBar's new branch button
        if new:
            # Create branch via NewBranchHandler
            branchDialog = NewBranchHandler(self.repository)
            if branchDialog.result(): # Result == 1
                branchName = branchDialog.branchName.text()
                branch = self.repository.create_head( branchName )
                msg = QMessageBox()
                msg.setText('Branch created: '+str(branchName))
                msg.exec_()
            elif not branchDialog.result(): # Result == 0
                msg = QMessageBox()
                msg.setText('Branch creation aborted...')
                msg.exec_()
                return
        # Called from checkout branch button of BranchList
        else: 
            # Retrieve branch object
            item = self.branches.selectedItems().pop()
            branch = item.branch
        try:
            branch.checkout() # Checkout branch
            # Refresh commitList with commits from new branch
            self.branches.refresh()
            self.commits.refresh()
        except GitCommandError:
            if not lastTry: # Give another chance to handle before aborting attempt
                if self.repository.is_dirty():
                    handler = DirtyHandler(self.repository)
                self.checkoutBranch(lastTry=True)
        self.functions.clickConsole() # Show new repo status
    def checkoutCommit(self):
        '''Reset HEAD to commit and refresh() lists'''
        # Retrive commit object
        item = self.commits.selectedItems().pop()
        commit = item.commit
        self.repository.git.checkout(commit) # Reset head to commit
        self.branches.refresh()
        # self.commits.refresh() # removes commits more recent than the one being checkedout
        self.commits.loadColors()
        # Display console
        self.functions.clickConsole()
    def loadLayout(self):
        # BranchList and CommitList
        branchesAndCommits = QVBoxLayout()
        branchesLabel = QLabel('Branches')
        branchesLabelandRef = QHBoxLayout()
        branchesLabelandRef.addWidget(branchesLabel)
        branchesLabelandRef.addWidget(self.refreshBut)
        branchesAndCommits.addLayout( branchesLabelandRef )
        branchesAndCommits.addWidget(self.branches)
        branchesAndCommits.addWidget(self.pickBranch)
        commitsLabel = QLabel('Commits')
        branchesAndCommits.addWidget( commitsLabel )
        branchesAndCommits.addWidget(self.commits)
        branchesAndCommits.addWidget(self.pickCommit)
        # Functions and View
        functionsAndView = QVBoxLayout()
        functionsAndView.addWidget(self.view)
        functionsAndView.addWidget(self.functions)
        # Main container
        container = QHBoxLayout()
        container.addLayout(branchesAndCommits)
        container.addLayout(functionsAndView)
        self.setLayout(container)

class FunctionsBar(QWidget): #===
    def __init__(self, repository, viewer=None):
        QWidget.__init__(self)
        self.repository = repository
        self.viewer = viewer
        self.loadObjects()
        self.loadFunctions()
        self.loadLayout()
        self.clickConsole()
    def loadObjects(self):
        self.log = QPushButton('Log')
        self.log.setToolTip('View the log of git commands')
        self.console = QPushButton('Console')
        self.console.setToolTip('Open the console to run more sophisticated git commands')
        self.merge = QPushButton('Merge Tool')
        self.merge.setToolTip('Begin the process of merging two repository states')
        self.branch = QPushButton('New Branch')
        self.branch.setToolTip('Create a new branch from the currently selected commit')
        self.pull = QPushButton('Update/Pull')
        self.pull.setToolTip('Pulls the most current version of this branch into the local repository')
        self.push = QPushButton('Commit/Push')
        self.push.setToolTip('Create a new commit for the current status and push to the chosen branch')
        self.functionView = QStackedWidget()
        # Load functions into QStackedWidget()
        self.functionView.addWidget( QTextEdit() ) # 0th index: Log
        self.functionView.addWidget( CommandConsole(self.repository) ) # 1st index: Console
        # self.functionView.addWidget() # 2nd index: Merge #===
        # self.functionView.addWidget() # 3rd index: Branch #===
    def loadFunctions(self):
        self.log.clicked.connect( self.clickLog )
        self.console.clicked.connect( self.clickConsole )
        self.merge.clicked.connect( self.clickMerge )
        self.branch.clicked.connect( self.clickBranch )
        self.pull.clicked.connect( self.clickPull )
        self.push.clicked.connect( self.clickPush )
    def loadLayout(self):
        container = QVBoxLayout()
        buttons = QHBoxLayout()
        buttons.addWidget(self.log)
        buttons.addWidget(self.console)
        buttons.addWidget(self.pull)
        buttons.addWidget(self.push)
        buttons.addWidget(self.branch)
        buttons.addWidget(self.merge)
        container.addLayout(buttons)
        container.addWidget(self.functionView)
        self.setLayout(container)
    def clickLog(self):
        ret = subprocess.check_output(['git', 'log'])
        self.functionView.widget(0).setText(ret)
        self.functionView.setCurrentIndex(0)
    def clickConsole(self):
        ret = subprocess.check_output(['git', 'status'])
        self.functionView.widget(1).output.setText(ret)
        self.functionView.setCurrentIndex(1)
    def clickMerge(self): #===
        print 'merge clicked'
        #=== begin mergeTool process
    def clickBranch(self):
        self.viewer.checkoutBranch(new=True)
    def clickPull(self, lastTry=False):
        '''Fetch and merge the most recent commit into the current state.'''
        try:
            self.repository.remotes.origin.pull() # pull from repo
            self.clickConsole()
            self.viewer.refresh()
        except BaseException, e:
            print 'Problem with pull()', e
            if not lastTry:
                a = DirtyHandler(self.repository)
                self.clickPull(lastTry=True)
    def clickPush(self): #===
        print 'push clicked'
        #=== begin commit process

class BranchList(QListWidget):
    def __init__(self, repository):
        QListWidget.__init__(self)
        self.setWindowTitle('Branches')
        self.repository = repository
        self.loadBranches()
        self.loadColors()
    def loadBranches(self):
        for branch in self.repository.branches:
            item = BranchListItem(branch)
            self.addItem(item)
    def loadColors(self):
        '''Alternates lightgray and white with green for the current HEAD'''
        count = 0
        for i in range(self.count()):
            item = self.item(i)
            if item.branch.commit == self.repository.head.commit:
                item.setBackground(QColor('lightgreen'))
            elif count%2 == 0:
                item.setBackground(QColor('lightgray'))
            else:
                item.setBackground(QColor('white'))
            count+=1
    def refresh(self):
        self.clear()
        self.loadBranches()
        self.loadColors()

class BranchListItem(QListWidgetItem):
    def __init__(self, branch):
        QListWidgetItem.__init__(self)
        self.branch = branch
        self.setText(self.branch.name)
        self.setTextAlignment(Qt.AlignHCenter)
        self.setSizeHint(QSize(self.sizeHint().width(), 30))

class CommitList(QListWidget):
    def __init__(self, repository):
        QListWidget.__init__(self)
        self.setWindowTitle('Commit History')
        self.repository = repository
        self.loadCommits()
        self.loadColors()
        self.setWordWrap(True)
    def loadCommits(self):
        for commit in self.repository.iter_commits(): #=== Get commits from branch, not repository... otherwise will remove commits greater than currently selected date
            item = CommitListItem(commit)
            self.addItem(item)
        # Check current state; Provide handling
        if self.repository.is_dirty(): #=== what about untracked files?
            a = DirtyHandler(self.repository)
    def loadColors(self):
        count = 0
        for i in range(self.count()):
            item = self.item(i)
            if item.commit == self.repository.head.commit: #===
                item.setBackground(QColor('lightgreen'))
            elif count%2 == 0:
                item.setBackground(QColor('lightgray'))
            else:
                item.setBackground(QColor('white'))
            count+=1
    def refresh(self):
        self.clear()
        self.loadCommits()
        self.loadColors()
    
class CommitListItem(QListWidgetItem):
    def __init__(self, commit):
        QListWidgetItem.__init__(self)
        self.commit = commit # GitPython commit object
        self.formatData()
        self.setText(self.date+'\n'+self.message)
        self.setToolTip('Hexsha: '+self.hexsha+'\n'+'Author:\t'+self.author)
        self.setTextAlignment(Qt.AlignHCenter)
    def formatData(self):
        # Format info to be displayed as item text
        self.date = str(time.asctime(time.gmtime(self.commit.committed_date)))
        self.author = str(self.commit.author)
        self.hexsha = str(self.commit.hexsha)
        self.message = str(self.commit.message)

class CommandConsole(QWidget):
    def __init__(self, repository):
        QWidget.__init__(self)
        self.repository = repository
        self.loadObjects()
        self.loadFunctions()
        self.loadLayout()
        self.subprocessCommand() # Run the default command
    def loadObjects(self):
        self.inputLine = QLineEdit('git status')
        self.output = QTextEdit()
    def loadFunctions(self):
        self.inputLine.returnPressed.connect( self.subprocessCommand )
    def loadLayout(self):
        inputBox = QHBoxLayout()
        inputBox.addWidget( self.inputLine )
        outputBox = QHBoxLayout()
        outputBox.addWidget( self.output )
        container = QVBoxLayout()
        container.addLayout(inputBox)
        container.addLayout(outputBox)
        self.setLayout(container)
    def subprocessCommand(self):
        '''Perform the command in self.inputLine and display the results'''
        cmdList = self.inputLine.text().split(' ')
        try:
            rets = subprocess.check_output( cmdList )
        except subprocess.CalledProcessError:
            rets = 'Error running command: '+str(cmdList)+'\n'+str(subprocess.CalledProcessError)
        except Exception, e:
            rets = 'Error running command: '+str(cmdList)+'\n'+str(e)+'\n'+e.__doc__+'\n'+e.message
        self.output.setText( rets )

def main(repository=None): #===
    '''Pass in a path to git repository... return populated RepositoryViewer object'''
    if repository is None: #=== replace this with new BrowseRepository dialog
        # msg = QMessageBox()
        # msg.setText('gitTool: Please browse for your repository')
        # msg.exec_()
        # # Browse for folder 
        # browse = BrowseOutputDirectory()
        # repository = browse.output
        print ('NONE REPO') #===
    try: # Open repository for gitTool
        repo = Repo(repository)
    except InvalidGitRepositoryError: #===
        InvalidRepoHandler(repository)
        #=== set up remote repo?
        repo = Repo(repository)
    except: #===
        print 'Problem loading repository, quitting...' #===
        return
    return RepositoryViewer(repo)

#=== TEST SCRIPT
if __name__ == '__main__':
    app = QApplication.instance()
    if app == None:
        app = QApplication([])
    a = main('/home/michaelm/Documents/pyreconGitTesting')
    a.show()
    app.exec_()
