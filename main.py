import streamlit as st
from azure.storage.blob import BlobServiceClient
import os
import pymssql
import uuid
import json
from dotenv import load_dotenv

load_dotenv()

BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING")
BLOB_CONTAINER_NAME = os.getenv("BLOB_CONTAINER_NAME")
BLOB_ACCOUNT_NAME = os.getenv("BLOB_ACCOUNT_NAME")

SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

st.title("Cadastro de Produtos")

# Formulário de Cadastro de Produtos
product_name = st.text_input("Nome do Produto")
product_price = st.number_input("Preço do Produto", min_value=0.0, format='%.2f')
product_description = st.text_area("Descrição do Produto")
product_image = st.file_uploader("Imagem do Produto", type=['jpg', 'png', 'jpeg'])

# Salvar imagem no blob
def upload_image(file):
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(BLOB_CONTAINER_NAME)
    blob_name = str(uuid.uuid4()) + file.name
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(file.read(), overwrite=True)
    image_url = f"https://{BLOB_ACCOUNT_NAME}.blob.core.windows.net/{BLOB_CONTAINER_NAME}/{blob_name}"
    return image_url

def insert_product(product_name, product_price, product_description, product_image):
    try:
        image_url = upload_image(product_image)
        conn = pymssql.connect(server=SQL_SERVER, user=SQL_USER, password=SQL_PASSWORD, database=SQL_DATABASE)
        cursor = conn.cursor()
        insert_sql = """
            INSERT INTO Produtos (nome, descricao, preco, imagem_url)
            VALUES (%s, %s, %s, %s)
        """
        values = (product_name, product_description, product_price, image_url)
        cursor.execute(insert_sql, values)
        conn.commit()
        conn.close()

        return True
    except Exception as e:
        st.error(f'Erro ao inserir o produto: {e}')
        return False
    
def list_products():
    try:
        conn = pymssql.connect(server=SQL_SERVER, user=SQL_USER, password=SQL_PASSWORD, database=SQL_DATABASE)
        cursor = conn.cursor(as_dict=True)
        cursor.execute("SELECT * FROM Produtos")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        st.error(f'Erro ao inserir o produto: {e}')
        return []
    
def list_products_screen():
    products = list_products()
    if products:
        cards_por_linha = 3
        cols = st.columns(cards_por_linha)
        for i, product in enumerate(products):
            col = cols[i % cards_por_linha]
            with col:
                if product["imagem_url"]:
                    html_img = f'<img src="{product["imagem_url"]}" width="200" height="200" alt="Imagem do Produto" />'
                    st.markdown(html_img, unsafe_allow_html=True)
                st.markdown(f'### {product["nome"]}')
                st.write(f'**Descrição**: {product["descricao"]}')
                st.write(f'**Preço**: R$ {float(product["preco"]):.2f}')
            if (i + 1) % cards_por_linha == 0 and (i + 1) < len(products):
                cols = st.columns(cards_por_linha)
    else:
        st.info("Nenhum produto encontrado")

if st.button("Salvar Produto"):
    insert_product(product_name, product_price, product_description, product_image)
    return_message = "Produto salvo com sucesso"
    list_products_screen()

st.header("Produtos Cadastrados")

if st.button("Listar Produtos"):
    list_products_screen()
    return_message = "Produtos listados com sucesso"