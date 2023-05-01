import sqlite3


class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS modelos (id INTEGER PRIMARY KEY autoincrement, nome text, "
                         "modelo text, a float, b float, c float, d float, e float, drel text)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS derivadas (id INTEGER PRIMARY KEY autoincrement, modelo text, "
                         "d1 text, d2 text, d3 text, d4 text)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS valores (id INTEGER PRIMARY KEY autoincrement, nome text,"
                         "imamax float, imamaxidade float, icamax float, aclmax float, dclmax float)")
        self.conn.commit()

    def fetch_modelos(self):
        self.cur.execute("SELECT * FROM modelos ORDER BY rowid")
        rows = self.cur.fetchall()
        return rows

    def fetch_derivadas(self):
        self.cur.execute("SELECT * FROM derivadas ORDER BY rowid")
        rows = self.cur.fetchall()
        return rows

    def fetch_valores(self):
        self.cur.execute("SELECT * FROM valores ORDER BY rowid")
        rows = self.cur.fetchall()
        return rows

    def fetch_um_valores(self, nome):
        self.cur.execute("SELECT nome FROM valores WHERE nome = ?", (nome,))
        rows = self.cur.fetchone()
        return rows

    def headers(self):
        return self.cur.description

    def insert_modelos(self, nome, modelo, a, b, c, d, e, drel):
        self.cur.execute("INSERT INTO modelos VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)",
                         (nome, modelo, a, b, c, d, e, drel))
        self.conn.commit()

    def insert_derivadas(self, modelo, d1, d2, d3, d4):
        self.cur.execute("INSERT INTO derivadas VALUES (NULL, ?, ?, ?, ?, ?)",
                         (modelo, d1, d2, d3, d4))
        self.conn.commit()

    def insert_valores(self, nome, imamax, imamaxidade, icamax, aclmax, dclmax):
        self.cur.execute("INSERT INTO valores VALUES (NULL, ?, ?, ?, ?, ?, ?)",
                         (nome, imamax, imamaxidade, icamax, aclmax, dclmax))
        self.conn.commit()

    def remove(self, rowid):
        self.cur.execute("DELETE FROM modelos WHERE rowid = ?",
                         (rowid,))
        self.cur.execute("DELETE FROM derivadas WHERE rowid = ?",
                         (rowid,))
        self.cur.execute("DELETE FROM valores WHERE rowid = ?",
                         (rowid,))
        self.conn.commit()

    def update_modelos(self, rowid, nome, modelo, a, b, c, d, e, drel):
        self.cur.execute(
            "UPDATE modelos SET nome=?, modelo=?, a=?, b=?, c=?, d=?, e=?, drel=? WHERE rowid= ?",
            (nome, modelo, a, b, c, d, e, drel, rowid))
        self.conn.commit()

    def update_derivadas(self, rowid, modelo, d1, d2, d3, d4):
        self.cur.execute(
            "UPDATE derivadas SET modelo=?, d1=?, d2=?, d3=?, d4=? WHERE rowid= ?",
            (modelo, d1, d2, d3, d4, rowid))
        self.conn.commit()

    def __del__(self):
        self.conn.close()
