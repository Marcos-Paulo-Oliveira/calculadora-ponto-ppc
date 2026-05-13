import streamlit as st
import pdfplumber
import re

# Configurações do Contrato Marcos (PP&C)
SALARIO_BASE = 2605.00
VALOR_HORA_SECA = SALARIO_BASE / 220

def converter_hora_decimal(h_str):
    if not h_str or ':' not in h_str: return 0.0
    try:
        h, m = map(int, h_str.strip().split(':'))
        return h + (m / 60)
    except: return 0.0

st.set_page_config(page_title="Calculadora Ponto PP&C", page_icon="📊", layout="wide")

st.title("📊 Analisador Inteligente de Banco de Horas")
st.markdown(f"**Contrato:** Regra Escalonada (60%/80%/100%) | **Salário:** R$ {SALARIO_BASE:.2f}")

arquivo = st.file_uploader("Suba seu Espelho de Ponto PDF (Pontotel)", type="pdf")

if arquivo:
    with pdfplumber.open(arquivo) as pdf:
        texto_completo = ""
        for page in pdf.pages:
            texto_completo += page.extract_text() + "\n"
    
    # --- LÓGICA DE EXTRAÇÃO VIA REGEX (Busca por padrões no texto) ---
    # Procuramos o padrão de horas (00:00) que aparecem logo após os termos de extra
    def extrair_horas(termo, texto):
        # Procura o termo e pega o primeiro padrão HH:MM que aparecer na sequência
        padrao = re.compile(rf"{termo}.*?(\d{{2}}:\d{{2}})", re.DOTALL)
        matches = padrao.findall(texto)
        return sum(converter_hora_decimal(m) for m in matches)

    # Extraindo totais do período do PDF
    h_60 = extrair_horas("H. Extra 60%", texto_completo)
    h_80 = extrair_horas("H. Extra 80%", texto_completo)
    h_100 = extrair_horas("100%", texto_completo) # Para feriados/domingos
    atrasos = extrair_horas("Atraso", texto_completo)

    # --- CÁLCULOS FINANCEIROS ---
    valor_60 = h_60 * VALOR_HORA_SECA * 1.60
    valor_80 = h_80 * VALOR_HORA_SECA * 1.80
    valor_100 = h_100 * VALOR_HORA_SECA * 2.00
    
    bruto_extras = valor_60 + valor_80 + valor_100
    # O DSR no seu caso é calculado sobre as horas extras pagas
    dsr = bruto_extras * 0.25 

    # --- INTERFACE ---
    st.divider()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Horas 60%", f"{h_60:.2f}h")
    col2.metric("Horas 80%", f"{h_80:.2f}h")
    col3.metric("Horas 100%", f"{h_100:.2f}h")
    col4.metric("Atrasos (Abater)", f"-{atrasos:.2f}h", delta_color="inverse")

    st.divider()
    
    res1, res2 = st.columns(2)
    saldo_total_h = h_60 + h_80 + h_100 - atrasos
    
    res1.subheader("💰 Resumo Financeiro")
    res1.write(f"**Valor Bruto das Extras:** R$ {bruto_extras:.2f}")
    res1.write(f"**Reflexo DSR (Estimado):** R$ {dsr:.2f}")
    res1.success(f"### Total a Receber: R$ {bruto_extras + dsr:.2f}")
    
    res2.subheader("📅 Projeção Quadrimestral")
    res2.info(f"Seu saldo líquido atual é de **{saldo_total_h:.2f} horas**. No fechamento do quadrimestre (Julho), este será o valor base para conversão em folha.")

    if st.checkbox("Visualizar texto extraído do PDF"):
        st.text(texto_completo)
