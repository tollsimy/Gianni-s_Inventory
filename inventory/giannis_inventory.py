from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from Inventory import Inventory
from Product import Product
import Auxiliary as Auxiliary
import sys
import psycopg2
from PyQt5.QtGui import QValidator, QIntValidator, QDoubleValidator, QIcon

class MainWindow(QMainWindow):

    isTableChanged = False
    STAQMode = False

    dbName = None
    dbUser = None
    dbPass = None
    dbHost = None

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gianni's Inventory")

        w = 900; h = 600
        self.resize(w, h)
        self.setWindowIcon(QIcon(Auxiliary.absPathResDir('icon.png')))
        self.show()

        self.dbName, self.dbUser, self.dbPass, self.dbHost = Auxiliary.loadDBCredentials()

        self.myInventory = self.insertCredentials()
        if(self.myInventory is None):
            sys.exit(1)

        self.myMenubarFactory()
        self.gridLayout = QGridLayout()
        self.gridLayout.addWidget(self.myTableFactory(), 0, 0, 1, 1)
        self.gridLayout.addLayout(self.mySearchBoxesFactory(), 1, 0, 1, 1)
        self.gridLayout.addLayout(self.myButtonLayoutFactory(), 2, 0, 1, 1)

        self.widget = QWidget()
        self.widget.setLayout(self.gridLayout)
        self.setCentralWidget(self.widget)

        # Connect signals when inventory changes
        self.myInventory.changeSignal.connect(lambda: self.refreshTable(self.myInventory.productDict))

        # Set focus on searchCell
        self.searchCellBarcodeStecca.setFocus()

    def insertCredentials(self):
        # Create dialog to ask for database credentials
        self.dbCredentialsDialog = Auxiliary.DatabaseCredentialsDialog(self.dbName, self.dbUser, self.dbPass, self.dbHost)
        res = self.dbCredentialsDialog.exec()
        if(res != 0):
            self.dbName = self.dbCredentialsDialog.dbName
            self.dbUser = self.dbCredentialsDialog.dbUser
            self.dbPass = self.dbCredentialsDialog.dbPass
            self.dbHost = self.dbCredentialsDialog.dbHost
            try:
                inventory = Inventory(self.dbName, self.dbUser, self.dbPass, self.dbHost)
                if(res == 2):
                    # Save credentials to file for next time
                    #print("Saving credentials")
                    Auxiliary.saveDBCredentials(self.dbName, self.dbUser, self.dbPass, self.dbHost)
                return inventory
            except psycopg2.Error as e:
                if(Auxiliary.InvalidCredentialsDialog().exec()):
                    print(e)
                    # Retry
                    return self.insertCredentials()
                else:
                    return None
            except Exception as e:
                print(e)
                return None
        else:
            return None

    def myButtonLayoutFactory(self):
        self.myButtonLayoutFactory = QHBoxLayout()
        self.myButtonLayoutFactory.width = 100
        self.myButtonLayoutFactory.height = 100

        # Scan-To-Add-Quantity mode
        self.buttonSTAQMode = QPushButton("STAQ Mode")
        self.buttonSTAQMode.clicked.connect(self.toggleSTAQMode)
        
        self.buttonSave = QPushButton("Save")
        self.buttonSave.clicked.connect(self.applyChanges)
        self.buttonSave.setEnabled(False)
        self.buttonUndo = QPushButton("Undo")
        self.buttonUndo.clicked.connect(self.discardChanges)
        self.buttonUndo.setEnabled(False)

        self.myButtonLayoutFactory.addWidget(self.buttonSTAQMode)
        self.myButtonLayoutFactory.addWidget(self.buttonSave)
        self.myButtonLayoutFactory.addWidget(self.buttonUndo)
        return self.myButtonLayoutFactory

    def mySearchBoxesFactory(self):
        self.searchCellBarcodeStecca = QLineEdit()
        self.searchCellBarcodeStecca.setPlaceholderText("Search by barcodeStecca")
        self.searchCellBarcodeStecca.setMaxLength(13)
        self.searchCellBarcodeStecca.setValidator(Auxiliary.QBigIntValidator())
        self.searchCellBarcodeStecca.width = 100
        self.searchCellBarcodeStecca.height = 100
        self.searchCellBarcodeStecca.textChanged.connect(self.on_text_changed_search_barcode_stecca)

        self.searchCellBarcode = QLineEdit()
        self.searchCellBarcode.setPlaceholderText("Search by barcode")
        self.searchCellBarcode.setMaxLength(13)
        self.searchCellBarcode.setValidator(Auxiliary.QBigIntValidator())
        self.searchCellBarcode.width = 100
        self.searchCellBarcode.height = 100
        self.searchCellBarcode.textChanged.connect(self.on_text_changed_search_barcode)

        self.hLayoutSearch = QHBoxLayout()
        self.hLayoutSearch.width = 100
        self.hLayoutSearch.height = 100
        self.hLayoutSearch.addWidget(self.searchCellBarcodeStecca)
        self.hLayoutSearch.addWidget(self.searchCellBarcode)
        return self.hLayoutSearch

    def myTableFactory(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.setAlternatingRowColors(True)
        # Color selected row
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        # Order by column

        # TODO: add independency 
        # ProdCode cannot be changed
        self.tableWidget.setItemDelegateForColumn(1, Auxiliary.ReadOnlyDelegate(self))
        # Barcodes should be numbers only
        self.tableWidget.setItemDelegateForColumn(3, Auxiliary.IntegerOnlyDelegate(self))
        # PriceKG should be numbers only
        self.tableWidget.setItemDelegateForColumn(4, Auxiliary.DoubleOnlyDelegate(self))
        # PricePZ should be numbers only
        self.tableWidget.setItemDelegateForColumn(5, Auxiliary.DoubleOnlyDelegate(self))
        # PackageNumber should be numbers only
        self.tableWidget.setItemDelegateForColumn(7, Auxiliary.IntegerOnlyDelegate(self))
        # Quantity should be increment/decrement only
        self.tableWidget.setItemDelegateForColumn(8, Auxiliary.IncrementDecrementDelegate(self))
        # BarcodeStecca should be numbers only
        self.tableWidget.setItemDelegateForColumn(9, Auxiliary.IntegerOnlyDelegate(self))

        # Add callback for when a cell is changed
        self.tableWidget.itemChanged.connect(self.on_item_changed)
        # Add callback for when a cell is entered
        self.tableWidget.itemDoubleClicked.connect(self.on_item_clicked)

        self.refreshTable(self.myInventory.getProductList())

        return self.tableWidget

    def myMenubarFactory(self):
        self.myMenubarFactory = QMenuBar()
        self.fileMenu = self.myMenubarFactory.addMenu("File")
        self.saveAction = QAction("Save", self)
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAction.triggered.connect(self.applyChanges)
        self.fileMenu.addAction(self.saveAction)
        self.saveAction.setEnabled(self.isTableChanged)
        self.undoAction = QAction("Undo", self)
        self.undoAction.setShortcut("Ctrl+Z")
        self.undoAction.triggered.connect(self.discardChanges)
        self.fileMenu.addAction(self.undoAction)
        self.undoAction.setEnabled(self.isTableChanged)
        self.exitAction = QAction("Exit", self)
        self.exitAction.setShortcut("Ctrl+Q")
        self.exitAction.triggered.connect(self.close)
        self.fileMenu.addAction(self.exitAction)
        self.editMenu = self.myMenubarFactory.addMenu("Edit")
        self.addAction = QAction("Add", self)
        self.addAction.setShortcut("Ctrl+B")
        self.addAction.triggered.connect(self.addProduct)
        self.editMenu.addAction(self.addAction)
        self.removeAction = QAction("Remove", self)
        self.removeAction.setShortcut("Ctrl+R")
        self.removeAction.triggered.connect(self.removeProduct)
        self.editMenu.addAction(self.removeAction)
        self.resetQuantitiesAction = QAction("Reset quantities", self)
        self.resetQuantitiesAction.setShortcut("Ctrl+T")
        self.resetQuantitiesAction.triggered.connect(self.resetQuantities)
        self.editMenu.addAction(self.resetQuantitiesAction)
        self.exportToCSVAction = QAction("Export to CSV", self)
        self.exportToCSVAction.setShortcut("Ctrl+E")
        self.exportToCSVAction.triggered.connect(self.exportToCSVFilePicker)
        self.editMenu.addAction(self.exportToCSVAction)
        self.importFromCSVAction = QAction("Import from CSV", self)
        self.importFromCSVAction.setShortcut("Ctrl+I")
        self.importFromCSVAction.triggered.connect(self.importFromCSVFilePicker)
        self.editMenu.addAction(self.importFromCSVAction)
        self.STAQModeAction = QAction("STAQ Mode", self)
        self.STAQModeAction.setShortcut("Ctrl+M")
        self.STAQModeAction.triggered.connect(self.toggleSTAQMode)
        self.editMenu.addAction(self.STAQModeAction)
        self.setMenuBar(self.myMenubarFactory)

    def toggleSTAQMode(self):
        if(not self.STAQMode):
            if(self.isTableChanged):
                confirmDialog = Auxiliary.ConfirmChangesFirstDialog("You must confirm or reset changes before entering STAQ Mode!")
                confirmDialog.exec()
            else:
                self.STAQMode = not self.STAQMode
                self.lockTable()
                self.buttonSTAQMode.setText("Exit STAQ Mode")
                self.buttonSTAQMode.setStyleSheet("background-color: green")
                # Set focus on searchCell
                self.searchCellBarcodeStecca.setFocus()
        else:
            if(self.isTableChanged):
                confirmDialog = Auxiliary.ConfirmChangesFirstDialog("You must confirm or reset changes before exiting STAQ Mode!")
                confirmDialog.exec()
            else:
                self.STAQMode = not self.STAQMode
                self.unlockTable()
                self.buttonSTAQMode.setText("STAQ Mode")
                self.buttonSTAQMode.setStyleSheet("background-color: none")

    def lockTable(self):
        # Disable editing
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # Disable selection
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)

    def unlockTable(self):
        # Enable editing
        self.tableWidget.setEditTriggers(QAbstractItemView.AllEditTriggers)
        # Enable selection
        self.tableWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def on_item_changed(self, item):
        self.isTableChanged = True
        # Disconnect callback to prevent infinite loop
        self.tableWidget.itemChanged.disconnect()
        # If quantity is changed
        if(item.column() == Product.attributesNames.index("quantity")):
            # Set quantity to 0 if not valid (e.g. + or -)
            if(item.text() == "" or item.text() == "+" or item.text() == "-"):
                item.setText("0")
            # Increment/decrement if quantity ends with =, set otherwise
            if(item.text().endswith("=")):
                # Get previous quantity
                prodCode = int(self.tableWidget.item(item.row(), Product.attributesNames.index("prodCode")).text())
                prevQuantity = self.myInventory.productDict.get(prodCode).attributesDict.get("quantity")
                # Update quantity with increment
                quantity = prevQuantity + int(item.text()[0:-1])
                # Set quantity in table to new value
                self.tableWidget.item(item.row(), item.column()).setText(str(quantity))
            # Else set quantity to the new value without increment
        newProduct = Product(*[self.tableWidget.item(item.row(), i).text() for i in range(Product.attributesNum)])
        try:
            self.myInventory.updateProduct(newProduct)
            self.buttonSave.setEnabled(self.isTableChanged)
            self.buttonUndo.setEnabled(self.isTableChanged)
            self.saveAction.setEnabled(self.isTableChanged)
            self.undoAction.setEnabled(self.isTableChanged)
        except psycopg2.errors.UniqueViolation:
            self.myInventory.conn.rollback()
            Auxiliary.ProductAlreadyExistDialog().exec()
            item.setText("")
        # Reconnect callback
        self.tableWidget.itemChanged.connect(self.on_item_changed)

    # Putting same number above another is not working because is not changed
    def on_item_clicked(self, item):
        # Disconnect callback so that +0 is visible
        self.tableWidget.itemChanged.disconnect()
        # Reset cell to previous increment when clicking on quantity cell to add increment/decrement
        # e.g. if double clicking on +20 it will show by default +20, then you can edit it
        if(item.column() == Product.attributesNames.index("quantity")):
            if(not item.text().startswith("+") and not item.text().startswith("-")):
                item.setText("+" + item.text())
        # Reconnect callback
        self.tableWidget.itemChanged.connect(self.on_item_changed)

    def refreshTable(self, productDict):
        # Temporary remove callback on itemChanged since being called when refreshing table
        self.tableWidget.itemChanged.disconnect()
        # Disable sorting before refreshing table
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.setColumnCount(Product.attributesNum)
        self.tableWidget.setRowCount(len(productDict))
        self.tableWidget.clear()
        # Re-add header labels
        self.tableWidget.setHorizontalHeaderLabels(Product.attributesNames)
        for row_number, product in enumerate(list(productDict.values())):
            for column_number, data in enumerate(product):
                # Remove None values and replace with empty string for better visualization
                if data is None:
                    data = ""
                self.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        # Re-enable sorting after refreshing table
        self.tableWidget.setSortingEnabled(True)
        # Set callback again
        self.tableWidget.itemChanged.connect(self.on_item_changed)
    
    def on_text_changed_search_barcode(self, item):
        # If STAQMode is enabled, add 1 quantity to product
        if(self.STAQMode):
            products = self.myInventory.getProductsByBarcode(item)
            # If only one product is found, add quantity to it
            # Should be only one product since barcode is unique
            if(len(products) == 1):
                product = list(products.values())[0]
                # Get row of product in table
                row = self.tableWidget.findItems(str(product.attributesDict.get("prodCode")), Qt.MatchExactly)[0].row()
                # Add quantity
                quantity = int(self.tableWidget.item(row, Product.attributesNames.index("quantity")).text())
                self.tableWidget.item(row, 8).setText(str(quantity + 1))
                # Reset searchCellBarcode for next scan
                self.searchCellBarcode.setText("")
        # If STAQMode is disabled, search for product
        else:
            prodDict = self.myInventory.productDict.copy()
            if(len(item) == 0):
                self.refreshTable(self.myInventory.productDict)
            else:
                prodDict = {k: v for k, v in prodDict.items() if v.attributesDict.get("barcode") == int(item)}
                if(len(prodDict) == 1):
                    self.refreshTable(prodDict)
                else:
                    self.refreshTable({})

    def on_text_changed_search_barcode_stecca(self, item):
        # If STAQMode is enabled, add 10 quantity to product
        if(self.STAQMode):
            products = self.myInventory.getProductsByBarcodeStecca(item)
            # If only one product is found, add quantity to it
            # Should be only one product since barcodeStecca is unique
            if(len(products) == 1):
                product = list(products.values())[0]
                # Get row of product in table
                row = self.tableWidget.findItems(str(product.attributesDict.get("prodCode")), Qt.MatchExactly)[0].row()
                # Add quantity
                quantity = int(self.tableWidget.item(row, Product.attributesNames.index("quantity")).text())
                self.tableWidget.item(row, 8).setText(str(quantity + 10))
                # Reset searchCellBarcodeStecca for next scan
                self.searchCellBarcodeStecca.setText("")
        # If STAQMode is disabled, search for product
        else:
            prodDict = self.myInventory.productDict.copy()
            if(len(item) == 0):
                self.refreshTable(self.myInventory.productDict)
            else:
                prodDict = {k: v for k, v in prodDict.items() if v.attributesDict.get("barcodeStecca") == int(item)}
                if(len(prodDict) == 1):
                    self.refreshTable(prodDict)
                else:
                    self.refreshTable({})
        
    def applyChanges(self):
        self.isTableChanged = False
        self.myInventory.applyChanges()
        self.refreshTable(self.myInventory.getProductList())
        self.buttonSave.setEnabled(self.isTableChanged)
        self.buttonUndo.setEnabled(self.isTableChanged)
        self.saveAction.setEnabled(self.isTableChanged)
        self.undoAction.setEnabled(self.isTableChanged)

    def discardChanges(self):
        self.isTableChanged = False
        self.myInventory.discardChanges()
        self.refreshTable(self.myInventory.getProductList())
        self.buttonSave.setEnabled(self.isTableChanged)
        self.buttonUndo.setEnabled(self.isTableChanged)
        self.saveAction.setEnabled(self.isTableChanged)
        self.undoAction.setEnabled(self.isTableChanged)

    def addProduct(self):
        if(self.isTableChanged == False):
            AddDialog = Auxiliary.AddItemDialog()
            if(AddDialog.exec()):
                newProduct = AddDialog.product
                # Check if product already exists (prodCode, barcode, barcodeStecca unique)
                try:
                    self.myInventory.addProduct(newProduct)
                    self.applyChanges()
                except psycopg2.errors.UniqueViolation:
                    self.myInventory.conn.rollback()
                    Auxiliary.ProductAlreadyExistDialog().exec()
            else:
                self.discardChanges()
        else:
            confirmDialog = Auxiliary.ConfirmChangesFirstDialog("You must confirm or reset changes before adding or removing entries!")
            confirmDialog.exec()

    def removeProduct(self):
        if(self.isTableChanged == False):
            prodCodeList = []
            prodList = []
            for item in self.tableWidget.selectionModel().selectedRows():
                prodCodeList.append(self.tableWidget.item(item.row(), 1).text())
            if(len(prodCodeList) != 0):
                for prodCode in prodCodeList:
                    prodList.append(self.myInventory.getProductByProdCode(prodCode))
                confirmDialog = Auxiliary.DeleteItemConfirmationDialog(prodList)
                if(confirmDialog.exec()):
                    for prodCode in prodCodeList:
                        self.myInventory.deleteProduct(prodCode)
                    self.applyChanges()
                else:
                    self.discardChanges()
        else:
            confirmDialog = Auxiliary.ConfirmChangesFirstDialog("You must confirm or reset changes before adding or removing entries!")
            confirmDialog.exec()

    def resetQuantities(self):
        if(self.isTableChanged == False):
            confirmDialog = Auxiliary.ResetQuantitiesConfirmationDialog()
            if(confirmDialog.exec()):
                self.myInventory.resetQuantities()
                self.applyChanges()
        else:
            confirmDialog = Auxiliary.ConfirmChangesFirstDialog("You must confirm or reset changes before resetting quantities!")
            confirmDialog.exec()

    def exportToCSVFilePicker(self):
        if(self.isTableChanged == False):
            filename = QFileDialog.getSaveFileName(self, 'Save File', '', ".csv")
            filename = filename[0]+filename[1]
            if(filename != ''):
                self.myInventory.exportCSV(filename)
                Auxiliary.ExportToCSVConfirmationDialog(filename).exec()
        else:
            confirmDialog = Auxiliary.ConfirmChangesFirstDialog("You must confirm or reset changes before exporting to CSV!")
            confirmDialog.exec()

    def importFromCSVFilePicker(self):
        if(self.isTableChanged == False):
            dialog = QFileDialog()
            options = QFileDialog.Options()
            options |= QFileDialog.ReadOnly
            filename = dialog.getOpenFileName(self, 'Open File', '', "All Files (*);;CSV Files (*.csv)", options=options)[0]
            if(filename != '' and filename.endswith('.csv')):
                confirmDialog = Auxiliary.ImportFromCSVConfirmationDialog()
                if(confirmDialog.exec()):
                    self.myInventory.importCSV(filename)
                    self.applyChanges()
            else:
                Auxiliary.InvalidFileFormatDialog().exec()
        else:
            confirmDialog = Auxiliary.ConfirmChangesFirstDialog("You must confirm or reset changes before importing from CSV!")
            confirmDialog.exec()

    def closeEvent(self, event):
        if(self.isTableChanged):
            confirmDialog = Auxiliary.ConfirmChangesFirstDialog("You must confirm or reset changes before exiting!")
            confirmDialog.exec()
            event.ignore()
        else:
            self.myInventory.stopSignalThread = True
            event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    app.exec()