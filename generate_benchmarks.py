"""
generate_benchmarks.py
Erstellt die 3 Benchmark-Varianten für die Präsentation im minimalen Bahnschrift-Stil:
1. benchmark_openai.png: Hervorhebung aller OpenAI / ChatGPT Modelle
2. benchmark_anthropic.png: Hervorhebung aller Anthropic / Claude Modelle
3. benchmark_open_weights.png: Empfohlene Open-Weights Modelle (Grün) & Modelle mit Nuancen (Gelb)
"""

import os
from PIL import Image, ImageDraw, ImageFont

BASE_IMG_PATH = "Artificial Analysis Intelligence Index by Open Weights - Proprietary (2 Oct '26) (2).png"
OUTPUT_DIR = "assets/benchmarks"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 29 Bars Definitions (1-based index)
# (index, name, org, score, category, x1, x2, xc, top_y)
BAR_GEOM = [
    (1,  "Claude Opus 5.5 (max with fallback)", "Anthropic", 58, "Proprietary",   92,  153,  122, 391),
    (2,  "GPT-6 Astra (max)",                  "OpenAI",    53, "Proprietary",  173,  234,  203, 422),
    (3,  "Claude Opus 5 (max)",                  "Anthropic", 51, "Proprietary",  254,  315,  284, 434),
    (4,  "Claude Opus 4.8 (max)",                "Anthropic", 42, "Proprietary",  336,  397,  366, 492),
    (5,  "Claude Opus 4.7 (max)",                "Anthropic", 41, "Proprietary",  417,  478,  447, 499),
    (6,  "Qwen3.8-Flash-Next",                  "Alibaba",   40, "Open Weights",  499,  559,  529, 504),
    (7,  "GPT-5.5 (xhigh)",                     "OpenAI",    38, "Proprietary",  580,  641,  610, 513),
    (8,  "Qwen3.8 27B (xhigh)",                 "Alibaba",   34, "Open Weights",  661,  722,  691, 543),
    (9,  "Claude Opus 4.6 (max)",                "Anthropic", 32, "Proprietary",  743,  804,  773, 554),
    (10, "GPT-5.2 (xhigh)",                     "OpenAI",    30, "Proprietary",  824,  885,  854, 564),
    (11, "Claude Opus 4.5",                      "Anthropic", 29, "Proprietary",  906,  966,  936, 572),
    (12, "K2 Horizon MoVA 36B A4B",             "K2",        25, "Open Weights",  987, 1048, 1017, 597),
    (13, "GPT-5 (high)",                        "OpenAI",    23, "Proprietary", 1068, 1129, 1098, 611),
    (14, "Claude 4.1 Opus",                     "Anthropic", 23, "Proprietary", 1150, 1211, 1180, 612),
    (15, "Claude 4 Opus",                       "Anthropic", 21, "Proprietary", 1231, 1292, 1261, 626),
    (16, "Qwen3.6 35B A3B",                     "Alibaba",   18, "Open Weights", 1312, 1373, 1342, 642),
    (17, "Muse Glimmer (high)",                 "Meta",      17, "Open Weights", 1394, 1455, 1424, 647),
    (18, "Gemma 4 26B A4B",                     "Google",    17, "Open Weights", 1475, 1536, 1505, 652),
    (19, "Gemma 4 31B",                         "Google",    15, "Open Weights", 1557, 1617, 1587, 665),
    (20, "Gemma 4 12B",                         "Google",    14, "Open Weights", 1638, 1699, 1668, 668),
    (21, "Nemotron 3.5 Lightning",              "Nvidia",    13, "Open Weights", 1719, 1780, 1749, 676),
    (22, "GPT-4.1",                             "OpenAI",    13, "Proprietary", 1801, 1862, 1831, 677),
    (23, "gpt-oss-120b (high)",                 "OpenAI",    12, "Open Weights", 1882, 1943, 1912, 684),
    (24, "GPT-4o (Mar)",                        "OpenAI",     9, "Proprietary", 1963, 2024, 1993, 701),
    (25, "Gemma 4 E4B",                         "Google",     9, "Open Weights", 2045, 2106, 2075, 701),
    (26, "Claude 3 Opus",                       "Anthropic",  9, "Proprietary", 2126, 2187, 2156, 702),
    (27, "LFM2.5-2.6B",                         "Liquid AI",  8, "Open Weights", 2208, 2268, 2238, 704),
    (28, "Gemma 4 E2B",                         "Google",     8, "Open Weights", 2289, 2350, 2319, 709),
    (29, "LFM2.5-1.2B-Thinking",                 "Liquid AI",  5, "Open Weights", 2370, 2431, 2400, 725),
]

BASELINE_Y = 756

def get_font(size):
    font_path = r"C:\Windows\Fonts\bahnschrift.ttf"
    if os.path.exists(font_path):
        return ImageFont.truetype(font_path, size)
    return ImageFont.load_default()

def draw_dimming_overlay(base_img, active_indices):
    overlay = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    
    for item in BAR_GEOM:
        idx = item[0]
        x1, x2 = item[5], item[6]
        if idx not in active_indices:
            pad_left = x1 - 5
            pad_right = x2 + 5
            # Subtiler Schleier (65% Deckkraft) stoppt exakt an der Baseline (schützt Modellnamen und Logos unten!)
            draw.rectangle([pad_left, 140, pad_right, BASELINE_Y], fill=(255, 255, 255, 175))
            
    return Image.alpha_composite(base_img.convert("RGBA"), overlay)

def draw_arrow_down(draw, center_x, tip_y, length=40, color=(30, 30, 35), outline_color=(255, 255, 255), width=4):
    start_y = tip_y - length
    # White outline for contrast
    draw.line([(center_x, start_y), (center_x, tip_y)], fill=outline_color, width=width+3)
    head_size = 12
    p1 = (center_x, tip_y + 3)
    p2 = (center_x - head_size - 1, tip_y - head_size - 1)
    p3 = (center_x + head_size + 1, tip_y - head_size - 1)
    draw.polygon([p1, p2, p3], fill=outline_color)
    
    # Sharp minimalist arrow
    draw.line([(center_x, start_y), (center_x, tip_y)], fill=color, width=width)
    p1_in = (center_x, tip_y)
    p2_in = (center_x - head_size, tip_y - head_size)
    p3_in = (center_x + head_size, tip_y - head_size)
    draw.polygon([p1_in, p2_in, p3_in], fill=color)

def generate_openai_chart():
    base = Image.open(BASE_IMG_PATH).convert("RGBA")
    openai_indices = [2, 7, 10, 13, 22, 23, 24]
    
    img = draw_dimming_overlay(base, openai_indices)
    draw = ImageDraw.Draw(img)
    
    accent = (16, 140, 100) # Minimalist muted green
    
    font_badge = get_font(18)
    font_title = get_font(26)
    font_bullet = get_font(21)
    font_desc = get_font(18)
    
    for item in BAR_GEOM:
        idx = item[0]
        if idx in openai_indices:
            score = item[3]
            x1, x2, xc, top_y = item[5], item[6], item[7], item[8]
            
            draw.rounded_rectangle([x1 - 3, top_y - 3, x2 + 3, BASELINE_Y + 2], radius=4, outline=accent, width=3)
            
            arrow_tip_y = top_y - 6
            draw_arrow_down(draw, xc, arrow_tip_y, length=38, color=accent, width=4)
            
            # Minimalist rectangular score badge
            pill_y = arrow_tip_y - 38 - 26
            pill_text = f"{score}"
            pill_w = 42
            pill_h = 24
            draw.rounded_rectangle([xc - pill_w//2, pill_y, xc + pill_w//2, pill_y + pill_h], radius=4, fill=accent)
            draw.text((xc, pill_y + 12), pill_text, fill=(255, 255, 255), font=font_badge, anchor="mm")
    
    # Minimalist Info Card (Industrial/Bauhaus clean)
    card_x1 = 1320
    card_y1 = 110
    card_x2 = 2410
    card_y2 = 485
    
    draw.rounded_rectangle([card_x1+3, card_y1+3, card_x2+3, card_y2+3], radius=6, fill=(220, 222, 225, 120))
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=6, fill=(255, 255, 255, 250), outline=(24, 24, 28), width=2)
    
    # Minimal Header Bar
    font_title = get_font(28)
    font_bullet = get_font(23)
    font_desc = get_font(20)
    
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y1+58], radius=4, fill=(24, 24, 28))
    draw.text((card_x1 + 24, card_y1 + 29), "OPENAI / CHATGPT IM BENCHMARK-VERGLEICH", fill=(255, 255, 255), font=font_title, anchor="lm")
    
    lines = [
        ("GPT-4o (Mar 2024) steht bei Score 9:", "Genau dieses Niveau erreichen heutige 4B/9B Modelle komplett lokal."),
        ("GPT-5.2 (Score 30) & GPT-5.5 (Score 38):", "Enormer Sprung durch Test-Time Compute in der Cloud."),
        ("Open-Weights Realitäts-Check:", "Offene Modelle wie Qwen 3.8 Flash-Next (Score 40) überholen GPT-5.5!")
    ]
    
    cur_y = card_y1 + 78
    for title, desc in lines:
        draw.rectangle([card_x1 + 24, cur_y + 4, card_x1 + 32, cur_y + 24], fill=accent)
        draw.text((card_x1 + 44, cur_y), title, fill=(20, 20, 24), font=font_bullet)
        draw.text((card_x1 + 44, cur_y + 32), desc, fill=(90, 95, 105), font=font_desc)
        cur_y += 86
        
    out_path = os.path.join(OUTPUT_DIR, "benchmark_openai.png")
    img.save(out_path)
    print(f"Saved: {out_path}")

def generate_anthropic_chart():
    base = Image.open(BASE_IMG_PATH).convert("RGBA")
    anthropic_indices = [1, 3, 4, 5, 9, 11, 14, 15, 26]
    
    img = draw_dimming_overlay(base, anthropic_indices)
    draw = ImageDraw.Draw(img)
    
    accent = (195, 85, 50) # Muted terracotta
    
    font_badge = get_font(18)
    font_title = get_font(28)
    font_bullet = get_font(23)
    font_desc = get_font(20)
    
    for item in BAR_GEOM:
        idx = item[0]
        if idx in anthropic_indices:
            score = item[3]
            x1, x2, xc, top_y = item[5], item[6], item[7], item[8]
            
            draw.rounded_rectangle([x1 - 3, top_y - 3, x2 + 3, BASELINE_Y + 2], radius=4, outline=accent, width=3)
            
            arrow_tip_y = top_y - 6
            draw_arrow_down(draw, xc, arrow_tip_y, length=38, color=accent, width=4)
            
            pill_y = arrow_tip_y - 38 - 26
            pill_text = f"{score}"
            pill_w = 42
            pill_h = 24
            draw.rounded_rectangle([xc - pill_w//2, pill_y, xc + pill_w//2, pill_y + pill_h], radius=4, fill=accent)
            draw.text((xc, pill_y + 12), pill_text, fill=(255, 255, 255), font=font_badge, anchor="mm")
    
    card_x1 = 1320
    card_y1 = 110
    card_x2 = 2410
    card_y2 = 485
    
    draw.rounded_rectangle([card_x1+3, card_y1+3, card_x2+3, card_y2+3], radius=6, fill=(220, 222, 225, 120))
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=6, fill=(255, 255, 255, 250), outline=(24, 24, 28), width=2)
    
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y1+58], radius=4, fill=(24, 24, 28))
    draw.text((card_x1 + 24, card_y1 + 29), "ANTHROPIC / CLAUDE IM BENCHMARK-VERGLEICH", fill=(255, 255, 255), font=font_title, anchor="lm")
    
    lines = [
        ("Claude 3 Opus (März 2024) steht bei Score 9:", "Genau dieses Niveau erreichen heutige 4B bis 12B Open-Weights Modelle."),
        ("Claude Opus 4.6 (Score 32) bis 5.5 (Score 58):", "Anthropic führt die absolute Benchmark-Spitze bei Agenten-Workflows an."),
        ("Lokaler Zielkorridor für llama.cpp:", "Qwen 3.8 27B (Score 34) erreicht lokale Intelligenz über Opus 4.6!")
    ]
    
    cur_y = card_y1 + 78
    for title, desc in lines:
        draw.rectangle([card_x1 + 24, cur_y + 4, card_x1 + 32, cur_y + 24], fill=accent)
        draw.text((card_x1 + 44, cur_y), title, fill=(20, 20, 24), font=font_bullet)
        draw.text((card_x1 + 44, cur_y + 32), desc, fill=(90, 95, 105), font=font_desc)
        cur_y += 86
        
    out_path = os.path.join(OUTPUT_DIR, "benchmark_anthropic.png")
    img.save(out_path)
    print(f"Saved: {out_path}")

def generate_open_weights_chart():
    base = Image.open(BASE_IMG_PATH).convert("RGBA")
    
    green_indices = [6, 8, 16, 20, 25, 27, 28, 29]
    yellow_indices = [12, 17, 18, 21]
    active_indices = green_indices + yellow_indices
    
    img = draw_dimming_overlay(base, active_indices)
    draw = ImageDraw.Draw(img)
    
    green_color = (16, 140, 75)   # Muted deep forest green
    yellow_color = (210, 130, 0)  # Muted warm amber
    
    font_badge = get_font(18)
    font_title = get_font(26)
    font_h2 = get_font(22)
    font_body = get_font(19)
    
    for item in BAR_GEOM:
        idx = item[0]
        if idx in green_indices:
            score = item[3]
            x1, x2, xc, top_y = item[5], item[6], item[7], item[8]
            
            draw.rounded_rectangle([x1 - 3, top_y - 3, x2 + 3, BASELINE_Y + 2], radius=4, outline=green_color, width=3)
            arrow_tip_y = top_y - 6
            draw_arrow_down(draw, xc, arrow_tip_y, length=38, color=green_color, width=4)
            
            pill_y = arrow_tip_y - 38 - 26
            pill_text = f"{score}"
            pill_w = 42
            pill_h = 24
            draw.rounded_rectangle([xc - pill_w//2, pill_y, xc + pill_w//2, pill_y + pill_h], radius=4, fill=green_color)
            draw.text((xc, pill_y + 12), pill_text, fill=(255, 255, 255), font=font_badge, anchor="mm")

    for item in BAR_GEOM:
        idx = item[0]
        if idx in yellow_indices:
            score = item[3]
            x1, x2, xc, top_y = item[5], item[6], item[7], item[8]
            
            draw.rounded_rectangle([x1 - 3, top_y - 3, x2 + 3, BASELINE_Y + 2], radius=4, outline=yellow_color, width=3)
            arrow_tip_y = top_y - 6
            draw_arrow_down(draw, xc, arrow_tip_y, length=38, color=yellow_color, width=4)
            
            pill_y = arrow_tip_y - 38 - 26
            pill_text = f"{score}"
            pill_w = 42
            pill_h = 24
            draw.rounded_rectangle([xc - pill_w//2, pill_y, xc + pill_w//2, pill_y + pill_h], radius=4, fill=yellow_color)
            draw.text((xc, pill_y + 12), pill_text, fill=(255, 255, 255), font=font_badge, anchor="mm")

    card_x1 = 1320
    card_y1 = 110
    card_x2 = 2410
    card_y2 = 505
    
    draw.rounded_rectangle([card_x1+3, card_y1+3, card_x2+3, card_y2+3], radius=6, fill=(220, 222, 225, 120))
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=6, fill=(255, 255, 255, 250), outline=(24, 24, 28), width=2)
    
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y1+56], radius=4, fill=(24, 24, 28))
    draw.text((card_x1 + 24, card_y1 + 28), "OPEN-WEIGHTS REALITÄTS-CHECK: EMPFEHLUNGEN", fill=(255, 255, 255), font=font_title, anchor="lm")
    
    # Section 1: GRÜN
    cur_y = card_y1 + 72
    draw.rectangle([card_x1 + 24, cur_y + 3, card_x1 + 32, cur_y + 21], fill=green_color)
    draw.text((card_x1 + 44, cur_y), "GRÜN: KLARE DOWNLOAD-EMPFEHLUNGEN FÜR LLAMA.CPP", fill=green_color, font=font_h2)
    
    cur_y += 30
    green_bullets = [
        "• Qwen 3.8 (Flash-Next & 27B): Übertrifft GPT-5.5 & Claude Opus 4.6 lokal!",
        "• Gemma 4 (E2B, E4B, 12B): Native Audio- & Bildverarbeitung; E4B schlägt GPT-4o.",
        "• LFM 2.5 (1.2B & 2.6B): Liquid AI – extrem schnell & sparsam auf CPU/Edge."
    ]
    for b in green_bullets:
        draw.text((card_x1 + 44, cur_y), b, fill=(35, 40, 50), font=font_body)
        cur_y += 27
        
    # Section 2: GELB
    cur_y += 12
    draw.rectangle([card_x1 + 24, cur_y + 3, card_x1 + 32, cur_y + 21], fill=yellow_color)
    draw.text((card_x1 + 44, cur_y), "GELB: NUANCEN & VORBEHALTE BEACHTEN", fill=yellow_color, font=font_h2)
    
    cur_y += 30
    yellow_bullets = [
        "• K2 Horizon MoVA (Score 25): Hohes Potenzial, aber Support in llama.cpp noch experimentell.",
        "• Nemotron 3.5 Lightning: Modellqualität nur 'meh', aber 100% OFFENE Trainingsdaten!",
        "• Muse Glimmer (high): Modellqualität im Vergleich zu Qwen/Gemma eher durchschnittlich."
    ]
    for b in yellow_bullets:
        draw.text((card_x1 + 44, cur_y), b, fill=(35, 40, 50), font=font_body)
        cur_y += 27
        
    out_path = os.path.join(OUTPUT_DIR, "benchmark_open_weights.png")
    img.save(out_path)
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    generate_openai_chart()
    generate_anthropic_chart()
    generate_open_weights_chart()
    print("All 3 benchmark images generated successfully with Bahnschrift minimal style!")
