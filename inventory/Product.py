__name__ = "Product"

class Product:
    """Product Class"""

    # ==================== ATTENTION ====================
    #
    # When editing Product attributes, edit only
    # SQLAttribDescriptionDict, everything else is
    # automatically generated.
    #
    # Of course you then need to add/remove arguments
    # where Product constuctor is called.
    # Also, arguments must be passed in the same order as
    # SQLAttribDescriptionDict.
    #
    # ====================================================

    # Dictionary of attributes for SQL table creation
    SQLAttribDescriptionDict = {    "category":         [{ "type":  "text",     "notNull": False,   "primaryKey": False, "unique": False }],
                                    "prodCode":         [{ "type":  "bigint",   "notNull": True,    "primaryKey": True,  "unique": True }],
                                    "denomComm":        [{ "type":  "text",     "notNull": False,   "primaryKey": False, "unique": False }],
                                    "barcode":          [{ "type":  "bigint",   "notNull": False,   "primaryKey": False, "unique": True }],
                                    "priceKg":          [{ "type":  "real",     "notNull": False,   "primaryKey": False, "unique": False }],
                                    "pricePz":          [{ "type":  "real",     "notNull": False,   "primaryKey": False, "unique": False }],
                                    "packageType":      [{ "type":  "text",     "notNull": False,   "primaryKey": False, "unique": False }],
                                    "packageNumber":    [{ "type":  "integer",  "notNull": False,   "primaryKey": False, "unique": False }],
                                    "quantity":         [{ "type":  "integer",  "notNull": False,   "primaryKey": False, "unique": False }],
                                    "barcodeStecca":    [{ "type":  "bigint",   "notNull": False,   "primaryKey": False, "unique": True }],
                                }
    
    # List of attributes names
    attributesNames = list(SQLAttribDescriptionDict.keys())
    # Number of attributes
    attributesNum = len(attributesNames)
    
    def __init__(self, *args):
        self.attributesDict = {}
        # Check if number of arguments is correct
        if(len(args) != Product.attributesNum):
            raise Exception("Product.__init__: wrong number of arguments according to SQLAttribDescriptionDict")
            sys.exit(1)
        # For every argument
        for i, arg in enumerate(args):
            # Fill dictionary of attributes
            # e.g. { "category": "Sigarette", "prodCode": 1, ... }
            self.attributesDict[Product.attributesNames[i]] = arg

    def __str__(self):
        return str(self.attributesDict).replace('\'', '').strip("{}")

    def __eq__(self, other):
        return self.attributesDict.get("prodCode") == other.attributesDict.get("prodCode")
    
    def __hash__(self):
        return hash(self.attributesDict.get("prodCode"))
    
    def __lt__(self, other):
        return self.attributesDict.get("prodCode") < other.attributesDict.get("prodCode")
    
    def __le__(self, other):
        return self.attributesDict.get("prodCode") <= other.attributesDict.get("prodCode")
    
    def __gt__(self, other):
        return self.attributesDict.get("prodCode") > other.attributesDict.get("prodCode")
    
    def __ge__(self, other):
        return self.attributesDict.get("prodCode") >= other.attributesDict.get("prodCode")
    
    def __ne__(self, other):
        return self.attributesDict.get("prodCode") != other.attributesDict.get("prodCode")
    
    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index < len(list(self.attributesDict.values())):
            result = list(self.attributesDict.values())[self.index]
            self.index += 1
            return result
        else:
            raise StopIteration