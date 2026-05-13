import streamlit as st
import pdfplumber
import pandas as pd
import re

# Configurações do seu contrato PP&C
SALARIO_BASE = 2605.00
VALOR_HORA_SECA = SALARIO_BASE / 220

def converter_para_decimal(tempo_str):
    if not tempo_str or ':' not in str(tempo_str): return 0.0
    try:
        h, m = map(int, str(tempo_str).strip().split(':'))
        return h + (m / 60)
    except: return 0.0

st.set_page_config(page_title="Calculadora Auditoria PP&C", layout="wide")
st.title("📊 Analisador de Banco de Horas (Regra Escalonada)")

arquivo = st.file_uploader("Suba seu Espelho de Ponto (PDF)", type="pdf")

if arquivo:
    with pdfplumber.open(arquivo) as pdf:
        dados_completos = []
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                dados_completos.extend(table[1:]) # Pula o cabeçalho
        
        # Criando DataFrame com as colunas do Pontotel
        df = pd.DataFrame(dados_completos)
        
        # Identificando as horas na coluna de 'Apontamento' (Geralmente a 7ª ou 8ª coluna)
        # Vamos buscar por linhas que contenham "H. Extra 60%"
        total_60 = 0.0
        total_80 = 0.0
        total_100 = 0.0

        for row in dados_completos:
            linha_texto = " ".join([str(item) for item in row if item])
            
            # Busca valores de horas (ex: 01:30) próximos aos termos de extra
            matches = re.findall(r'(\d{2}:\d{2})', linha_texto)
            
            if "H. Extra 60%" in linha_texto and matches:
                total_60 += converter_para_decimal(matches[0])
            elif "H. Extra 80%" in linha_texto and matches:
                total_80 += converter_para_decimal(matches[0])
            elif "100%" in linha_texto and matches:
                total_100 += converter_para_decimal(matches[0])

        # Cálculos Financeiros
        valor_60 = total_60 * VALOR_HORA_SECA * 1.60
        valor_80 = total_80 * VALOR_HORA_SECA * 1.80
        valor_100 = total_100 * VALOR_HORA_SECA * 2.00
        
        bruto_total = valor_60 + valor_80 + valor_100
        dsr = bruto_total * 0.25 # Reflexo médio de DSR conforme sua folha

        st.subheader("Análise Detalhada do Período")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Horas 60% (Até 2h/dia)", f"{total_60:.2f}h")
        c2.metric("Horas 80% (>2h/dia)", f"{total_80:.2f}h")
        c3.metric("Horas 100% (FDS/Fer)", f"{total_100:.2f}h")
        c4.metric("Saldo Total Horas", f"{total_60 + total_80 + total_100:.2f}h")

        st.divider()
        st.subheader("Estimativa Financeira para o Fechamento")
        
        res_c1, res_c2 = st.columns(2)
        res_c1.info(f"**Valor Bruto das Horas:** R$ {bruto_total:.2f}")
        res_c2.success(f"**Total com DSR (Estimado):** R$ {bruto_total + dsr:.2f}")
        
        st.caption(f"Cálculos baseados no seu salário de R$ {SALARIO_BASE:.2f} e nas regras do Acordo Quadrimestral assinado em Abril/2026.")
