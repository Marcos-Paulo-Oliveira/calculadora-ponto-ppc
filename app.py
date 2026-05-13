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

# --- NOVO: ENTRADA DE DADOS DO USUÁRIO ---
st.sidebar.header("Configurações Financeiras")
salario_informado = st.sidebar.number_input("Informe seu Salário Bruto (R$):", min_value=0.0, value=2605.00, step=100.0)
valor_hora_seca = salario_informado / 220

arquivo = st.file_uploader("Suba seu Espelho de Ponto PDF (Pontotel)", type="pdf")

if arquivo:
    with pdfplumber.open(arquivo) as pdf:
        texto_total = ""
        for page in pdf.pages:
            texto_total += page.extract_text() + "\n"

    # --- BUSCA DO SALDO ACUMULADO ---
    match_saldo = re.findall(r"Saldo\s+[-\d:]+\s+\(([-\d:]+)\)", texto_total)
    saldo_exibicao = match_saldo[-1].strip() if match_saldo else "00:00"
    saldo_decimal = converter_hora_decimal(saldo_exibicao)

    # --- CÁLCULO FINANCEIRO BASEADO NO SALÁRIO INFORMADO ---
    valor_final = 0.0
    dsr = 0.0
    if saldo_decimal > 0:
        # Mantendo a regra de 60% do acordo coletivo
        valor_final = saldo_decimal * valor_hora_seca * 1.60
        dsr = valor_final * 0.25 # Reflexo de DSR médio

    # --- INTERFACE ---
    st.divider()
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric(
            label="Seu Saldo Final (PDF)", 
            value=saldo_exibicao, 
            delta="Horas Acumuladas", 
            delta_color="normal" if saldo_decimal >= 0 else "inverse"
        )

    with c2:
        st.subheader("💰 Estimativa Personalizada")
        st.write(f"**Valor da sua hora:** R$ {valor_hora_seca:.2f}")
        st.write(f"**Bruto Extras:** R$ {valor_final:.2f}")
        st.write(f"**DSR Estimado:** R$ {dsr:.2f}")

    with c3:
        total_receber = valor_final + dsr
        st.metric("Total Estimado a Receber", f"R$ {total_receber:.2f}")
        
    st.info(f"Cálculo realizado com base no salário de R$ {salario_informado:,.2f} informado lateralmente.")
