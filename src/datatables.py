from PySide.QtCore import *
from PySide.QtGui import *
from pandas import DataFrame, Index,ExcelFile
import numpy as np
import os

QVariant = lambda value=None: value

class TableTabsWidget(QTabWidget):
    def __init__(self, mainWindow=None):
        super(TableTabsWidget, self).__init__(mainWindow)
        self.mainWindow = mainWindow
        self.currentChanged.connect(self.mainWindow.actions.changeTable)

    def addTable(self,name = "New Table"):
        tab = TableTab(self,name)
        tab.settings = self.mainWindow.settings
        #tab.toolbar.addActions(self.mainWindow.actions.tableActions.actions())

        return tab

    def getTabByName(self,name):
        tab = None
        if self.count() > 0:
            for idx in range(self.count()):
                if self.widget(idx).name == name:
                    tab = self.widget(idx)
                    break
        return tab

class TableTab(QWidget):
    """
    Generic TableTab Class
    """

    closeEvent = Signal()

    def __init__(self, parent=None, name="New Table"):
        super(TableTab, self).__init__(parent)

        self.tableTabs = parent

        self.setName(name)
        self.isClosing = False
        self.settings = None

        # Construct main-Layout
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)




        #Data
        self.dataModel = DataFrameModel()
        self.dataTable = QTableView()
        self.dataTable.setModel(self.dataModel)
        self.mainLayout.addWidget(self.dataTable)

        #Statusbar
#         self.statusBar = QStatusBar(self)
#         self.mainLayout.addWidget (self.statusBar)
#         self.statusBar.showMessage("{0} records".format(self.dataModel.rowCount()))

        #Toolbar
#         self.toolbar = QToolBar(self)
#         self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon);
#         self.toolbar.setIconSize(QSize(16,16))
#         self.mainLayout.addWidget (self.toolbar)


        self.statusBar = QLabel(self)
        self.statusBar.setText("{0} records ".format(self.dataModel.rowCount()))

        self.mainLayout.addWidget(self.statusBar)
        #self.toolbar.addSeparator()

        self.tableTabs.addTab(self,name)






        #self.buttonLayout = QHBoxLayout()
        #self.mainLayout.addLayout(self.buttonLayout)

#         button=QPushButton("Load Table")
#         button.clicked.connect(self.loadData)
#         self.buttonLayout.addWidget(button,1)
#
#         button=QPushButton("Save Table")
#         button.clicked.connect(self.saveData)
#         self.buttonLayout.addWidget(button,1)
#
#         button=QPushButton("Close Table")
#         button.clicked.connect(self.closeData)
#         self.buttonLayout.addWidget(button,1)

        #df = self.testDf()  # make up some data
        #self.tableWidget.setDataFrame(df)


    def setName(self,name):
        self.index = self.tableTabs.indexOf(self)
        alltabs = [self.tableTabs.tabText(idx) for idx in range(self.tableTabs.count()-1 ) if idx != self.index] if self.tableTabs.count() > 0 else []
        newname = name
        no = 1
        while newname in alltabs:
            newname = name+" ["+ str(no) +"]"
            no += 1
        self.name = newname
        self.tableTabs.setTabText(self.index,newname)

    def show(self):
        self.tableTabs.setCurrentWidget(self)

    def setDataFrame(self, dataFrame):
        self.dataModel.setDataFrame(dataFrame)
        self.dataModel.signalUpdate()

        self.statusBar.setText("{0} records / {1} columns ".format(self.dataModel.rowCount(),self.dataModel.columnCount()))
        #self.dataTable.resizeColumnsToContents()


    def testDf(self):
        ''' creates test dataframe '''
        data = {'int': [1, 2, 3], 'float': [1.5, 2.5, 3.5],
                'string': ['a', 'b', 'c'], 'nan': [np.nan, np.nan, np.nan]}
        return DataFrame(data, index=Index(['AAA', 'BBB', 'CCC']),
                         columns=['int', 'float', 'string', 'nan'])

#
#     def saveData(self):
#         pass


#     def closeData(self):
#         if not self.isClosing:
#             self.isClosing = True
#             self.closeEvent.emit()





class DataFrameModel(QAbstractTableModel):
    ''' data model for a DataFrame class '''
    def __init__(self):
        super(DataFrameModel, self).__init__()
        self.df = DataFrame()

    def setDataFrame(self, dataFrame):
        if dataFrame is None:
            self.df = DataFrame()
        else:
            self.df = dataFrame

    def signalUpdate(self):
        ''' tell viewers to update their data (this is full update, not
        efficient)'''
        self.layoutChanged.emit()

    #------------- table display functions -----------------
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()

        if orientation == Qt.Horizontal:
            try:
                return self.df.columns.tolist()[section]
            except (IndexError, ):
                return QVariant()
        elif orientation == Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return self.df.index.tolist()[section]
            except (IndexError, ):
                return QVariant()

    def data(self, index, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()

        if not index.isValid():
            return QVariant()

        return QVariant(unicode(self.df.ix[index.row(), index.column()]))

    def flags(self, index):
            flags = super(DataFrameModel, self).flags(index)
            #flags |= Qt.ItemIsEditable
            return flags

#     def setData(self, index, value, role):
#         row = self.df.index[index.row()]
#         col = self.df.columns[index.column()]
#         if hasattr(value, 'toPyObject'):
#             # PyQt4 gets a QVariant
#             value = value.toPyObject()
#         else:
#             # PySide gets an unicode
#             dtype = self.df[col].dtype
#             if dtype != object:
#                 value = None if value == '' else dtype.type(value)
#         self.df.set_value(row, col, value)
#         return True

    def rowCount(self, index=QModelIndex()):
        return self.df.shape[0]

    def columnCount(self, index=QModelIndex()):
        return self.df.shape[1]

