# Gianni's Inventory
This is a simple inventory management system made for counting and tracking in the quickest way possible items in a warehouse.
It was made initially for tobacco shops to count cigarettes, but it can be easily adapted to any other kind of item.

Gianni's Inventory has got the following features:
- [x] Add items to the inventory
- [x] Remove items from the inventory
- [x] Edit items in the inventory
- [x] Save/Undo changes
- [x] Search items in the inventory
- [x] STAQ Mode (Scan barcode to add quantity)
- [x] Export inventory to CSV
- [x] Import inventory from CSV

Moreover, Gianni's Inventory can be run in different machines simultaneously, and it will automatically sync the inventory between them. However, items in the inventory can be modified only in one instance at a time: if one instance has got some pending changes, other instances will not be able to modify the inventory until the changes are saved or undone. This is particularly useful when you have multiple stores / warehouses.

## Usage
Basic functionalities:
![Basic Usage](media/basic_usage.GIF)

Edit quantity (absolute and incremental):
Quantity can be edited by typing the new absolute quantity or by adding/subtracting a certain quantity to the current one using "=" suffix.
![Edit Quantity](media/quantity.GIF)

Search and STAQ (Scan To Add Quantity) Mode:
![Search and STAQ Mode](media/seach_and_STAQ_mode.GIF)

# Install PostgreSQL Server
Install PostgreSQL Server on your machine following the instructions at https://www.postgresql.org/download/.

Create database and user with the following commands on your server machine:
```bash
sudo -u postgres psql
``` 
```sql
CREATE DATABASE inventory;
CREATE USER <yourusername> WITH ENCRYPTED PASSWORD '<yourpass>';
GRANT ALL PRIVILEGES ON DATABASE inventory TO <yourusername>;
```