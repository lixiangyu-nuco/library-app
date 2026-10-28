# 本の情報を管理するクラス
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
    def add_book(self,book):
        self.books.append(book)

    # 登録済みの本の取得する
    def get_books(self):
        return self.books

    # 本の貸し出す
    def borrow_book(self,book_id):
        for book in self.books:
            if book.book_id == book_id:
                if book.is_borrowed == False:
                    book.is_borrowed = True 

    # 本の返却する
    def return_book(self,book_id):
        for book in self.books:
            if book.book_id == book_id:
                if book.is_borrowed == True:
                    book.is_borrowed = False
                 


        
        
    




