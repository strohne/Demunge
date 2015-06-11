from PySide.QtCore import *
from PySide.QtGui import *
from pandas import DataFrame, Index,ExcelFile, read_excel, read_csv
import os
from datatables import *
import codecs

filetype_xlsx = "Excel files (*.xlsx)" #native xlsx
filetype_excelcsv = "Excel CSV files (*.csv)" #Windows encoding (Ansi?), separator=semicolon
filetype_excelunicode = "Excel Unicode Text files (*.csv)" #UTF16-LE mit BOM, separator=tab
filetype_facepager = "Facepager CSV files (*.csv)" #UTF-8 with BOM, separator=semicolon
filetypes = [filetype_facepager,filetype_excelcsv,filetype_excelunicode,filetype_xlsx]

class Actions(object):
    def __init__(self, mainWindow):

        self.mainWindow = mainWindow
        self.settings = self.mainWindow.settings

        #Basic actions
        self.basicActions = QActionGroup(self.mainWindow)
        self.actionAddTable = self.basicActions.addAction("Add Table")
        self.actionAddTable.triggered.connect(self.addTable)


        self.tableActions = QActionGroup(self.mainWindow)
        self.actionLoadData = self.tableActions.addAction("Load Data")
        self.actionLoadData.triggered.connect(self.loadData)

        self.actionSaveData = self.tableActions.addAction("Save Data")
        self.actionSaveData.triggered.connect(self.saveData)

        self.actionCloseTable = self.tableActions.addAction("Close Table")
        self.actionCloseTable.triggered.connect(self.closeTable)




    @Slot()
    def addTable(self):
        try:
            datadir = self.mainWindow.settings.value("lastpath", os.path.expanduser("~"))

            fldg = QFileDialog(caption="Open Data File", directory=datadir)
            fldg.setNameFilters(filetypes)
            fldg.setFileMode(QFileDialog.ExistingFile)

            if fldg.exec_():
                self.mainWindow.settings.setValue("lastpath", fldg.selectedFiles()[0])
                self.readDataFile(fldg.selectedFiles()[0],fldg.selectedFilter())
                self.updateOperators()
        except Exception as e:
            self.mainWindow.logmessage(e)

        self.updateActions()


    @Slot()
    def changeTable(self):
        self.updateOperators()

    def updateActions(self):
        if (self.mainWindow.TableTabs.count() > 0):
            self.tableActions.setEnabled(True)
        else:
            self.tableActions.setEnabled(False)

    def updateOperators(self):
        if hasattr(self.mainWindow,'operationTabs'):
            if (self.mainWindow.operationTabs.count() > 0):
                for idx in range(self.mainWindow.operationTabs.count()):
                    #op_tab = self.mainWindow.operationTabs.currentWidget()
                    op_tab = self.mainWindow.operationTabs.widget(idx)
                    op_tab.updateSettings()

    @Slot()
    def closeTable(self):
        tab = self.mainWindow.TableTabs.currentWidget()
        tab.setDataFrame(None)
        self.mainWindow.TableTabs.removeTab(self.mainWindow.TableTabs.currentIndex())
        self.updateOperators()
        self.updateActions()


    @Slot()
    def loadData(self):
        try:
            tab = self.mainWindow.TableTabs.currentWidget()

            if self.settings is not None:
                datadir = self.settings.value("lastpath", os.path.expanduser("~"))
            else:
                datadir = os.path.expanduser("~")

            fldg = QFileDialog(caption="Open Data File", directory=datadir)
            fldg.setNameFilters(filetypes)
            fldg.setFileMode(QFileDialog.ExistingFile)

            if fldg.exec_():
                if self.settings is not None:
                    self.settings.setValue("lastpath", fldg.selectedFiles()[0])
                progress = QProgressDialog("Loading",None,0,0)
                progress.setWindowModality(Qt.WindowModal)
                progress.open()
                try:
                    self.readDataFile(fldg.selectedFiles()[0],fldg.selectedFilter(),tab)
                finally:
                    progress.cancel()

            self.updateOperators()

        except Exception as e:
            self.mainWindow.logmessage(e)
        self.updateActions()

    def readDataFile(self,filename,filetype,tab=None):
        try:
            filepath, fileext = os.path.splitext(filename)
            filepath, filebasename = os.path.split(filename)

            if not filetype in filetypes:
                if fileext == '.xlsx':
                    filetype = filetype_xlsx
                if fileext == '.csv':
                    filetype = filetype = filetype_excelcsv


            if filetype == filetype_xlsx:
                xl = ExcelFile(filename)
                for sheet in xl.sheet_names:
                    try:
                        df = xl.parse(sheet)

                        if tab is None:
                            tab = self.mainWindow.TableTabs.addTable()
                            tab.setDataFrame(df)
                            tab.setName(filebasename+" "+sheet)
                            tab = None
                        else:
                            tab.setDataFrame(df)
                            tab.setName(filebasename+" "+sheet)
                            break

                    except IndexError:
                        pass

            elif filetype == filetype_excelcsv:
                df = read_csv(filename, sep=';',encoding='cp1252',dtype=str)
                if tab is None:
                    tab = self.mainWindow.TableTabs.addTable()
                tab.setDataFrame(df)
                tab.setName(filebasename)

            elif filetype == filetype_excelunicode:
                df = read_csv(filename, sep="\t",encoding='utf-16LE',dtype=str)
                if tab is None:
                    tab = self.mainWindow.TableTabs.addTable()
                tab.setDataFrame(df)
                tab.setName(filebasename)

            elif filetype == filetype_facepager:

# Automatically detect and remove BOM?
#                 infile = open(filename, 'rb')
#                 raw = infile.read(2)
#                 for enc,boms in \
#                         ('utf-8',(codecs.BOM_UTF8,)),\
#                         ('utf-16',(codecs.BOM_UTF16_LE,codecs.BOM_UTF16_BE)),\
#                         ('utf-32',(codecs.BOM_UTF32_LE,codecs.BOM_UTF32_BE)):
#                     if any(raw.startswith(bom) for bom in boms):
#                         encoding = enc
#
#                         break

                df = read_csv(filename, sep=";",encoding='utf-8-sig',dtype=str)

                firstcolumn = df.columns.values[0]
                firstcolumn = firstcolumn[1:]
                firstcolumn = firstcolumn[:-1]
                df.columns = [firstcolumn] + df.columns.values[1:].tolist()


                if tab is None:
                    tab = self.mainWindow.TableTabs.addTable()
                tab.setDataFrame(df)
                tab.setName(filebasename)

            if tab is not None:
                tab.show()

        except Exception as e:
            self.mainWindow.logmessage(e)

    @Slot()
    def saveData(self):
        try:
            datadir = self.mainWindow.settings.value("lastpath", os.path.expanduser("~"))

            fldg = QFileDialog(caption="Open Data File", directory=datadir)
            filter =  list(filetypes)
            fldg.setNameFilters(filter)
            fldg.setAcceptMode(QFileDialog.AcceptSave)

            if fldg.exec_():
                self.mainWindow.settings.setValue("lastpath", fldg.selectedFiles()[0])
                self.saveDataFile(fldg.selectedFiles()[0],fldg.selectedFilter())
        except Exception as e:
            self.mainWindow.logmessage(e)

    def saveDataFile(self,filename,filetype,tab=None):
        try:
            if tab is None:
                tab = self.mainWindow.TableTabs.currentWidget()
            df = tab.dataModel.df

            filepath, fileext = os.path.splitext(filename)
            filepath, filebasename = os.path.split(filename)

            if not filetype in filetypes:
                if fileext == '.xlsx':
                    filetype = filetype_xlsx
                if fileext == '.csv':
                    filetype = filetype = filetype_excelcsv



            if filetype == filetype_xlsx:
                df.to_excel(filename)

            elif filetype == filetype_excelcsv:
                df.to_csv(filename,sep=";",index=False,encoding="cp1252")

            elif filetype == filetype_excelunicode:
                outfile = open(filename, 'wb')
                try:
                    outfile.write(codecs.BOM_UTF16_LE) #UTF8 BOM
                    df.to_csv(outfile,sep="\t",index=False,encoding="utf-16LE")
                finally:
                    outfile.close()

            elif filetype == filetype_facepager:
                outfile = open(filename, 'wb')
                try:
                    outfile.write(codecs.BOM_UTF8) #UTF8 BOM
                    df.to_csv(outfile,sep=';',index=False,encoding="utf-8")
                finally:
                    outfile.close()
        except Exception as e:
            self.mainWindow.logmessage(e)