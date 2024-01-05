from PyQt5.QtWidgets import *
import inventory
import sys
from PyQt5.QtGui import QIntValidator, QDoubleValidator

from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtGui import QValidator
from PyQt5.QtGui import QIcon

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

class IntegerOnlyDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(IntOrEmptyValidator())
        return editor
    
class DoubleOnlyDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(QDoubleValidator())
        return editor

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gianni's Inventory")
    
        self.gridLayout = QGridLayout()
        self.tableWidget = QTableWidget()
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        #TODO: keep label synced with product.py defintion
        self.tableWidget.setColumnCount(9)
        self.tableWidget.setHorizontalHeaderLabels(["Category", "ProdCode", "DenomComm", "Barcode", "PriceKg", "PricePz", "PackageType", "PackageNumber", "Quantity"])
        self.tableWidget.setRowCount(len(myInventory.getProductList()))
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)

        # ProdCode should be numbers only
        self.tableWidget.setItemDelegateForColumn(1, IntegerOnlyDelegate(self))
        # Barcodes should be numbers only
        self.tableWidget.setItemDelegateForColumn(3, IntegerOnlyDelegate(self))
        # PriceKG should be numbers only
        self.tableWidget.setItemDelegateForColumn(4, DoubleOnlyDelegate(self))
        # PricePZ should be numbers only
        self.tableWidget.setItemDelegateForColumn(5, DoubleOnlyDelegate(self))
        # PackageNumber should be numbers only
        self.tableWidget.setItemDelegateForColumn(7, IntegerOnlyDelegate(self))
        # Quantity should be numbers only
        self.tableWidget.setItemDelegateForColumn(8, IntegerOnlyDelegate(self))

        # Populate the table with data from the productList
        for row_number, product in enumerate(myInventory.getProductList()):
            for column_number, data in enumerate(product):
                self.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

        # Add callback for when a cell is changed
        self.tableWidget.itemChanged.connect(self.on_item_changed)

        self.searchCell = QLineEdit()
        self.searchCell.setPlaceholderText("Search by barcode")
        self.searchCell.setMaxLength(13)
        self.searchCell.setValidator(QIntValidator())
        self.searchCell.width = 100
        self.searchCell.height = 100
        self.searchCell.textChanged.connect(self.on_text_changed_search)

        self.gridLayout.addWidget(self.searchCell, 1, 0, 1, 1)

        self.widget = QWidget()
        self.widget.setLayout(self.gridLayout)
        self.setCentralWidget(self.widget)

        w = 900; h = 600
        self.resize(w, h)
        self.setWindowIcon(QIcon('icon.png'))
        self.show()

    def on_item_changed(self, item):
        #print(item.row(), item.column(), int(item.text()))
        newProduct = inventory.product.product(*[self.tableWidget.item(item.row(), i).text() for i in range(9)])
        myInventory.updateProduct(newProduct)

    def refreshTable(self, productList):
        # Populate the table with data from the productList
        self.tableWidget.clear()
        for row_number, product in enumerate(productList):
            for column_number, data in enumerate(product):
                self.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    def on_text_changed_search(self, item):
        # Temporary remove callback on itemChanged since being called when refreshing table
        self.tableWidget.itemChanged.disconnect()
        self.refreshTable(myInventory.getProductsByBarcode(item))
        # Set callback again
        self.tableWidget.itemChanged.connect(self.on_item_changed)

if __name__ == '__main__':
    myInventory = inventory.inventory()
    #myInventory.addProductListFromFile("lista_tabacchi.xls")

    app = QApplication(sys.argv)
    w = MainWindow()
    app.exec()