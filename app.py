from flask import Flask, render_template, redirect, request, flash, url_for
from library import Book, Member, Library

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

@app.route("/borrow_book/<int:book_id>/<int:member_id>", methods=["POST"])
def borrow_book(book_id, member_id):
    result = library.borrow_book(book_id, member_id)
    if result:
        flash("貸出が完了しました。")
    else:
        flash("貸出できませんでした。")
    return redirect(url_for("member_page", member_id=member_id))

@app.route("/return_book/<int:book_id>/<int:member_id>", methods=["POST"])
def return_book(book_id, member_id):
    result = library.return_book(book_id, member_id)
    if result:
        flash("返却が完了しました。")
    else:
        flash("返却できませんでした。")
    return redirect(url_for("member_page", member_id=member_id))

@app.route("/add_member", methods=["POST"])
def add_member():
    name = request.form["name"].strip()
    if not name:
        flash("会員名を入力してください。")
        return redirect("/")

    try:
        member_id = int(request.form["member_id"])
    except ValueError:
        flash("会員IDには整数を入力してください。")
        return redirect("/")

    if member_id < 1:
        flash("会員IDには1以上の整数を入力してください。")
        return redirect("/")

    member = Member(member_id, name)
    result = library.add_member(member)
    if result:
        flash("会員登録が完了しました。")
    else:
        flash("同じ会員IDが既に登録されています。")
    return redirect("/")

@app.route("/get_member", methods=["POST"])
def get_member():
    member_id = request.form["member_id"].strip()
    if not member_id:
        flash("会員IDを入力してください。")
        return redirect("/")

    try:
        member_id = int(member_id)
    except ValueError:
        flash("会員IDには整数を入力してください。")
        return redirect("/")

    if member_id < 1:
        flash("会員IDには1以上の整数を入力してください。")
        return redirect("/")

    member = library.get_member(member_id)
    if member is None:
        flash("会員IDが見つかりませんでした。")
        return redirect("/")
    
    # 会員専用画面へ移動する
    return redirect(url_for("member_page", member_id=member.member_id))

@app.route("/member/<int:member_id>")
def member_page(member_id):
    member = library.get_member(member_id)

    if member is None:
        flash("会員IDが見つかりませんでした。")
        return redirect("/")

    return render_template(
        "member.html",
        member=member,
        books=library.get_books(),
    )