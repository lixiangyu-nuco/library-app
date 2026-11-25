import sqlite3

class Book:
    def __init__(self, title, book_id):
        self.title = title 
        self.is_borrowed = False 
        self.book_id = book_id 

class Member:
    def __init__(self, member_id, name):
        self.member_id = member_id
        self.name = name

class Library:
    def __init__(self, db_path="library.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('PRAGMA foreign_keys = ON')  # 外部キー制約を有効にする
        return conn

    # データベースの初期化
    def init_db(self):
        conn = self.get_connection()

        try:
            with open("schema.txt", "r", encoding="utf-8") as f:
                sql = f.read()

            conn.executescript(sql)
            conn.commit()

        finally:
            conn.close()

    
    #SQLiteデータベースに書籍を登録する
    def add_book(self, book):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO books (book_id, title, is_borrowed)
                VALUES (?, ?, ?)
            ''', (book.book_id, book.title, book.is_borrowed))
            conn.commit()
            return True
        
        except sqlite3.IntegrityError:
            conn.rollback()
            return False

        except sqlite3.Error:
            conn.rollback()
            raise
        
        finally:
            conn.close()

    #登録済みの書籍をデータベースから取得する
    def get_books(self):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM books')
            rows = cursor.fetchall()

        finally:
            conn.close()

        books = []
        for row in rows:
            book = Book(row[1], row[0])
            book.is_borrowed = bool(row[2])
            books.append(book) 

        return books 

    # 指定された会員が現在借りている書籍を取得する
    def get_borrowed_books(self, member_id):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT b.book_id, b.title
                FROM books AS b
                JOIN borrowing_history AS bh
                  ON b.book_id = bh.book_id
                WHERE bh.member_id = ?
                  AND bh.return_date IS NULL
            ''', (member_id,))
            rows = cursor.fetchall()

        finally:
            conn.close()

        borrowed_books = []
        for row in rows:
            book = Book(row[1], row[0])
            book.is_borrowed = True
            borrowed_books.append(book)

        return borrowed_books


    #SQLiteデータベースで書籍の貸出状態を更新する
    def borrow_book(self, book_id, member_id):

        #会員が存在するか確認する
        member = self.get_member(member_id)

        if member is None:
            return False

        #データベースに接続する
        conn = self.get_connection()

        try: 
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE books
                SET is_borrowed = ?
                WHERE book_id = ? AND is_borrowed = 0
            ''', (True, book_id))

            if cursor.rowcount == 1:

                #貸出履歴を登録する
                cursor.execute('''
                    INSERT INTO borrowing_history (member_id, book_id, borrow_date)
                    VALUES (?, ?, datetime('now'))
                ''', (member_id, book_id))      

                conn.commit()
                return True
            else:
                conn.rollback()
                return False        
        
        except sqlite3.Error:
            conn.rollback()
            raise
        
        finally:
            conn.close()

    #SQLiteデータベースで書籍の返却状態を更新する
    def return_book(self, book_id, member_id):
        #会員が存在するか確認する
        member = self.get_member(member_id)

        if member is None:
            return False
        
        #データベースに接続する
        conn = self.get_connection()

        try: 
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE books
                SET is_borrowed = ?
                WHERE book_id = ? AND is_borrowed = 1
            ''', (False, book_id))

            if cursor.rowcount == 1:
                #貸出履歴の返却日時を更新する
                cursor.execute('''
                    UPDATE borrowing_history
                    SET return_date = datetime('now')
                    WHERE member_id = ? 
                      AND book_id = ? 
                      AND return_date IS NULL
                ''', (member_id, book_id))

                #貸出履歴の更新が成功したか確認する
                if cursor.rowcount != 1:
                    conn.rollback()
                    return False

                conn.commit()
                return True
                    
            else:
                conn.rollback()
                return False        
        
        except sqlite3.Error:
            conn.rollback()
            raise
        
        finally:
            conn.close()

    #SQLiteデータベースに会員を登録する
    def add_member(self, member):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO members (member_id, name)
                VALUES (?, ?)
            ''', (member.member_id, member.name))
            conn.commit()
            return True

        except sqlite3.IntegrityError:
            conn.rollback()
            return False
        
        except sqlite3.Error:
            conn.rollback()
            raise

        finally:
            conn.close()

    #登録済みの会員をデータベースから取得する
    def get_member(self, member_id):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT member_id, name
                FROM members
                WHERE member_id = ?
            ''', (member_id,))
            row = cursor.fetchone()

        finally:
            conn.close()

        if row is None:
            return None

        return Member(row[0], row[1])


    # すべての貸出履歴を取得する
    def get_borrowing_history(self):
        conn = self.get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT bh.member_id, m.name,
                       bh.book_id, b.title,
                       bh.borrow_date, bh.return_date
                FROM borrowing_history AS bh
                JOIN members AS m
                  ON bh.member_id = m.member_id
                JOIN books AS b
                  ON bh.book_id = b.book_id
            ''')
            rows = cursor.fetchall()

        finally:
            conn.close()

        history = []
        for row in rows:
            history.append({
                "member_id": row[0],
                "member_name": row[1],
                "book_id": row[2],
                "book_title": row[3],
                "borrow_date": row[4],
                "return_date": row[5]
            })

        return history