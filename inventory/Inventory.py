__name__ = "Inventory"

from Product import Product
from PyQt5.QtCore import QObject, pyqtSignal
import psycopg2
import threading
import time
import csv

#NOTE: for how it is implemented psycopg2, executing two queries means automatically
# that the first one is committed.
# So, make sure to not execute queries if user has not pressed apply or undo changes

def create_connection(db_name, db_user, db_pass, db_host):
    connection = None
    try:
        connection = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_pass,
            host=db_host,
            )
        print("Connection to SQLite DB successful")
    except psycopg2.Error as e:
        if connection:
            connection.close()
            print("Connection closed")
            return None
        raise e
    else:
        return connection

# Create table from product.py attribDescriptionDict
def create_table(cursor, connection):
    tableString = "CREATE TABLE IF NOT EXISTS products ("
    for (index,attrib) in enumerate(Product.SQLAttribDescriptionDict.items()):
        if index != 0:
            tableString += ", "
        tableString += \
            attrib[0] + " " + \
            attrib[1][0]["type"] + " " + \
            ("NOT NULL " if attrib[1][0]["notNull"] else "") + \
            ("PRIMARY KEY " if attrib[1][0]["primaryKey"] else "") + \
            ("UNIQUE" if attrib[1][0]["unique"] else "")
    tableString += ");"
    create_table_sql = tableString
    try:
        cursor.execute(create_table_sql)
        connection.commit()
    except psycopg2.Error as e:
        connection.rollback()
        raise e

# Inherit from QObject to be able to emit signals when the database changes
class Inventory(QObject):
    """Inventory Class"""
    conn = None
    cur = None
    productDict = {}

    # String to store multiple SQL statements for updating products so 
    # we can execute them all at once when applyChanges() is called
    # or discard them all when discardChanges() is called
    update_product_sql_statements = ""

    # Signal emitted when the database changes, need to be connected in the main window
    changeSignal = pyqtSignal()

    listenNotifyThread = None               

    def __init__(self, db_name, db_user, db_pass, db_host):
        super().__init__()
        # Variable used to stop thread that listen to the change signal
        self.stopSignalThread = False
        try:
            self.conn = create_connection(db_name, db_user, db_pass, db_host)
        except psycopg2.Error as e:
            raise e
        self.cur = self.conn.cursor()
        try:
            create_table(self.cur, self.conn)
            # Execute the LISTEN command
            self.cur.execute("LISTEN changeNotification;")
            # Start a thread to execute the listen() method
            self.listenNotifyThread = threading.Thread(target=self.listenChange)
            self.listenNotifyThread.start()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise e
        except RuntimeError as e:
            raise e

    def __del__(self):
        if(self.listenNotifyThread is not None):
            self.listenNotifyThread.join()
        if(self.conn is not None):
            self.conn.close()
            print("Connection closed")

    def listenChange(self):
        # Create a loop that waits for a notification
        while not self.stopSignalThread:
            try:
                self.conn.poll()
                while self.conn.notifies:
                    try:
                        notify = self.conn.notifies.pop(0)
                        #print("Got NOTIFY:", notify.pid, notify.channel, notify.payload)
                    except IndexError as e:
                        print(e)
                    # Update productList
                    # Note: this won't automatically apply changes even if it is executing
                    # a query because other instances are blocked until the other commits the
                    # pending changes
                    self.getProductList()
                    # Send signal to update the table
                    self.changeSignal.emit()
            except psycopg2.InterfaceError:
                # Break the loop if the connection is closed
                break
            time.sleep(5)
        
    def getProduct(self, prodCode):
        get_product_sql = "SELECT * FROM products WHERE prodCode = %s;"
        self.cur.execute(get_product_sql, (prodCode,))
        self.conn.commit()
        rows = self.cur.fetchall()
        if len(rows) == 0:
            return None
        else:
            return Product(*rows[0])
        
    def getProductList(self):
        get_product_list_sql = "SELECT * FROM products;"
        self.cur.execute(get_product_list_sql)
        self.conn.commit()
        rows = self.cur.fetchall()
        self.productDict = {}
        for row in rows:
            self.productDict[row[1]] = Product(*row)
        return self.productDict
    
    # Commit or discard is caller's responsibility through applyChanges() or discardChanges()
    def addProduct(self, product):
        add_product_sql = "INSERT INTO products VALUES (" 
        add_product_sql += ("%s," * (Product.attributesNum - 1)) + "%s);"
        # Replace "None" and empty string with None
        attributes = [None if (attr == "None" or attr == "") else attr for attr in list(product.attributesDict.values())]
        self.cur.execute(add_product_sql, attributes)

    # Commit or discard is caller's responsibility through applyChanges() or discardChanges()
    def updateProduct(self, product):
        attrDict = product.attributesDict
        attrList = list(product.attributesDict.keys())
        self.update_product_sql_statements = "UPDATE products SET "
        self.update_product_sql_statements += ", ".join([attrib + " = %s" for attrib in attrList])
        self.update_product_sql_statements += " WHERE prodCode = %s;"
        # Replace "None" and empty string with None
        attributes = [None if (attr == "None" or attr == "") else attr for attr in attrDict.values()]
        # Add prodCode to the end of attributes because it's used in the WHERE clause
        attributes.append(attrDict.get("prodCode"))
        self.cur.execute(self.update_product_sql_statements, attributes)

    # Commit or discard is caller's responsibility through applyChanges() or discardChanges()
    def deleteProduct(self, prodCode):
        delete_product_sql = "DELETE FROM products WHERE prodCode = %s;"
        self.cur.execute(delete_product_sql, (prodCode,))

    # Commit or discard is caller's responsibility through applyChanges() or discardChanges()
    def deleteAllProducts(self):
        delete_all_products_sql = "DELETE FROM products;"
        self.cur.execute(delete_all_products_sql)

    # Commit or discard is caller's responsibility through applyChanges() or discardChanges()
    def resetQuantities(self):
        reset_quantity_sql = "UPDATE products SET quantity = 0;"
        self.cur.execute(reset_quantity_sql)

    def addProductList(self):
        for product in self.productDict.values():
            self.addProduct(product)

    # Note: make sure to always notify the change after editing the database
    def applyChanges(self):
        self.conn.commit()
        # Notify the change
        self.cur.execute("NOTIFY changeNotification, 'change';")
        self.conn.commit()

    def discardChanges(self):
        self.conn.rollback()

    def exportCSV(self, filename):
        self.cur.execute("SELECT * FROM products")
        # fetch the results
        results = self.cur.fetchall()
        with open(filename, "w+", newline="") as f:
            # Create a CSV writer
            writer = csv.writer(f)
            # write the column names
            writer.writerow([col[0] for col in self.cur.description])
            # write the query results
            writer.writerows(results)
    
    def importCSV(self, filename):
        with open(filename, "r") as f:
            # Create a CSV reader
            reader = csv.reader(f)
            # Skip the header row
            next(reader)
            for row in reader:
                # Replace "None" and empty string with None
                row = [None if (col == "None" or col == "") else col for col in row]
                self.productDict[row[1]] = Product(*row)
            self.addProductList()

    # ========== Search functions =============
    
    def getProductByProdCode(self, prodCode):
        return self.getProduct(prodCode)
    
    def getProductsByBarcode(self, barcode):
        get_products_by_barcode_sql = "SELECT * FROM products WHERE barcode = %s;"
        self.cur.execute(get_products_by_barcode_sql, (barcode,))
        rows = self.cur.fetchall()
        self.productDict = {}
        for row in rows:
            self.productDict[row[1]] = Product(*row)
        return self.productDict
    
    def getProductsByBarcodeStecca(self, barcodeStecca):
        get_products_by_barcodeStecca_sql = "SELECT * FROM products WHERE barcodeStecca = %s;"
        self.cur.execute(get_products_by_barcodeStecca_sql, (barcodeStecca,))
        rows = self.cur.fetchall()
        self.productDict = {}
        for row in rows:
            self.productDict[row[1]] = Product(*row)
        return self.productDict