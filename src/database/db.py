import sqlite3

class Database():
    def __init__(self, db_file):
        self.connection= sqlite3.connect(db_file)
        self.cursor= self.connection.cursor()
        
    def create_table(self, name):
        with self.connection:
            self.cursor.execute(f"""CREATE TABLE {name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                name TEXT,
                lastname TEXT,
                patronymic TEXT,
                number TEXT
                )""")
            
    def add_lottery(self, name, table_name, count, price):
        with self.connection:
            self.cursor.execute("INSERT INTO info (name, table_name, count, price) VALUES (?, ?, ?, ?)",
                                (name, table_name, count, price, ))
            
    def add_ids(self, table_name):
        with self.connection:
            self.cursor.execute(f"""INSERT INTO {table_name} (name) VALUES (?)""", ("", ))
            
    def get_lotteries(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM info").fetchall()

    def get_lottery(self, table_name):
        with self.connection:
            return self.cursor.execute("SELECT * FROM info WHERE table_name= ?", (table_name, )).fetchone()

    def del_lottery(self, table_name):
        with self.connection:
            self.cursor.execute(f"DELETE FROM info WHERE table_name= ?", (table_name, ))
            self.cursor.execute(f"DROP TABLE {table_name}")
            
    def get_tickets(self, table_name):
        with self.connection:
            return self.cursor.execute(f"SELECT * FROM {table_name}").fetchall()
        
    def count_notSold(self, table_name):
        with self.connection:
            return self.cursor.execute(f"SELECT COUNT(id) FROM {str(table_name)} WHERE name= '' ").fetchone()
        
    def get_ticket(self, table_name):
        with self.connection:
            return self.cursor.execute(f"SELECT id FROM {table_name} WHERE name = '' ").fetchone()
                
    def get_user(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id, )).fetchone()
        
    def add_user(self, user_id, username, name, lastname, patronymic, number):
        with self.connection:
            self.cursor.execute("INSERT INTO users (user_id, username, name, lastname, patronymic, number) VALUES (?, ?, ?, ?, ?, ?)",
                                (user_id,
                                 username,
                                 name,
                                 lastname,
                                 patronymic,
                                 number, ))

    def up_user(self, user_id, username, name, lastname, patronymic, number):
        with self.connection:
            self.cursor.execute("UPDATE users SET username= ?, name= ?, lastname= ?, patronymic= ?, number= ? WHERE user_id= ?",
                                (username,
                                 name,
                                 lastname,
                                 patronymic,
                                 number,
                                 user_id,))
            
    def up_ticket(self, table_name, user_id, username, name, lastname, patronymic, number, id):
        with self.connection:
            self.cursor.execute(f"UPDATE {table_name} SET username= ?, name= ?, lastname= ?, patronymic= ?, number= ?, user_id= ? WHERE id= ?",
                                (username,
                                 name,
                                 lastname,
                                 patronymic,
                                 number,
                                 user_id,
                                 id, ))