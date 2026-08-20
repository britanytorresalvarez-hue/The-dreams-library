from flask import Flask, render_template, request, redirect, url_for, session, send_file
from pymongo import MongoClient
from bson.binary import Binary
from bson.objectid import ObjectId
import io, datetime, ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
app.secret_key = "clave_secreta_super_segura"  # Necesario para las sesiones de usuario

# Conexión a tu MongoDB Atlas existente
client = MongoClient("mongodb+srv://santiobando2709_db_user:zRJP6t3ceiIrJRnb@cluster0.fmbmmz9.mongodb.net/")
db = client["TheDreamsLibrary"]
users_col = db["users"]
books_col = db["books"]

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        action = request.form.get("action")
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if action == "login":
            if users_col.find_one({"username": username, "password": password}):
                session["user"] = username
                return redirect(url_for("main"))
            return render_template("login.html", error="Usuario o contraseña incorrectos", mode="login")
            
        elif action == "register":
            email = request.form.get("email", "").strip()
            if not username or not password or not email:
                return render_template("login.html", error="Todos los campos son obligatorios", mode="register")
            if users_col.find_one({"username": username}):
                return render_template("login.html", error="El usuario ya existe", mode="register")
            
            users_col.insert_one({"username": username, "password": password, "email": email})
            return render_template("login.html", success="Cuenta creada con éxito. Ingresa ahora.", mode="login")
            
    return render_template("login.html", mode="login")

@app.route("/main")
def main():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("main.html", user=session["user"])

@app.route("/books/<filter_type>")
def books(filter_type):
    if "user" not in session:
        return redirect(url_for("login"))
    
    query = {"username": session["user"]}
    title = "Tus Libros Guardados"
    
    if filter_type == "favorites":
        query["favorite"] = True
        title = "Tus Libros Preferidos ⭐"
    elif filter_type == "pending":
        query["pending"] = True
        title = "Tu Lista de Pendientes ⏳"
        
    user_books = list(books_col.find(query))
    return render_template("books.html", books=user_books, title=title)

@app.route("/upload", methods=["POST"])
def upload():
    if "user" not in session:
        return redirect(url_for("login"))
        
    file = request.files.get("epub_file")
    if file and file.filename.endswith(".epub"):
        file_data = file.read()
        filename = file.filename
        
        author = "Desconocido"
        try:
            book_obj = epub.read_epub(io.BytesIO(file_data))
            authors = book_obj.get_metadata('DC', 'creator')
            if authors:
                author = authors[0][0]
        except:
            pass
            
        books_col.insert_one({
            "username": session["user"],
            "filename": filename,
            "data": Binary(file_data),
            "author": author,
            "date_added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "date_started": "No iniciado",
            "rating": 0,
            "review": "",
            "favorite": False,
            "read_status": False,
            "pending": True
        })
    return redirect(url_for("books", filter_type="all"))

@app.route("/delete/<book_id>")
def delete(book_id):
    if "user" not in session:
        return redirect(url_for("login"))
    books_col.delete_one({"_id": ObjectId(book_id)})
    return redirect(url_for("books", filter_type="all"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
