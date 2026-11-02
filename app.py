# 本の情報を管理するクラス
from flask import Flask, render_template, redirect , request, flash, url_for
import sqlite3

#SQLiteデータベースの初期化
conn = sqlite3.connect("library.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        book_id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        is_borrowed BOOLEAN DEFAULT FALSE
    )
''')

conn.commit()
conn.close()

class Book:
    def __init__(self, title, book_id):
        self.title = title 
        self.is_borrowed = False 
        self.book_id = book_id 

class Library:

    def __init__(self, db_path="library.db"):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    #SQLiteデータベースに書籍を登録する
    def add_book(self, book):
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO books (book_id, title, is_borrowed)
                VALUES (?, ?, ?)
            ''', (book.book_id, book.title, book.is_borrowed))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            conn.rollback()
            return False
        
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

    #SQLiteデータベースで書籍の貸出状態を更新する
    def borrow_book(self, book_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        try: 
            cursor.execute('''
                UPDATE books
                SET is_borrowed = ?
                WHERE book_id = ? AND is_borrowed = 0
            ''', (True, book_id))

            if cursor.rowcount == 1:
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
    def return_book(self, book_id):
        conn = self.get_connection()
        cursor = conn.cursor()

        try: 
            cursor.execute('''
                UPDATE books
                SET is_borrowed = ?
                WHERE book_id = ? AND is_borrowed = 1
            ''', (False, book_id))

            if cursor.rowcount == 1:
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


# #図書館の本を管理するクラス
# class Library:

#     #本のリストを初期化する
#     def __init__(self):
#         self.books = []

#     #本を登録する
#     def add_book(self, book):
#         for existing_book in self.books:
#             if existing_book.book_id == book.book_id:
#                 return False 
#         self.books.append(book)
#         return True

#     # 登録済みの本の取得する
#     def get_books(self):
#         return self.books

#     # 本を貸し出す
#     def borrow_book(self, book_id):
#         for existing_book in self.books:
#             if existing_book.book_id == book_id:
#                 if not existing_book.is_borrowed:
#                     existing_book.is_borrowed = True 
#                     return True
#                 else:
#                     return False
#         return False

            
#     # 本を返却する
#     def return_book(self, book_id):
#         for existing_book in self.books:
#             if existing_book.book_id == book_id:
#                 if existing_book.is_borrowed:
#                     existing_book.is_borrowed = False 
#                     return True
#                 else:
#                     return False 
#         return False 

#Flask
library = Library()
app = Flask(__name__)
app.secret_key = "dev-secret-key"
    
@app.route("/")
def index():
    return render_template(
        "index.html", 
        books=library.get_books(),
    )

@app.route("/add", methods=["POST"])
def add_book():
    title = request.form["title"].strip()
    if not title:
        flash("書籍名を入力してください。")
        return redirect("/")

    try:
        book_id = int(request.form["book_id"])
    except ValueError:
        flash("書籍IDには整数を入力してください。")
        return redirect("/")

    if book_id < 1:
        flash("書籍IDには1以上の整数を入力してください。")
        return redirect("/")

    book = Book(title, book_id)
    result = library.add_book(book)
    if result:
        flash("登録が完了しました。")
    else:
        flash("同じ書籍IDが既に登録されています。")
    return redirect("/")


@app.route("/borrow_book/<int:book_id>", methods=["POST"])
def borrow_book(book_id):
    result = library.borrow_book(book_id)
    if result:
        flash("貸出が完了しました。")
    else:
        flash("貸出できませんでした。")
    return redirect("/")

@app.route("/return_book/<int:book_id>", methods=["POST"])
def return_book(book_id):
    result = library.return_book(book_id)
    if result:
        flash("返却が完了しました。")
    else:
        flash("返却できませんでした。")
    return redirect("/")

