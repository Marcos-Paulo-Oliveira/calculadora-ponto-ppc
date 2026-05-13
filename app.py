import streamlit as st
import pdfplumber
import re

def converter_hora_decimal(h_str):
    if not h_str: return 0.0
    try:
        # Detecta se é negativo analisando o símbolo de menos
        multiplicador = -1 if '-' in h_str else 1
        # Mantém apenas números e os dois pontos
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
        for page in pdf.pages:
            texto_total += page.extract_text() + "\n"

    # --- NOVA LÓGICA DE CAPTURA (O SEGREDO) ---
    # 1. Primeiro, tentamos achar o valor dentro do parênteses da linha que contém "Saldo"
    # 2. Se falhar, pegamos o último valor entre parênteses do documento todo (padrão do Pontotel)
    padrão_saldo_linha = re.findall(r"Saldo.*?\((\s*[-\d:]+\s*)\)", texto_total, re.DOTALL | re.IGNORECASE)
    padrão_qualquer_parenteses = re.findall(r"\((\s*[-\d:]+\s*)\)", texto_total)

    if padrão_saldo_linha:
        saldo_exibicao = padrão_saldo_linha[-1].strip()
    elif padrão_qualquer_parenteses:
        saldo_exibicao = padrão_qualquer_parenteses[-1].strip()
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
            label="Saldo Identificado", 
            value=saldo_exibicao, 
            delta="Banco de Horas", 
            delta_color="normal" if saldo_decimal >= 0 else "inverse"
        )

    with c2:
        st.subheader("💰 Cálculo")
        st.write(f"**Valor da Hora:** R$ {valor_hora_seca:.2f}")
        st.write(f"**Total Extras (Bruto):** R$ {valor_final:.2f}")

    with c3:
        total_com_dsr = valor_final + dsr
        st.metric("Total c/ DSR", f"R$ {total_com_dsr:.2f}")
        st.caption("Base: Adicional 60% + Reflexo DSR")

    if st.checkbox("Depuração: Ver texto bruto"):
        st.text(texto_total)
