import sqlite3
from PyQt5 import QtSql

class MY_DB():
    def connect(self):
        self.conn = sqlite3.connect("dulieu.db")

    def create_products_table(self):
        sql_create_table = """
            CREATE TABLE IF NOT EXISTS Products (
                id INTEGER,
                name TEXT,
                price INTEGER
            );
        """
        self.conn.execute(sql_create_table)

    def create_userdata_table(self):
        sql_create_table = """
            CREATE TABLE IF NOT EXISTS userdata (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                username VARCHAR(100) NOT NULL,
                password VARCHAR(100) NOT NULL
            );
        """
        self.conn.execute(sql_create_table)

    def create_bill_table(self):
        sql_create_table = """
           CREATE TABLE IF NOT EXISTS bill (
                id INTEGER PRIMARY KEY,
                product_name TEXT,
                weight REAL,
                price REAL,
                total_price REAL
            );
        """
        self.conn.execute(sql_create_table)

    def openDB(self):
            self.db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
            self.db.setDatabaseName("dulieu.db")
            if not self.db.open():
                print("Error")
            self.query = QtSql.QSqlQuery()

    def disconnect(self):
        self.conn.close()

    def insert_row(self, id, name, price):
        self.sql_insert = """INSERT INTO Products VALUES (?, ?, ?);"""
        with self.conn:
            self.conn.execute(self.sql_insert, (id, name, price))

    def delete_by_id(self, id:int):
        self.sql_delete = """DELETE FROM Products WHERE id=?;"""
        with self.conn:
            self.conn.execute(self.sql_delete, (id,))
    
    # def update_by_id(self, id, name, price):
    #     self.sql_update_by_id = """UPDATE Products SET name=?, price =? WHERE id=?;"""
    #     self.result = self.conn.execute(self.sql_update_by_id, (name, price, id))
    #     self.conn.commit()
    def update_by_id(self, id, price):
        self.sql_update_by_id = """UPDATE Products SET price =? WHERE id=?;"""
        self.result = self.conn.execute(self.sql_update_by_id, (price, id))
        self.conn.commit()

    def select_all(self):
        self.sql_select = """SELECT * FROM Products;"""
        self.result = self.conn.execute(self.sql_select)
        return self.result
    
    def select_by_id(self, id):
        self.sql_select_by_id = """SELECT * FROM Products Where id=?;"""
        self.result = self.conn.execute(self.sql_select_by_id, (id,))
        return self.result
    
    def get_price(self, id):
        cursor = self.conn.cursor()
        query = "SELECT price FROM Products WHERE id = ?"
        params = (id,)
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        if result:
            return result[0]
        else:
            return None
    
    def save_to_bill(self, product_name, weight, price, total_price):
        cursor = self.conn.cursor()
        query = "INSERT INTO bill (product_name, weight, price, total_price) VALUES (?, ?, ?, ?)"
        values = (product_name, weight, price, total_price)
        cursor.execute(query, values)
        self.conn.commit() 

    def get_bill_data(self):
        cursor = self.conn.cursor()
        query = "SELECT * FROM bill"
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows

    def delete_bill_data(self):
        sql_delete_data = "DELETE FROM bill"
        self.conn.execute(sql_delete_data)
        self.conn.commit()

     
    def sqlquerytitlesearch(self, keyword):
        cursor = self.conn.cursor()
        query = "SELECT * FROM Products WHERE name LIKE ?"
        pattern = f"%{keyword}%"
        cursor.execute(query, (pattern,))
        result = cursor.fetchall()
        return result
    
    def sql_registerAccount(self, usernamerg, passwordrg, passwordagain):
        query = QtSql.QSqlQuery() 
        if passwordrg == passwordagain:
            query.prepare("INSERT INTO userdata (username, password) VALUES (:username, :password)")
            query.bindValue(":username", usernamerg)
            query.bindValue(":password", passwordrg)
            
            if query.exec_():
                print("Account registered successfully!")
                query.finish() 
                return 0
            else:
                print("Failed to register account:", query.lastError().text())
                query.finish() 
                return 1
        else:
            print("Passwords do not match!")
            query.finish() 
            return 2
        
    def sql_checkUser(self, username1, password1):
        self.query.exec_("select * from userdata where username = '%s' and password =  '%s'; "%(username1, password1))
        self.query.first()
        if self.query.value("username") != None and self.query.value("password") != None:
            print("Login successful!")
            self.query.finish() 
            return True
        else:
            print("Login failed!")
            self.query.finish()
            return False
    
    def sql_changePassword(self, username, old_password, new_password):
        # Kiểm tra mật khẩu hiện tại
        self.query = QtSql.QSqlQuery()
        self.query.prepare("SELECT password FROM userdata WHERE username = :username")
        self.query.bindValue(":username", username)
        
        if self.query.exec_() and self.query.first():
            current_password = self.query.value(0)
            if current_password == old_password:
                # Thực hiện truy vấn SQL để cập nhật mật khẩu mới
                self.query.prepare("UPDATE userdata SET password = :new_password WHERE username = :username")
                self.query.bindValue(":new_password", new_password)
                self.query.bindValue(":username", username)
                
                # Thực thi truy vấn
                if self.query.exec_():
                    print("Password changed successfully!")
                    self.query.finish() 
                    return 0
                else:
                    print("Failed to change password!")
                    self.query.finish() 
                    return 1
            else:
                print("Incorrect current password!")
                self.query.finish() 
                return 2
        else:
            print("Invalid username!")
            self.query.finish() 
            return 3