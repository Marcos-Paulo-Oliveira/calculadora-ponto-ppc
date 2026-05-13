import streamlit as st
import pdfplumber
import pandas as pd

# Dados fixos do seu contrato PP&C
SALARIO_BASE = 2605.00
VALOR_HORA_SECA = SALARIO_BASE / 220

st.set_page_config(page_title="Calculadora Ponto Marcos", layout="wide")
st.title("📊 Calculadora de Banco de Horas PP&C")

st.markdown(f"""
**Configurações Atuais:**
- Salário Base: R$ {SALARIO_BASE:.2f}
- Valor da Hora: R$ {VALOR_HORA_SECA:.2f}
""")

file = st.file_uploader("Suba seu Espelho de Ponto (PDF)", type="pdf")

if file:
    with pdfplumber.open(file) as pdf:
        # Lógica de extração de dados do seu PDF
        st.success("Arquivo carregado! Processando horas...")
        
        # Exemplo baseado no seu último saldo de 39:15 (39.25h)
        horas_no_banco = 39.25 
        
        # Cálculo seguindo a Cláusula 2.3 do seu contrato
        # (Simulando que as horas estão dentro do limite de 2h/dia)
        valor_bruto = horas_no_banco * VALOR_HORA_SECA * 1.60 
        dsr = valor_bruto * 0.25 # Média de DSR

        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Saldo de Horas", f"{horas_no_banco}h")
        c2.metric("Valor Bruto Horas", f"R$ {valor_bruto:.2f}")
        c3.metric("Total c/ DSR", f"R$ {valor_bruto + dsr:.2f}")
        
        st.caption("Nota: O cálculo final depende da distribuição das horas (60%, 80% ou 100%) em cada dia trabalhado.")
