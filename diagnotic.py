import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("/home/jonas/workspace/euf-projeto/.env.local")

URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
KEY = os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY")

# Forçamos a barra final para calar o aviso do SDK
# if not URL.endswith('/'): URL += '/'

supabase = create_client(URL, KEY)

def diagnostico():
    print(f"--- Diagnóstico de Storage ---")
    try:
        # 1. Lista todos os buckets disponíveis
        buckets = supabase.storage.list_buckets()
        print(f"Buckets encontrados: {[b.name for b in buckets]}")
        
        # 2. Tenta listar o conteúdo especificamente
        # Se aqui der erro ou vazio, o problema é a Policy do passo anterior
        files = supabase.storage.from_("questoes-euf").list()
        print(f"Arquivos no bucket 'questoes-euf': {len(files)}")
        
        for f in files[:5]: # Mostra os primeiros 5 nomes
            print(f" - Encontrado: {f['name']}")

    except Exception as e:
        print(f"❌ Erro no diagnóstico: {e}")

if __name__ == "__main__":
    diagnostico()