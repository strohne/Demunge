from PySide.QtCore import *
from PySide.QtGui import *

from pandas import DataFrame, Index,ExcelFile,merge
import numpy as np
import os
import re
import json

from datatables import *

QVariant = lambda value=None: value

class OperationTabsWidget(QTabWidget):
    def __init__(self, mainWindow=None):
        super(OperationTabsWidget, self).__init__(mainWindow)
        self.mainWindow = mainWindow
        self.loadTabs()

    def loadTabs(self):
        FlattenOperationTab(self)
        ExtractOperationTab(self)
        SplitOperationTab(self)
        JoinOperationTab(self)

#Abstract base class for operations
class OperationTab(QWidget):
    def __init__(self, parent=None, name="NoName"):
        super(OperationTab, self).__init__(parent)

        self.name = name
        self.mainWindow = parent.mainWindow
        self.settings = parent.mainWindow.settings

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.settingsWidget = QWidget()
        self.mainLayout.addWidget(self.settingsWidget)

        self.mainLayout.addStretch(1)

        self.performButton = QPushButton("Perform transformation")
        self.performButton.clicked.connect(self.perform)
        self.mainLayout.addWidget(self.performButton)


        parent.addTab(self,name)

    @Slot()
    def updateSettings(self):
        pass

    @Slot()
    def perform(self):
        pass


class SplitOperationTab(OperationTab):

    def __init__(self, parent=None, name="Split"):
        super(SplitOperationTab, self).__init__(parent,name)

        # Construct main-Layout
        self.settingsLayout = QFormLayout()
        self.settingsWidget.setLayout(self.settingsLayout)

        self.splitColumn = QComboBox()
        self.splitColumn.setEditable(False)
        self.settingsLayout.addRow("Column to split",self.splitColumn)

        self.separatorEdit = QLineEdit()
        self.settingsLayout.addRow("Separator",self.separatorEdit)
        self.separatorEdit.setText(" ")

        self.indexColumnEdit = QLineEdit()
        self.settingsLayout.addRow("New Index Column",self.indexColumnEdit)
        self.indexColumnEdit.setText("Number")



    @Slot()
    def updateSettings(self):
        self.splitColumn.clear()
        currenttab = self.mainWindow.TableTabs.currentWidget()
        if currenttab is not None:
            self.splitColumn.addItems(currenttab.dataModel.df.columns.tolist())

    @Slot()
    def perform(self):
        try:
            datatab = self.mainWindow.TableTabs.currentWidget()
            data = datatab.dataModel.df

            newdata = self.splitDataFrameList(data,self.splitColumn.currentText(),self.separatorEdit.text(),self.indexColumnEdit.text())

            newtab = self.mainWindow.TableTabs.addTable(datatab.name + " - split")
            newtab.setDataFrame(newdata)
            newtab.show()

        except Exception as e:
            self.mainWindow.logmessage(e)



    def splitDataFrameList(self,df,target_column,separator,target_counter):
        ''' df = dataframe to split,
        target_column = the column containing the values to split
        separator = the symbol used to perform the split

        returns: a dataframe with each entry for the target column separated, with each element moved into a new row.
        The values in the other columns are duplicated across the newly divided rows.
        '''
        def splitListToRows(row,row_accumulator,target_column,separator,target_counter):
            split_row = row[target_column].split(separator)
            no = 0
            for s in split_row:
                no +=1
                new_row = row.to_dict()
                new_row[target_column] = s
                new_row[target_counter] = no
                row_accumulator.append(new_row)

        colnames = df.columns.tolist()
        new_target_counter = target_counter
        no = 2
        while new_target_counter in colnames:
            new_target_counter = target_counter + "_" + str(no)

        new_rows = []
        df.apply(splitListToRows,axis=1,args = (new_rows,target_column,separator,new_target_counter))
        new_df = DataFrame(new_rows)

        colnames.insert(0,new_target_counter)
        new_df = new_df[colnames]
        return new_df


class FlattenOperationTab(OperationTab):

    def __init__(self, parent=None, name="Flatten"):
        super(FlattenOperationTab, self).__init__(parent,name)

        # Construct main-Layout
        self.settingsLayout = QFormLayout()
        self.settingsWidget.setLayout(self.settingsLayout)


        self.levelColumnEdit = QComboBox()
        self.levelColumnEdit.setEditable(False)
        self.settingsLayout.addRow("Level Column",self.levelColumnEdit)

        self.idColumnEdit = QComboBox()
        self.idColumnEdit.setEditable(False)
        self.settingsLayout.addRow("ID Column",self.idColumnEdit)

        self.parentIdColumnEdit = QComboBox()
        self.parentIdColumnEdit.setEditable(False)
        self.settingsLayout.addRow("Parent ID Column",self.parentIdColumnEdit)

        self.childcounterEdit = QLineEdit()
        self.settingsLayout.addRow("Columns to count children (separated by whitespace)",self.childcounterEdit)
        self.childcounterEdit.setText("object_type query_status")



    def updateSettings(self):
        currenttab = self.mainWindow.TableTabs.currentWidget()
        cols = currenttab.dataModel.df.columns.tolist() if currenttab is not None else []

        self.levelColumnEdit.clear()
        self.levelColumnEdit.addItems(cols)
        if "level" in cols:
            self.levelColumnEdit.setCurrentIndex(cols.index('level'))

        self.idColumnEdit.clear()
        self.idColumnEdit.addItems(cols)
        if "id" in cols:
            self.idColumnEdit.setCurrentIndex(cols.index('id'))

        self.parentIdColumnEdit.clear()
        self.parentIdColumnEdit.addItems(cols)
        if "parent_id" in cols:
            self.parentIdColumnEdit.setCurrentIndex(cols.index('parent_id'))


    #Sepearate levels
    def flattenTable(self,fulltable,levelcol,idcol,parentidcol,countchildren):
        fulltable[[levelcol]] = fulltable[[levelcol]].astype(int)
        #fulltable[[idcol]] = fulltable[[idcol]].astype(int)
        #fulltable[[parentidcol]] = fulltable[[parentidcol]].astype(int)

        levels = dict(list(fulltable.groupby(levelcol)))
        minlevel = fulltable.level.min()
        for level, data in sorted(levels.iteritems()):
            #First level is the starting point for the following merges
            if level == minlevel:
                #data = data[[idcol,'object_id','object_type']]
                data = data.add_prefix('level_{}-'.format(level))
                flattable = data
            else:
                #Aggregate object types and join them
                for col_countchildren in countchildren:
                    children = data[parentidcol].groupby([data[parentidcol],data[col_countchildren]]).count()
                    children = children.unstack(col_countchildren)
                    children['total'] = children.sum(axis=1)
                    children = children.add_prefix('level_{}-children-{}-'.format(level-1,col_countchildren))

                    leftkey = 'level_{}-id'.format(level-1)
                    flattable = merge(flattable,children,left_on=leftkey,right_index=True)
                    flattable[children.columns.values.tolist()] = flattable[children.columns.values.tolist()].fillna(0).astype(int)

                #Join data
                data['childnumber'] = data.groupby(parentidcol).cumcount()
                leftkey = 'level_{}-{}'.format(level-1,idcol)
                rightkey = 'level_{}-{}'.format(level,parentidcol)
                data = data.drop([levelcol],axis=1)
                data = data.add_prefix('level_{}-'.format(level))
                flattable = merge(flattable,data,how="outer",left_on=leftkey,right_on=rightkey)
        return flattable

    def getSettings(self):
        countchildren = self.childcounterEdit.text().split(" ")
        return {'level_column':self.levelColumnEdit.currentText(),
                'id_column':self.idColumnEdit.currentText(),
                'parentid_column':self.parentIdColumnEdit.currentText(),
                'countchildren':countchildren
                }

    def perform(self):
        try:
            datatab = self.mainWindow.TableTabs.currentWidget()
            data = datatab.dataModel.df
            settings = self.getSettings()
            self.mainWindow.logmessage("Flatten table {0} with settings {1}".format(datatab.name,json.dumps(settings)) )

            newdata = self.flattenTable(data,settings['level_column'],settings['id_column'],settings['parentid_column'],settings['countchildren'])

            newtab = self.mainWindow.TableTabs.addTable(datatab.name + " - flat")
            newtab.setDataFrame(newdata)
            newtab.show()

        except Exception as e:
            self.mainWindow.logmessage(e)


class JoinOperationTab(OperationTab):

    def __init__(self, parent=None, name="Join"):
        super(JoinOperationTab, self).__init__(parent,name)

        # Construct main-Layout
        self.settingsLayout = QFormLayout()
        self.settingsWidget.setLayout(self.settingsLayout)


        self.joinColumnEdit = QComboBox()
        self.joinColumnEdit.setEditable(False)
        self.settingsLayout.addRow("Join Column",self.joinColumnEdit)

        self.joinHowEdit = QComboBox()
        self.joinHowEdit.setEditable(False)
        self.joinHowEdit.addItems(["left","right","inner","outer"])
        self.settingsLayout.addRow("How to join",self.joinHowEdit)


        self.table2Edit = QComboBox()
        self.table2Edit.setEditable(False)
        self.table2Edit.currentIndexChanged.connect(self.updateForeignCols)
        self.settingsLayout.addRow("Foreign Table",self.table2Edit)

        self.table2JoinColumnEdit = QComboBox()
        self.table2JoinColumnEdit.setEditable(False)
        self.settingsLayout.addRow("Foreign Join Column",self.table2JoinColumnEdit)



    def updateForeignCols(self):
        foreigntab = self.mainWindow.TableTabs.getTabByName(self.table2Edit.currentText())
        cols = foreigntab.dataModel.df.columns.tolist() if foreigntab is not None else []

        self.table2JoinColumnEdit.clear()
        self.table2JoinColumnEdit.addItems(cols)


    def updateSettings(self):
        currenttab = self.mainWindow.TableTabs.currentWidget()
        cols = currenttab.dataModel.df.columns.tolist() if currenttab is not None else []
        self.joinColumnEdit.clear()
        self.joinColumnEdit.addItems(cols)

        alltabs = [self.mainWindow.TableTabs.widget(idx).name for idx in range(self.mainWindow.TableTabs.count())] if self.mainWindow.TableTabs is not None else []
        self.table2Edit.clear()
        self.table2Edit.addItems(alltabs)

        self.updateForeignCols()

    def getSettings(self):
        return {'joincolumn':self.joinColumnEdit.currentText(),
                'foreign_table':self.table2Edit.currentText(),
                'foreign_column':self.table2JoinColumnEdit.currentText(),
                'how':self.joinHowEdit.currentText(),
                }


    def joinTable(self,table,joincolumn,foreign_table,foreign_column,how):
        outtable = merge(table,foreign_table,how=how,left_on=joincolumn,right_on=foreign_column)
        return outtable


    def perform(self):
        try:
            settings = self.getSettings()

            datatab = self.mainWindow.TableTabs.currentWidget()
            data = datatab.dataModel.df

            foreigntab = self.mainWindow.TableTabs.getTabByName(settings['foreign_table'])
            foreigndata = foreigntab.dataModel.df

            self.mainWindow.logmessage("Join table {0} with settings {1}".format(datatab.name,json.dumps(settings)) )

            newdata = self.joinTable(data,settings['joincolumn'],foreigndata,settings['foreign_column'],settings['how'],)

            newtab = self.mainWindow.TableTabs.addTable(datatab.name + " - joined")
            newtab.setDataFrame(newdata)
            newtab.show()

        except Exception as e:
            self.mainWindow.logmessage(e)


class ExtractOperationTab(OperationTab):

    def __init__(self, parent=None, name="Extract"):
        super(ExtractOperationTab, self).__init__(parent,name)

        # Construct main-Layout
        self.settingsLayout = QFormLayout()
        self.settingsWidget.setLayout(self.settingsLayout)

        self.extractColumn = QComboBox()
        self.extractColumn.setEditable(False)
        self.settingsLayout.addRow("Column to extract values from",self.extractColumn)

        self.targetColumn = QLineEdit()
        self.targetColumn.setText("Extracted")
        self.settingsLayout.addRow("Column to save values to",self.targetColumn)

        self.cleanEdit = QCheckBox()
        self.settingsLayout.addRow("Clean linebreaks",self.cleanEdit)
        self.cleanEdit.setChecked(True)

        self.patternEdit = QLineEdit()
        self.settingsLayout.addRow("Regular Expression to extract",self.patternEdit)
        self.patternEdit.setText(r'#[^ ,\.\\/]+')

        self.joinEdit = QLineEdit()
        self.settingsLayout.addRow("Glue for multiple matches",self.joinEdit)
        self.joinEdit.setText(" ")


    @Slot()
    def updateSettings(self):
        self.extractColumn.clear()
        currenttab = self.mainWindow.TableTabs.currentWidget()
        if currenttab is not None:
            self.extractColumn.addItems(currenttab.dataModel.df.columns.tolist())

    @Slot()
    def perform(self):
        try:
            datatab = self.mainWindow.TableTabs.currentWidget()
            data = datatab.dataModel.df.copy()

            newdata = self.extractRegex(data,
                                        self.extractColumn.currentText(),
                                        self.targetColumn.text(),
                                        self.cleanEdit.isChecked(),
                                        self.patternEdit.text(),
                                        self.joinEdit.text())

            newtab = self.mainWindow.TableTabs.addTable(datatab.name + " - extracted")
            newtab.setDataFrame(newdata)
            newtab.show()

        except Exception as e:
            self.mainWindow.logmessage(e)

    def extractRegex(self,df,source_column,target_column,clean,pattern,glue):
        df[target_column] = ''
        #fulltable['level_2-message-hashtags-count'] = 0
        for index, row in df.iterrows():
            msg = row[source_column]
            if isinstance(msg, basestring):
                if clean:
                    msg = msg.replace('\n', ' ').replace('\r', '')
                matches = re.findall(pattern, msg)
                df.ix[index,target_column] = glue.join(matches)
                #fulltable.ix[index,'level_2-message-hashtags-count'] = len(tags)

        return df

