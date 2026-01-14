import cv2
import numpy as np
import os
import json
import random

# --- CONFIGURAÇÕES ---
PATH_INPUT = "./process/output_final"
PATH_OUTPUT = "./process/output_final_random"
os.makedirs(PATH_OUTPUT, exist_ok=True)

def safe_copy(img):
    return np.array(img, copy=True, order='C', dtype=np.uint8)

def get_boxes_multi_stage(img):
    """Tenta detectar os quadrados usando diferentes níveis de sensibilidade."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Lista de thresholds para tentar (do mais rígido ao mais flexível)
    thresholds = [220, 200, 180, 150]
    
    for t_val in thresholds:
        _, thresh = cv2.threshold(gray, t_val, 255, cv2.THRESH_BINARY_INV)
        # Dilatação leve para fechar contornos de caixas digitalizadas com falhas
        kernel = np.ones((2,2), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=1)
        
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        boxes = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w)/h if h > 0 else 0
            # Critérios: Tamanho entre 25-85px e formato quase quadrado
            if 25 < w < 85 and 25 < h < 85 and 0.75 < aspect_ratio < 1.25:
                boxes.append({'x': x, 'y': y, 'w': w, 'h': h})
        
        # Se achamos exatamente 5 (ou muito perto disso), paramos a busca
        if len(boxes) >= 5:
            # Ordenamos por Y (altura) e X (posição lateral)
            return sorted(boxes, key=lambda b: (b['y'], b['x']))
            
    return [] # Retorna vazio se falhar em todos os níveis

def process_v15(path):
    img = cv2.imread(path)
    if img is None: return None, None
    
    original_boxes = get_boxes_multi_stage(img)
    
    # PROTEÇÃO CONTRA O ERRO 'INDEX OUT OF RANGE'
    if len(original_boxes) < 2: 
        print(f"⚠️ {os.path.basename(path)}: Não foram detectadas alternativas suficientes.")
        return None, None

    # O gabarito original (A) é o primeiro box da lista
    correct_box = original_boxes[0]

    # --- 1. EXTRAÇÃO DOS CARDS ---
    cards = []
    for box in original_boxes:
        # Pega a faixa horizontal da alternativa
        y1, y2 = max(0, box['y'] - 12), min(img.shape[0], box['y'] + box['h'] + 12)
        x1, x2 = max(0, box['x'] - 10), img.shape[1]
        
        card_img = img[y1:y2, x1:x2].copy()
        cards.append({
            'img': card_img,
            'box_pos': (10, 12, box['w'], box['h']), # Posição relativa dentro do card
            'is_correct': (box == correct_box)
        })

    # --- 2. PREPARAÇÃO DO ENUNCIADO ---
    clean_img = safe_copy(img)
    for box in original_boxes:
        # Apaga os boxes originais para não sobrarem "fantasmas"
        cv2.rectangle(clean_img, (box['x']-5, box['y']-5), (box['x']+box['w']+5, box['y']+box['h']+5), (255, 255, 255), -1)
    
    # O enunciado é tudo acima do topo do primeiro box encontrado
    top_y = min([b['y'] for b in original_boxes])
    enunciado = clean_img[0:max(0, top_y - 15), :].copy()

    # --- 3. RANDOMIZAÇÃO ---
    random.shuffle(cards)

    # --- 4. RECONSTRUÇÃO VERTICAL ---
    final_img = enunciado
    letras = ["A", "B", "C", "D", "E", "F", "G"] # Suporte a mais se detectado
    novo_gabarito = "N/D"

    for idx, card in enumerate(cards):
        if idx >= len(letras): break
        letra = letras[idx]
        
        # Desenha a nova letra no card recortado
        processed_card = draw_card_ui(card['img'], card['box_pos'], letra)
        
        # Ajusta largura se necessário
        if processed_card.shape[1] != final_img.shape[1]:
            canvas = np.ones((processed_card.shape[0], final_img.shape[1], 3), dtype=np.uint8) * 255
            w_limit = min(processed_card.shape[1], final_img.shape[1])
            canvas[:, 0:w_limit] = processed_card[:, 0:w_limit]
            processed_card = canvas

        final_img = np.vstack((final_img, processed_card))
        if card['is_correct']:
            novo_gabarito = letra

    return final_img, novo_gabarito

def draw_card_ui(card_img, box_pos, letra):
    res = safe_copy(card_img)
    x, y, w, h = box_pos
    cv2.rectangle(res, (x, y), (x+w, y+h), (255, 255, 255), -1)
    cv2.rectangle(res, (x, y), (x+w, y+h), (0, 0, 0), 2)
    font = cv2.FONT_HERSHEY_SIMPLEX
    t_size = cv2.getTextSize(letra, font, 0.7, 2)[0]
    cv2.putText(res, letra, (x+(w-t_size[0])//2, y+(h+t_size[1])//2), font, 0.7, (0, 0, 0), 2)
    return res

def main():
    files = [f for f in os.listdir(PATH_INPUT) if f.endswith('.png')]
    db = []
    print(f"--- Iniciando v15: Normalizador Resiliente ({len(files)} questões) ---")

    for f in files:
        try:
            path = os.path.join(PATH_INPUT, f)
            res_img, res_gab = process_v15(path)
            
            if res_img is not None:
                out_name = f"random_{f}"
                cv2.imwrite(os.path.join(PATH_OUTPUT, out_name), res_img)
                db.append({"id": f, "arquivo": out_name, "gabarito": res_gab})
                print(f"✅ {f} -> {res_gab}")
            else:
                # O script pula mas não trava
                print(f"⏩ {f}: Ignorada por erro de detecção.")
        except Exception as e:
            print(f"❌ Erro em {f}: {e}")

    with open(os.path.join(PATH_OUTPUT, "gabarito_v15.json"), "w") as j:
        json.dump(db, j, indent=4)
    print(f"\nFinalizado! Pasta: {PATH_OUTPUT}")

if __name__ == "__main__":
    main()