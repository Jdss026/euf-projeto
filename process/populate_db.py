import os
import re
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# 1. Localização do .env.local
caminho_base = Path(__file__).resolve().parent.parent
env_path = caminho_base / ".env.local"
load_dotenv(dotenv_path=env_path)

URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL").strip()
KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY").strip()

if not URL.endswith('/'): URL += '/'

# --- CONFIGURAÇÕES ---
BUCKET_NAME = "questoes-euf"
TABLE_NAME = "questoes"

def extrair_dados_arquivo(nome):
    """
    Extrai informações do padrão: euf_[materia][numero][versao]...
    Exemplo: euf_em1a_2023_2.png -> materia: em, numero: 1
    """
    # Busca a sigla da matéria e o número logo após o primeiro '_'
    match = re.search(r'euf_([a-z]+)(\d+)', nome.lower())
    if match:
        sigla = match.group(1)
        numero = int(match.group(2))
        
        mapa_materias = {
            "mc": "Mecânica Clássica",
            "em": "Eletromagnetismo",
            "mq": "Mecânica Quântica",
            "te": "Termodinâmica",
            "fm": "Física Moderna",
            "fe": "Física Estatística"
        }
        return numero, mapa_materias.get(sigla, "Física Geral")
    return None, "Física"

def popular():
    supabase = create_client(URL, KEY)
    
    print(f"🚀 Iniciando inserção no banco de dados...")
    
    # Lista arquivos no bucket
    res = supabase.storage.from_(BUCKET_NAME).list('')
    
    count = 0
    for file in res:
        nome = file['name']
        
        # Filtra apenas imagens .png
        if not nome.lower().endswith('.png'):
            continue

        # 1. Gerar URL Pública
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(nome)

        # 2. Extrair metadados do nome do arquivo
        numero, materia = extrair_dados_arquivo(nome)
        
        # 3. Montar o Payload
        payload = {
            "numero": numero if numero else count + 1,
            "materia": materia,
            "nome_arquivo": nome,
            "imagem_url": public_url,
            "gabarito": "A", # Todos como 'A' conforme solicitado
            "ano": "2023",
            "periodo": "2"
        }

        # 4. Inserir (Upsert baseado no nome_arquivo)
        try:
            supabase.table(TABLE_NAME).upsert(payload, on_conflict="nome_arquivo").execute()
            print(f" ✅ {nome} -> Inserido como Questão {numero} ({materia})")
            count += 1
        except Exception as e:
            print(f" ❌ Erro ao inserir {nome}: {e}")

    print(f"\n✨ Sucesso! {count} questões foram cadastradas no banco de dados.")

if __name__ == "__main__":
    popular()