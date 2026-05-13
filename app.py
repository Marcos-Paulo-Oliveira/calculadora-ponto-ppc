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
        multiplicador = -1 if '-' in h_str else 1
        h_str = h_str.replace('-', '').replace('(', '').replace(')', '')
        h, m = map(int, h_str.strip().split(':'))
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

    # --- BUSCA PELO SALDO ACUMULADO NO TEXTO ---
    match_saldo = re.findall(r"Saldo\s+[-\d:]+\s+\(([-\d:]+)\)", texto_total)
    saldo_acumulado_str = match_saldo[-1] if match_saldo else "00:00"
    saldo_decimal = converter_hora_decimal(saldo_acumulado_str)

    # --- CÁLCULO FINANCEIRO ---
    valor_final = 0.0
    dsr = 0.0
    if saldo_decimal > 0:
        valor_final = saldo_decimal * VALOR_HORA_SECA * 1.60
        dsr = valor_final * 0.25

    # --- INTERFACE ATUALIZADA ---
    st.divider()
    
    # Criamos 3 colunas para distribuir melhor as informações
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # Exibe o saldo exatamente como no PDF (-00:26)
        # O delta_color="normal" faz ficar vermelho se for negativo e verde se positivo
        st.metric(
            label="Saldo Atual do Banco", 
            value=saldo_acumulado_str, 
            delta="Horas Acumuladas", 
            delta_color="normal" if saldo_decimal >= 0 else "inverse"
        )

    with c2:
        st.subheader("📈 Status")
        if saldo_decimal < 0:
            st.error("Saldo Negativo")
            st.info("Você precisa compensar essas horas.")
        else:
            st.success("Saldo Positivo")
            st.balloons()

    with c3:
        st.subheader("💰 Estimativa")
        st.metric("Valor Bruto + DSR", f"R$ {valor_final + dsr:.2f}")
        st.caption("Cálculo para o fechamento do quadrimestre.")

    if st.checkbox("Ver log de processamento"):
        st.write(f"Data de corte: {DATA_INICIO_BANCO.strftime('%d/%m/%Y')}")
        st.write(f"Saldo bruto identificado: {saldo_acumulado_str}")
