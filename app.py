import streamlit as st
import pdfplumber
import re

def converter_hora_decimal(h_str):
    if not h_str: return 0.0
    try:
        multiplicador = -1 if '-' in h_str else 1
        limpo = re.sub(r'[^\d:]', '', h_str)
        if ':' not in limpo: return 0.0
        h, m = map(int, limpo.split(':'))
        return (h + (m / 60)) * multiplicador
    except: return 0.0

st.set_page_config(page_title="Calculadora Ponto PP&C", page_icon="📊", layout="wide")
st.title("📊 Calculadora de Banco de Horas Geral - PP&C")

# --- BARRA LATERAL ---
st.sidebar.header("Configurações")
salario_texto = st.sidebar.text_input("Salário Bruto (R$):", value="2605.00")
try:
    salario_informado = float(salario_texto.replace(',', '.'))
except:
    salario_informado = 0.0
valor_hora_seca = salario_informado / 220 if salario_informado > 0 else 0.0

arquivo = st.file_uploader("Suba seu Espelho de Ponto PDF", type="pdf")

if arquivo:
    with pdfplumber.open(arquivo) as pdf:
        texto_total = ""
        # Lemos apenas as páginas do espelho (geralmente as 2 primeiras), 
        # ignorando a última página de log de assinatura
        paginas_uteis = pdf.pages[:-1] if len(pdf.pages) > 1 else pdf.pages
        for page in paginas_uteis:
            texto_total += page.extract_text() + "\n"

    # --- NOVA LÓGICA DE CAPTURA (Focada na palavra Saldo) ---
    # Busca a palavra Saldo e pega o primeiro padrão de horas (00:00 ou -00:00) que vier depois
    # No caso da Larissa, ele deve achar "04:22"
    match_saldo = re.findall(r"Saldo\s+([-\d:]+)", texto_total, re.IGNORECASE)
    
    if match_saldo:
        # Pegamos o último "Saldo" mencionado antes dos logs de assinatura
        saldo_exibicao = match_saldo[-1].strip()
    else:
        # Se não achar por texto, tenta o padrão de parênteses mas só nas páginas iniciais
        match_parenteses = re.findall(r"\((\s*[-\d:]+\s*)\)", texto_total)
        saldo_exibicao = match_parenteses[-1].strip() if match_parenteses else "00:00"
    
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
            label="Saldo Identificado", 
            value=saldo_exibicao, 
            delta="Horas Acumuladas", 
            delta_color="normal" if saldo_decimal >= 0 else "inverse"
        )

    with c2:
        st.subheader("💰 Resumo Financeiro")
        st.write(f"**Salário:** R$ {salario_informado:,.2f}")
        st.write(f"**Valor da Hora:** R$ {valor_hora_seca:.2f}")

    with c3:
        total_com_dsr = valor_final + dsr
        st.metric("Total Estimado (60% + DSR)", f"R$ {total_com_dsr:.2f}")

    if st.checkbox("Verificar texto lido"):
        st.text(texto_total)
