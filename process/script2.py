import fitz
import cv2
import numpy as np
import os
import json
import re

def processar_euf_v6(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)
    zoom = 4.0 # Aumentado para 4.0 para maior precisão em diagramas complexos
    mat = fitz.Matrix(zoom, zoom)
    
    pattern_ref = re.compile(r"\[([a-z]+)\d+[ab]\]")
    metadados = []

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        texto_pagina = page.get_text()
        
        # Busca por títulos
        titulos = page.search_for("Questão")
        refs = pattern_ref.findall(texto_pagina.lower())
        
        # Filtro de gabarito
        if len(titulos) > 8 and not refs: continue
        if not titulos: continue

        pix = page.get_pixmap(matrix=mat)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, 3)
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        for i, rect in enumerate(titulos):
            area_busca = fitz.Rect(rect.x0, rect.y0 - 5, page.rect.width, rect.y1 + 10)
            texto_area = page.get_text("text", clip=area_busca).lower()
            match = pattern_ref.search(texto_area)
            if not match: continue
            
            ref_questao = match.group().replace("[", "").replace("]", "")
            y0, y1 = rect.y0, (titulos[i+1].y0 if i+1 < len(titulos) else page.rect.height)
            
            iy0, iy1 = max(0, int((y0 - 15) * zoom)), min(img_bgr.shape[0], int((y1 - 10) * zoom))
            crop = img_bgr[iy0:iy1, :].copy()

            # CHAMADA DA NOVA FUNÇÃO ROBUSTA
            crop_final, gabarito = substituir_quadrados_robusto(crop)

            nome_arquivo = f"{ref_questao}.png"
            cv2.imwrite(os.path.join(output_folder, nome_arquivo), crop_final)
            metadados.append({"ref": ref_questao, "gabarito": gabarito})
            print(f"✅ {ref_questao} processada. Gabarito: {gabarito}")

    with open(os.path.join(output_folder, "database_euf.json"), "w") as f:
        json.dump(metadados, f, indent=4)

def substituir_quadrados_robusto(img):
    """
    Detecta quadrados com filtros de solidez e organiza em grade 
    com tolerância vertical aumentada para layouts como em8a.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Filtro Bilateral para reduzir ruído de diagramas sem perder bordas
    blur = cv2.bilateralFilter(gray, 9, 75, 75)
    _, thresh = cv2.threshold(blur, 160, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    candidatos = []
    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)
        
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w)/h
            area = cv2.contourArea(cnt)
            solidity = area / (w * h)

            # FILTROS ANTI-RUÍDO RÍGIDOS
            # 1. Tamanho (ajustado para zoom 4.0)
            # 2. Aspect Ratio (deve ser quase um quadrado perfeito)
            # 3. Solidez (deve estar bem preenchido, não pode ser um 'L' ou eixo)
            if 40 < w < 160 and 40 < h < 160:
                if 0.85 < aspect_ratio < 1.15 and solidity > 0.90:
                    roi = thresh[y:y+h, x:x+w]
                    is_gabarito = (cv2.countNonZero(roi) / (w * h)) > 0.70
                    candidatos.append({'x': x, 'y': y, 'w': w, 'h': h, 'is_gabarito': is_gabarito})

    if not candidatos: return img, "N/D"

    # ORDENAÇÃO POR GRADE ELÁSTICA
    # Ordena por Y e agrupa linhas com 150px de tolerância (resolve o gap da em8a)
    candidatos = sorted(candidatos, key=lambda c: c['y'])
    linhas_final = []
    if candidatos:
        temp_linha = [candidatos[0]]
        for i in range(1, len(candidatos)):
            if candidatos[i]['y'] - temp_linha[-1]['y'] < 150: # Tolerância aumentada
                temp_linha.append(candidatos[i])
            else:
                linhas_final.extend(sorted(temp_linha, key=lambda c: c['x']))
                temp_linha = [candidatos[i]]
        linhas_final.extend(sorted(temp_linha, key=lambda c: c['x']))

    letras = ["A", "B", "C", "D", "E", "F"] # F adicionado por precaução (erros de diagramação do PDF)
    gabarito = "N/D"
    
    for idx, quad in enumerate(linhas_final):
        if idx < len(letras):
            letra = letras[idx]
            if quad['is_gabarito']: gabarito = letra
            x, y, w, h = quad['x'], quad['y'], quad['w'], quad['h']
            
            # Limpeza e Padronização
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 255, 255), -1)
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 0), 2)
            t_size = cv2.getTextSize(letra, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
            cv2.putText(img, letra, (x+(w-t_size[0])//2, y+(h+t_size[1])//2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)

    return img, gabarito

# Executar
processar_euf_v6("euf_2023_2.pdf", "output_final")