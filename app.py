import streamlit as st
from pymongo import MongoClient
from bson.binary import Binary
import io, datetime, ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from PIL import Image

# Configuración de la página web
st.set_page_config(page_title="THE DREAMS LIBRARY", page_icon="📚", layout="centered")

# Conexión a MongoDB Atlas
@st.cache_resource
def init_connection():
    client = MongoClient("mongodb+srv://santiobando2709_db_user:zRJP6t3ceiIrJRnb@cluster0.fmbmmz9.mongodb.net/")
    return client

client = init_connection()
db = client["TheDreamsLibrary"]
users_col = db["users"]
books_col = db["books"]

# Control de sesión simple
if "user" not in st.session_state:
    st.session_state.user = None

# --- PANTALLA DE LOGIN / REGISTRO ---
if st.session_state.user is None:
    st.markdown("<h1 style='text-align: center; color: #e94560; font-family: Brush Script MT; font-size: 60px;'>THE DREAMS LIBRARY</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Ingresar", "Registrarse"])
    
    with tab1:
        st.subheader("Iniciar Sesión")
        u_log = st.text_input("Usuario", key="u_log")
        p_log = st.text_input("Contraseña", type="password", key="p_log")
        if st.button("INGRESAR"):
            if users_col.find_one({"username": u_log.strip(), "password": p_log.strip()}):
                st.session_state.user = u_log.strip()
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
                
    with tab2:
        st.subheader("Crear Cuenta Nueva")
        u_reg = st.text_input("Usuario", key="u_reg")
        p_reg = st.text_input("Contraseña", type="password", key="p_reg")
        e_reg = st.text_input("Correo", key="e_reg")
        if st.button("REGISTRARSE"):
            if not u_reg or not p_reg or not e_reg:
                st.error("Todos los campos son obligatorios")
            elif users_col.find_one({"username": u_reg.strip()}):
                st.error("El usuario ya existe")
            else:
                users_col.insert_one({"username": u_reg.strip(), "password": p_reg.strip(), "email": e_reg.strip()})
                st.success("Cuenta creada con éxito. Ve a la pestaña 'Ingresar'.")

# --- PANTALLA PRINCIPAL Y APLICACIÓN ---
else:
    # Menú lateral
    st.sidebar.title(f"Hola, {st.session_state.user}")
    menu = st.sidebar.radio("Navegación", ["Pantalla Principal", "Mis Libros", "Libros Preferidos", "Lista de Pendientes"])
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None
        st.rerun()

    # 1. PANTALLA PRINCIPAL
    if menu == "Pantalla Principal":
        # Mostrar logo en grande (busca logo.jpeg o logo.jpg)
        try:
            logo = Image.open("logo.jpeg")
            st.image(logo, width=250)
        except:
            try:
                logo = Image.open("logo.jpg")
                st.image(logo, width=250)
            except:
                st.markdown("<h2 style='color: #e94560;'>📚 THE DREAMS LIBRARY 📚</h2>", unsafe_allow_html=True)
                
        st.title(f"Bienvenido a la librería de tus sueños, {st.session_state.user}")
        
        st.markdown("---")
        st.subheader("Cargar nuevo libro EPUB")
        uploaded_file = st.file_uploader("Elige un archivo EPUB", type="epub")
        
        if uploaded_file is not None:
            if st.button("Guardar en mi Biblioteca"):
                file_data = uploaded_file.read()
                filename = uploaded_file.name
                
                author = "Desconocido"
                try:
                    book_obj = epub.read_epub(io.BytesIO(file_data))
                    authors = book_obj.get_metadata('DC', 'creator')
                    if authors:
                        author = authors[0][0]
                except:
                    pass
                
                books_col.insert_one({
                    "username": st.session_state.user,
                    "filename": filename,
                    "data": Binary(file_data),
                    "author": author,
                    "date_added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "favorite": False,
                    "pending": True
                })
                st.success(f"¡El libro '{filename}' se guardó correctamente!")

    # 2. SECCIÓN DE LIBROS (Mis Libros / Preferidos / Pendientes)
    else:
        query = {"username": st.session_state.user}
        title = "Tus Libros Guardados"
        
        if menu == "Libros Preferidos":
            query["favorite"] = True
            title = "Tus Libros Preferidos ⭐"
        elif menu == "Lista de Pendientes":
            query["pending"] = True
            title = "Tu Lista de Pendientes ⏳"
            
        st.title(title)
        st.markdown("---")
        
        books = list(books_col.find(query))
        if not books:
            st.info("No hay libros en esta sección.")
            
        for b in books:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📖 **{b['filename']}**")
                st.caption(f"Autor: {b.get('author', 'Desconocido')} | Agregado: {b.get('date_added', '')}")
            with col2:
                # Botón de descarga
                st.download_button("Descargar", data=b['data'], file_name=b['filename'], mime="application/epub+zip", key=str(b['_id']))
