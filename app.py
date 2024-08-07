import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# Configuração da página
st.set_page_config(page_title="Mira - Calculadora de GEE", layout="wide")

# Fatores de emissão para diferentes categorias
FATORES_EMISSAO = {
    'pecuária': {
        'Vaca de Corte': 99.0, 'Vaca de Leite': 102.0, 'Búfalo': 107.0, 'Frango': 6.0, 'Porcos': 21.0, 'Ovelhas': 15.0, 'Cabras': 15.0, 'Camelo': 84.0, 'Cavalos': 56.0
    },
    'culturas': {
        'Trigo': 0.69, 'Cevada': 0.54, 'Milho': 0.77, 'Aveia': 0.64, 'Centeio': 0.68, 'Arroz': 1.50, 'Milhete': 0.67, 'Sorgo': 0.61, 'Pastagem': 0.15, 'Ervilhas': 0.45,
        'Feijões': 0.62, 'Soja': 0.62, 'Batatas': 0.43, 'Beterraba de Forragem': 0.47, 'Cana-de-Açúcar': 0.73, 'Amendoim': 0.80
    },
    'fertilizante': {
        'Ureia': 1.87, 'Cal': 0.61, 'Gesso': 0.10, 'Estrume Animal': 0.20, 'Composto Orgânico': 0.20, 'Bagaço de Filtragem': 0.25, 'Vinasse': 0.10
    },
    'combustível': {
        'Óleo Diesel': 2.68, 'Gasolina': 2.31, 'Biodiesel': 1.83, 'Etanol Anidro': 1.50, 'Etanol Hidratado': 1.44, 'Gás Natural': 2.75
    },
    'eletricidade': {
        'Solar': 0.05, 'Eólica': 0.03, 'Hidrelétrica': 0.02
    }
}

def obter_fatores_emissao():
    """Recuperar fatores de emissão para todas as categorias."""
    return FATORES_EMISSAO

def calcular_emissoes(quantidade, fator):
    """Calcular emissões com base na quantidade e fator de emissão."""
    return quantidade * fator

def calcular_emissoes_totais(dados):
    """Calcular emissões totais para diferentes categorias."""
    fatores = obter_fatores_emissao()
    emissoes = {
        categoria: sum(calcular_emissoes(quantidade, fatores[categoria].get(item, 0))
                      for item, quantidade in itens.items())
        for categoria, itens in dados.items()
    }
    return emissoes

def plotar_grafico_comparacao(dados):
    """Gerar um gráfico de comparação entre emissões tradicionais e reduzidas."""
    rotulos, valores_tradicionais, valores_reduzidos = [], [], []

    def adicionar_emissoes(tipo_dict, fator_dict):
        for item, quantidade in tipo_dict.items():
            emissoes_anuais = calcular_emissoes(quantidade, fator_dict[item])
            emissoes_reduzidas = emissoes_anuais * 0.8
            rotulos.append(item)
            valores_tradicionais.append(emissoes_anuais)
            valores_reduzidos.append(emissoes_reduzidas)

    fatores = obter_fatores_emissao()
    for categoria in fatores:
        adicionar_emissoes(dados[categoria], fatores[categoria])

    fig = go.Figure()
    fig.add_trace(go.Bar(x=rotulos, y=valores_tradicionais, name='Pecuária Tradicional', marker_color='pink'))
    fig.add_trace(go.Bar(x=rotulos, y=valores_reduzidos, name='GEE Reduzido', marker_color='purple'))

    fig.update_layout(
        xaxis_title='Agricultura',
        yaxis_title='Emissões Anuais (kg CO2e)',
        barmode='group',
        legend=dict(
            orientation="h",
            entrywidth=100,
            yanchor="bottom",
            y=1.09,
            xanchor="right",
            x=1,
            tracegroupgap=10
        )
    )
    return fig

def plotar_grafico_serie_temporal(emissoes_previstas):
    """Gerar um gráfico de série temporal para emissões previstas ao longo de uma década."""
    anos = list(range(2024, 2034))
    emissoes_tradicionais = emissoes_previstas['tradicional']
    emissoes_reduzidas = emissoes_previstas['reduzido']

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=anos, y=emissoes_tradicionais, mode='lines+markers', name='Pecuária Tradicional', marker_color='pink'))
    fig.add_trace(go.Scatter(x=anos, y=emissoes_reduzidas, mode='lines+markers', name='GEE Reduzido', marker_color='purple'))

    fig.update_layout(
        xaxis_title='Ano',
        yaxis_title='Emissões (kg CO2e)',
        legend=dict(
            orientation="h",
            entrywidth=100,
            yanchor="bottom",
            y=1.09,
            xanchor="right",
            x=1,
            tracegroupgap=10
        )
    )
    return fig

def plotar_grafico_emissoes_totais(emissoes_totais):
    """Gerar um gráfico de barras para emissões totais por categoria."""
    fig = go.Figure(data=[go.Bar(x=list(emissoes_totais.keys()), y=list(emissoes_totais.values()))])
    fig.update_layout(
        title_text='Emissões Totais por Categoria',
        xaxis_title='Categoria',
        yaxis_title='Emissões Totais (kg CO2e)',
    )
    return fig

def prever_emissoes_futuras(dados):
    """Prever emissões futuras ao longo de uma década."""
    fatores = obter_fatores_emissao()
    emissoes_base = calcular_emissoes_totais(dados)

    anos = list(range(2024, 2034))
    emissoes_tradicionais = [emissoes_base['pecuária'] + emissoes_base['culturas'] + emissoes_base['fertilizante'] +
                             emissoes_base['combustível'] + emissoes_base['eletricidade']]
    emissoes_reduzidas = [e * 0.8 for e in emissoes_tradicionais]
    
    for _ in range(1, len(anos)):
        emissoes_tradicionais.append(emissoes_tradicionais[-1] * 1.05)
        emissoes_reduzidas.append(emissoes_reduzidas[-1] * 1.05)

    return {
        'tradicional': emissoes_tradicionais,
        'reduzido': emissoes_reduzidas
    }

def gerar_recomendacoes(dados):
    recomendacoes = []
    
    if 'pecuária' in dados and dados['pecuária']:
        recomendacoes.append("### Recomendações para Pecuária")
        for animal, quantidade in dados['pecuária'].items():
            if quantidade > 0:
                recomendacoes.append(f"- Considere melhorar a eficiência alimentar e o manejo de esterco para {animal}. Isso pode ajudar a reduzir as emissões de metano.")
                
    if 'culturas' in dados and dados['culturas']:
        recomendacoes.append("### Recomendações para Culturas")
        for cultura, quantidade in dados['culturas'].items():
            if quantidade > 0:
                recomendacoes.append(f"- Otimize o uso de fertilizantes e adote técnicas de agricultura de precisão para {cultura} para minimizar as emissões.")
                
    if 'fertilizante' in dados and dados['fertilizante']:
        recomendacoes.append("### Recomendações para Fertilizantes")
        for fertilizante, quantidade in dados['fertilizante'].items():
            if quantidade > 0:
                recomendacoes.append(f"- Use fertilizantes como Composto Orgânico ou Bagaço de Filtragem para reduzir as emissões em comparação com opções convencionais.")
                
    if 'combustível' in dados and dados['combustível']:
        recomendacoes.append("### Recomendações para Combustíveis")
        for combustivel, quantidade in dados['combustível'].items():
            if quantidade > 0:
                recomendacoes.append(f"- Troque para combustíveis mais limpos como Biodiesel ou reduza a dependência de Óleo Diesel para diminuir as emissões.")
                
    if 'eletricidade' in dados and dados['eletricidade']:
        recomendacoes.append("### Recomendações para Eletricidade")
        for fonte, quantidade in dados['eletricidade'].items():
            if quantidade > 0:
                recomendacoes.append(f"- Aumente o uso de fontes de energia renovável, como Solar ou Eólica, para reduzir as emissões da eletricidade consumida.")
    
    return recomendacoes

def mostrar_introducao():
    st.title("Segurança Alimentar & Agricultura Sustentável")
    st.image("assets/mira.png", use_column_width=True)
    st.write("""
    ### Mudanças Climáticas e Redução de Emissões

    A mudança climática é um dos problemas mais prementes do nosso tempo, impulsionado em grande parte pelo aumento dos gases de efeito estufa (GEE) na nossa atmosfera. Esses gases retêm calor e contribuem para o aquecimento global, o que leva a uma série de impactos ambientais, incluindo eventos climáticos extremos mais frequentes, aumento do nível do mar e distúrbios nos ecossistemas.

    A agricultura é uma contribuinte significativa para as emissões de GEE, particularmente por meio de atividades como criação de gado, produção de culturas, uso de fertilizantes, consumo de combustíveis e geração de eletricidade. Reduzir as emissões nessas áreas é crucial para mitigar a mudança climática e promover práticas sustentáveis.

    A Calculadora de GEE da Mira ajuda você a estimar suas emissões de várias atividades agrícolas e fornece insights sobre como você pode reduzir sua pegada de carbono. Ao inserir seus dados, você pode visualizar suas emissões, comparar cenários tradicionais e reduzidos de emissão e receber recomendações acionáveis para minimizar seu impacto.

    Vamos trabalhar juntos para fazer uma diferença positiva para o nosso planeta.
    """)
    
    if st.button("Inserir Seus Dados"):
        st.session_state.page = "Inserir Seus Dados"
        st.rerun()

def mostrar_entrada():
    st.title("Inserir Seus Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pecuária")
        quantidades_pecuaria = {animal: st.number_input(f"Quantidade de {animal} (cabeças)", min_value=0, value=0, key=f"pecuaria_{animal}")
                                for animal in st.multiselect("Selecione Tipos de Pecuária", options=list(FATORES_EMISSAO['pecuária'].keys()))}

        st.subheader("Culturas")
        quantidades_culturas = {cultura: st.number_input(f"Quantidade de {cultura} (ha)", min_value=0, value=0, key=f"culturas_{cultura}")
                                for cultura in st.multiselect("Selecione Tipos de Culturas", options=list(FATORES_EMISSAO['culturas'].keys()))}

    with col2:
        st.subheader("Fertilizante")
        quantidades_fertilizante = {fertilizante: st.number_input(f"Quantidade de {fertilizante} (kg)", min_value=0, value=0, key=f"fertilizante_{fertilizante}")
                                     for fertilizante in st.multiselect("Selecione Tipos de Fertilizantes", options=list(FATORES_EMISSAO['fertilizante'].keys()))}

        st.subheader("Combustível")
        quantidades_combustivel = {combustivel: st.number_input(f"Quantidade de {combustivel} (litros/m³)", min_value=0, value=0, key=f"combustível_{combustivel}")
                                    for combustivel in st.multiselect("Selecione Tipos de Combustíveis", options=list(FATORES_EMISSAO['combustível'].keys()))}

        st.subheader("Eletricidade")
        quantidades_eletricidade = {fonte: st.number_input(f"Quantidade de {fonte} (kWh)", min_value=0, value=0, key=f"eletricidade_{fonte}")
                                     for fonte in st.multiselect("Selecione Fontes de Eletricidade", options=list(FATORES_EMISSAO['eletricidade'].keys()))}
    
    if st.button("Calcular Emissões"):
        dados = {
            'pecuária': quantidades_pecuaria,
            'culturas': quantidades_culturas,
            'fertilizante': quantidades_fertilizante,
            'combustível': quantidades_combustivel,
            'eletricidade': quantidades_eletricidade
        }
        
        st.session_state.dados = dados
        st.session_state.page = "Resultado"
        st.rerun()

def mostrar_resultados():
    """Exibir os resultados dos cálculos de emissões e fornecer recomendações."""
    st.title("Resultados")
    
    if 'dados' in st.session_state:
        dados = st.session_state.dados
        emissoes_totais = calcular_emissoes_totais(dados)
        emissoes_previstas = prever_emissoes_futuras(dados)
        recomendacoes = gerar_recomendacoes(dados)
        
        # Criar um layout de grade para os gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Emissões Totais (kg CO2e):")
            st.plotly_chart(plotar_grafico_emissoes_totais(emissoes_totais), use_container_width=True)
        
        with col2:
            st.write("### Comparação de Emissões:")
            st.plotly_chart(plotar_grafico_comparacao(dados), use_container_width=True)
        
        st.write("### Emissões Previstas para a Próxima Década:")
        st.plotly_chart(plotar_grafico_serie_temporal(emissoes_previstas), use_container_width=True)
        
        st.write("### Recomendações")
        for rec in recomendacoes:
            st.write(rec)
       
    else:
        st.error("Nenhum dado disponível. Por favor, insira seus dados primeiro.")

def mostrar_barra_navegacao():
    """Exibir uma barra de navegação no topo do aplicativo."""
    # Exibir logo no topo da barra lateral
    st.sidebar.image("assets/logo.png", use_column_width=True)
    
    # Título e seleção de página
    st.sidebar.title("Calculadora de GEE")
    paginas = ["Início", "Inserir Seus Dados", "Resultado"]
    pagina = st.sidebar.radio("", paginas, index=paginas.index(st.session_state.page) if 'page' in st.session_state else 0)
    st.session_state.page = pagina

    # Instruções e Isenção de Responsabilidade
    st.sidebar.write("### Instruções")
    st.sidebar.write("""
    - Navegue entre as páginas usando a barra lateral.
    - Na página "Inserir Seus Dados", insira as informações relevantes.
    - Na página "Resultado", visualize a comparação de emissões e recomendações.
    """)
    
    st.sidebar.write("### Isenção de Responsabilidade")
    st.sidebar.write("""
    - Os fatores de emissão usados são baseados em dados gerais e podem não refletir as condições exatas em sua área.
    - Esta calculadora fornece estimativas e deve ser usada apenas como guia.
    - Para cálculos e recomendações precisos, entre em contato com os consultores da Mira.
    """)

# Lógica principal
if 'page' not in st.session_state:
    st.session_state.page = "Início"

mostrar_barra_navegacao()

if st.session_state.page == "Início":
    mostrar_introducao()
elif st.session_state.page == "Inserir Seus Dados":
    mostrar_entrada()
elif st.session_state.page == "Resultado":
    mostrar_resultados()
else:
    st.error("Página desconhecida.")
