import os
import re
import requests
import unicodedata
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Pasta local para salvar os arquivos
PASTA_DESTINO = os.path.join(os.getcwd(), "input")

def normalizar_texto(texto):
    """Corrige encoding e remove acentos para facilitar o match da Regex"""
    try:
        # Tenta corrigir problemas de encoding do site
        texto = texto.encode('latin1').decode('utf-8')
    except:
        pass
    
    # Transforma '2ª aplicação de 2017' em '2a aplicacao de 2017'
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()

def baixar_apenas_provas():
    if not os.path.exists(PASTA_DESTINO):
        os.makedirs(PASTA_DESTINO)

    url = "https://www.uaifisica.com.br/euf"
    print(f"Monitorando: {url} com trava de segurança ativa.\n")
    
    response = requests.get(url)
    response.encoding = response.apparent_encoding 
    soup = BeautifulSoup(response.text, 'html.parser')
    
    links = soup.find_all('a')
    contagem = 0

    # PADRÃO DO LOCK: (número) + (a/o/ª/º) + (aplicacao de) + (ano)
    # Ex: '2a aplicacao de 2017' ou '1 aplicacao de 2020'
    padrao_prova = re.compile(r'(\d+)\s*(?:a|o|ª|º)?\s*aplicacao\s*de\s*(20\d{2}|19\d{2})')

    for link in links:
        texto_original = link.get_text().strip()
        texto_limpo = normalizar_texto(texto_original)
        href = link.get('href')

        # O LOCK: Só entra no IF se o texto do link casar EXATAMENTE com o padrão de prova
        match = padrao_prova.search(texto_limpo)
        
        if match and href and href.lower().endswith('.pdf'):
            num_aplicacao = match.group(1)
            ano = match.group(2)
            
            # Monta o nome no padrão solicitado
            nome_final = f"euf_{ano}_{num_aplicacao}.pdf"
            
            # Bloqueio extra: Ignora se no texto original houver palavras indesejadas
            # (Caso algum edital tenha um nome muito parecido)
            if any(word in texto_limpo for word in ['edital', 'formulario', 'inscricao', 'manual']):
                continue

            url_completa = urljoin(url, href)
            caminho_arquivo = os.path.join(PASTA_DESTINO, nome_final)

            print(f"Lock validado: {texto_original[:30]}... -> {nome_final}")
            
            try:
                conteudo = requests.get(url_completa).content
                with open(caminho_arquivo, 'wb') as f:
                    f.write(conteudo)
                contagem += 1
            except Exception as e:
                print(f"Erro ao baixar {nome_final}: {e}")

    print(f"\n--- Finalizado ---")
    print(f"Total de provas capturadas com sucesso: {contagem}")

if __name__ == "__main__":
    baixar_apenas_provas()
