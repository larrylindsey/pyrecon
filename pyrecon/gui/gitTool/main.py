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
        # self.view = QStackedWidget() #===
        self.view = self.functions.functionView #===
    def loadFunctions(self):
        self.pickBranch.clicked.connect( self.checkoutBranch )
        self.pickCommit.clicked.connect( self.checkoutCommit )
        self.refreshBut.clicked.connect( self.refresh )
        self.branches.itemDoubleClicked.connect( self.openBranchMenu )
    def refresh(self): 
        '''Refresh lists to match current repository status'''
        self.branches.refresh()
        self.commits.refresh()
        self.functions.clickConsole() #=== show git status
    def checkoutBranch(self, lastTry=False, new=False):
        '''Checkout branch and refresh() lists'''
        # Called from functionBar's new branch button
        if new:
            # Create branch via NewBranchHandler
            branchDialog = NewBranchHandler(self.repository)
            if branchDialog.result(): # Result == 1
                branchName = branchDialog.branchName.text()
                branch = self.repository.create_head( branchName )
                branch.checkout()
                subprocess.call(['git','branch','-u','origin'])
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
        try:
            # Retrive commit object
            item = self.commits.selectedItems().pop()
            commit = item.commit
            self.repository.git.checkout(commit)
            self.branches.refresh()
            # self.commits.refresh() # removes commits more recent than the one being checkedout
            self.commits.loadColors()
            # Display console
            self.functions.clickConsole()
        except BaseException, e:
            msg = QMessageBox()
            msg.setInformativeText(str(e))
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            if self.repository.is_dirty(untracked_files=True):
                msg.setText('Error: Would you like to manage possible untracked files?')
                ret = msg.exec_()
                if ret == QMessageBox.Yes:
                    DirtyHandler( self.repository )
                else:
                    return
            else:
                msg.exec_()
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
    def openBranchMenu(self, item):
        # Double click menu
        menu = QMenu()
        menu.addAction('Rename')
        menu.addAction('Delete')
        action = menu.exec_( QCursor.pos() )
        if action.text() == 'Rename':
            self.renameBranch(item.branch)
        elif action.text() == 'Delete':
            self.deleteBranch(item.branch)
    def renameBranch(self, branch):
        renameDialog = RenameBranch(branch)
        if renameDialog.result():
            #=== this may only change local branch, not remote
            ret = subprocess.check_output(['git','branch','-m',str(branch.name),str(renameDialog.textLine.text())])
            self.refresh()
        else:
            msg = QMessageBox()
            msg.setText('Aborting rename...')
            msg.exec_()
    def deleteBranch(self, branch):
        msg = QMessageBox()
        msg.setText('You are about to delete the branch: %s\nThis canNOT be undone, and you will lose data.'%(branch.name))
        msg.setInformativeText('Are you sure you want to do this?')
        msg.setStandardButtons( QMessageBox.Yes | QMessageBox.No )
        confirm = msg.exec_()
        if confirm == QMessageBox.Yes:
            self.repository.branches.master.checkout() #=== necessary to switch before delete
            ret = subprocess.check_output(['git','branch','-D',branch.name])
            self.refresh()
        else:
            msg = QMessageBox()
            msg.setText('Aborting branch delete...')
            msg.exec_()

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
        ret = subprocess.check_output(['git', 'log', '--graph', '--pretty=oneline', '--abbrev-commit'])
        self.functionView.widget(0).setText(ret)
        self.functionView.setCurrentIndex(0)
    def clickConsole(self):
        ret = subprocess.check_output(['git', 'status'])
        self.functionView.widget(1).output.setText(ret)
        self.functionView.setCurrentIndex(1)
    def clickMerge(self):
        if self.repository.is_dirty():
            msg = QMessageBox()
            msg.setText('Repository contains modifications! Please clean before using mergeTool.')
            msg.exec_()
            DirtyHandler(self.repository)
            self.viewer.refresh() #===
            return
        merging = MergeHandler(self.repository)
        self.viewer.refresh()
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
        if self.repository.is_dirty(untracked_files=True):
            a = CommitHandler(self.repository)
        else:
            msg = QMessageBox()
            msg.setText('No changes to commit!')
            msg.exec_()

class BranchList(QListWidget):
    def __init__(self, repository):
        QListWidget.__init__(self)
        self.setWindowTitle('Branches')
        self.repository = repository
        self.loadBranches()
        self.loadColors()
        # self.itemDoubleClicked.connect( self.doubleClick ) # moved signal/slot to RepositoryViewer instead... better refresh functionality
    def loadBranches(self):
        for branch in self.repository.branches:
            item = BranchListItem(branch)
            self.addItem(item)
    def loadColors(self):
        '''Alternates lightgray and white with green for the current HEAD'''
        count = 0
        for i in range(self.count()):
            item = self.item(i)
            if (not self.repository.head.is_detached and
                item.branch.commit == self.repository.head.commit):
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
        if not self.repository.head.is_detached: # check for detached head
            head = self.repository.head.ref
            for commit in self.repository.iter_commits('origin/'+str(head.name)):
                item = CommitListItem(commit)
                self.addItem(item)
        # Check current state; Provide handling
        if self.repository.is_dirty():
            a = DirtyHandler(self.repository)
    def loadColors(self):
        count = 0
        for i in range(self.count()):
            item = self.item(i)
            if (item.commit == self.repository.head.commit):
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
    if repository is None:
        msg = QMessageBox()
        msg.setText('gitTool: Please browse for your repository')
        msg.exec_()
        # Browse for folder 
        browse = BrowseRepository()
        repository = browse.output
    try: # Open repository for gitTool
        repo = Repo(repository)
    except InvalidGitRepositoryError, e: # Git repository not initialized
        a = InvalidRepoHandler(repository)
        if a.result(): # success: result == 1
            repo = Repo(repository)
        else:
            print 'Did not initialize repository'
            return
    except:
        print 'Problem loading repository, quitting...' #===
        return
    finally:
        return RepositoryViewer(repo)

#=== TEST SCRIPT
if __name__ == '__main__':
    app = QApplication.instance()
    if app == None:
        app = QApplication([])
    a = main()
    a.show()
    app.exec_()
