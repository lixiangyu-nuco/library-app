# 本の情報を管理するクラス
from flask import Flask, render_template, redirect , request, flash

class Book:
    def __init__(self, title, book_id):
        self.title = title 
        self.is_borrowed = False 
        self.book_id = book_id 

#図書館の本を管理するクラス
class Library:

    #本のリストを初期化する
    def __init__(self):
        self.books = []

    #本を登録する
    def add_book(self, book):
        for existing_book in self.books:
            if existing_book.book_id == book.book_id:
                return False 
        self.books.append(book)
        return True

    # 登録済みの本の取得する
    def get_books(self):
        return self.books

    # 本を貸し出す
    def borrow_book(self, book_id):
        for book in self.books:
            if book.book_id == book_id:
                if not book.is_borrowed:
                    book.is_borrowed = True 
                    return True
                else:
                    return False
        return False

            
    # 本を返却する
    def return_book(self, book_id):
        for book in self.books:
            if book.book_id == book_id:
                if book.is_borrowed:
                    book.is_borrowed = False 
                    return True
                else:
                    return False 
        return False 


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
    title = request.form["title"]
    book_id = request.form["book_id"]
    book = Book(title, book_id)
    result = library.add_book(book)
    if result:
        flash("登録が完了しました。")
    else:
        flash("同じ書籍IDが既に登録されています。")
    return redirect("/")





