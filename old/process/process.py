import os
import torch
from dotenv import load_dotenv

# Importações da API Marker
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import save_output

load_dotenv()

def main():
    fpath = "./scrap/input/euf_2023_2.pdf"
    output_dir = "./process/output"

    # --- CONFIGURAÇÕES DE EMERGÊNCIA PARA 4GB ---
    # 1. Força o modelo de Layout para a CPU (Libera ~1.5GB de VRAM)
    os.environ["LAYOUT_DEVICE"] = "cpu"
    
    # 2. Mantém o OCR e Equações na GPU
    os.environ["TORCH_DEVICE"] = "cuda"
    
    # 3. Reduz resoluções para economizar memória de processamento
    os.environ["RECOGNITION_BATCH_SIZE"] = "1"
    os.environ["LAYOUT_BATCH_SIZE"] = "1"
    
    # 4. Define apenas a primeira página para o teste
    os.environ["PAGE_RANGE"] = "0"

    print("🚀 Carregando modelos com Offloading (Layout -> CPU | OCR -> GPU)...")
    
    # create_model_dict lerá as variáveis de ambiente acima
    model_dict = create_model_dict() 

    # Inicializa o conversor
    converter = PdfConverter(artifact_dict=model_dict)

    print(f"📄 Processando página 1 de: {fpath}...")
    
    try:
        # Executa a conversão
        rendered = converter(fpath) 
        
        # Salva o resultado
        save_output(rendered, output_dir, "teste_euf_p1")
        print(f"✅ Sucesso! Arquivos em: {output_dir}")
        
    except RuntimeError as e:
        if "out of memory" in str(e).lower():
            print("❌ Erro: VRAM insuficiente mesmo com Offloading. Tente fechar o navegador.")
        else:
            print(f"❌ Erro inesperado: {e}")
            
    finally:
        # Limpeza agressiva de memória
        if 'model_dict' in locals(): del model_dict
        if 'converter' in locals(): del converter
        torch.cuda.empty_cache()

if __name__ == "__main__":
    main()