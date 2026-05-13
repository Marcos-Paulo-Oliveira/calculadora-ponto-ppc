import streamlit as st
import pdfplumber
import re
from datetime import datetime

# Configurações do seu contrato
SALARIO_BASE = 2605.00
VALOR_HORA_SECA = SALARIO_BASE / 220
DATA_INICIO_BANCO = datetime(2026, 4, 1) 

def converter_hora_decimal(h_str):
    if not h_str or ':' not in h_str: return 0.0
    try:
        multiplicador = -1 if '-' in h_str else 1
        limpo = re.sub(r'[^\d:]', '', h_str)
        h, m = map(int, limpo.split(':'))
        return (h + (m / 60)) * multiplicador
    except: return 0.0

st.set_page_config(page_title="Calculadora Ponto PP&C", page_icon="📊", layout="wide")
st.title("📊 Calculadora de Saldo Quadrimestral (Pós-01/04)")

arquivo = st.file_uploader("Suba seu Espelho de Ponto PDF", type="pdf")

if arquivo:
    with pdfplumber.open(arquivo) as pdf:
        texto_total = ""
        for page in pdf.pages:
            texto_total += page.extract_text() + "\n"

    # --- BUSCA DO SALDO (EXIBIÇÃO) ---
    # Busca a palavra Saldo e captura o valor entre parênteses
    match_saldo = re.findall(r"Saldo\s+[-\d:]+\s+\(([-\d:]+)\)", texto_total)
    
    if match_saldo:
        saldo_exibicao = match_saldo[-1].strip() # Ex: "-00:26"
    else:
        saldo_exibicao = "00:00"
    
    saldo_decimal = converter_hora_decimal(saldo_exibicao)

    # --- CÁLCULO FINANCEIRO (MANTIDO CONFORME SUA APROVAÇÃO) ---
    valor_final = 0.0
    dsr = 0.0
    if saldo_decimal > 0:
        valor_final = saldo_decimal * VALOR_HORA_SECA * 1.60
        dsr = valor_final * 0.25

    # --- INTERFACE (FOCO NA SUA IMAGEM CIRCULADA) ---
    st.divider()
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # Aqui é onde você circulou: Mostra o saldo independente de ser + ou -
        st.metric(
            label="Saldo Final (PDF)", 
            value=saldo_exibicao, 
            delta="Horas Acumuladas", 
            delta_color="normal" if saldo_decimal >= 0 else "inverse"
        )

    with c2:
        if saldo_decimal < 0:
            st.error("📉 Saldo Devedor")
        elif saldo_decimal > 0:
            st.success("📈 Saldo Credor")
        else:
            st.info("⚖️ Saldo Zerado")

    with c3:
        st.subheader("💰 Estimativa de Recebimento")
        total_receber = valor_final + dsr
        st.metric("Total Bruto + DSR", f"R$ {total_receber:.2f}")

    if st.checkbox("Ver texto extraído para conferência"):
        st.text(texto_total)
