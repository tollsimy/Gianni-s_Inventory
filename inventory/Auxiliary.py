__name__ = "Auxiliary"

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from Product import Product
from PyQt5.QtGui import QValidator, QIntValidator, QDoubleValidator
import os
import appdirs
import sys
import json

# ======== Credentials Helpers =========

#NOTE: password is stored in plain text, this is not secure at all

def saveDBCredentials(dbName, dbUser, dbPass, dbHost):
    with open(absPathDataDir('dbCredentials.json'), 'w+') as f:
        json.dump({'dbName': dbName, 'dbUser': dbUser, 'dbPass': dbPass, 'dbHost': dbHost}, f)

def loadDBCredentials():
    try:
        with open(absPathDataDir('dbCredentials.json'), 'r') as f:
            credentials = json.load(f)
            dbName = credentials['dbName']
            dbUser = credentials['dbUser']
            dbPass = credentials['dbPass']
            dbHost = credentials['dbHost']
            return dbName, dbUser, dbPass, dbHost
    except FileNotFoundError:
        #print("No credentials file found")
        return None, None, None, None
    except json.decoder.JSONDecodeError:
        #print("Credentials file is empty or corrupted")
        os.remove(absPathDataDir('dbCredentials.json'))
        return None, None, None, None

# ======== Path Helpers =========

def absPathDataDir(relative_path):
    appname = "Gianni's_Inventory"
    appauthor = "tollsimy"
    datapath = appdirs.user_data_dir(appname, appauthor)
    os.makedirs(datapath, exist_ok=True)  # Ensure the directory exists
    return os.path.join(datapath, relative_path)

def absPathResDir(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# =========== GUI Helpers ===========

class MyTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        if ( isinstance(other, QTableWidgetItem) ):
            my_value, my_ok = self.data(Qt.EditRole).toInt()
            other_value, other_ok = other.data(Qt.EditRole).toInt()

            if ( my_ok and other_ok ):
                return my_value < other_value

        return super(MyTableWidgetItem, self).__lt__(other)

class IntOrEmptyValidator(QValidator):
    def validate(self, string, pos):
        if string == "":
            return QValidator.Acceptable, string, pos
        else:
            try:
                val = int(string)
                return QValidator.Acceptable, string, pos
            except ValueError:
                return QValidator.Invalid, string, pos

# 13 digits
class QBigIntValidator(QValidator):
    def validate(self, string, pos):
        if string == "":
            return QValidator.Acceptable, string, pos
        else:
            if (len(string) > 9):
                string1 = string[:9]
                string2 = string[9:]
                try:
                    val1 = int(string1)
                    val2 = int(string2)
                    return QValidator.Acceptable, string, pos
                except ValueError:
                    return QValidator.Invalid, string, pos
            else:
                try:
                    val = int(string)
                    return QValidator.Acceptable, string, pos
                except ValueError:
                    return QValidator.Invalid, string, pos

# Valid combinations:
# 3, +1, -1, +20=, -20=, +, -, ""
class IncrementDecrementValidator(QValidator):
    def validate(self, string, pos):
        if string == "":
            return QValidator.Acceptable, string, pos
        elif string == '+' or string == '-':
            return QValidator.Acceptable, string, pos
        else:
            if string[-1] == "=":
                try:
                    val = int(string[:-1])
                    return QValidator.Acceptable, string, pos
                except ValueError:
                    return QValidator.Invalid, string, pos
            else:
                try:
                    val = int(string)
                    return QValidator.Acceptable, string, pos
                except ValueError:
                    return QValidator.Invalid, string, pos
            
class QDoubleOrEmptyValidatorDot(QDoubleValidator):
    def validate(self, string, pos):
        if string == "":
            return QValidator.Acceptable, string, pos
        else:
            try:
                val = float(string)
                return QValidator.Acceptable, string, pos
            except ValueError:
                return QValidator.Invalid, string, pos

class IntegerOnlyDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(IntOrEmptyValidator())
        return editor
    
class DoubleOnlyDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(QDoubleOrEmptyValidatorDot())
        return editor

class ReadOnlyDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        return None  # Returning None makes the cell read-only
    
class IncrementDecrementDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(IncrementDecrementValidator())
        return editor
    
class SelectProductDialog(QDialog):
    def __init__(self, prodList):
        super().__init__()

        self.setWindowTitle("Select a product")

        self.QBtnOk = QPushButton("Ok")
        self.QBtnOk.setEnabled(False)
        self.QBtnOk.clicked.connect(self.accept)
        self.QBtnCancel = QPushButton("Cancel")
        self.QBtnCancel.clicked.connect(self.reject)
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.addButton(self.QBtnOk, QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton(self.QBtnCancel, QDialogButtonBox.RejectRole)

        self.layout = QVBoxLayout()
        message = QLabel("Select the product to update:")

        # Table to insert the new product data
        self.productListWidget= QTableWidget()
        self.productListWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.productListWidget.setColumnCount(Product.attributesNum)
        self.productListWidget.setHorizontalHeaderLabels(Product.attributesNames)
        self.productListWidget.setRowCount(len(prodList))

class DatabaseCredentialsDialog(QDialog):
    def __init__(self, dbName, dbUser, dbPass, dbHost):
        super().__init__()

        self.setWindowTitle("Connect to database")

        self.QBtnLogin = QPushButton("Login")
        self.QBtnLogin.setEnabled(False)
        self.QBtnLogin.clicked.connect(self.onLoginClicked)
        self.QBtnLoginAndSave = QPushButton("Login and save")
        self.QBtnLoginAndSave.setEnabled(False)
        self.QBtnLoginAndSave.clicked.connect(self.onLoginAndSaveClicked)
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.addButton(self.QBtnLogin, QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton(self.QBtnLoginAndSave, QDialogButtonBox.AcceptRole)

        self.layout = QVBoxLayout()
        message = QLabel("Insert the database credentials:")
        self.layout.addWidget(message)

        # Insert db name
        self.dbNameWidget = QLineEdit()
        self.dbNameWidget.setPlaceholderText("Database name")
        if(dbName != ""):
            self.dbNameWidget.setText(dbName)
        self.layout.addWidget(self.dbNameWidget)
        self.dbNameWidget.textChanged.connect(self.update)
        # Insert db user
        self.dbUserWidget = QLineEdit()
        self.dbUserWidget.setPlaceholderText("Database user")
        if(dbUser != ""):
            self.dbUserWidget.setText(dbUser)
        self.layout.addWidget(self.dbUserWidget)
        self.dbUserWidget.textChanged.connect(self.update)
        # Insert db password
        self.dbPasswordWidget = QLineEdit()
        self.dbPasswordWidget.setPlaceholderText("Database password")
        if(dbPass != ""):
            self.dbPasswordWidget.setText(dbPass)
        self.dbPasswordWidget.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.dbPasswordWidget)
        self.dbPasswordWidget.textChanged.connect(self.update)
        # Insert db host
        self.dbHostWidget = QLineEdit()
        self.dbHostWidget.setPlaceholderText("Database host")
        if(dbHost != ""):
            self.dbHostWidget.setText(dbHost)
        self.layout.addWidget(self.dbHostWidget)
        self.dbHostWidget.textChanged.connect(self.update)

        self.layout.addWidget(self.buttonBox, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)
        self.update()

    def update(self):
        if(self.dbNameWidget.text() != "" and self.dbUserWidget.text() != "" and self.dbPasswordWidget.text() != "" and self.dbHostWidget.text() != ""):
            self.QBtnLogin.setEnabled(True)
            self.QBtnLoginAndSave.setEnabled(True)
            self.dbName = self.dbNameWidget.text()
            self.dbUser = self.dbUserWidget.text()
            self.dbPass = self.dbPasswordWidget.text()
            self.dbHost = self.dbHostWidget.text()

    def onLoginClicked(self):
        # Exec return 1
        self.done(1)

    def onLoginAndSaveClicked(self):
        # Exec return 2
        self.done(2)

class InvalidCredentialsDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Invalid credentials!")

        self.QBtn = QPushButton("Retry")
        self.QBtn.clicked.connect(self.accept)
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.addButton(self.QBtn, QDialogButtonBox.AcceptRole)
        self.buttonBox.accepted.connect(self.accept)     

        self.layout = QVBoxLayout()
        message = QLabel("Error: The database credentials you inserted are not valid.")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

class ConfirmChangesFirstDialog(QDialog):
    def __init__(self, msg):
        super().__init__()

        self.setWindowTitle("Pending changes!")

        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)        

        self.layout = QVBoxLayout()
        message = QLabel(msg)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

class DeleteItemConfirmationDialog(QDialog):
    def __init__(self, prodList):
        super().__init__()

        self.setWindowTitle("Delete confirmation!")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # Create a new layout for the dialog and add the scroll area and button box to it
        dialogLayout = QVBoxLayout()
        message = QLabel("Do you really want to delete the following items? This action cannot be undone.")
        dialogLayout.addWidget(message)

        self.itemsToRemoveLayout = QVBoxLayout()
        for prod in prodList:
            item = QLabel(str(prod))
            self.itemsToRemoveLayout.addWidget(item)

        # Create a new widget for the layout
        layoutWidget = QWidget()
        layoutWidget.setLayout(self.itemsToRemoveLayout)

        # Create a scroll area and set its widget to the layout widget
        scrollArea = QScrollArea()
        scrollArea.setWidget(layoutWidget)

        dialogLayout.addWidget(scrollArea)
        dialogLayout.addWidget(self.buttonBox)

        self.setLayout(dialogLayout)

class ProductAlreadyExistDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Item already exists!")

        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)        

        self.layout = QVBoxLayout()
        message = QLabel("Error: An item with this prodCode / barcode / barcodeStecca already exists.")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

class AddItemDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add a new product")

        self.QBtnOk = QPushButton("Ok")
        self.QBtnOk.setEnabled(False)
        self.QBtnOk.clicked.connect(self.accept)
        self.QBtnCancel = QPushButton("Cancel")
        self.QBtnCancel.clicked.connect(self.reject)
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.addButton(self.QBtnOk, QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton(self.QBtnCancel, QDialogButtonBox.RejectRole)

        self.layout = QVBoxLayout()
        message = QLabel("Insert the new product data:")

        # Table to insert the new product data
        self.newProductWidget= QTableWidget()
        self.newProductWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.newProductWidget.setColumnCount(Product.attributesNum)
        self.newProductWidget.setHorizontalHeaderLabels(Product.attributesNames)
        self.newProductWidget.setRowCount(1)

        # TODO: add independency
        # ProdCode cannot be changed
        self.newProductWidget.setItemDelegateForColumn(1, IntegerOnlyDelegate(self))
        # Barcodes should be numbers only
        self.newProductWidget.setItemDelegateForColumn(3, IntegerOnlyDelegate(self))
        # PriceKG should be numbers only
        self.newProductWidget.setItemDelegateForColumn(4, DoubleOnlyDelegate(self))
        # PricePZ should be numbers only
        self.newProductWidget.setItemDelegateForColumn(5, DoubleOnlyDelegate(self))
        # PackageNumber should be numbers only
        self.newProductWidget.setItemDelegateForColumn(7, IntegerOnlyDelegate(self))
        # Quantity should be numbers only
        self.newProductWidget.setItemDelegateForColumn(8, IntegerOnlyDelegate(self))
        # BarcodeStecca should be numbers only
        self.newProductWidget.setItemDelegateForColumn(9, IntegerOnlyDelegate(self))

        # TODO
        self.newProductWidget.setItem(0, 0, QTableWidgetItem(""))
        self.newProductWidget.setItem(0, 1, QTableWidgetItem(""))
        self.newProductWidget.setItem(0, 2, QTableWidgetItem(""))
        self.newProductWidget.setItem(0, 3, QTableWidgetItem(""))
        self.newProductWidget.setItem(0, 4, QTableWidgetItem(""))
        self.newProductWidget.setItem(0, 5, QTableWidgetItem(""))
        self.newProductWidget.setItem(0, 6, QTableWidgetItem(""))
        self.newProductWidget.setItem(0, 7, QTableWidgetItem(""))
        self.newProductWidget.setItem(0, 8, QTableWidgetItem(""))
        self.newProductWidget.setItem(0, 9, QTableWidgetItem(""))

        # callback
        self.newProductWidget.itemChanged.connect(self.update)

        self.layout.addWidget(message)
        self.layout.addWidget(self.newProductWidget)   
        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)
        self.resize(800, 200)

    def update(self):
        self.QBtnOk.setEnabled(False)
        if(self.newProductWidget.item(0, 1) is not None and self.newProductWidget.item(0, 1).text() != ''):
            self.QBtnOk.setEnabled(True)
            self.product = Product(*(self.newProductWidget.item(0, i).text() for i in range(Product.attributesNum)))

class ResetQuantitiesConfirmationDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Reset confirmation!")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Do you really want to reset all inventory quantities? This action cannot be undone.")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

class ImportFromCSVConfirmationDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Import confirmation!")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Do you really want to import all inventory data from a CSV file and discard current data? This action cannot be undone.")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

class ExportToCSVConfirmationDialog(QDialog):
    def __init__(self, filename):
        super().__init__()

        self.setWindowTitle("Export complete!")

        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        message = QLabel("Inventory exported successfully!")
        self.layout.addWidget(message)
        message = QLabel("File name: " + filename)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

class InvalidFileFormatDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Invalid file format!")

        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)        

        self.layout = QVBoxLayout()
        message = QLabel("Error: The file you are trying to import is not a valid CSV file.")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)