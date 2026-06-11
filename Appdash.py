import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone, timedelta
import time
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Painel Operacional - LMG 19", layout="wide", page_icon="📈")

# ── Inicializa session_state ─────────────────────────────
if "aba_atual" not in st.session_state:
    st.session_state.aba_atual = 0
if "apresentacao_ativa" not in st.session_state:
    st.session_state.apresentacao_ativa = False

# ── Cabeçalho com data e hora ────────────────────────────
col_titulo, col_hora = st.columns([3, 1])
with col_titulo:
    st.title("📊 Painel Operacional")
with col_hora:
    fuso_brasilia = timezone(timedelta(hours=-3))
    agora = datetime.now(fuso_brasilia).strftime("%d/%m/%Y %H:%M")
    st.markdown(f"""
    <div style="text-align:right; padding-top:20px; color:#888; font-size:14px;">
        🕐 Atualizado em<br><b style="color:#ccc">{agora}</b>
    </div>
    """, unsafe_allow_html=True)

# ── Função de conexão Google Sheets ─────────────────────
@st.cache_data(ttl=300)
def carregar_indicadores():
    try:
        SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=SCOPES)
        client = gspread.authorize(creds)
        planilha = client.open_by_key('1TAe_Bgqhjw_o8-xUHqE0T1CCPkymEMSugoSQCkuGP_0')
        aba = planilha.sheet1
        dados = aba.get_all_records()
        df = pd.DataFrame(dados)
        df.columns = df.columns.str.strip()
        df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Data'])
        return df, None
    except Exception as e:
        return None, str(e)

# ── Sidebar ─────────────────────────────────────────────
with st.sidebar:
    st.header("📁 Carregar Relatórios")
    st.divider()

    st.markdown("**📦 Produtividade**")
    uploaded_prod = st.file_uploader("Upload CSV de Produção", type=["csv"], key="prod")
    if uploaded_prod:
        st.success("✅ Produção carregada!")
        st.caption(f"📄 {uploaded_prod.name}")

    st.divider()

    st.markdown("**🔍 Auditoria(Conferência)**")
    uploaded_audit = st.file_uploader("Upload CSV de Gestão Audit", type=["csv"], key="audit")
    if uploaded_audit:
        st.success("✅ Auditoria carregada!")
        st.caption(f"📄 {uploaded_audit.name}")

    st.divider()

    # ── Controle de Apresentação ─────────────────────────
    st.markdown("**🎬 Modo Apresentação**")
    intervalo = st.slider("Intervalo entre abas (s)", min_value=5, max_value=60, value=15, step=5)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("▶ Iniciar", use_container_width=True, type="primary"):
            st.session_state.apresentacao_ativa = True
    with col_btn2:
        if st.button("⏹ Parar", use_container_width=True):
            st.session_state.apresentacao_ativa = False

    if st.session_state.apresentacao_ativa:
        abas_nomes = ["📦 Produção hora a hora", "🔍 Auditoria por Operador", "📊 Indicadores Operacionais"]
        aba_exibindo = abas_nomes[st.session_state.aba_atual]
        st.success(f"🟢 Ativo — {aba_exibindo}")
    else:
        st.caption("🔴 Apresentação pausada")

    st.divider()

    # ── Legenda mapa de calor ────────────────────────────
    st.markdown("**🎨 Legenda — Produção/Hora**")
    st.markdown("""
    <div style="font-size:13px; line-height:2">
        <span style="background:#1a7a1a;color:white;padding:2px 8px;border-radius:4px">■</span> ≥ 1100 — Meta atingida<br>
        <span style="background:#e6a817;color:white;padding:2px 8px;border-radius:4px">■</span> 700–1099 — Próximo da meta<br>
        <span style="background:#cc5500;color:white;padding:2px 8px;border-radius:4px">■</span> 300–699 — Abaixo da meta<br>
        <span style="background:#990000;color:white;padding:2px 8px;border-radius:4px">■</span> 1–299 — Muito abaixo<br>
        <span style="background:#2d2d2d;color:#2d2d2d;padding:2px 8px;border-radius:4px">■</span> 0 — Sem produção
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("**🎨 Legenda — Média(Tconferência)**")
    st.markdown("""
    <div style="font-size:13px; line-height:2">
        <span style="background:#1a7a1a;color:white;padding:2px 8px;border-radius:4px">■</span> &lt; 06:00 — Ótimo<br>
        <span style="background:#e6a817;color:white;padding:2px 8px;border-radius:4px">■</span> 06:00–07:00 — Moderado<br>
        <span style="background:#990000;color:white;padding:2px 8px;border-radius:4px">■</span> &gt; 07:00 — Abaixo da meta
    </div>
    """, unsafe_allow_html=True)

# ── Navegação manual entre abas (botões) ─────────────────
ABAS = ["📦 Produção hora a hora", "🔍 Auditoria por Operador", "📊 Indicadores Operacionais"]

col_nav1, col_nav2, col_nav3 = st.columns(3)
with col_nav1:
    if st.button(ABAS[0], use_container_width=True,
                 type="primary" if st.session_state.aba_atual == 0 else "secondary"):
        st.session_state.aba_atual = 0
        st.session_state.apresentacao_ativa = False
with col_nav2:
    if st.button(ABAS[1], use_container_width=True,
                 type="primary" if st.session_state.aba_atual == 1 else "secondary"):
        st.session_state.aba_atual = 1
        st.session_state.apresentacao_ativa = False
with col_nav3:
    if st.button(ABAS[2], use_container_width=True,
                 type="primary" if st.session_state.aba_atual == 2 else "secondary"):
        st.session_state.aba_atual = 2
        st.session_state.apresentacao_ativa = False

st.divider()

# ════════════════════════════════════════════════════════
# ABA 1 — PRODUÇÃO
# ════════════════════════════════════════════════════════
if st.session_state.aba_atual == 0:
    if uploaded_prod is not None:
        df = pd.read_csv(uploaded_prod)

        df['ID'] = df['User Email'].str.extract(r'\[(\w+)\]', expand=False).str.upper()
        df['Nome'] = df['User Email'].str.replace(r'\[.*?\]', '', regex=True).str.strip().str.title()
        df['ID'] = df['ID'].fillna(df['User Email'])

        hora_cols = [c for c in df.columns if c.startswith('202')]
        hora_rename = {c: pd.to_datetime(c).strftime('%H:%M') for c in hora_cols}
        df = df.rename(columns=hora_rename)
        horas = list(hora_rename.values())

        df_consolidado = df.groupby(['ID', 'Nome'])[horas + ['Total']].sum().reset_index()
        horas_sorted = sorted(horas)
        df_final = df_consolidado[['Nome', 'Total'] + horas_sorted]
        df_final = df_final.sort_values('Total', ascending=False).reset_index(drop=True)

        horas_com_dados = [h for h in horas_sorted if df_final[h].sum() > 0]
        df_final = df_final[['Nome', 'Total'] + horas_com_dados]

        subtotal = df_final[horas_com_dados + ['Total']].sum().to_frame().T
        subtotal['Nome'] = '🔢 Subtotal'
        subtotal = subtotal[['Nome', 'Total'] + horas_com_dados]
        df_com_subtotal = pd.concat([df_final, subtotal], ignore_index=True)

        def colorir_meta(val):
            if val == 0:
                return 'background-color: #2d2d2d; color: #2d2d2d'
            elif val >= 1100:
                return 'background-color: #1a7a1a; color: white'
            elif val >= 700:
                return 'background-color: #e6a817; color: white'
            elif val >= 300:
                return 'background-color: #cc5500; color: white'
            else:
                return 'background-color: #990000; color: white'

        def colorir_subtotal(row):
            if row['Nome'] == '🔢 Subtotal':
                return ['background-color: #1a3a5c; color: white; font-weight: bold'] * len(row)
            return [''] * len(row)

        styled = (
            df_com_subtotal.style
            .map(colorir_meta, subset=horas_com_dados)
            .apply(colorir_subtotal, axis=1)
        )

        st.subheader("📋 Produção hora a hora por operador")
        st.dataframe(styled, use_container_width=True, hide_index=True)

        st.subheader("🏆 Top 3 Operadores")
        top3 = df_final.nlargest(3, 'Total').reset_index(drop=True)
        col2, col1, col3 = st.columns(3)
        config = {
            0: {'medalha': '🥇', 'cor': '#FFD700', 'altura': '250px', 'fonte': '32px'},
            1: {'medalha': '🥈', 'cor': '#C0C0C0', 'altura': '200px', 'fonte': '26px'},
            2: {'medalha': '🥉', 'cor': '#CD7F32', 'altura': '170px', 'fonte': '22px'},
        }
        colunas = [col2, col1, col3]
        posicoes = [1, 0, 2]
        for col, pos in zip(colunas, posicoes):
            if pos < len(top3):
                nome = top3.loc[pos, 'Nome']
                total = int(top3.loc[pos, 'Total'])
                c = config[pos]
                with col:
                    st.markdown(f"""
                    <div style="background-color:{c['cor']};border-radius:16px;padding:24px 16px;
                    text-align:center;min-height:{c['altura']};display:flex;flex-direction:column;
                    justify-content:center;align-items:center;box-shadow:0 6px 16px rgba(0,0,0,0.4);
                    margin-top:{'0px' if pos==0 else '40px' if pos==1 else '60px'};">
                        <div style="font-size:48px;margin-bottom:8px">{c['medalha']}</div>
                        <div style="font-size:{c['fonte']};font-weight:bold;color:#1a1a1a;margin-bottom:8px">{nome}</div>
                        <div style="font-size:36px;font-weight:bold;color:#1a1a1a">{total:,}</div>
                        <div style="font-size:13px;color:#444;margin-top:4px">unidades</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("👆 Faça o upload do CSV de Produção na barra lateral.")

# ════════════════════════════════════════════════════════
# ABA 2 — AUDITORIA
# ════════════════════════════════════════════════════════
elif st.session_state.aba_atual == 1:
    if uploaded_audit is not None:
        df2 = pd.read_csv(uploaded_audit)

        df2['Nome'] = df2['Validation Operator'].str.replace(r'\[.*?\]', '', regex=True).str.strip().str.title()
        df2['Start'] = pd.to_datetime(df2['Validation Start Time'])
        df2['End'] = pd.to_datetime(df2['Validation End Time'])
        df2['Tempo_seg'] = (df2['End'] - df2['Start']).dt.total_seconds()

        total_pacotes = df2['Total Scanned Orders'].sum()

        df_audit = df2.groupby('Nome').agg(
            Pacotes=('Total Scanned Orders', 'sum'),
            Rotas=('AT/TO', 'count'),
            Tempo_total_seg=('Tempo_seg', 'sum')
        ).reset_index()

        df_audit['Média'] = pd.to_datetime(
            df_audit['Tempo_total_seg'] / df_audit['Rotas'], unit='s'
        ).dt.strftime('%M:%S')

        df_audit['% Processado'] = (df_audit['Pacotes'] / total_pacotes * 100).round(0).astype(int).astype(str) + '%'

        df2 = df2.sort_values(['Nome', 'Start'])
        df2['Prox_Start'] = df2.groupby('Nome')['Start'].shift(-1)
        df2['Ociosidade_seg'] = (df2['Prox_Start'] - df2['End']).dt.total_seconds()
        df2['Ociosidade_seg'] = df2['Ociosidade_seg'].clip(lower=0)

        oci = df2.groupby('Nome')['Ociosidade_seg'].mean().reset_index()
        oci.columns = ['Nome', 'Media_Oci_seg']

        df_audit = df_audit.merge(oci, on='Nome', how='left')
        df_audit['Média Ociosidade'] = pd.to_datetime(
            df_audit['Media_Oci_seg'].fillna(0), unit='s'
        ).dt.strftime('%M:%S')
        df_audit = df_audit.drop(columns=['Media_Oci_seg'])
        df_audit = df_audit[['Nome', 'Pacotes', 'Rotas', 'Média', '% Processado', 'Média Ociosidade']]
        df_audit = df_audit.sort_values('Pacotes', ascending=False).reset_index(drop=True)

        def colorir_media(val):
            try:
                minutos, segundos = map(int, val.split(':'))
                total_seg = minutos * 60 + segundos
                if total_seg < 360:
                    return 'background-color: #1a7a1a; color: white'
                elif total_seg <= 420:
                    return 'background-color: #e6a817; color: white'
                else:
                    return 'background-color: #990000; color: white'
            except:
                return ''

        st.subheader("📋 Desempenhos - Auditoria")

        media_geral_seg = df2['Tempo_seg'].sum() / len(df2)
        media_geral_fmt = f"{int(media_geral_seg // 60):02d}:{int(media_geral_seg % 60):02d}"
        oci_geral_seg = df2['Ociosidade_seg'].mean()
        oci_geral_fmt = f"{int(oci_geral_seg // 60):02d}:{int(oci_geral_seg % 60):02d}"
        total_revalidacoes = int(df2['Revalidated Count'].sum())

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(label="⏱️ Média Geral por Rota", value=media_geral_fmt)
        with c2:
            st.metric(label="💤 Média Geral de Ociosidade", value=oci_geral_fmt)
        with c3:
            st.metric(label="🔁 Total de Reconferências", value=total_revalidacoes)

        st.divider()
        st.subheader("🏆 Rankings")

        rank_col1, espaco, rank_col2 = st.columns([1, 0.1, 1])
        config_rank = {
            0: {'medalha': '🥇', 'cor': '#FFD700', 'altura': '220px', 'fonte': '20px'},
            1: {'medalha': '🥈', 'cor': '#C0C0C0', 'altura': '180px', 'fonte': '17px'},
            2: {'medalha': '🥉', 'cor': '#CD7F32', 'altura': '150px', 'fonte': '15px'},
        }

        with rank_col1:
            st.markdown("**📦 Top 3 — Mais Pacotes**")
            top_pacotes = df_audit.nlargest(3, 'Pacotes').reset_index(drop=True)
            p2, p1, p3 = st.columns(3)
            for col, pos in zip([p2, p1, p3], [1, 0, 2]):
                if pos < len(top_pacotes):
                    c = config_rank[pos]
                    with col:
                        st.markdown(f"""
                        <div style="background-color:{c['cor']};border-radius:12px;padding:16px 8px;
                        text-align:center;min-height:{c['altura']};display:flex;flex-direction:column;
                        justify-content:center;align-items:center;box-shadow:0 4px 10px rgba(0,0,0,0.3);
                        margin-top:{'0px' if pos==0 else '30px' if pos==1 else '50px'};">
                            <div style="font-size:32px">{c['medalha']}</div>
                            <div style="font-size:{c['fonte']};font-weight:bold;color:#1a1a1a;margin:6px 0">
                                {top_pacotes.loc[pos,'Nome']}
                            </div>
                            <div style="font-size:22px;font-weight:bold;color:#1a1a1a">
                                {int(top_pacotes.loc[pos,'Pacotes']):,}
                            </div>
                            <div style="font-size:11px;color:#444">pacotes</div>
                        </div>
                        """, unsafe_allow_html=True)

        with rank_col2:
            st.markdown("**⏱️ Top 3 — Melhor Média**")
            df_audit['Média_seg'] = df_audit['Média'].apply(
                lambda v: int(v.split(':')[0]) * 60 + int(v.split(':')[1])
            )
            top_media = df_audit.nsmallest(3, 'Média_seg').reset_index(drop=True)
            m2, m1, m3 = st.columns(3)
            for col, pos in zip([m2, m1, m3], [1, 0, 2]):
                if pos < len(top_media):
                    c = config_rank[pos]
                    with col:
                        st.markdown(f"""
                        <div style="background-color:{c['cor']};border-radius:12px;padding:16px 8px;
                        text-align:center;min-height:{c['altura']};display:flex;flex-direction:column;
                        justify-content:center;align-items:center;box-shadow:0 4px 10px rgba(0,0,0,0.3);
                        margin-top:{'0px' if pos==0 else '30px' if pos==1 else '50px'};">
                            <div style="font-size:32px">{c['medalha']}</div>
                            <div style="font-size:{c['fonte']};font-weight:bold;color:#1a1a1a;margin:6px 0">
                                {top_media.loc[pos,'Nome']}
                            </div>
                            <div style="font-size:22px;font-weight:bold;color:#1a1a1a">
                                {top_media.loc[pos,'Média']}
                            </div>
                            <div style="font-size:11px;color:#444">min/rota</div>
                        </div>
                        """, unsafe_allow_html=True)
            df_audit = df_audit.drop(columns=['Média_seg'])

        st.divider()
        st.subheader("📋 Performance da Equipe")
        df_exibir = df_audit.drop(columns=['Média_seg'], errors='ignore')
        styled2 = df_exibir.style.map(colorir_media, subset=['Média'])
        st.dataframe(styled2, use_container_width=True, hide_index=True)

    else:
        st.info("👆 Faça o upload do CSV do Audit na barra lateral.")

# ════════════════════════════════════════════════════════
# ABA 3 — INDICADORES OPERACIONAIS (Google Sheets)
# ════════════════════════════════════════════════════════
elif st.session_state.aba_atual == 2:

    # Nomes dos dias em português
    DIAS_PT = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta', 5: 'Sábado', 6: 'Domingo'}

    # Colunas de indicadores da planilha
    COLUNAS_INDICADORES = [
        'Line Haul - Qtd pacotes',
        'Line Haul - Veículos',
        'Roteirização - Qtd rotas',
        'Processamento - Qtd pacotes',
        'Processsamento - Missorting',
        'Expedição - Qtd pacotes',
        'Pessoas - Produtividade',
        'Pessoas - Abs',
        'Erros Processo',
        'Reversa - RTS',
        'Reversa - On Hold',
        'Avarias',
        'Lost',
    ]

    st.subheader("📊 Indicadores Operacionais — Semana Atual")

    # Botão de atualizar
    col_refresh, col_info = st.columns([1, 5])
    with col_refresh:
        if st.button("🔄 Atualizar dados", type="primary"):
            st.cache_data.clear()

    df_ind, erro = carregar_indicadores()

    if erro:
        st.error(f"❌ Erro ao conectar com Google Sheets: {erro}")
    elif df_ind is None or df_ind.empty:
        st.info("📋 Nenhum dado encontrado na planilha.")
    else:
        # Filtra semana atual (segunda a domingo)
        hoje = datetime.now(timezone(timedelta(hours=-3))).date()
        inicio_semana = hoje - timedelta(days=hoje.weekday())  # Segunda-feira
        fim_semana = inicio_semana + timedelta(days=6)         # Domingo

        df_semana = df_ind[
            (df_ind['Data'].dt.date >= inicio_semana) &
            (df_ind['Data'].dt.date <= fim_semana)
        ].copy()

        # Garante que só usa colunas que existem no dataframe
        colunas_existentes = [c for c in COLUNAS_INDICADORES if c in df_ind.columns]

        # ── Cards resumo da semana ───────────────────────
        if not df_semana.empty:
            st.markdown(f"**📅 Semana: {inicio_semana.strftime('%d/%m/%Y')} a {fim_semana.strftime('%d/%m/%Y')}**")
            st.divider()

            # Cards com totais da semana
            cols_cards = st.columns(4)
            cards_principais = [
                ('Line Haul - Qtd pacotes', '📦 Line Haul', '#1a3a5c'),
                ('Processamento - Qtd pacotes', '⚙️ Processamento', '#1a5c1a'),
                ('Expedição - Qtd pacotes', '🚚 Expedição', '#5c3a1a'),
                ('Erros Processo', '⚠️ Erros', '#5c1a1a'),
            ]
            for i, (col_nome, label, cor) in enumerate(cards_principais):
                if col_nome in df_semana.columns:
                    valor = pd.to_numeric(df_semana[col_nome], errors='coerce').sum()
                    with cols_cards[i]:
                        st.markdown(f"""
                        <div style="background:{cor};border-radius:12px;padding:20px;text-align:center;
                        box-shadow:0 4px 10px rgba(0,0,0,0.3);margin-bottom:16px;">
                            <div style="font-size:14px;color:#aaa;margin-bottom:6px">{label}</div>
                            <div style="font-size:32px;font-weight:bold;color:white">{int(valor):,}</div>
                            <div style="font-size:11px;color:#aaa;margin-top:4px">total na semana</div>
                        </div>
                        """, unsafe_allow_html=True)

            st.divider()

        # ── Tabela estilo Toyota por dia da semana ───────
        st.markdown("**📋 Detalhamento por Dia da Semana**")

        # Monta estrutura da tabela com todos os dias da semana
        dias_semana = []
        for i in range(6):  # Segunda a Sábado
            dia = inicio_semana + timedelta(days=i)
            dias_semana.append(dia)

        linhas = []
        for dia in dias_semana:
            linha = {'Dia': DIAS_PT[dia.weekday()], 'Data': dia.strftime('%d/%m')}
            dados_dia = df_semana[df_semana['Data'].dt.date == dia]
            for col in colunas_existentes:
                if not dados_dia.empty:
                    val = pd.to_numeric(dados_dia[col], errors='coerce').sum()
                    linha[col.strip()] = int(val) if val > 0 else '—'
                else:
                    linha[col.strip()] = '—'
            linhas.append(linha)

        # Linha de média semanal
        linha_media = {'Dia': '📊 Média Semanal', 'Data': ''}
        for col in colunas_existentes:
            vals = pd.to_numeric(df_semana[col], errors='coerce')
            dias_com_dados = (vals > 0).sum()
            if dias_com_dados > 0:
                linha_media[col.strip()] = round(vals.sum() / dias_com_dados, 1)
            else:
                linha_media[col.strip()] = '—'
        linhas.append(linha_media)

        df_tabela = pd.DataFrame(linhas)

        # Estilo da tabela
        def estilo_tabela(row):
            if row['Dia'] == '📊 Média Semanal':
                return ['background-color: #1a3a5c; color: white; font-weight: bold'] * len(row)
            # Destaca o dia de hoje
            hoje_fmt = hoje.strftime('%d/%m')
            if row['Data'] == hoje_fmt:
                return ['background-color: #2d4a1a; color: white'] * len(row)
            return [''] * len(row)

        styled_tabela = df_tabela.style.apply(estilo_tabela, axis=1)
        st.dataframe(styled_tabela, use_container_width=True, hide_index=True)

        st.caption("🟦 Média Semanal   🟩 Dia atual   — Sem dados")

        # ── Histórico completo (expansível) ─────────────
        st.divider()
        with st.expander("📂 Ver histórico completo"):
            df_hist = df_ind.copy()
            df_hist['Data'] = df_hist['Data'].dt.strftime('%d/%m/%Y')
            cols_hist = ['Data'] + colunas_existentes
            df_hist = df_hist[cols_hist].sort_values('Data', ascending=False)
            st.dataframe(df_hist, use_container_width=True, hide_index=True)

# ── Auto-avanço de abas ──────────────────────────────────
if st.session_state.apresentacao_ativa:
    time.sleep(intervalo)
    st.session_state.aba_atual = (st.session_state.aba_atual + 1) % len(ABAS)
    st.rerun()
