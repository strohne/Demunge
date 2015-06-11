import sys
import datetime
import logging
import threading
import os

from PySide.QtCore import *
from PySide.QtGui import *
#import icons
#from datatree import *
#from dictionarytree import *
#from database import *
from actions import *
from operations import *
#from apimodules import *
#from help import *
#from presets import *
#from timer import *
#from selectnodes import *


from datatables import *

class MainWindow(QMainWindow):

    def __init__(self,central=None):
        super(MainWindow,self).__init__()

        self.setWindowTitle("Demunge 1.0b")
        #self.setWindowIcon(QIcon(":/icons/icon_demunge.png"))
        self.setMinimumSize(800,600)
        self.move(QDesktopWidget().availableGeometry().center() - self.frameGeometry().center()-QPoint(0,100))



        self.lock_logging = threading.Lock()

        #self.setStyleSheet("* {font-size:21px;}")
        #self.deleteSettings()


        self.readSettings()
        self.createActions()
        self.createUI()
        self.updateUI()




    def createActions(self):
        self.actions=Actions(self)


    def createUI(self):

        #
        #  Statusbar and toolbar
        #

        #self.statusBar().addPermanentWidget(self.timerStatus)
        self.toolbar=Toolbar(parent=self,mainWindow=self)
        self.addToolBar(Qt.TopToolBarArea,self.toolbar)



        #
        #  Layout
        #

        #dummy widget to contain the layout manager
        self.mainWidget=QSplitter(self)
        self.mainWidget.setOrientation(Qt.Vertical)
        self.setCentralWidget(self.mainWidget)

        #top
        topWidget=QWidget(self)
        self.mainWidget.addWidget(topWidget)
        dataLayout=QHBoxLayout()
        topWidget.setLayout(dataLayout)
        dataSplitter = QSplitter(self)
        dataLayout.addWidget(dataSplitter)

        #top left
        dataWidget=QWidget()
        dataLayout=QVBoxLayout()
        dataLayout.setContentsMargins(0,0,0,0)
        dataWidget.setLayout(dataLayout)
        dataSplitter.addWidget(dataWidget)
        dataSplitter.setStretchFactor(0, 1);

        #top right
        detailWidget=QWidget()
        detailLayout=QVBoxLayout()
        detailLayout.setContentsMargins(11,0,0,0)
        detailWidget.setLayout(detailLayout)
        dataSplitter.addWidget(detailWidget)
        dataSplitter.setStretchFactor(1, 0);

        #bottom
        bottomWidget=QWidget(self)
        self.mainWidget.addWidget(bottomWidget)
        self.mainWidget.setStretchFactor(0, 1);

        bottomLayout=QHBoxLayout()
        bottomWidget.setLayout(bottomLayout)

        bottomSplitter = QSplitter(self)
        bottomLayout.addWidget(bottomSplitter)


        #
        #  COmponents
        #

        #Tables
        self.TableTabs=TableTabsWidget(self)
        #self.TableTabs.addTable()
        dataLayout.addWidget(self.TableTabs)

        #Operations

        self.operationTabs=OperationTabsWidget(self)
        bottomSplitter.addWidget(self.operationTabs)
        bottomSplitter.setStretchFactor(0, 1);

        #Status
        statusGroupBox=QGroupBox("Status Log")
        statusGroupBoxLayout=QVBoxLayout()
        statusGroupBox.setLayout(statusGroupBoxLayout)
        bottomSplitter.addWidget(statusGroupBox)
        bottomSplitter.setStretchFactor(1, 0);

        self.loglist=QTextEdit()
        self.loglist.setLineWrapMode(QTextEdit.NoWrap)
        self.loglist.setWordWrapMode(QTextOption.NoWrap)
        self.loglist.acceptRichText=False
        self.loglist.clear()
        statusGroupBoxLayout.addWidget(self.loglist)



    def updateUI(self):
        self.actions.updateActions()



    def writeSettings(self):
        QCoreApplication.setOrganizationName("Juenger")
        QCoreApplication.setApplicationName("Unmunger")

        self.settings = QSettings()
        self.settings.beginGroup("MainWindow")
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        self.settings.setValue("version","1.0")
        self.settings.endGroup()

        #self.settings.setValue('columns',self.fieldList.toPlainText())

#         for i in range(self.RequestTabs.count()):
#             self.RequestTabs.widget(i).saveSettings()

    def readSettings(self):
        QSettings.setDefaultFormat(QSettings.IniFormat)
        QCoreApplication.setOrganizationName("Juenger")
        QCoreApplication.setApplicationName("Unmunger")
        self.settings = QSettings()
        self.settings.beginGroup("MainWindow")

        #self.resize(self.settings.value("size", QSize(800, 800)))
        #self.move(self.settings.value("pos", QPoint(200, 10)))
        self.settings.endGroup()

    def deleteSettings(self):
        QSettings.setDefaultFormat(QSettings.IniFormat)
        QCoreApplication.setOrganizationName("Juenger")
        QCoreApplication.setApplicationName("Unmunger")
        self.settings = QSettings()

        self.settings.clear()
        self.settings.sync()


    def closeEvent(self, event=QCloseEvent()):
        if self.close():
            self.writeSettings()
            event.accept()
        else:
            event.ignore()

    @Slot(str)
    def logmessage(self,message):
        with self.lock_logging:
            if isinstance(message,Exception):
                self.loglist.append(str(datetime.datetime.now())+" Exception: "+str(message))
                logging.exception(message)

            else:
                self.loglist.append(str(datetime.datetime.now())+" "+message)


class Toolbar(QToolBar):
    """
    Initialize the main toolbar
    """
    def __init__(self,parent=None,mainWindow=None):
        super(Toolbar,self).__init__(parent)
        self.mainWindow=mainWindow
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon);
        self.setIconSize(QSize(24,24))

        self.addActions(self.mainWindow.actions.basicActions.actions())
        self.addSeparator()
        self.addActions(self.mainWindow.actions.tableActions.actions())



def startMain():
    app = QApplication(sys.argv)

    main=MainWindow()
    main.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        logfolder = os.path.join(os.path.expanduser("~"),'Unmunger','Logs')
        if not os.path.isdir(logfolder):
            os.makedirs(logfolder)
        logging.basicConfig(filename=os.path.join(logfolder,'unmunger.log'),level=logging.ERROR,format='%(asctime)s %(levelname)s:%(message)s')
    except Exception as e:
        print u"Error intitializing log file: {}".format(e.message)
    finally:
        #cProfile.run('startMain()')
        #yappi.start()
        startMain()
        #yappi.print_stats()


