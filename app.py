import streamlit as st
import pdfplumber
import re
from datetime import datetime

# Configurações do Contrato Marcos (PP&C)
SALARIO_BASE = 2605.00
VALOR_HORA_SECA = SALARIO_BASE / 220
DATA_INICIO_BANCO = datetime(2026, 4, 1) # Início do novo quadrimestre

def converter_hora_decimal(h_str):
    if not h_str or ':' not in h_str: return 0.0
    try:
        # Trata casos de saldo negativo no texto
        multiplicador = -1 if '-' in h_str else 1
        h_str = h_str.replace('-', '')
        h, m = map(int, h_str.strip().split(':'))
        return (h + (m / 60)) * multiplicador
    except: return 0.0

st.set_page_config(page_title="Calculadora Ponto PP&C", page_icon="📊", layout="wide")
st.title("📊 Calculadora de Saldo Quadrimestral (Pós-01/04)")

arquivo = st.file_uploader("Suba seu Espelho de Ponto PDF", type="pdf")

if arquivo:
    with pdfplumber.open(arquivo) as pdf:
        dados_filtrados = []
        texto_total = ""
        
        for page in pdf.pages:
            tabela = page.extract_table()
            texto_total += page.extract_text() + "\n"
            if tabela:
                for linha in tabela[1:]:
                    try:
                        # Tenta extrair a data da primeira coluna (ex: "16 Seg." ou "01 Qua.")
                        dia_mes = linha[0].split()[0]
                        # O PDF não traz o ano na linha, então assumimos 2026 baseado no cabeçalho
                        data_linha = datetime.strptime(f"{dia_mes}/04/2026", "%d/%m/%Y")
                        
                        # FILTRO CRUCIAL: Só aceita dados a partir de 01/04/2026
                        if data_linha >= DATA_INICIO_BANCO:
                            dados_filtrados.append(linha)
                    except:
                        continue

    # --- BUSCA PELO SALDO ACUMULADO NO TEXTO ---
    # Procuramos a linha "Saldo" que contém o valor entre parênteses (o acumulado)
    match_saldo = re.findall(r"Saldo\s+[-\d:]+\s+\(([-\d:]+)\)", texto_total)
    saldo_acumulado_str = match_saldo[-1] if match_saldo else "00:00"
    saldo_decimal = converter_hora_decimal(saldo_acumulado_str)

    # --- CÁLCULO FINANCEIRO (REGRA DE SEGURANÇA) ---
    # Se o saldo for negativo, o valor a receber é ZERO.
    valor_final = 0.0
    dsr = 0.0
    
    if saldo_decimal > 0:
        # Aplicamos a média de 60% (podemos refinar para separar 80% se houver horas no dia)
        valor_final = saldo_decimal * VALOR_HORA_SECA * 1.60
        dsr = valor_final * 0.25

    # --- INTERFACE ---
    st.divider()
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("📈 Status do Banco de Horas")
        if saldo_decimal < 0:
            st.error(f"Saldo Atual: {saldo_acumulado_str} (Negativo)")
            st.info("No momento você não possui horas a receber. O saldo negativo deve ser compensado com trabalho.")
        else:
            st.success(f"Saldo Atual: {saldo_acumulado_str} (Positivo)")
            st.balloons()

    with c2:
        st.subheader("💰 Estimativa para Agosto/2026")
        st.metric("Valor Bruto + DSR", f"R$ {valor_final + dsr:.2f}")
        st.caption("Cálculo bloqueado para saldos negativos ou anteriores a 01/04.")

    if st.checkbox("Ver log de processamento"):
        st.write(f"Data de corte aplicada: {DATA_INICIO_BANCO.strftime('%d/%m/%Y')}")
        st.write(f"Saldo identificado no rodapé: {saldo_acumulado_str}")
