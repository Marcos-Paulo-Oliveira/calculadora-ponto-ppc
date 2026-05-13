import streamlit as st
import pdfplumber
import re
from datetime import datetime

def converter_hora_decimal(h_str):
    if not h_str or ':' not in h_str: return 0.0
    try:
        multiplicador = -1 if '-' in h_str else 1
        limpo = re.sub(r'[^\d:]', '', h_str)
        h, m = map(int, limpo.split(':'))
        return (h + (m / 60)) * multiplicador
    except: return 0.0

st.set_page_config(page_title="Calculadora Ponto PP&C", page_icon="📊", layout="wide")
st.title("📊 Calculadora de Banco de Horas Geral - PP&C")

# --- AJUSTE NO CAMPO DE SALÁRIO (Permite digitar livremente) ---
st.sidebar.header("Configurações Financeiras")
salario_texto = st.sidebar.text_input("Informe seu Salário Bruto (Ex: 2605.00):", value="2605.00")

try:
    salario_informado = float(salario_texto.replace(',', '.'))
except:
    st.sidebar.error("Por favor, insira um número válido para o salário.")
    salario_informado = 0.0

valor_hora_seca = salario_informado / 220 if salario_informado > 0 else 0.0

arquivo = st.file_uploader("Suba seu Espelho de Ponto PDF (Pontotel)", type="pdf")

if arquivo:
    with pdfplumber.open(arquivo) as pdf:
        texto_total = ""
        for page in pdf.pages:
            texto_total += page.extract_text() + "\n"

    # --- BUSCA DE SALDO MELHORADA (Ignora espaços e quebras de linha) ---
    # Busca a palavra Saldo e tenta capturar o valor final entre parênteses
    match_saldo = re.findall(r"Saldo.*?\(?\s*([-\d:]+)\s*\)?", texto_total, re.IGNORECASE | re.DOTALL)
    
    # Pegamos o último valor que se parece com um saldo (HH:MM) no final do PDF
    if match_saldo:
        saldo_exibicao = match_saldo[-1].strip()
    else:
        saldo_exibicao = "00:00"
    
    saldo_decimal = converter_hora_decimal(saldo_exibicao)

    # --- CÁLCULO FINANCEIRO ---
    valor_final = 0.0
    dsr = 0.0
    if saldo_decimal > 0:
        valor_final = saldo_decimal * valor_hora_seca * 1.60
        dsr = valor_final * 0.25

    # --- INTERFACE ---
    st.divider()
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric(
            label="Saldo Identificado no PDF", 
            value=saldo_exibicao, 
            delta="Horas Acumuladas", 
            delta_color="normal" if saldo_decimal >= 0 else "inverse"
        )

    with c2:
        st.subheader("💰 Estimativa")
        st.write(f"**Valor da Hora:** R$ {valor_hora_seca:.2f}")
        st.write(f"**Bruto Extras:** R$ {valor_final:.2f}")

    with c3:
        total_receber = valor_final + dsr
        st.metric("Total c/ DSR", f"R$ {total_receber:.2f}")
        
    if st.checkbox("Visualizar texto lido (Para conferência)"):
        st.text(texto_total)
