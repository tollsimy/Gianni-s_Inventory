__name__ = "inventory"

import product
import appdirs
import sqlite3
from sqlite3 import Error
import os
import pandas as pd
import csv

def create_connection(db_name):
    appname = "Gianni's_Inventory"
    appauthor = "tollsimy"
    datapath = appdirs.user_data_dir(appname, appauthor)
    db_path = os.path.join(datapath, db_name)
    
    os.makedirs(datapath, exist_ok=True)  # Ensure the directory exists

    connection = None
    try:
        connection = sqlite3.connect(db_path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(e)
        if connection:
            connection.close()
            print("Connection closed")
            return None
    else:
        return connection

# Create table from product.py attribDescriptionDict
def create_table(cursor):
    tableString = "CREATE TABLE IF NOT EXISTS products ("
    for (index,attrib) in enumerate(product.product.SQLAttribDescriptionDict.items()):
        if index != 0:
            tableString += ", "
        tableString += \
            attrib[0] + " " + \
            attrib[1][0]["type"] + " " + \
            ("NOT NULL " if attrib[1][0]["notNull"] else "") + \
            ("PRIMARY KEY" if attrib[1][0]["primaryKey"] else "")
    tableString += ");"
    create_table_sql = tableString
    cursor.execute(create_table_sql)

class inventory:
    """Inventory Class"""
    conn = None
    cur = None
    productList = []

    def __init__(self):
        self.conn = create_connection("inventory.db")
        self.cur = self.conn.cursor()
        create_table(self.cur)

    def __del__(self):
        self.conn.close()
        print("Connection closed")

    def addProduct(self, product):
        add_product_sql = "INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?);"
        self.cur.execute(add_product_sql, (product.category, product.prodCode, product.denomComm, product.barcode, product.priceKg, product.pricePz, product.packageType, product.packageNumber, product.quantity))
        self.conn.commit()
    
    def getProduct(self, prodCode):
        get_product_sql = "SELECT * FROM products WHERE prodCode = ?;"
        self.cur.execute(get_product_sql, (prodCode,))
        rows = self.cur.fetchall()
        if len(rows) == 0:
            return None
        else:
            return product.product(rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], rows[0][5], rows[0][6], rows[0][7], rows[0][8])
        
    def getProductList(self):
        get_product_list_sql = "SELECT * FROM products;"
        self.cur.execute(get_product_list_sql)
        rows = self.cur.fetchall()
        self.productList = []
        for row in rows:
            self.productList.append(product.product(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        return self.productList

    #TODO: keep SQL queries independent from product.py
    def updateProduct(self, product):
        update_product_sql = "UPDATE products SET category = ?, denomComm = ?, barcode = ?, priceKg = ?, pricePz = ?, packageType = ?, packageNumber = ?, quantity = ? WHERE prodCode = ?;"
        self.cur.execute(update_product_sql, (product.category, product.denomComm, product.barcode, product.priceKg, product.pricePz, product.packageType, product.packageNumber, product.quantity, product.prodCode))
        self.conn.commit()

    def deleteProduct(self, prodCode):
        delete_product_sql = "DELETE FROM products WHERE prodCode = ?;"
        self.cur.execute(delete_product_sql, (prodCode,))
        self.conn.commit()

    def deleteAllProducts(self):
        delete_all_products_sql = "DELETE FROM products;"
        self.cur.execute(delete_all_products_sql)
        self.conn.commit()

    def addProductList(self):
        for product in self.productList:
            self.addProduct(product)

    def addProductListFromFile(self, filename):
        read_file = pd.read_excel (filename) 
        # Convert to csv and replace if exists
        read_file.to_csv (filename+".csv", index = None, header=True)
        with open(filename+".csv", "r") as file:
            # Skip first two lines of header
            reader = csv.reader(file, delimiter=',')
            next(reader, None)  # skip the headers
            next(reader, None)  # skip the headers
            for line in reader:
                prod = product.product(line[0], line[1], line[2], line[3], line[4], line[5], line[6], line[7], line[8])
                self.productList.append(prod)
        self.addProductList(self.productList)

#TODO: add quantity
    # ========== Search functions =============

    def getProductsByCategory(self, category):
        get_products_by_category_sql = "SELECT * FROM products WHERE category = ?;"
        self.cur.execute(get_products_by_category_sql, (category,))
        rows = self.cur.fetchall()
        self.productList = []
        for row in rows:
            self.productList.append(product.product(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
    
    def getProductsByProdCode(self, prodCode):
        get_products_by_prodCode_sql = "SELECT * FROM products WHERE prodCode = ?;"
        self.cur.execute(get_products_by_prodCode_sql, (prodCode,))
        rows = self.cur.fetchall()
        self.productList = []
        for row in rows:
            self.productList.append(product.product(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        return self.productList
    
    def getProductsByDenomComm(self, denomComm):
        get_products_by_denomComm_sql = "SELECT * FROM products WHERE denomComm = ?;"
        self.cur.execute(get_products_by_denomComm_sql, (denomComm,))
        rows = self.cur.fetchall()
        self.productList = []
        for row in rows:
            self.productList.append(product.product(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        return self.productList
    
    def getProductsByBarcode(self, barcode):
        get_products_by_barcode_sql = "SELECT * FROM products WHERE barcode LIKE ?;"
        self.cur.execute(get_products_by_barcode_sql, ('%' + barcode + '%',))
        rows = self.cur.fetchall()
        self.productList = []
        for row in rows:
            self.productList.append(product.product(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        return self.productList
    
    def getProductsByPriceKg(self, priceKg):
        get_products_by_priceKg_sql = "SELECT * FROM products WHERE priceKg = ?;"
        self.cur.execute(get_products_by_priceKg_sql, (priceKg,))
        rows = self.cur.fetchall()
        self.productList = []
        for row in rows:
            self.productList.append(product.product(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        return self.productList
    
    def getProductsByPricePz(self, pricePz):
        get_products_by_pricePz_sql = "SELECT * FROM products WHERE pricePz = ?;"
        self.cur.execute(get_products_by_pricePz_sql, (pricePz,))
        rows = self.cur.fetchall()
        self.productList = []
        for row in rows:
            self.productList.append(product.product(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        return self.productList
    
    def getProductsByPackageType(self, packageType):
        get_products_by_packageType_sql = "SELECT * FROM products WHERE packageType = ?;"
        self.cur.execute(get_products_by_packageType_sql, (packageType,))
        rows = self.cur.fetchall()
        self.productList = []
        for row in rows:
            self.productList.append(product.product(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        return self.productList
    
    def getProductsByPackageNumber(self, packageNumber):
        get_products_by_packageNumber_sql = "SELECT * FROM products WHERE packageNumber = ?;"
        self.cur.execute(get_products_by_packageNumber_sql, (packageNumber,))
        rows = self.cur.fetchall()
        self.productList = []
        for row in rows:
            self.productList.append(product.product(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
        return self.productList
    
    # =============== Order functions ===============

    def getOrderedByCategory(self):
        get_ordered_by_category_sql = "SELECT * FROM products ORDER BY category;"
        self.cur.execute(get_ordered_by_category_sql)
        rows = self.cur.fetchall()
        self.productList = []
        for row in rows:
            self.productList.append(product.product(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))        
        return self.productList

    def getOrderedByProdCode(self):
        get_ordered_by_prodCode_sql = "SELECT * FROM products ORDER BY prodCode;"
        self.cur.execute(get_ordered_by_prodCode_sql)
        rows = self.cur.fetchall()
        self.productList = []
        for row in rows:
            self.productList.append(product.product(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))        
        return self.productList
    
    def getOrderedByDenomComm(self):
        get_ordered_by_denomComm_sql = "SELECT * FROM products ORDER BY denomComm;"
        self.cur.execute(get_ordered_by_denomComm_sql)
        rows = self.cur.fetchall()
        self.productList = []
        for row in rows:
            self.productList.append(product.product(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))        
        return self.productList
    
    def getOrderedByBarcode(self):
        get_ordered_by_barcode_sql = "SELECT * FROM products ORDER BY barcode;"
        self.cur.execute(get_ordered_by_barcode_sql)
        rows = self.cur.fetchall()
        self.productList = []
        for row in rows:
            self.productList.append(product.product(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))        
        return self.productList
    
    def getOrderedByPriceKg(self):
        get_ordered_by_priceKg_sql = "SELECT * FROM products ORDER BY priceKg;"
        self.cur.execute(get_ordered_by_priceKg_sql)
        rows = self.cur.fetchall()
        self.productList = []
        for row in rows:
            self.productList.append(product.product(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))        
        return self.productList
    
    def getOrderedByPricePz(self):
        get_ordered_by_pricePz_sql = "SELECT * FROM products ORDER BY pricePz;"
        self.cur.execute(get_ordered_by_pricePz_sql)
        rows = self.cur.fetchall()
        self.productList = []
        for row in rows:
            self.productList.append(product.product(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))        
        return self.productList
    
    def getOrderedByPackageType(self):
        get_ordered_by_packageType_sql = "SELECT * FROM products ORDER BY packageType;"
        self.cur.execute(get_ordered_by_packageType_sql)
        rows = self.cur.fetchall()
        self.productList = []
        for row in rows:
            self.productList.append(product.product(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))        
        return self.productList
    
    def getOrderedByPackageNumber(self):
        get_ordered_by_packageNumber_sql = "SELECT * FROM products ORDER BY packageNumber;"
        self.cur.execute(get_ordered_by_packageNumber_sql)
        rows = self.cur.fetchall()
        self.productList = []
        for row in rows:
            self.productList.append(product.product(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))        
        return self.productList