__name__ = "product"

class product:
    """Product Class"""
    attributes = []

    category = None
    prodCode = None
    denomComm = None
    barcode = None
    priceKg = None
    pricePz = None
    packageType = None
    packageNumber = None
    quantity = None
    
    # Dictionary of attributes for SQL table creation
    SQLAttribDescriptionDict = {    "category":         [{ "type":  "text",     "notNull": True,    "primaryKey": False }],
                                    "prodCode":         [{ "type":  "integer",  "notNull": True,    "primaryKey": True  }],
                                    "denomComm":        [{ "type":  "text",     "notNull": True,    "primaryKey": False }],
                                    "barcode":          [{ "type":  "integer",  "notNull": True,    "primaryKey": False }],
                                    "priceKg":          [{ "type":  "real",     "notNull": False,   "primaryKey": False }],
                                    "pricePz":          [{ "type":  "real",     "notNull": True,    "primaryKey": False }],
                                    "packageType":      [{ "type":  "text",     "notNull": False,   "primaryKey": False }],
                                    "packageNumber":    [{ "type":  "integer",  "notNull": False,   "primaryKey": False }],
                                    "quantity":         [{ "type":  "integer",  "notNull": False,   "primaryKey": False }]
                                }
    
    def __init__(self, category, prodCode, denomComm, barcode, priceKg, pricePz, packageType, packageNumber, quantity):
        self.category = category
        self.prodCode = prodCode
        self.denomComm = denomComm
        self.barcode = barcode
        self.priceKg = priceKg
        self.pricePz = pricePz
        self.packageType = packageType
        self.packageNumber = packageNumber
        self.quantity = quantity

        self.attributes = [self.category, self.prodCode, self.denomComm, self.barcode, self.priceKg, self.pricePz, self.packageType, self.packageNumber, self.quantity]

    def __str__(self):
        return "Product: " + self.category + " " + self.denomComm + " " + str(self.prodCode) + " " + str(self.barcode) + " " + str(self.priceKg) + " " + str(self.pricePz) + " " + self.packageType + " " + str(self.packageNumber) + " " + str(self.quantity)
    
    def __eq__(self, other):
        return self.prodCode == other.prodCode
    
    def __hash__(self):
        return hash(self.prodCode)
    
    def __lt__(self, other):
        return self.prodCode < other.prodCode
    
    def __le__(self, other):
        return self.prodCode <= other.prodCode
    
    def __gt__(self, other):
        return self.prodCode > other.prodCode
    
    def __ge__(self, other):
        return self.prodCode >= other.prodCode
    
    def __ne__(self, other):
        return self.prodCode != other.prodCode
    
    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index < len(self.attributes):
            result = self.attributes[self.index]
            self.index += 1
            return result
        else:
            raise StopIteration
    