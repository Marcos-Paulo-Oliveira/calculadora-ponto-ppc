import streamlit as st
import pdfplumber
import re
from datetime import datetime

# Configurações do Contrato Marcos (PP&C)
SALARIO_BASE = 2605.00
VALOR_HORA_SECA = SALARIO_BASE / 220
DATA_INICIO_BANCO = datetime(2026, 4, 1) 

def converter_hora_decimal(h_str):
    if not h_str or ':' not in h_str: return 0.0
    try:
        # Detecta se é negativo
        multiplicador = -1 if '-' in h_str else 1
        # Remove caracteres indesejados
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

    # --- NOVA BUSCA MAIS ROBUSTA ---
    # Esta regex busca a palavra Saldo e pega o que está dentro do último parênteses da linha
    match_saldo = re.findall(r"Saldo.*?\((\s*[-\d:]+\s*)\)", texto_total, re.DOTALL)
    
    if match_saldo:
        saldo_acumulado_str = match_saldo[-1].strip() # Pega o último saldo do documento
    else:
        saldo_acumulado_str = "00:00"
    
    saldo_decimal = converter_hora_decimal(saldo_acumulado_str)

    # --- CÁLCULO FINANCEIRO ---
    valor_final = 0.0
    dsr = 0.0
    if saldo_decimal > 0:
        valor_final = saldo_decimal * VALOR_HORA_SECA * 1.60
        dsr = valor_final * 0.25

    # --- INTERFACE ---
    st.divider()
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric(
            label="Saldo Atual Identificado", 
            value=saldo_acumulado_str, 
            delta="Horas no Banco", 
            delta_color="normal" if saldo_decimal >= 0 else "inverse"
        )

    with c2:
        if saldo_decimal < 0:
            st.error("📉 Saldo Devedor")
            st.info("Você possui horas negativas a compensar.")
        elif saldo_decimal > 0:
            st.success("📈 Saldo Credor")
            st.balloons()
        else:
            st.warning("⚖️ Saldo Zerado")

    with c3:
        st.subheader("💰 Projeção Financeira")
        st.write(f"**Valor das Extras:** R$ {valor_final:.2f}")
        st.write(f"**DSR Estimado:** R$ {dsr:.2f}")
        st.success(f"### Total: R$ {valor_final + dsr:.2f}")

    if st.checkbox("Depuração: Ver texto bruto do PDF"):
        st.text(texto_total)
