import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO
import textwrap

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="🌽 Editor Junino", layout="wide")

st.title("🔥🌽 Correio Elegante da GEPES Atendimento")
st.markdown("Escolha a foto do colega e uma frase pronta, e veja a pré-visualização em tempo real.")

# 1) Carrega os fundos
FUNDO_PATH_1 = "FUNDO_JUNINO.png"
FUNDO_PATH_2 = "FUNDO_JUNINO_2.png"

@st.cache_data
def load_background(path):
    img = Image.open(path).convert("RGBA")
    return img

background_1 = load_background(FUNDO_PATH_1)
background_2 = load_background(FUNDO_PATH_2)

# Tamanho padrão para ambos os fundos
SIZE = (600, 800)
background_1 = background_1.resize(SIZE, Image.LANCZOS)
background_2 = background_2.resize(SIZE, Image.LANCZOS)

# 2) Lista de fotos do diretório
FOTOS_DIR = "junina"
colaboradores = [
    f for f in os.listdir(FOTOS_DIR)
    if f.lower().endswith((".jpg", ".png", ".jpeg"))
]
# Selectbox sem seleção inicial
col_option = st.selectbox("Escolha um colega:", [""] + colaboradores, index=0)

# Carregar imagem do colaborador
def load_colaborador():
    if col_option and col_option != "":
        return Image.open(os.path.join(FOTOS_DIR, col_option)).convert("RGBA")
    else:
        return None

col_img = load_colaborador()

# 3) Frase pronta: seleção de frases
frases_juninas = [
    "No arraiá da Gepes Atendimento, você é uma estrela brilhante da nossa fogueira!",
    "Se Gestão de Pessoas fosse quadrilha, você seria o Anjo que arruma a bagunça e ainda faz todo mundo dançar no mesmo ritmo! ",
    "Você é como pamonha: envolve a gente com cuidado e deixa tudo mais doce! Obrigado por cuidar da nossa equipe!",
    "Se a Gepes Atendimento fosse uma festa junina, você seria o milho: versátil, quentinho e indispensável! ",
    "Você é como o correio elegante: leva mensagens de amor (e às vezes de ‘ajuste’ rs), mas sempre com um sorriso no rosto e muito amor no coração.",
    "No arraiá da Gepes, você é o mestre da quadrilha: organiza, orienta e ainda faz a festa ficar melhor! ",
    "Você é o ‘Puxador de Quadrilha’ da Gepes,  sabe conduzir a equipe sem deixar ninguém tropeçar no salão!",
    "No ‘Bingo de Talentos’, você é uma jóia na nossa equipe.",
    "Com você na equipe, até tema sensível fica mais doce",
    "Estamos separados pela plataforma, mas nossa parceria e amizade vai além desse Brasil.",
    "Não preciso te conhecer pessoalmente para ter certeza que a sua estrela tem uma luz forte e reluzente!",
    "Espero o seu convite para visitar a sua cidade! Chama eu! ",
    "A equipe solução balançou meu coração. Ter você você na equipe vale mais que 1 milhão",
    "Passando para agradecer por tudo! Trabalhar contigo é bão demais! ",
    "Analisei todas as planilhas, dados e informações,  hoje eu tenho certeza: Você é sensacional! "
]
frase_selecionada = st.selectbox("Escolha uma frase:", frases_juninas)

# --- PERSONALIZAÇÃO DE TEXTO ---
st.subheader("📝 Personalização do Texto")

# Layout em colunas
col1, col2, col3, col4 = st.columns(4)

with col1:
    text_color = st.color_picker("Cor do texto:", "#FFFFFF")  # Branco como padrão
    
with col2:
    # FONTES COMPATÍVEIS COM UTF-8 (ACENTOS)
    font_options = {
        "DejaVu Sans (Recomendada)": "DejaVuSans.ttf",  # Fonte compatível com UTF-8
        "Arial": "arial.ttf",
        "Times New Roman": "times.ttf",
        "Comic Sans MS": "comic.ttf",
        "Impact": "impact.ttf",
        "Courier New": "cour.ttf"
    }
    selected_font = st.selectbox("Fonte:", list(font_options.keys()), index=0)
    
with col3:
    font_size = st.slider("Tamanho da fonte:", 20, 60, 32)
    
with col4:
    vertical_offset = st.slider("Posição vertical:", -100, 100, 0, 
                              help="Valores negativos descem o texto, valores positivos sobem")

# --- CONFIGURAÇÃO DA BORDA ---
st.subheader("🔲 Borda do Texto")
use_border = st.checkbox("Adicionar borda ao texto?", value=True)

if use_border:
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        border_color = st.color_picker("Cor da borda:", "#000000")  # Preto como padrão
    with col_b2:
        border_width = st.slider("Espessura da borda:", 1, 5, 2)

# 4) Função para desenhar texto com quebra automática, centralização e borda
def draw_wrapped_text(draw, text, position, font, max_width, color, max_lines=4, max_chars=55, 
                     border_width=0, border_color=None):
    # Função auxiliar para calcular tamanho do texto
    def get_text_size(text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    # Divide o texto em linhas com limite de caracteres
    lines = []
    words = text.split()
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        test_width, _ = get_text_size(test_line, font)
        
        # Verifica limite de caracteres e largura
        if len(test_line) > max_chars or test_width > max_width:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
        else:
            current_line.append(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    # Limita o número de linhas
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        if len(lines[-1]) > 3:
            lines[-1] = lines[-1][:-3] + "..."
    
    # Desenha cada linha centralizada horizontalmente
    x, y = position
    for line in lines:
        line_width, line_height = get_text_size(line, font)
        x_pos = (max_width - line_width) / 2
        
        # Desenha borda se necessário
        if border_width > 0 and border_color:
            # Desenha o texto em várias direções para criar o efeito de borda
            for dx in [-border_width, 0, border_width]:
                for dy in [-border_width, 0, border_width]:
                    if dx != 0 or dy != 0:
                        draw.text((x + x_pos + dx, y + dy), line, font=font, fill=border_color)
        
        # Desenha o texto principal
        draw.text((x + x_pos, y), line, font=font, fill=color)
        
        y += line_height * 1.2  # Espaço entre linhas

# 5) Monta a imagem com o primeiro fundo
canvas_1 = background_1.copy()
draw_1 = ImageDraw.Draw(canvas_1)

if col_img:
    col_img_resized = col_img.resize((200, 300), Image.LANCZOS)
    x = (canvas_1.width - col_img_resized.width) // 2
    y = (canvas_1.height - col_img_resized.height) // 2 - 50
    canvas_1.paste(col_img_resized, (x, y), col_img_resized)

if frase_selecionada:
    try:
        # CORREÇÃO: Especificar encoding UTF-8 explicitamente
        font_path = font_options[selected_font]
        font = ImageFont.truetype(font_path, font_size, encoding="unic")
    except:
        try:
            # Fallback para fonte UTF-8
            font = ImageFont.truetype("DejaVuSans.ttf", font_size, encoding="unic")
        except:
            try:
                # Fallback para Arial
                font = ImageFont.truetype("arial.ttf", font_size, encoding="unic")
            except:
                # Fallback final para fonte padrão com encoding
                font = ImageFont.load_default()
                # Ajuste para tamanho (não suportado nativamente)
    
    # Área de texto com margens e ajuste vertical
    text_area_width = canvas_1.width - 100
    text_area_x = 50  # Margem esquerda
    
    # Posição Y ajustável
    text_y = canvas_1.height - 230 - vertical_offset
    
    # Configuração da borda
    border_config = {
        "border_width": border_width if use_border else 0,
        "border_color": border_color if use_border else None
    }
    
    draw_wrapped_text(draw_1, frase_selecionada, (text_area_x, text_y), 
                     font, text_area_width, text_color, **border_config)

# 6) Monta a imagem com o segundo fundo
canvas_2 = background_2.copy()
draw_2 = ImageDraw.Draw(canvas_2)

if col_img:
    col_img_resized = col_img.resize((200, 300), Image.LANCZOS)
    x = (canvas_2.width - col_img_resized.width) // 2
    y = (canvas_2.height - col_img_resized.height) // 2 - 70
    canvas_2.paste(col_img_resized, (x, y), col_img_resized)

if frase_selecionada:
    try:
        # CORREÇÃO: Mesmo tratamento de encoding
        font_path = font_options[selected_font]
        font = ImageFont.truetype(font_path, font_size, encoding="unic")
    except:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", font_size, encoding="unic")
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size, encoding="unic")
            except:
                font = ImageFont.load_default()
    
    text_area_width = canvas_2.width - 100
    text_area_x = 50
    
    # Mesmo ajuste vertical para o segundo fundo
    text_y = canvas_2.height - 230 - vertical_offset
    
    # Configuração da borda
    draw_wrapped_text(draw_2, frase_selecionada, (text_area_x, text_y), 
                     font, text_area_width, text_color, **border_config)

# 7) Exibe ambos os fundos lado a lado
col1, col2 = st.columns(2)

with col1:
    st.image(canvas_1, caption="Pré-visualização - Fundo 1", use_container_width=True)
    buf_1 = BytesIO()
    canvas_1.save(buf_1, format="PNG")
    st.download_button(
        label="🚀 Baixar Cartão com Fundo 1",
        data=buf_1.getvalue(),
        file_name="cartao_junino_fundo_1.png",
        mime="image/png"
    )

with col2:
    st.image(canvas_2, caption="Pré-visualização - Fundo 2", use_container_width=True)
    buf_2 = BytesIO()
    canvas_2.save(buf_2, format="PNG")
    st.download_button(
        label="🚀 Baixar Cartão com Fundo 2",
        data=buf_2.getvalue(),
        file_name="cartao_junino_fundo_2.png",
        mime="image/png"
    )
