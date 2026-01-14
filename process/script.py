import fitz
import cv2
import numpy as np
import os
import json
import re

def processar_euf_completo(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    zoom = 3.0
    mat = fitz.Matrix(zoom, zoom)
    
    # Regex para capturar referências: [mc1a], [em2b], etc.
    pattern_ref = re.compile(r"\[(mc|em|te|fm|mq|fe)\d+[ab]\]")
    
    # Dicionário para o mapeamento final: { "mc1a": "C", ... }
    gabarito_map = {}
    # Lista detalhada para metadados do Supabase
    metadados_completos = []

    print(f"--- Iniciando Processamento Completo: {pdf_path} ---")

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        texto_pagina = page.get_text()
        
        # Filtro de Gabarito: Muitas "Questão" e zero referências []
        questoes_no_texto = page.search_for("Questão")
        referencias_encontradas = pattern_ref.findall(texto_pagina)
        
        if len(questoes_no_texto) > 8 and not referencias_encontradas:
            print(f"⏩ Página {page_idx+1} pulada (Gabarito detectado).")
            continue

        if not questoes_no_texto:
            continue

        # Renderizar página em alta resolução
        pix = page.get_pixmap(matrix=mat)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 3)
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        for i, rect in enumerate(questoes_no_texto):
            # 1. Capturar Referência [mc1a]
            area_header = fitz.Rect(rect.x0, rect.y0 - 5, page.rect.width, rect.y1 + 10)
            texto_header = page.get_text("text", clip=area_header)
            match = pattern_ref.search(texto_header)
            
            if not match:
                continue
                
            ref_questao = match.group().replace("[", "").replace("]", "")

            # 2. Definir Área de Recorte
            y0 = rect.y0
            y1 = questoes_no_texto[i+1].y0 if i+1 < len(questoes_no_texto) else page.rect.height
            iy0, iy1 = max(0, int((y0 - 15) * zoom)), min(img_bgr.shape[0], int((y1 - 10) * zoom))
            crop = img_bgr[iy0:iy1, :]

            # 3. Processar Imagem e Identificar Letra Correta
            crop_final, letra_correta = substituir_e_capturar_gabarito(crop)

            # 4. Salvar Imagem Padronizada
            nome_arquivo = f"{ref_questao}.png"
            cv2.imwrite(os.path.join(output_folder, nome_arquivo), crop_final)
            
            # 5. Guardar nos Dicionários
            gabarito_map[ref_questao] = letra_correta
            metadados_completos.append({
                "ref": ref_questao,
                "arquivo": nome_arquivo,
                "alternativa_correta": letra_correta,
                "materia": ref_questao[:2],
                "versao": ref_questao[-1]
            })
            
            print(f"✅ Processada: {ref_questao} -> Resposta: {letra_correta}")

    # Salvar os arquivos JSON
    # 1. O mapeamento simples solicitado: { "mc1a": "C" }
    with open(os.path.join(output_folder, "gabarito_resumido.json"), "w") as f:
        json.dump(gabarito_map, f, indent=4)
        
    # 2. O arquivo completo para o Banco de Dados
    with open(os.path.join(output_folder, "database_import.json"), "w", encoding='utf-8') as f:
        json.dump(metadados_completos, f, indent=4, ensure_ascii=False)

    print(f"\n🚀 Finalizado! {len(gabarito_map)} questões prontas para o Supabase.")

def substituir_e_capturar_gabarito(img):
    """
    Detecta todos os quadrados, identifica o pintado e substitui todos 
    por versões limpas com letras A-E.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    candidatos = []
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            if 30 < w < 110 and 30 < h < 110:
                roi = thresh[y:y+h, x:x+w]
                # Verifica se estava pintado antes de limpar
                is_gabarito = (cv2.countNonZero(roi) / (w * h)) > 0.75
                candidatos.append({'x': x, 'y': y, 'w': w, 'h': h, 'is_gabarito': is_gabarito})

    # Ordenar verticalmente (A -> E)
    candidatos = sorted(candidatos, key=lambda c: c['y'])
    letras = ["A", "B", "C", "D", "E"]
    gabarito_final = "N/D"
    
    for idx, quad in enumerate(candidatos):
        if idx < len(letras):
            letra_atual = letras[idx]
            if quad['is_gabarito']:
                gabarito_final = letra_atual
            
            # Padronização Visual
            x, y, w, h = quad['x'], quad['y'], quad['w'], quad['h']
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 255), -1)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), 2)
            
            t_size = cv2.getTextSize(letra_atual, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            cv2.putText(img, letra_atual, (x+(w-t_size[0])//2, y+(h+t_size[1])//2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    return img, gabarito_final

# Execução
processar_euf_completo("euf_2023_2.pdf", "output_final")