import tkinter as tk
from tkinter import messagebox, filedialog
from pymongo import MongoClient
from bson.binary import Binary
import io, datetime, ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from PIL import Image, ImageTk

class DreamsLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("THE DREAMS LIBRARY")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0f0f0f")
        
        try:
            self.client = MongoClient("mongodb+srv://santiobando2709_db_user:zRJP6t3ceiIrJRnb@cluster0.fmbmmz9.mongodb.net/")
            self.db = self.client["TheDreamsLibrary"]
            self.users_col = self.db["users"]
            self.books_col = self.db["books"]
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar a MongoDB: {e}")
            
        self.current_user = None
        self.show_login()

    def clear(self):
        for w in self.root.winfo_children(): 
            w.destroy()

    def show_login(self, is_register=False):
        self.clear()
        tk.Label(self.root, text="THE DREAMS LIBRARY", font=("Brush Script MT", 50), bg="#0f0f0f", fg="#e94560").pack(pady=40)
        frame = tk.Frame(self.root, bg="#1a1a2e", padx=40, pady=40)
        frame.pack()
        
        tk.Label(frame, text="Usuario:", bg="#1a1a2e", fg="white", font=("Arial", 12)).pack(anchor="w")
        self.entry_u = tk.Entry(frame, font=("Arial", 14), bg="#2d2d2d", fg="white", insertbackground="white")
        self.entry_u.pack(pady=5)
        
        tk.Label(frame, text="Contraseña:", bg="#1a1a2e", fg="white", font=("Arial", 12)).pack(anchor="w")
        self.entry_p = tk.Entry(frame, show="*", font=("Arial", 14), bg="#2d2d2d", fg="white", insertbackground="white")
        self.entry_p.pack(pady=5)
        
        if is_register:
            tk.Label(frame, text="Correo:", bg="#1a1a2e", fg="white", font=("Arial", 12)).pack(anchor="w")
            self.entry_e = tk.Entry(frame, font=("Arial", 14), bg="#2d2d2d", fg="white", insertbackground="white")
            self.entry_e.pack(pady=5)
            tk.Button(frame, text="REGISTRARSE", bg="#e94560", fg="white", font=("Arial", 12, "bold"), command=self.register_user).pack(fill="x", pady=15)
            tk.Button(frame, text="¿Ya tienes cuenta? Ingresa", bg="#1a1a2e", fg="#cccccc", bd=0, command=lambda: self.show_login(False)).pack()
        else:
            tk.Button(frame, text="INGRESAR", bg="#e94560", fg="white", font=("Arial", 12, "bold"), command=self.login).pack(fill="x", pady=15)
            tk.Button(frame, text="¿No tienes cuenta? Crear cuenta", bg="#1a1a2e", fg="#cccccc", bd=0, command=lambda: self.show_login(True)).pack()

    def login(self):
        user = self.entry_u.get().strip()
        passw = self.entry_p.get().strip()
        if self.users_col.find_one({"username": user, "password": passw}):
            self.current_user = user
            self.show_main()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def register_user(self):
        user = self.entry_u.get().strip()
        passw = self.entry_p.get().strip()
        email = self.entry_e.get().strip()
        if not user or not passw or not email:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        if self.users_col.find_one({"username": user}):
            messagebox.showerror("Error", "El usuario ya existe")
        else:
            self.users_col.insert_one({"username": user, "password": passw, "email": email})
            messagebox.showinfo("Éxito", "Cuenta creada correctamente. Ahora puedes ingresar.")
            self.show_login(False)

    def show_main(self):
        self.clear()
        tk.Label(self.root, text="THE DREAMS LIBRARY", font=("Brush Script MT", 35), bg="#1a1a2e", fg="#e94560", pady=10).pack(fill="x")
        
        body = tk.Frame(self.root, bg="#0f0f0f")
        body.pack(expand=True, fill="both")
        
        sidebar = tk.Frame(body, bg="#1a1a2e", width=250)
        sidebar.pack(side=tk.RIGHT, fill="y")
        sidebar.pack_propagate(False)
        
        self.content = tk.Frame(body, bg="#0f0f0f", padx=30, pady=30)
        self.content.pack(side=tk.LEFT, expand=True, fill="both")
        
        tk.Button(sidebar, text="Pantalla Principal", font=("Arial", 13), bg="#0f3460", fg="white", bd=0, padx=15, pady=10, command=self.home_page).pack(fill="x", padx=10, pady=10)
        tk.Button(sidebar, text="Mis Libros", font=("Arial", 13), bg="#e94560", fg="white", bd=0, padx=15, pady=10, command=self.books_page).pack(fill="x", padx=10, pady=5)
        tk.Button(sidebar, text="Libros Preferidos", font=("Arial", 13), bg="#0f3460", fg="white", bd=0, padx=15, pady=10, command=self.favorites_page).pack(fill="x", padx=10, pady=5)
        tk.Button(sidebar, text="Lista de Pendientes", font=("Arial", 13), bg="#0f3460", fg="white", bd=0, padx=15, pady=10, command=self.pending_page).pack(fill="x", padx=10, pady=5)
        tk.Button(sidebar, text="Cerrar Sesión", font=("Arial", 13), bg="#cc3333", fg="white", bd=0, padx=15, pady=10, command=self.logout).pack(fill="x", padx=10, pady=25)
        
        self.home_page()

    def logout(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Estás seguro de que deseas salir de tu cuenta?"):
            self.current_user = None
            self.show_login(False)

    def home_page(self):
        for w in self.content.winfo_children(): 
            w.destroy()
            
        # Logo JPEG en grande en la pantalla principal
        loaded_logo = False
        for filename in ["logo.jpeg", "logo.jpg"]:
            try:
                logo_img = Image.open(filename)
                logo_img.thumbnail((250, 250))
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                tk.Label(self.content, image=self.logo_photo, bg="#0f0f0f").pack(pady=10)
                loaded_logo = True
                break
            except:
                pass
                
        if not loaded_logo:
            tk.Label(self.content, text="📚 THE DREAMS LIBRARY 📚", font=("Brush Script MT", 40), bg="#0f0f0f", fg="#e94560").pack(pady=10)

        tk.Label(self.content, text=f"Bienvenido a la librería de tus sueños, {self.current_user}", font=("Arial", 20, "bold"), bg="#0f0f0f", fg="white").pack(pady=15)
        
        btn_f = tk.Frame(self.content, bg="#0f0f0f")
        btn_f.pack(pady=20)
        
        tk.Button(btn_f, text="MIS LIBROS", font=("Arial", 14, "bold"), bg="#e94560", fg="white", width=22, height=3, command=self.books_page).pack(side=tk.LEFT, padx=15)
        tk.Button(btn_f, text="CARGAR NUEVO EPUB", font=("Arial", 14, "bold"), bg="#0f3460", fg="white", width=22, height=3, command=self.upload_book).pack(side=tk.LEFT, padx=15)

    def upload_book(self):
        path = filedialog.askopenfilename(filetypes=[("Archivos EPUB", "*.epub")])
        if path:
            try:
                filename = path.split('/')[-1]
                with open(path, "rb") as f: 
                    file_data = f.read()
                
                author = "Desconocido"
                try:
                    book_obj = epub.read_epub(path)
                    authors = book_obj.get_metadata('DC', 'creator')
                    if authors:
                        author = authors[0][0]
                except:
                    pass
                
                self.books_col.insert_one({
                    "username": self.current_user,
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
                messagebox.showinfo("Éxito", f"El libro '{filename}' se ha guardado correctamente.")
                self.books_page()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")

    def extract_cover(self, data):
        try:
            book = epub.read_epub(io.BytesIO(data))
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_IMAGE and 'cover' in item.get_name().lower():
                    img = Image.open(io.BytesIO(item.get_content()))
                    img.thumbnail((80, 120))
                    return ImageTk.PhotoImage(img)
        except:
            pass
        return None

    def extract_large_cover(self, data):
        try:
            book = epub.read_epub(io.BytesIO(data))
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_IMAGE and 'cover' in item.get_name().lower():
                    img = Image.open(io.BytesIO(item.get_content()))
                    img.thumbnail((220, 320))
                    return ImageTk.PhotoImage(img)
        except:
            pass
        return None

    def display_book_list(self, query_filter, title_text):
        for w in self.content.winfo_children(): 
            w.destroy()
            
        tk.Label(self.content, text=title_text, font=("Arial", 20, "bold"), bg="#0f0f0f", fg="white").pack(anchor="w", pady=15)
        
        self.images_ref = []
        books = list(self.books_col.find(query_filter))
        
        if not books:
            tk.Label(self.content, text="No hay libros en esta lista.", font=("Arial", 14), bg="#0f0f0f", fg="#888888").pack(anchor="w", pady=10)
            return

        for b in books:
            row = tk.Frame(self.content, bg="#1a1a2e", pady=10, padx=10)
            row.pack(fill="x", pady=5)
            
            cover = self.extract_cover(b['data'])
            if cover:
                self.images_ref.append(cover)
                tk.Label(row, image=cover, bg="#1a1a2e").pack(side=tk.LEFT, padx=10)
            else:
                tk.Label(row, text="Sin Portada", bg="#2d2d2d", fg="white", width=10, height=6).pack(side=tk.LEFT, padx=10)
            
            tk.Label(row, text=b['filename'], bg="#1a1a2e", fg="white", font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=10)
            
            btn_f = tk.Frame(row, bg="#1a1a2e")
            btn_f.pack(side=tk.RIGHT)
            
            tk.Button(btn_f, text="Descargar", bg="#007acc", fg="white", font=("Arial", 11), command=lambda x=b: self.download(x)).pack(side=tk.LEFT, padx=3)
            tk.Button(btn_f, text="Previsualizar", bg="#444444", fg="white", font=("Arial", 11), command=lambda x=b: self.preview(x)).pack(side=tk.LEFT, padx=3)
            tk.Button(btn_f, text="Eliminar", bg="#cc3333", fg="white", font=("Arial", 11), command=lambda x=b: self.delete(x)).pack(side=tk.LEFT, padx=3)
            tk.Button(btn_f, text="Calificar", bg="#e94560", fg="white", font=("Arial", 11), command=lambda x=b: self.rate(x)).pack(side=tk.LEFT, padx=3)

    def books_page(self):
        self.display_book_list({"username": self.current_user}, "Tus Libros Guardados")

    def favorites_page(self):
        self.display_book_list({"username": self.current_user, "favorite": True}, "Tus Libros Preferidos ⭐")

    def pending_page(self):
        self.display_book_list({"username": self.current_user, "pending": True}, "Tu Lista de Pendientes ⏳")

    def download(self, b):
        path = filedialog.asksaveasfilename(defaultextension=".epub", initialfile=b['filename'])
        if path:
            with open(path, "wb") as f: 
                f.write(b['data'])
            messagebox.showinfo("Éxito", "Libro descargado correctamente.")

    def delete(self, b):
        if messagebox.askyesno("Eliminar", f"¿Estás seguro de eliminar '{b['filename']}'?"):
            self.books_col.delete_one({"_id": b['_id']})
            self.books_page()

    def preview(self, b):
        try:
            book = epub.read_epub(io.BytesIO(b['data']))
            text = ""
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    text += BeautifulSoup(item.get_content(), 'html.parser').get_text() + "\n\n"
                    if len(text) > 1500:
                        break
            
            win = tk.Toplevel(self.root)
            win.title(f"Previsualización - {b['filename']}")
            win.geometry("600x500")
            win.configure(bg="#121212")
            
            txt = tk.Text(win, bg="#121212", fg="white", font=("Arial", 12), padx=15, pady=15)
            txt.insert(tk.END, text if text else "No se pudo extraer texto legible.")
            txt.config(state=tk.DISABLED)
            txt.pack(expand=True, fill="both")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo previsualizar el libro: {e}")

    def rate(self, b):
        if b.get('date_started', 'No iniciado') == 'No iniciado':
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            self.books_col.update_one({"_id": b['_id']}, {"$set": {"date_started": now_str}})
            b['date_started'] = now_str

        top = tk.Toplevel(self.root)
        top.title(f"Calificar y Detalles - {b['filename']}")
        top.geometry("950x650")
        top.configure(bg="#1a1a2e")

        left_frame = tk.Frame(top, bg="#1a1a2e", padx=20, pady=20)
        left_frame.pack(side=tk.LEFT, fill="both", expand=True)

        right_frame = tk.Frame(top, bg="#1a1a2e", padx=20, pady=20)
        right_frame.pack(side=tk.RIGHT, fill="both")

        self.large_cover_ref = []
        large_cover = self.extract_large_cover(b['data'])
        if large_cover:
            self.large_cover_ref.append(large_cover)
            tk.Label(right_frame, image=large_cover, bg="#1a1a2e").pack(expand=True)
        else:
            tk.Label(right_frame, text="[Sin Portada Grande]", bg="#2d2d2d", fg="white", width=22, height=14, font=("Arial", 11)).pack(expand=True)

        filename = b.get('filename', 'Desconocido')
        author = b.get('author', 'Desconocido')
        size_kb = round(len(b['data']) / 1024, 2)
        date_started = b.get('date_started', 'No iniciado')

        tk.Label(left_frame, text=f"📖 Libro: {filename}", fg="white", bg="#1a1a2e", font=("Arial", 12, "bold"), anchor="w").pack(fill="x", pady=2)
        tk.Label(left_frame, text=f"✍️ Autor: {author}", fg="#cccccc", bg="#1a1a2e", font=("Arial", 11), anchor="w").pack(fill="x", pady=2)
        tk.Label(left_frame, text=f"⚖️ Peso del documento: {size_kb} KB", fg="#cccccc", bg="#1a1a2e", font=("Arial", 11), anchor="w").pack(fill="x", pady=2)
        tk.Label(left_frame, text=f"📅 Fecha de inicio de lectura: {date_started}", fg="#cccccc", bg="#1a1a2e", font=("Arial", 11), anchor="w").pack(fill="x", pady=2)

        tk.Frame(left_frame, height=2, bg="#0f3460").pack(fill="x", pady=10)

        tk.Label(left_frame, text="⭐ ¡CALIFICACIÓN DEL LIBRO! ⭐", fg="#e94560", bg="#1a1a2e", font=("Arial", 13, "bold"), anchor="w").pack(fill="x", pady=2)
        
        scale = tk.Scale(left_frame, from_=0, to=10, orient=tk.HORIZONTAL, bg="#1a1a2e", fg="white", highlightbackground="#1a1a2e", troughcolor="#0f3460", font=("Arial", 11))
        scale.set(b.get('rating', 0))
        scale.pack(fill="x", pady=5)

        tk.Label(left_frame, text="✍️ Reseña o comentario de la lectura:", fg="white", bg="#1a1a2e", font=("Arial", 11, "bold"), anchor="w").pack(fill="x", pady=(8, 2))
        txt_review = tk.Text(left_frame, height=3, bg="#2d2d2d", fg="white", font=("Arial", 10), insertbackground="white")
        txt_review.pack(fill="x", pady=2)
        if b.get('review'):
            txt_review.insert(tk.END, b.get('review'))

        chk_fav_var = tk.BooleanVar(value=b.get('favorite', False))
        chk_fin_var = tk.BooleanVar(value=b.get('read_status', False))
        chk_pen_var = tk.BooleanVar(value=b.get('pending', True))

        tk.Checkbutton(left_frame, text="Marcar como libro preferido ⭐", variable=chk_fav_var, bg="#1a1a2e", fg="white", selectcolor="#0f3460", activebackground="#1a1a2e", activeforeground="white", font=("Arial", 10)).pack(anchor="w", pady=2)
        tk.Checkbutton(left_frame, text="Marcar como libro finalizado ✅", variable=chk_fin_var, bg="#1a1a2e", fg="white", selectcolor="#0f3460", activebackground="#1a1a2e", activeforeground="white", font=("Arial", 10)).pack(anchor="w", pady=2)
        tk.Checkbutton(left_frame, text="Marcar como libro pendiente ⏳", variable=chk_pen_var, bg="#1a1a2e", fg="white", selectcolor="#0f3460", activebackground="#1a1a2e", activeforeground="white", font=("Arial", 10)).pack(anchor="w", pady=2)

        def save_all():
            new_rating = scale.get()
            new_review = txt_review.get("1.0", tk.END).strip()
            is_fav = chk_fav_var.get()
            is_fin = chk_fin_var.get()
            is_pen = chk_pen_var.get()

            self.books_col.update_one(
                {"_id": b['_id']},
                {
                    "$set": {
                        "rating": new_rating,
                        "review": new_review,
                        "favorite": is_fav,
                        "read_status": is_fin,
                        "pending": is_pen
                    }
                }
            )
            messagebox.showinfo("Éxito", "Los cambios se han guardado correctamente.")
            top.destroy()
            self.books_page()

        tk.Button(left_frame, text="GUARDAR", bg="#e94560", fg="white", font=("Arial", 12, "bold"), command=save_all).pack(fill="x", pady=15)

if __name__ == "__main__":
    root = tk.Tk()
    app = DreamsLibraryApp(root)
    root.mainloop()