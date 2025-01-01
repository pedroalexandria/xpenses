import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
import PyPDF2
from PIL import Image
import pytesseract
import openai
import pandas as pd

# Configuração da API do OpenAI
openai.api_key = "SUA_API_KEY_OPENAI"

# Configuração do caminho para o arquivo de credenciais
import os
import json

# Carregar o JSON da variável de ambiente
SERVICE_ACCOUNT_JSON = os.getenv("SERVICE_ACCOUNT_JSON")

# Configurar as credenciais usando o JSON carregado
creds = service_account.Credentials.from_service_account_info(
    json.loads(SERVICE_ACCOUNT_JSON)
)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

SPREADSHEET_ID = "SEU_SPREADSHEET_ID"  # Substitua pelo ID da sua planilha

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("sheets", "v4", credentials=creds)

# Função para extrair texto de um PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    extracted_text = ""
    for page in pdf_reader.pages:
        extracted_text += page.extract_text()
    return extracted_text

# Função para extrair texto de uma imagem
def extract_text_from_image(image):
    return pytesseract.image_to_string(image)

# Função para categorizar transações com IA
def categorize_with_ai(description):
    prompt = f"""
    Categorize a seguinte transação em uma das categorias: Alimentação, Transporte, Lazer, Compras, Saúde, Outros.
    Descrição: {description}
    """
    response = openai.Completion.create(
        engine="text-davinci-003", prompt=prompt, max_tokens=10
    )
    return response.choices[0].text.strip()

# Função para atualizar a planilha
def update_google_sheet(description, category):
    values = [[description, category]]
    body = {"values": values}
    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range="Planilha1!A1",
        valueInputOption="RAW",
        body=body,
    ).execute()

# Interface do Chat no Streamlit
st.title("Chat de Categorias de Transações")

# Upload de arquivos
uploaded_file = st.file_uploader("Envie um PDF ou imagem com as transações", type=["pdf", "jpg", "png", "jpeg"])

if uploaded_file:
    if uploaded_file.name.endswith(".pdf"):
        # Processar PDF
        extracted_text = extract_text_from_pdf(uploaded_file)
    else:
        # Processar Imagem
        image = Image.open(uploaded_file)
        extracted_text = extract_text_from_image(image)
    
    st.write(f"Texto extraído: {extracted_text}")
    
    # Categorizar com IA
    suggested_category = categorize_with_ai(extracted_text)
    st.write(f"Categoria sugerida: {suggested_category}")
    
    # Permitir ajuste manual
    category = st.text_input("Ajuste a categoria, se necessário:", suggested_category)
    
    # Atualizar planilha
    if st.button("Atualizar Planilha"):
        update_google_sheet(extracted_text, category)
        st.success("Planilha atualizada com sucesso!")

# Entrada de texto para transações desconhecidas
description = st.text_input("Digite a descrição da transação desconhecida:")

