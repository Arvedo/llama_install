import os
import pathlib
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = pathlib.Path(__file__).resolve().parent

# =============================================================================
# MINIMAL RETRO-ENGINEERING PALETTE (Bahnschrift / DIN 1451 Aesthetic)
# =============================================================================
BG_COLOR = RGBColor(16, 17, 21)          # #101115 Deep Matte Charcoal
CARD_BG = RGBColor(24, 25, 31)           # #18191F Technical Dark Slate
CARD_BG_ALT = RGBColor(20, 21, 26)       # #14151A Secondary Slate
CARD_BORDER = RGBColor(46, 48, 58)       # #2E303A Precision Hairline Border
CARD_BORDER_MUTED = RGBColor(38, 40, 48) # #262830 Ultra-subtle Border

TEXT_WHITE = RGBColor(245, 245, 247)     # #F5F5F7 Pure Crisp White
TEXT_SOFT = RGBColor(205, 208, 218)      # #C8CCD7 Technical Light Slate
TEXT_MUTED = RGBColor(140, 144, 156)     # #8C909C Neutral Slate Muted

# Restrained Accents (No Rainbow Clashing!)
ACCENT_AMBER = RGBColor(245, 158, 11)    # #F59E0B Warm Technical Amber (Theme Core)
ACCENT_GREEN = RGBColor(46, 160, 67)     # #2EA043 Muted Terminal Green
ACCENT_CORAL = RGBColor(218, 54, 51)     # #DA3633 Muted Warning Coral
ACCENT_BLUE = RGBColor(88, 166, 255)     # #58A6FF Precision Blue
ACCENT_PURPLE = RGBColor(187, 128, 247)  # #BB80F7 Muted Mauve (Accent)

FONT_HEADING = "Bahnschrift"
FONT_BODY = "Bahnschrift"
FONT_CODE = "Consolas"

# =============================================================================
# NAVIGATION BAR DEFINITION
# =============================================================================
SECTION_DEFS = [
    ("01 LANDSCHAFT", 0),      # Slides 1-3
    ("02 BENCHMARKS", 3),      # Slides 4-8
    ("03 GGUF & QUANTS", 8),   # Slides 9-11
    ("04 SETUP", 11),          # Slides 12-15
    ("05 LIVE-DEMO", 15),      # Slide 16
    ("06 FAZIT", 16),          # Slides 17-18
]

SLIDE_SECTIONS = [
    0, 0, 0,          # Slides 1, 2, 3
    1, 1, 1, 1, 1,    # Slides 4, 5, 6, 7, 8
    2, 2, 2,          # Slides 9, 10, 11
    3, 3, 3, 3,       # Slides 12, 13, 14, 15
    4,                # Slide 16
    5, 5              # Slides 17, 18
]

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    slides = []

    def set_slide_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_slide_title(slide, title_text):
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.78), Inches(11.733), Inches(0.55))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.name = FONT_HEADING
        p_title.font.size = Pt(21) if len(title_text) > 52 else Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE

    def add_card(slide, left, top, width, height, border_color=CARD_BORDER, bg_color=CARD_BG, line_width=Pt(1.0)):
        card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = line_width
        return card

    def add_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    # =========================================================================
    # SLIDE 1: TITEL & EISBRECHER
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide1)
    add_slide_title(slide1, "20-MINUTEN DEEP DIVE: LLAMA.CPP")

    c_hero = add_card(slide1, Inches(0.8), Inches(1.50), Inches(7.3), Inches(5.45))
    tb_hero = slide1.shapes.add_textbox(Inches(1.1), Inches(1.75), Inches(6.7), Inches(5.0))
    tf_h = tb_hero.text_frame
    tf_h.word_wrap = True

    p = tf_h.paragraphs[0]
    p.text = "llama.cpp"
    p.font.name = FONT_HEADING
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.space_after = Pt(6)

    p2 = tf_h.add_paragraph()
    p2.text = "Lokale LLM-Inferenz ohne Cloud-Zwang & Overhead"
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(21)
    p2.font.bold = True
    p2.font.color.rgb = ACCENT_AMBER
    p2.space_after = Pt(28)

    bullets = [
        ("Wann llama.cpp?", "Single-Stream, CPU/Misch-Deployment, Apple Silicon & Edge."),
        ("Die Macht kleiner Apps:", "Braucht dein Workflow (k)einen GPU-Cluster?"),
        ("GGUF & Quantisierung:", "Welche Quantisierung wähle ich wann?"),
        ("Live-Demo & Setup:", "Von Zero zu Token-Streaming in unter 60 Sekunden.")
    ]
    for title, desc in bullets:
        p = tf_h.add_paragraph()
        run1 = p.add_run()
        run1.text = title + "  ·  "
        run1.font.name = FONT_HEADING
        run1.font.bold = True
        run1.font.color.rgb = TEXT_WHITE
        run1.font.size = Pt(16.5)
        run2 = p.add_run()
        run2.text = desc
        run2.font.name = FONT_BODY
        run2.font.color.rgb = TEXT_MUTED
        run2.font.size = Pt(15.5)
        p.space_after = Pt(20)

    rick_morty_path = str(BASE_DIR / "assets" / "censys_exposed_instances.png")
    if os.path.exists(rick_morty_path):
        card = add_card(slide1, Inches(8.35), Inches(1.50), Inches(4.18), Inches(5.45))
        slide1.shapes.add_picture(rick_morty_path, Inches(8.74), Inches(1.66), Inches(3.40), Inches(5.12))

    add_notes(slide1, """[ZEIT: 0:00 - 1:00 | 1 Minute]
• Einstiegs-Hook & Eisbrecher (Rick-&-Morty-Meme rechts): „Wer von euch hat schon mal eine dicke GPU gekauft – nur um darauf einen Ollama-Daemon laufen zu lassen?“
• Ziel des Talks: In 20 Minuten klären wir, warum 90% aller internen Tools und Hintergrundprozesse auf Standard-Hardware blitzschnell laufen können – ohne Cloud-Kosten und ohne unnötige Wrapper.
• Gliederung: Landschaft → Benchmarks & Modelle → GGUF & Quants → Setup & CLI-Flags → Live-Demo → Fazit & Cheat Sheets.""")
    slides.append(slide1)

    # =========================================================================
    # SLIDE 2: DIE INFERENZ-LANDSCHAFT (TABELLE)
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide2)
    add_slide_title(slide2, "Die Inferenz-Landschaft: Fünf Engines im Vergleich")

    rows, cols = 6, 6
    tbl_left, tbl_top, tbl_w, tbl_h = Inches(0.8), Inches(1.50), Inches(11.733), Inches(5.45)
    table_shape = slide2.shapes.add_table(rows, cols, tbl_left, tbl_top, tbl_w, tbl_h)
    table = table_shape.table

    table.columns[0].width = Inches(2.20)  # Merkmal
    table.columns[1].width = Inches(1.88)  # Ollama
    table.columns[2].width = Inches(1.92)  # llama.cpp (highlighted)
    table.columns[3].width = Inches(1.90)  # K-Transformers
    table.columns[4].width = Inches(1.90)  # vLLM
    table.columns[5].width = Inches(1.933) # SGLang

    headers_data = ["Merkmal", "Ollama", "llama.cpp", "K-Transformers", "vLLM", "SGLang"]
    for c_idx, text in enumerate(headers_data):
        cell = table.cell(0, c_idx)
        cell.fill.solid()
        if c_idx == 2:
            cell.fill.fore_color.rgb = RGBColor(38, 40, 52)
        else:
            cell.fill.fore_color.rgb = CARD_BG
        p = cell.text_frame.paragraphs[0]
        p.text = text
        p.font.name = FONT_HEADING
        p.font.size = Pt(14.5)
        p.font.bold = True
        p.font.color.rgb = ACCENT_AMBER if c_idx == 2 else TEXT_WHITE
        p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT
        cell.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

    rows_data = [
        ("Architektur-Trenner", "Dynamic / On-Demand", "Dynamic / On-Demand", "Hybrid (CPU/GPU)", "Pre-allocated High-Throughput", "Pre-allocated High-Throughput"),
        ("Speicher-Verwaltung\n(VRAM)", "Allokiert dynamisch; gibt bei Inaktivität frei", "Minimaler Basis-VRAM; allokiert KV-Cache zur Runtime", "Hybrid: MoE im RAM, aktive Pfade auf GPU", "Reserviert vorab ~90% VRAM für PagedAttention", "Reserviert vorab fast gesamten VRAM (RadixAttention)"),
        ("Hardware-Fokus", "Lokale Rechner, Apple Silicon, Single-GPU", "CPU-only, Apple Silicon, VRAM/RAM-Offload", "Extremes Offload (große MoEs auf Heim-RAM)", "Reine Datacenter-/Cloud-GPUs, Multi-GPU", "Reine Datacenter-/Cloud-GPUs, Multi-GPU"),
        ("Batching / Durchsatz", "Gering (Single-User / wenige Anfragen)", "Limitiert (primär sequenziell / kleiner Batch)", "Limitiert auf Inferenz großer Hybrid-Modelle", "Exzellent (Continuous Batching)", "Exzellent + extrem schnell bei mehrstufigen Workflows"),
        ("Einsatz & Fazit", "Nur schnelles Ausprobieren; ungeeignet für Prod", "Ideal für Prototyping, CPU-Mischbetrieb & Edge", "Brücke: Riesen-MoEs auf Consumer-Hardware", "Standard für Serving & Produktiv-APIs", "Standard für Agenten, Structured Output & Multi-Turn")
    ]

    for r_idx, row in enumerate(rows_data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            if c_idx == 2:
                cell.fill.fore_color.rgb = RGBColor(30, 32, 42)
            else:
                cell.fill.fore_color.rgb = RGBColor(22, 23, 29) if (r_idx % 2 == 0) else CARD_BG_ALT
            
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.name = FONT_BODY
            p.font.size = Pt(12)
            if c_idx == 0:
                p.font.bold = True
                p.font.color.rgb = TEXT_WHITE
            elif c_idx == 1:
                p.font.color.rgb = ACCENT_CORAL
            elif c_idx == 2:
                p.font.bold = (r_idx == 0 or r_idx == 4)
                p.font.color.rgb = ACCENT_AMBER if (r_idx == 0 or r_idx == 4) else TEXT_WHITE
            else:
                p.font.color.rgb = TEXT_SOFT
            p.alignment = PP_ALIGN.CENTER if c_idx > 0 else PP_ALIGN.LEFT
            cell.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

    add_notes(slide2, """[ZEIT: 1:00 - 2:30 | 1.5 Minuten]
• Die zwei Lager erklären:
  - Links (Ollama, llama.cpp): Dynamisch. Startet in 1 Sekunde, belegt nur das Nötigste, blockiert Hardware nicht dauerhaft.
  - Rechts (vLLM, SGLang): Pre-allocated. Belegt sofort 90% VRAM für PagedAttention / RadixAttention, um Hunderte parallele Nutzer zu bedienen.
• K-Transformers als Sonderrolle: Hält MoE-Gewichte (z. B. DeepSeek) im normalen DDR5-System-RAM, Attention auf GPU.
• Kernaussage: Vergleicht Äpfel mit Äpfeln – llama.cpp und vLLM haben völlig unterschiedliche Zielarchitekturen!""")
    slides.append(slide2)

    # =========================================================================
    # SLIDE 3: POSITIONIERUNG: WANN LLAMA.CPP?
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide3)
    add_slide_title(slide3, "Positionierung: Wann llama.cpp?")

    c1 = add_card(slide3, Inches(0.8), Inches(1.50), Inches(5.90), Inches(5.45), border_color=ACCENT_AMBER)
    tb1 = slide3.shapes.add_textbox(Inches(1.0), Inches(1.68), Inches(5.50), Inches(5.1))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "WANN LLAMA.CPP? (DIE EINSATZFELDER)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(17.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(14)
    
    llama_points = [
        ("1. Prototyping & schnelles Testen:", "Modelle in Sekunden ohne Docker, Registry oder Daemon-Setup starten und evaluieren."),
        ("2. Single-Stream Workflows:", "Interne Entwickler-Agenten, CLI-Tools, Hintergrund-Crawler, RAG-Pipelines."),
        ("3. CPU- & Misch-Deployment:", "Vorhandene Alt-Server oder Laptops nutzen, statt teuren GPU-Cloud-Speicher zu mieten."),
        ("4. Edge & Apple Silicon:", "Nutzt Unified Memory via Metal bis zum letzten Gigabyte ohne VRAM-Kopier-Overhead."),
        ("5. Mobile & Offline Apps:", "Pocket AI Lab (iOS) & LM Playground (Android) bringen GGUF direkt aufs Smartphone."),
        ("Die Macht kleiner Apps:", "Für 90% interner Workflows reichen 20–50 Tokens/s völlig aus (kein GPU-Cluster nötig!)."),
        ("Hinweis zu Ollama:", "Für Hobbyisten nett – für planbare Latenz, Speicher-Audits und volle Parameterkontrolle ist llama.cpp der direkte Standard.")
    ]
    for title, desc in llama_points:
        p = tf1.add_paragraph()
        r1 = p.add_run()
        r1.text = title + " "
        r1.font.name = FONT_HEADING
        r1.font.bold = True
        r1.font.color.rgb = TEXT_WHITE
        r1.font.size = Pt(13)
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.color.rgb = TEXT_MUTED
        r2.font.size = Pt(12.5)
        p.space_after = Pt(11)

    meme_curve = str(BASE_DIR / "assets" / "memes" / "meme6_bell_curve.png")
    if os.path.exists(meme_curve):
        c2 = add_card(slide3, Inches(6.90), Inches(1.50), Inches(5.633), Inches(5.45), border_color=CARD_BORDER)
        # Dimensions 1774 x 887 -> 2:1 ratio. Width 5.25 -> Height 2.625
        slide3.shapes.add_picture(meme_curve, Inches(7.09), Inches(2.20), Inches(5.25), Inches(2.625))
        cap_box = slide3.shapes.add_textbox(Inches(7.09), Inches(5.05), Inches(5.25), Inches(1.00))
        cap_tf = cap_box.text_frame
        cap_tf.word_wrap = True
        cap_p = cap_tf.paragraphs[0]
        cap_p.text = "„4B on CPU is plenty for my use“"
        cap_p.font.name = FONT_HEADING
        cap_p.font.size = Pt(18)
        cap_p.font.bold = True
        cap_p.font.color.rgb = ACCENT_AMBER
        cap_p.alignment = PP_ALIGN.CENTER
        
        cap_p2 = cap_tf.add_paragraph()
        cap_p2.text = "Die Bell Curve der lokalen Inferenz: Mehr Pragmatismus, weniger VRAM-Hype."
        cap_p2.font.name = FONT_BODY
        cap_p2.font.size = Pt(13.5)
        cap_p2.font.color.rgb = TEXT_MUTED
        cap_p2.alignment = PP_ALIGN.CENTER

    add_notes(slide3, """[ZEIT: 2:30 - 4:00 | 1.5 Minuten]
• Wann llama.cpp? Genau die 5 Schlüsselbereiche: Prototyping, Single-Stream, CPU/Mischbetrieb, Apple Silicon und Mobile Apps.
• Die Macht kleiner Apps betonen: Die meisten Workflows brauchen keinen 8x H100 Cluster – 20 bis 50 T/s lokal reichen völlig aus.
• Bell-Curve-Meme aufgreifen: Am Anfang will man die größte GPU, in der Mitte verliert man sich im VRAM-Kaufrausch, und die echten Profis lassen pragmatisch 4B/8B auf der CPU laufen!
• Erwähnung: Pocket AI Lab (iOS) und LM Playground (Android).""")
    slides.append(slide3)

    # =========================================================================
    # SLIDE 4: EUER KI-EINSTIEG: CHATGPT ODER CLAUDE? (INTERAKTIVE PUBLIKUMS-FRAGE)
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide4)
    add_slide_title(slide4, "Euer KI-Einstieg: Seid ihr mit ChatGPT oder mit Claude gestartet?")

    # Left Card: Team ChatGPT / OpenAI
    c_openai = add_card(slide4, Inches(0.8), Inches(1.50), Inches(5.75), Inches(4.15), border_color=ACCENT_GREEN)
    tb_o = slide4.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.35), Inches(3.85))
    tf_o = tb_o.text_frame
    tf_o.word_wrap = True

    p = tf_o.paragraphs[0]
    p.text = "TEAM CHATGPT / OPENAI"
    p.font.name = FONT_HEADING
    p.font.size = Pt(18.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(4)

    p_sub = tf_o.add_paragraph()
    p_sub.text = "Der globale Einstiegspunkt für Millionen Entwickler"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(13)
    p_sub.font.color.rgb = TEXT_MUTED
    p_sub.space_after = Pt(11)

    o_points = [
        ("GPT-3.5 (Nov. 2022):", "Der globale Aha-Moment für Text- & Chatgenerierung."),
        ("GPT-4 (März 2023):", "Der Quantensprung: Echtes Reasoning & Code-Verständnis."),
        ("GPT-4o (Mai 2024):", "Blitzschnell, multimodal – der weltweite Cloud-Standard."),
        ("GPT-5 (Aug. 2025) & 5.2 (Dez. 2025):", "Der Sprung in autonomes Agenten-Reasoning."),
        ("GPT-5.5 (Apr. 2026) & GPT-6 Astra (Sept. 2026):", "Test-Time Compute & Frontier-Spitze."),
        ("Frage an euch:", "Wer von euch war bei GPT-3.5 / GPT-4 schon dabei?")
    ]
    for title, desc in o_points:
        p = tf_o.add_paragraph()
        r1 = p.add_run()
        r1.text = "• " + title + " "
        r1.font.name = FONT_HEADING
        r1.font.bold = True
        r1.font.color.rgb = ACCENT_GREEN if "Frage" in title else TEXT_WHITE
        r1.font.size = Pt(12.5)
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.color.rgb = TEXT_WHITE if "Frage" in title else TEXT_MUTED
        r2.font.bold = ("Frage" in title)
        r2.font.size = Pt(12)
        p.space_after = Pt(6)

    # Right Card: Team Claude / Anthropic
    c_anthropic = add_card(slide4, Inches(6.78), Inches(1.50), Inches(5.75), Inches(4.15), border_color=ACCENT_AMBER)
    tb_a = slide4.shapes.add_textbox(Inches(6.98), Inches(1.65), Inches(5.35), Inches(3.85))
    tf_a = tb_a.text_frame
    tf_a.word_wrap = True

    p = tf_a.paragraphs[0]
    p.text = "TEAM CLAUDE / ANTHROPIC"
    p.font.name = FONT_HEADING
    p.font.size = Pt(18.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(4)

    p_sub = tf_a.add_paragraph()
    p_sub.text = "Die Coding- & Nuancen-Referenz für professionelle Architekten"
    p_sub.font.name = FONT_BODY
    p_sub.font.size = Pt(13)
    p_sub.font.color.rgb = TEXT_MUTED
    p_sub.space_after = Pt(11)

    a_points = [
        ("Claude 3 Opus (März 2024):", "Erster Meilenstein, der GPT-4 im Coden spürbar deklassierte."),
        ("Claude 3.5 Sonnet (Juni 2024):", "Der globale De-facto-Standard für Entwickler-Tools."),
        ("Claude Opus 4 (Mai 2025) & 4.5 (Nov. 2025):", "Mathematisches Reasoning & Multi-File-Coding."),
        ("Claude Opus 4.6 (Feb. 2026) & 5.5 (Sept. 2026):", "Die Benchmark-Spitze proprietärer Modelle."),
        ("Frage an euch:", "Wer nutzt heute bevorzugt Claude für Architektur & Code?")
    ]
    for title, desc in a_points:
        p = tf_a.add_paragraph()
        r1 = p.add_run()
        r1.text = "• " + title + " "
        r1.font.name = FONT_HEADING
        r1.font.bold = True
        r1.font.color.rgb = ACCENT_AMBER if "Frage" in title else TEXT_WHITE
        r1.font.size = Pt(12.5)
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.color.rgb = TEXT_WHITE if "Frage" in title else TEXT_MUTED
        r2.font.bold = ("Frage" in title)
        r2.font.size = Pt(12)
        p.space_after = Pt(6)

    # Bottom Callout Card
    c_bot = add_card(slide4, Inches(0.8), Inches(5.80), Inches(11.733), Inches(1.15), border_color=CARD_BORDER_MUTED)
    tb_bot = slide4.shapes.add_textbox(Inches(1.0), Inches(5.92), Inches(11.333), Inches(0.95))
    tf_b = tb_bot.text_frame
    tf_b.word_wrap = True
    p = tf_b.paragraphs[0]
    r1 = p.add_run()
    r1.text = "DIE FUNDAMENTALE REFLEXION: "
    r1.font.name = FONT_HEADING
    r1.font.bold = True
    r1.font.color.rgb = ACCENT_AMBER
    r1.font.size = Pt(13.5)
    r2 = p.add_run()
    r2.text = "Erinnert ihr euch an das Gefühl, wie unerreichbar gut sich GPT-4 oder Claude 3 damals anfühlten? Schauen wir uns an, wo diese Modelle heute im Benchmark stehen – und wie viel dieser Intelligenz ihr heute vollkommen lokal und offline auf eurem Laptop betreiben könnt!"
    r2.font.name = FONT_BODY
    r2.font.color.rgb = TEXT_WHITE
    r2.font.size = Pt(12.5)

    add_notes(slide4, """[ZEIT: 4:00 - 4:45 | 45 Sekunden]
• Publikumsinteraktion:
  - „Hand aufs Herz: Wer von euch war bei ChatGPT 3.5 oder GPT-4 dabei?“ (Kurz Hände zählen).
  - „Und wer nutzt heute aktiv Claude – Sonnet oder Opus?“ (Hände zählen).
• Storytelling: „Erinnert euch, wie baff wir alle waren, als GPT-4 das Bar-Exam bestand oder Claude 3 Code schrieb. Wir dachten: Das geht nur in gigantischen Microsoft- oder AWS-Rechenzentren.“
• Überleitung: „Schauen wir uns an, wo die Modelle eures Einstiegs heute stehen – zuerst ChatGPT, dann Claude, und dann die Open-Weights-Realität!“""")
    slides.append(slide4)

    # =========================================================================
    # SLIDE 5: BENCHMARK 1 - OPENAI / CHATGPT FAMILIE
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide5)
    add_slide_title(slide5, "Benchmark 1: Wo steht die ChatGPT-Familie heute?")

    img_openai = str(BASE_DIR / "assets" / "benchmarks" / "benchmark_openai.png")
    if os.path.exists(img_openai):
        c_chart = add_card(slide5, Inches(0.8), Inches(1.50), Inches(11.733), Inches(5.45))
        slide5.shapes.add_picture(img_openai, Inches(0.9), Inches(1.60), Inches(11.533), Inches(5.25))

    add_notes(slide5, """[ZEIT: 4:45 - 5:30 | 45 Sekunden]
• Auf die Säulen zeigen:
  - GPT-4o (Mar): Steht bei Score 9! Dieser weltweite Standard von 2024 ist heute der unterste Balken der Grafik!
  - GPT-4.1: Score 13.
  - GPT-5 (high): Score 23.
  - GPT-5.2 (xhigh): Score 30.
  - GPT-5.5 (xhigh): Score 38.
  - GPT-6 Astra: Score 53.
• Kernaussage: „Behaltet diesen Score von 9 (GPT-4o) und 30 (GPT-5.2) im Kopf. Genau hier passiert jetzt das Unglaubliche.“""")
    slides.append(slide5)

    # =========================================================================
    # SLIDE 6: BENCHMARK 2 - ANTHROPIC / CLAUDE FAMILIE
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide6)
    add_slide_title(slide6, "Benchmark 2: Wo steht die Claude-Familie?")

    img_anthropic = str(BASE_DIR / "assets" / "benchmarks" / "benchmark_anthropic.png")
    if os.path.exists(img_anthropic):
        c_chart = add_card(slide6, Inches(0.8), Inches(1.50), Inches(11.733), Inches(5.45))
        slide6.shapes.add_picture(img_anthropic, Inches(0.9), Inches(1.60), Inches(11.533), Inches(5.25))

    add_notes(slide6, """[ZEIT: 5:30 - 6:15 | 45 Sekunden]
• Für die Claude-Fraktion:
  - Claude 3 Opus: Steht ebenfalls bei Score 9! Genau dort, wo GPT-4o steht.
  - Claude 4 Opus: Score 21.
  - Claude Opus 4.5: Score 29.
  - Claude Opus 4.6: Score 32.
  - Claude Opus 5.5: Score 58 (Spitzenreiter).
• Der Cliffhanger: „Opus 4.6 bei Score 32 ist ein absolutes Coding-Biest. Wie nah kommen wir daran ran, wenn wir KEIN Geld für Anthropic-Tokens zahlen wollen?“""")
    slides.append(slide6)

    # =========================================================================
    # SLIDE 7: BENCHMARK 3 - DIE OPEN-WEIGHTS REALITÄT
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide7)
    add_slide_title(slide7, "Benchmark 3: Open-Weights Realitäts-Check auf Augenhöhe")

    img_open = str(BASE_DIR / "assets" / "benchmarks" / "benchmark_open_weights.png")
    if os.path.exists(img_open):
        c_chart = add_card(slide7, Inches(0.8), Inches(1.50), Inches(11.733), Inches(5.45))
        slide7.shapes.add_picture(img_open, Inches(0.9), Inches(1.60), Inches(11.533), Inches(5.25))

    add_notes(slide7, """[ZEIT: 6:15 - 7:15 | 1 Minute]
• Die Sensation aufdecken:
  - Qwen 3.8 Flash-Next: Score 40! Schlägt GPT-5.5 (Score 38) und deklassiert Opus 4.6 (Score 32)!
  - Qwen 3.8 27B: Score 34! Läuft quantisiert auf einer einzigen RTX 4090 oder einem MacBook Pro mit 32 GB RAM – und schlägt Claude Opus 4.6!
  - Gemma 4 E4B: Score 9! Ein kompaktes 4B-Modell erreicht das Niveau von GPT-4o und Claude 3 Opus – und bringt native Audio- & Bildverarbeitung mit!
• Zu den gelben Pfeilen (Ehrlichkeit):
  - K2 Horizon MoVA (Score 25): Spannendes Modell, aber die llama.cpp Architekturunterstützung ist noch ganz frisch/unausgereift.
  - Nemotron 3.5 Lightning (Score 13): Qualität eher mittelmäßig ('meh'), aber ALLES ist offengelegt – 100% transparente Trainingsdaten für Enterprise-Compliance!""")
    slides.append(slide7)

    # =========================================================================
    # SLIDE 8: CHEAT SHEET: DIE BESTEN OPEN-WEIGHTS MODELLE FÜR LLAMA.CPP
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide8)
    add_slide_title(slide8, "Cheat Sheet: Die besten Open-Weights Modelle für llama.cpp")

    # Card 1: High-End Reasoning (Top-Left)
    c1 = add_card(slide8, Inches(0.8), Inches(1.46), Inches(5.75), Inches(2.40), border_color=ACCENT_GREEN)
    tb1 = slide8.shapes.add_textbox(Inches(0.95), Inches(1.56), Inches(5.45), Inches(2.22))
    tf1 = tb1.text_frame
    tf1.word_wrap = True
    p = tf1.paragraphs[0]
    p.text = "1. HIGH-END REASONING & CODING"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(4)
    c1_bullets = [
        ("Modelle & Benchmark:", "Qwen 3.8 (27B & Flash-Next) | Score 40 (schlägt GPT-5.5 & Claude Opus 4.6!)"),
        ("Modellgewichte:", "Q4_K_M ~16.5 GB  |  Q8_0 ~29.5 GB"),
        ("KV-Cache (8k Kontext):", "FP16 ~2.5 GB  →  Q8_0 (~1.2 GB via -ctk/-ctv q8_0)"),
        ("Speculative Decoding:", "+0.8 GB für Drafter / MTP (liefert 2–3x Speedup)"),
        ("VRAM-Gesamtbedarf:", "Q4: ~18.5 GB (ideal für 24 GB GPU / 32 GB RAM) | Q8: ~33 GB")
    ]
    for k, v in c1_bullets:
        p = tf1.add_paragraph()
        r1 = p.add_run(); r1.text = k + " "; r1.font.name = FONT_HEADING; r1.font.bold = True; r1.font.color.rgb = TEXT_WHITE; r1.font.size = Pt(11.5)
        r2 = p.add_run(); r2.text = v; r2.font.name = FONT_BODY; r2.font.color.rgb = TEXT_MUTED; r2.font.size = Pt(11)
        if "Q4: ~18.5 GB" in v: r2.font.color.rgb = ACCENT_GREEN
        p.space_after = Pt(3)

    # Card 2: Multimodale Allrounder (Top-Right)
    c2 = add_card(slide8, Inches(6.78), Inches(1.46), Inches(5.75), Inches(2.40), border_color=ACCENT_BLUE)
    tb2 = slide8.shapes.add_textbox(Inches(6.93), Inches(1.56), Inches(5.45), Inches(2.22))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.text = "2. MULTIMODALE ALLROUNDER (AUDIO + VISION)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(4)
    c2_bullets = [
        ("Modelle & Benchmark:", "Google Gemma 4 (E4B & 12B) | Score 9 (Audio + Vision nativ!)"),
        ("Modellgewichte:", "4B: Q4 ~2.8 GB / Q8 ~4.5 GB  |  12B: Q4 ~7.5 GB / Q8 ~13.5 GB"),
        ("mmproj (Vision/Audio):", "BF16 ~1.8 GB  →  FP8 nur ~0.9 GB (Geheimtipp AesSedai!)"),
        ("KV-Cache (8k Kontext):", "FP16 ~0.8 GB  →  Q8_0 ~0.4 GB"),
        ("VRAM-Gesamtbedarf:", "4B in Q4: ~4.1 GB (Budget-PCs/6GB GPU) | 12B in Q4: ~8.8 GB (12GB GPU)")
    ]
    for k, v in c2_bullets:
        p = tf2.add_paragraph()
        r1 = p.add_run(); r1.text = k + " "; r1.font.name = FONT_HEADING; r1.font.bold = True; r1.font.color.rgb = TEXT_WHITE; r1.font.size = Pt(11.5)
        r2 = p.add_run(); r2.text = v; r2.font.name = FONT_BODY; r2.font.color.rgb = TEXT_MUTED; r2.font.size = Pt(11)
        if "4B in Q4: ~4.1 GB" in v: r2.font.color.rgb = ACCENT_BLUE
        p.space_after = Pt(3)

    # Card 3: Ultra-Effizienz & Edge (Bottom-Left)
    c3 = add_card(slide8, Inches(0.8), Inches(3.96), Inches(5.75), Inches(2.40), border_color=ACCENT_AMBER)
    tb3 = slide8.shapes.add_textbox(Inches(0.95), Inches(4.06), Inches(5.45), Inches(2.22))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    p = tf3.paragraphs[0]
    p.text = "3. ULTRA-EFFIZIENZ & EDGE (CPU / MOBILE)"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(4)
    c3_bullets = [
        ("Modelle & Benchmark:", "Liquid AI LFM 2.5 (1.2B-Thinking & 2.6B) | Rasante CPU-Inferenz"),
        ("Modellgewichte:", "1.2B: Q4 ~0.8 GB / Q8 ~1.4 GB  |  2.6B: Q4 ~1.7 GB / Q8 ~2.9 GB"),
        ("KV-Cache & Drafter:", "LNN-Hybrid: Minimaler Cache-Bedarf (<0.3 GB), natives CoT-Thinking"),
        ("VRAM / RAM-Bedarf:", "1.2B: ~1.1 GB Total  |  2.6B: ~2.1 GB Total (in Q4)"),
        ("Hardware-Einsatz:", "Läuft extrem schnell auf CPU, Raspberry Pi & Smartphones (Pocket AI / LM)")
    ]
    for k, v in c3_bullets:
        p = tf3.add_paragraph()
        r1 = p.add_run(); r1.text = k + " "; r1.font.name = FONT_HEADING; r1.font.bold = True; r1.font.color.rgb = TEXT_WHITE; r1.font.size = Pt(11.5)
        r2 = p.add_run(); r2.text = v; r2.font.name = FONT_BODY; r2.font.color.rgb = TEXT_MUTED; r2.font.size = Pt(11)
        if "1.2B: ~1.1 GB Total" in v: r2.font.color.rgb = ACCENT_AMBER
        p.space_after = Pt(3)

    # Card 4: Open Data & Compliance (Bottom-Right)
    c4 = add_card(slide8, Inches(6.78), Inches(3.96), Inches(5.75), Inches(2.40), border_color=ACCENT_PURPLE)
    tb4 = slide8.shapes.add_textbox(Inches(6.93), Inches(4.06), Inches(5.45), Inches(2.22))
    tf4 = tb4.text_frame
    tf4.word_wrap = True
    p = tf4.paragraphs[0]
    p.text = "4. 100% OFFENE TRAININGSDATEN & COMPLIANCE"
    p.font.name = FONT_HEADING
    p.font.size = Pt(14.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE
    p.space_after = Pt(4)
    c4_bullets = [
        ("Modell & Benchmark:", "Nvidia Nemotron 3.5 Lightning (8B) | Score 13 | 100% offene Daten"),
        ("Modellgewichte (8B):", "Q4_K_M ~5.1 GB  |  Q8_0 ~9.2 GB"),
        ("KV-Cache (8k Kontext):", "FP16 ~1.0 GB  →  Q8_0 ~0.5 GB (halbiert via -ctk/-ctv q8_0)"),
        ("Drafter / MTP Head:", "+0.6 GB Drafter für schnelles Token-Streaming"),
        ("VRAM-Gesamtbedarf:", "Q4: ~6.2 GB (ideal für 8 GB Laptop-GPUs) | Q8: ~10.3 GB (12 GB VRAM)")
    ]
    for k, v in c4_bullets:
        p = tf4.add_paragraph()
        r1 = p.add_run(); r1.text = k + " "; r1.font.name = FONT_HEADING; r1.font.bold = True; r1.font.color.rgb = TEXT_WHITE; r1.font.size = Pt(11.5)
        r2 = p.add_run(); r2.text = v; r2.font.name = FONT_BODY; r2.font.color.rgb = TEXT_MUTED; r2.font.size = Pt(11)
        if "Q4: ~6.2 GB" in v: r2.font.color.rgb = ACCENT_PURPLE
        p.space_after = Pt(3)

    # Bottom Caveat Strip: K2 Horizon
    c_caveat = add_card(slide8, Inches(0.8), Inches(6.46), Inches(11.733), Inches(0.48), border_color=CARD_BORDER_MUTED)
    tb_c = slide8.shapes.add_textbox(Inches(0.95), Inches(6.50), Inches(11.433), Inches(0.40))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True
    p = tf_c.paragraphs[0]
    r1 = p.add_run()
    r1.text = "SOFTWARE-VORBEHALT: "
    r1.font.name = FONT_HEADING
    r1.font.bold = True
    r1.font.color.rgb = ACCENT_AMBER
    r1.font.size = Pt(12)
    r2 = p.add_run()
    r2.text = "K2 Horizon MoVA 36B erreicht mit Score 25 hohes Potenzial, die native llama.cpp Unterstützung ist jedoch aktuell noch experimentell."
    r2.font.name = FONT_BODY
    r2.font.color.rgb = TEXT_SOFT
    r2.font.size = Pt(11.5)

    add_notes(slide8, """[ZEIT: 7:15 - 8:30 | 1 Minute 15 Sek]
• Das ist die Orientierungsfolie für die Praxis:
  - Wer Coding & Reasoning will: Qwen 3.8 (Flash-Next oder 27B in Q4_K_M).
  - Wer Audio UND Bilder verarbeiten will: Google Gemma 4 (E4B schlägt GPT-4o, 12B schlägt GPT-4.1).
  - Wer minimale Ressourcen hat (Laptop/Handy): Liquid AI LFM 2.5.
  - Wer Firmen-Compliance & offene Daten braucht: Nvidia Nemotron 3.5 Lightning.
  - Vorbehalt bei K2 Horizon: Warten, bis der llama.cpp Main-Branch die MoVA-Architektur voll ausgereift unterstützt.
• Überleitung: „Jetzt wissen wir, WELCHE Modelle wir wollen. Aber in welchem Format laden wir sie herunter? Willkommen bei GGUF!“""")
    slides.append(slide8)

    # =========================================================================
    # SLIDE 9: GGUF FORMAT & COMMUNITY-HYPE
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide9)
    add_slide_title(slide9, "Das GGUF-Ökosystem: Warum es die Open-Source-Welt regiert")

    c_left = add_card(slide9, Inches(0.8), Inches(1.50), Inches(7.3), Inches(5.45))
    tb_left = slide9.shapes.add_textbox(Inches(1.0), Inches(1.68), Inches(6.9), Inches(5.1))
    tf_l = tb_left.text_frame
    tf_l.word_wrap = True

    p = tf_l.paragraphs[0]
    p.text = "DIE 4 SUPERKRÄFTE VON GGUF (GPT-GENERATED UNIFIED FORMAT):"
    p.font.name = FONT_HEADING
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(16)

    gguf_points = [
        ("1. Single-File Container:", "Modellgewichte, Tokenizer-Vokabular, Chat-Template & Metadaten in einer einzigen Datei. Nie wieder fehlende config.json!"),
        ("2. mmap-Schnelligkeit:", "Zero-Copy Memory Mapping. Modell startet in Sekundenschnelle direkt aus dem Dateisystem, ohne langwierige Deserialisierung."),
        ("3. Flexibles Layer-Offloading:", "Granulare Verteilung: Z. B. 24 Layer auf die GPU schieben und die restlichen 8 Layer nahtlos auf der CPU rechnen lassen."),
        ("4. Hardware-agnostisch:", "Läuft überall: x86 AVX2/AVX512, ARM64 (Apple Silicon Metal), NVIDIA CUDA, AMD ROCm, Intel SYCL & Vulkan."),
        ("Wo laden?", "Hugging Face! Die weltweite Plattform für Open Weights. Wer lädt neue Modelle am schnellsten hoch? Das schauen wir uns gleich an.")
    ]
    for title, desc in gguf_points:
        p = tf_l.add_paragraph()
        r1 = p.add_run()
        r1.text = title + " "
        r1.font.name = FONT_HEADING
        r1.font.bold = True
        r1.font.color.rgb = TEXT_WHITE
        r1.font.size = Pt(14)
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.color.rgb = TEXT_MUTED
        r2.font.size = Pt(13)
        p.space_after = Pt(14)

    meme_wen = str(BASE_DIR / "assets" / "memes" / "meme1_wen_gguf.jpg")
    meme_arsenal = str(BASE_DIR / "assets" / "memes" / "meme3_meme_arsenal.jpg")
    c_right = add_card(slide9, Inches(8.35), Inches(1.50), Inches(4.18), Inches(5.45))
    
    if os.path.exists(meme_wen):
        slide9.shapes.add_picture(meme_wen, Inches(8.55), Inches(1.68), Inches(3.78), Inches(2.4))
    if os.path.exists(meme_arsenal):
        slide9.shapes.add_picture(meme_arsenal, Inches(8.55), Inches(4.30), Inches(3.78), Inches(2.45))

    add_notes(slide9, """[ZEIT: 8:30 - 9:45 | 1 Minute 15 Sek]
• Erklären, was GGUF ausmacht: Kein Abhängigkeiten-Chaos mehr. Eine Datei reicht.
• Community-Anekdote zu den Memes: Sobald Meta, Mistral oder Qwen neue Gewichte veröffentlichen, fluten innerhalb von 5 Minuten Kommentare wie „WEN GGUF?“ HuggingFace.
• Warum? Weil erst mit GGUF 95% der Entwickler das Modell überhaupt auf ihren Laptops oder Workstations ausführen können!""")
    slides.append(slide9)

    # =========================================================================
    # SLIDE 10: QUANTISIERUNGS-MASTERY & DIE GOLDENE REGEL
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide10)
    add_slide_title(slide10, "Quantisierungs-Mastery: Mythen, Fakten & Die Goldene Regel")

    c_main = add_card(slide10, Inches(0.8), Inches(1.50), Inches(7.5), Inches(5.45))
    tb_m = slide10.shapes.add_textbox(Inches(1.0), Inches(1.68), Inches(7.1), Inches(5.1))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True

    quants_points = [
        ("16-Bit → 8-Bit (Q8_0): Immer machen!", 
         "Perplexitätsverlust < 0.05 PPL (menschlich ununterscheidbar).\n→ Halbiert den VRAM/RAM-Bedarf und verdoppelt Bandbreiten-Effizienz! F16 ist reine Verschwendung.",
         ACCENT_GREEN),
        
        ("4-Bit (Q4_K_M): Der Sweet Spot!", 
         "Reduktion auf ~25% der FP16-Originalgröße.\n→ Moderne Tensor Cores (Nvidia Ampere/Ada/Blackwell, Apple AMX) bieten optimierte Matrix-Pfade für 4-Bit.",
         ACCENT_AMBER),
        
        ("KV-Cache Quantisierung (Q8_0 / Q4_0): Mehr Kontext bei halbem VRAM!", 
         "Nicht nur Modellgewichte, auch der Kontext lässt sich quantisieren! `-ctk q8_0 -ctv q8_0` halbiert den Cache-VRAM bei langen Kontexten (z. B. 32k+) ohne spürbaren Qualitätsverlust.",
         ACCENT_BLUE),
        
        ("5-Bit & 6-Bit: Rechnerisch ineffizient (Notlösung)", 
         "Hardware rechnet in 2er-Potenzen (4, 8, 16). 5- und 6-Bit müssen zur Laufzeit bitgepackt entpackt werden. Nur sinnvoll, wenn Q8 knapp nicht in den VRAM passt.",
         TEXT_SOFT),
        
        ("Unter 4-Bit (Q2, Q3): Finger weg in Production!", 
         "Dramatischer Qualitätsabsturz ('Perplexity Cliff'): Halluzinationen, Syntaxfehler im Code und logische Repetitionen nehmen massiv zu.",
         ACCENT_CORAL),
        
        ("Faustformel / Goldene Regel:", 
         "Größeres Modell in 4-Bit schlägt kleineres Modell in 8-Bit!\nBeispiel: Ein 27B-Modell in Q4 (~16.5 GB) schlägt ein 14B-Modell in Q8 (~15 GB) in jedem Benchmark um Längen.",
         TEXT_SOFT)
    ]

    for idx, (title, desc, color) in enumerate(quants_points):
        p = tf_m.paragraphs[0] if idx == 0 else tf_m.add_paragraph()
        r1 = p.add_run()
        r1.text = title + "\n"
        r1.font.name = FONT_HEADING
        r1.font.bold = True
        r1.font.size = Pt(13.5)
        r1.font.color.rgb = color
        
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.color.rgb = TEXT_MUTED
        r2.font.size = Pt(11.5)
        p.space_after = Pt(7)

    meme_glm = str(BASE_DIR / "assets" / "memes" / "meme4_glm4_gguf.jpeg")
    meme_risitas = str(BASE_DIR / "assets" / "memes" / "meme2_careful_gguf_quants.jpeg")
    c_r = add_card(slide10, Inches(8.55), Inches(1.50), Inches(3.98), Inches(5.45))
    
    if os.path.exists(meme_glm):
        slide10.shapes.add_picture(meme_glm, Inches(8.75), Inches(1.68), Inches(3.58), Inches(2.45))
    if os.path.exists(meme_risitas):
        slide10.shapes.add_picture(meme_risitas, Inches(8.75), Inches(4.30), Inches(3.58), Inches(2.40))

    add_notes(slide10, """[ZEIT: 9:45 - 11:15 | 1.5 Minuten]
• Die wissenschaftliche Botschaft: Q8 statt F16 ist ein Geschenk. Es gibt keinen Grund für F16.
• Krumme Bits (5-Bit, 6-Bit): Erklären, dass Hardware nativ in 4, 8, 16 Bit rechnet. 5/6 Bit kosten Rechenzeit beim Entpacken.
• Memes rechts aufgreifen:
  - Oben das Unsloth-Meme: Große Freude, als Daniel Han-Chen GLM-4.6 als GGUF bringt – und dann der Schock: Q8_0 hat 379 GB!
  - Unten der Spanier (El Risitas): „It's smaller they said, it's optimized they said!“ – wenn Leute versuchen, 70B in 2-Bit zu quetschen und nur noch Müll rauskommt.
• DIE GOLDENE REGEL betonen: Mehr Parameter bei 4-Bit schlägt weniger Parameter bei 8-Bit!
• Überleitung: Wer ist eigentlich dieser 'danielhanchen' von Unsloth – und wo holt man sich GGUFs am besten?""")
    slides.append(slide10)

    # =========================================================================
    # SLIDE 11: GGUF-QUELLEN AUF HUGGING FACE: UNSLOTH & DER GEHEIMTIPP AESSEDAI
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide11)
    add_slide_title(slide11, "GGUF-Quellen auf Hugging Face: Unsloth & Underdog AesSedai")

    c_unsloth = add_card(slide11, Inches(0.8), Inches(1.50), Inches(5.75), Inches(4.45), border_color=ACCENT_BLUE)
    tb_u = slide11.shapes.add_textbox(Inches(1.0), Inches(1.68), Inches(5.35), Inches(4.1))
    tf_u = tb_u.text_frame
    tf_u.word_wrap = True

    p = tf_u.paragraphs[0]
    p.text = "DER PLATZHIRSCH: UNSLOTH"
    p.font.name = FONT_HEADING
    p.font.size = Pt(18.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(10)

    unsloth_items = [
        ("Repo:", "huggingface.co/unsloth"),
        ("Gründer:", "Daniel & Michael Han-Chen"),
        ("Das 'Release-Radar':", "Sobald Meta, Mistral oder Qwen neue Gewichte droppen, hat Unsloth oft nach 30 Minuten saubere GGUFs online."),
        ("Spezialität:", "Dynamic Quants (z. B. Q4_K_M mit partiellen FP16/Q8 Layern an kritischen Stellen) für minimalen Perplexitätsverlust."),
        ("Tipp:", "Ideal als erste Anlaufstelle, um zu prüfen, welche neuen Modelle gerade die Open-Source-Szene aufmischen.")
    ]
    for label, desc in unsloth_items:
        p = tf_u.add_paragraph()
        r1 = p.add_run(); r1.text = label + " "; r1.font.name = FONT_HEADING; r1.font.bold = True; r1.font.color.rgb = TEXT_WHITE; r1.font.size = Pt(13.5)
        r2 = p.add_run(); r2.text = desc; r2.font.name = FONT_BODY; r2.font.color.rgb = TEXT_MUTED; r2.font.size = Pt(13)
        p.space_after = Pt(10)

    c_aessedai = add_card(slide11, Inches(6.78), Inches(1.50), Inches(5.75), Inches(4.45), border_color=ACCENT_PURPLE)
    tb_a = slide11.shapes.add_textbox(Inches(6.98), Inches(1.68), Inches(5.35), Inches(4.1))
    tf_a = tb_a.text_frame
    tf_a.word_wrap = True

    p = tf_a.paragraphs[0]
    p.text = "DER GENIALE UNDERDOG: AESSEDAI"
    p.font.name = FONT_HEADING
    p.font.size = Pt(18.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE
    p.space_after = Pt(10)

    aessedai_items = [
        ("Repo:", "huggingface.co/AesSedai"),
        ("Aussprache:", "„Eis Se-dai“ (aus Robert Jordans 'The Wheel of Time')"),
        ("Underdog-Story:", "Ähnlich herausragende Qualität wie Unsloth, wird aber oft übersehen, weil die Community nicht so gigantisch ist."),
        ("Der FP8-VRAM-Hack:", "Normalerweise werden Vision Projector Files (mmproj-*.gguf) nur in BF16/FP16 bereitgestellt (1–3 GB extra VRAM)."),
        ("Das Killer-Feature:", "AesSedai liefert IMMER eine FP8-Version der mmproj-Files mit!"),
        ("Mix & Match:", "Die schlanken FP8-Vision-Dateien von AesSedai sind meist 100% kompatibel mit den Unsloth-Sprachmodellen!")
    ]
    for label, desc in aessedai_items:
        p = tf_a.add_paragraph()
        r1 = p.add_run(); r1.text = label + " "; r1.font.name = FONT_HEADING; r1.font.bold = True; r1.font.color.rgb = TEXT_WHITE; r1.font.size = Pt(13.5)
        r2 = p.add_run(); r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.color.rgb = ACCENT_AMBER if ("Killer" in label or "Hack" in label) else TEXT_MUTED
        r2.font.size = Pt(12.5)
        if "Killer" in label: r2.font.bold = True
        p.space_after = Pt(8)

    c_bot = add_card(slide11, Inches(0.8), Inches(6.15), Inches(11.733), Inches(0.80), border_color=CARD_BORDER_MUTED)
    tb_b = slide11.shapes.add_textbox(Inches(1.0), Inches(6.25), Inches(11.333), Inches(0.60))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True
    p = tf_b.paragraphs[0]
    r1 = p.add_run()
    r1.text = "BEST-PRACTICE WORKFLOW: "
    r1.font.name = FONT_HEADING
    r1.font.bold = True
    r1.font.color.rgb = ACCENT_AMBER
    r1.font.size = Pt(13.5)
    r2 = p.add_run()
    r2.text = "Modell-Check bei Unsloth starten → Bei Vision-Modellen sofort zu AesSedai wechseln und das FP8-mmproj laden → Wertvollen VRAM sparen und flüssiger arbeiten!"
    r2.font.name = FONT_BODY
    r2.font.color.rgb = TEXT_WHITE
    r2.font.size = Pt(13)

    add_notes(slide11, """[ZEIT: 11:15 - 12:30 | 1 Minute 15 Sek]
• Die beiden wichtigsten HuggingFace-Quellen vorstellen:
  - Unsloth (Daniel & Michael Han-Chen): Der Platzhirsch. Extrem schnell, saubere Dynamic Quants.
  - AesSedai: Der Underdog! Aussprache erklären: [Eis Se-dai] wie die Magierinnen aus 'Wheel of Time'.
• Das Geheimnis von AesSedai betonen:
  - Bei Vision-Modellen (Llama-Vision, Qwen-VL) liegt der Flaschenhals oft am Vision Projector (`mmproj`).
  - Offizielle Quellen und Unsloth packen den Projector meist nur in BF16 (braucht unnötig viel Speicher).
  - AesSedai quantisiert den Projector in FP8!
  - Man kann das Unsloth-Sprachmodell nehmen und die AesSedai FP8-mmproj-Datei dazustecken: Läuft perfekt und spart sofort 500 MB bis 1.5 GB VRAM!""")
    slides.append(slide11)

    # =========================================================================
    # SLIDE 12: DOWNLOAD-KOMPASS: WINDOWS & LINUX
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide12)
    add_slide_title(slide12, "GitHub-Releases entschlüsselt: Windows & Linux")

    tree_win = str(BASE_DIR / "cheatsheets" / "download_windows.png")
    if os.path.exists(tree_win):
        c_tree = add_card(slide12, Inches(0.8), Inches(1.50), Inches(7.5), Inches(5.45))
        slide12.shapes.add_picture(tree_win, Inches(0.9), Inches(1.62), Inches(7.3), Inches(5.2))

    c_box = add_card(slide12, Inches(8.55), Inches(1.50), Inches(3.98), Inches(5.45), border_color=CARD_BORDER)
    tb_box = slide12.shapes.add_textbox(Inches(8.75), Inches(1.68), Inches(3.58), Inches(5.1))
    tf_box = tb_box.text_frame
    tf_box.word_wrap = True

    p = tf_box.paragraphs[0]
    p.text = "DIE GOLDENEN REGELN FÜR WINDOWS & LINUX:"
    p.font.name = FONT_HEADING
    p.font.size = Pt(17.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(12)

    rules = [
        ("NVIDIA (RTX 50xx / Blackwell):", "CUDA 13.4 Release wählen (z. B. win-cuda-13.4-x64.zip)."),
        ("NVIDIA (RTX 40xx / 30xx / 20xx):", "CUDA 12.8 Release wählen (stabilste Performance)."),
        ("DER CUDART-FEHLER:", "Nvidia-Builds erfordern ZWEI Archive: Das Binary-Archiv UND cudart-...zip! Beide in denselben Ordner entpacken!"),
        ("Linux / Ubuntu:", "Exakt dieselbe Logik: ubuntu-cuda-12.8-x64.tar.gz + cudart."),
        ("AMD Radeon (Linux):", "ROCm 10.0 Archive nutzen (kein CUDA nötig)."),
        ("Ohne dedizierte GPU:", "Immer das CPU-Build mit AVX2/AVX512 Support wählen!")
    ]
    for title, desc in rules:
        p = tf_box.add_paragraph()
        r1 = p.add_run()
        r1.text = title + "\n" if "FEHLER" in title else title + " "
        r1.font.name = FONT_HEADING
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = ACCENT_CORAL if "FEHLER" in title else TEXT_WHITE
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.color.rgb = TEXT_WHITE if "FEHLER" in title else TEXT_MUTED
        r2.font.size = Pt(12)
        p.space_after = Pt(11)

    add_notes(slide12, """[ZEIT: 12:30 - 13:30 | 1 Minute]
• Auf die Release-Seite von llama.cpp gehen: Über 25 verschiedene ZIP-Dateien!
• Entwickler verzweifeln oft: „Welche Datei brauche ich?“
• Der Entscheidungsbaum links löst das in 5 Sekunden auf.
• WICHTIGSTE FALLSTRICKE betonen:
  - Bei Nvidia immer die `cudart`-Libraries mitnehmen, sonst startet `llama-server.exe` mit fehlender DLL!
  - Wer keine GPU hat: CPU-Builds laufen dank AVX2 erstaunlich flott.""")
    slides.append(slide12)

    # =========================================================================
    # SLIDE 13: DOWNLOAD-KOMPASS: MACOS & MOBILE APPS
    # =========================================================================
    slide13 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide13)
    add_slide_title(slide13, "Apple Silicon, Mobile & Edge: Mac, iOS & Android")

    tree_apple = str(BASE_DIR / "cheatsheets" / "download_apple_mobile.png")
    if os.path.exists(tree_apple):
        c_tree2 = add_card(slide13, Inches(0.8), Inches(1.50), Inches(7.5), Inches(5.45))
        slide13.shapes.add_picture(tree_apple, Inches(0.9), Inches(1.62), Inches(7.3), Inches(5.2))

    c_mob = add_card(slide13, Inches(8.55), Inches(1.50), Inches(3.98), Inches(5.45), border_color=CARD_BORDER)
    tb_mob = slide13.shapes.add_textbox(Inches(8.75), Inches(1.68), Inches(3.58), Inches(5.1))
    tf_mob = tb_mob.text_frame
    tf_mob.word_wrap = True

    p = tf_mob.paragraphs[0]
    p.text = "DIE MOBILE & APPLE SUPERKRÄFTE:"
    p.font.name = FONT_HEADING
    p.font.size = Pt(17.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(12)

    apple_points = [
        ("macOS Apple Silicon (M1–M5):", "llama-bin-macos-arm64.tar.gz herunterladen. Metal ist standardmäßig aktiviert!"),
        ("Unified Memory Vorteil:", "CPU und GPU teilen sich denselben 128 GB RAM-Pool – 70B Modelle laufen ohne PCIe-Flaschenhals!"),
        ("iOS App: Pocket AI Lab:", "Kostenlose App für iPhone & iPad. Ermöglicht das Laden eigener GGUF-Dateien mit nativer Metal-Beschleunigung."),
        ("Android: LM Playground:", "Freie, Open-Source Android App (lmplayground.app). Nutzt Snapdragon NPU & Adreno GPU via Vulkan."),
        ("Snapdragon X Elite / Laptops:", "Eigene Binaries mit Hexagon NPU-Unterstützung verfügbar!")
    ]
    for title, desc in apple_points:
        p = tf_mob.add_paragraph()
        r1 = p.add_run()
        r1.text = title + "\n" if "App" in title else title + " "
        r1.font.name = FONT_HEADING
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = ACCENT_AMBER if ("iOS" in title or "Android" in title) else TEXT_WHITE
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.color.rgb = TEXT_MUTED
        r2.font.size = Pt(12)
        p.space_after = Pt(12)

    add_notes(slide13, """[ZEIT: 13:30 - 14:30 | 1 Minute]
• Apple Silicon ist der Liebling von llama.cpp: Kein Kopiervorgang über PCIe. Unified Memory bedeutet: Ein 64GB Mac kann ein 30B Modell komplett in Metal halten.
• Mobile Inferenz ist kein Spielzeug mehr:
  - Pocket AI Lab (iOS): Einfach GGUF in die Dateien-App werfen und auf dem iPhone ausführen.
  - LM Playground (Android): Open-Source auf GitHub & Play Store, läuft auf modernen Chips mit 20+ Tokens/s.
• Überleitung: Wir haben das Binary, wir haben das GGUF – wie starten wir es jetzt in 3 Schritten?""")
    slides.append(slide13)

    # =========================================================================
    # SLIDE 14: DIE WICHTIGSTEN CLI-FLAGS & PARAMETER
    # =========================================================================
    slide14 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide14)
    add_slide_title(slide14, "In 3 Schritten starten & Die wichtigsten CLI-Flags")

    c_steps = add_card(slide14, Inches(0.8), Inches(1.50), Inches(11.733), Inches(1.35))
    tb_st = slide14.shapes.add_textbox(Inches(1.0), Inches(1.60), Inches(11.333), Inches(1.15))
    tf_st = tb_st.text_frame
    tf_st.word_wrap = True

    p = tf_st.paragraphs[0]
    p.text = "IN 3 SCHRITTEN ZUM STARTKLAREN LLM-SERVER:"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(6)

    steps_text = [
        ("1. ZIP entpacken:", "Release-Archiv herunterladen und in einen beliebigen Ordner entpacken (z. B. C:\\llama oder ~/llama)."),
        ("2. GGUF ablegen:", "Gewünschtes Modell von HuggingFace (z. B. via Unsloth oder AesSedai) direkt daneben speichern."),
        ("3. Server starten:", "./llama-server -m qwen27b.gguf -c 8192 -ctk q8_0 -ctv q8_0 --port 8080 (Fertig! WebUI & API aktiv).")
    ]
    for s_title, s_desc in steps_text:
        p = tf_st.add_paragraph()
        r1 = p.add_run(); r1.text = s_title + " "; r1.font.name = FONT_HEADING; r1.font.bold = True; r1.font.color.rgb = TEXT_WHITE; r1.font.size = Pt(12.5)
        r2 = p.add_run(); r2.text = s_desc; r2.font.name = FONT_BODY; r2.font.color.rgb = TEXT_MUTED; r2.font.size = Pt(12)
        if "./" in s_desc: r2.font.name = FONT_CODE; r2.font.color.rgb = ACCENT_GREEN

    rows_f, cols_f = 8, 3
    tbl_f_shape = slide14.shapes.add_table(rows_f, cols_f, Inches(0.8), Inches(3.00), Inches(11.733), Inches(4.00))
    tbl_f = tbl_f_shape.table
    tbl_f.columns[0].width = Inches(2.30)
    tbl_f.columns[1].width = Inches(2.80)
    tbl_f.columns[2].width = Inches(6.633)

    f_headers = ["Flag / Parameter", "Empfohlener Wert", "Funktion & Performance-Impact"]
    for c_i, h in enumerate(f_headers):
        cell = tbl_f.cell(0, c_i)
        cell.fill.solid()
        cell.fill.fore_color.rgb = CARD_BG
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_HEADING
        p.font.size = Pt(13.5)
        p.font.bold = True
        p.font.color.rgb = ACCENT_AMBER
        cell.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

    flags_data = [
        ("-m / --model", "pfad/zum/modell.gguf", "Pfad zur GGUF-Datei (Single-File Container mit Gewichten & Tokenizer)."),
        ("-c / --ctx-size", "8192 (oder 32768)", "Kontextgröße in Tokens. llama.cpp allokiert den KV-Cache exakt passend dazu."),
        ("-ctk / -ctv", "q8_0 (für Key & Value)", "KV-Cache Quantisierung: Halbiert den VRAM-Bedarf langer Kontexte ohne Qualitätsverlust!"),
        ("--mmproj", "pfad/zum/mmproj.gguf", "Multi-Modal Projector: Lädt Vision- & Audio-Encoder (Tipp: FP8 von AesSedai spart VRAM!)."),
        ("-md / --draft-model", "pfad/zum/drafter.gguf", "Speculative Decoding / MTP: Nutzt kleines Drafter-Modell für 2–3x Speedup (v. a. Dense-Modelle)."),
        ("-t / --threads", "Anzahl physischer CPU-Kerne", "CPU-Worker Threads. Regel: Niemals Hyperthreading-Kerne mitzählen (vermeidet Latenz-Spikes)."),
        ("--port / --host", "--port 8080 --host 0.0.0.0", "Startet sofort eine OpenAI-kompatible REST-API + eingebaute WebUI im lokalen Netzwerk.")
    ]
    for r_i, (f_name, f_val, f_desc) in enumerate(flags_data):
        cell0 = tbl_f.cell(r_i+1, 0)
        cell1 = tbl_f.cell(r_i+1, 1)
        cell2 = tbl_f.cell(r_i+1, 2)
        
        for c in [cell0, cell1, cell2]:
            c.fill.solid()
            c.fill.fore_color.rgb = RGBColor(22, 23, 29) if r_i % 2 == 0 else CARD_BG_ALT
            c.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        
        p0 = cell0.text_frame.paragraphs[0]
        p0.text = f_name
        p0.font.name = FONT_CODE
        p0.font.size = Pt(12)
        p0.font.bold = True
        p0.font.color.rgb = ACCENT_AMBER
        
        p1 = cell1.text_frame.paragraphs[0]
        p1.text = f_val
        p1.font.name = FONT_CODE
        p1.font.size = Pt(12)
        p1.font.color.rgb = TEXT_WHITE
        
        p2 = cell2.text_frame.paragraphs[0]
        p2.text = f_desc
        p2.font.name = FONT_BODY
        p2.font.size = Pt(12)
        p2.font.color.rgb = TEXT_MUTED

    add_notes(slide14, """[ZEIT: 14:00 - 15:00 | 1 Minute]
• Die 7 Flags durchgehen:
  - `-m` & `-c`: Pflichtparameter für Modell und Kontextfenster.
  - `-ctk / -ctv q8_0`: KV-Cache halbieren! Spart wertvollen VRAM bei langen Prompts.
  - `--mmproj`: Für Multimodalität (Vision/Audio) wie Gemma 4 oder Qwen-VL.
  - `-md`: Speculative Decoding / MTP – kleines Drafter-Modell rät vor, großes validiert im Pulk (2–3x Speedup bei Dense-Modellen!).
  - `-t`: Nur physische Kerne angeben.
  - `--port / --host`: Sofortige API-Bereitstellung für externe Clients.
  - Hinweis: Reasoning- und Tool-Parser sind in modernen GGUFs schon voll integriert und werden automatisch erkannt!
• Überleitung: Jetzt werfen wir genau diesen Befehl live an und schauen uns den Server an!""")
    slides.append(slide14)

    # =========================================================================
    # SLIDE 15: ZUSATZMODELLE: VISION & TURBO MIT DRAFT / MTP
    # =========================================================================
    slide15 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide15)
    add_slide_title(slide15, "Zusatzmodelle: Vision (--mmproj) & Turbo mit Draft / MTP")

    c_vision = add_card(slide15, Inches(0.8), Inches(1.50), Inches(5.75), Inches(5.45), border_color=CARD_BORDER)
    tb_v = slide15.shapes.add_textbox(Inches(1.0), Inches(1.68), Inches(5.35), Inches(5.1))
    tf_v = tb_v.text_frame
    tf_v.word_wrap = True

    p = tf_v.paragraphs[0]
    p.text = "VISION-MODELLE: DAS 2-DATEIEN-PRINZIP"
    p.font.name = FONT_HEADING
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(14)

    vision_points = [
        ("Warum zwei Dateien?", "Sprachmodell (model.gguf) und Vision Projector (mmproj-*.gguf) sind getrennt."),
        ("Der Startbefehl:", "./llama-server -m llama3-vision.gguf --mmproj mmproj-model-f16.gguf"),
        ("Die Superkraft:", "Volle OCR-, Dokumenten- & Bildanalyse lokal auf dem Rechner. DSGVO-konform für sensible Belege!"),
        ("Geheimtipp AesSedai:", "Nutzt das FP8-quantisierte mmproj von AesSedai auf HuggingFace! Spart VRAM und läuft genauso akkurat."),
        ("Native Alternative:", "Google Gemma 4 bringt Audio + Vision direkt integriert mit!")
    ]
    for title, desc in vision_points:
        p = tf_v.add_paragraph()
        r1 = p.add_run()
        r1.text = title + "\n" if "./" in desc else title + " "
        r1.font.name = FONT_HEADING
        r1.font.bold = True
        r1.font.size = Pt(13.5)
        r1.font.color.rgb = TEXT_WHITE
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = FONT_CODE if "./" in desc else FONT_BODY
        r2.font.size = Pt(12.5)
        r2.font.color.rgb = ACCENT_GREEN if "./" in desc else TEXT_MUTED
        p.space_after = Pt(12)

    c_spec = add_card(slide15, Inches(6.78), Inches(1.50), Inches(5.75), Inches(5.45), border_color=CARD_BORDER)
    tb_s = slide15.shapes.add_textbox(Inches(6.98), Inches(1.68), Inches(5.35), Inches(5.1))
    tf_s = tb_s.text_frame
    tf_s.word_wrap = True

    p = tf_s.paragraphs[0]
    p.text = "TURBO-INFERENZ: SPECULATIVE DECODING & MTP"
    p.font.name = FONT_HEADING
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(12)

    spec_points = [
        ("Das Problem:", "Große Modelle sind Memory-Bandwidth-bound (jedes Token liest alle Gewichte neu ein)."),
        ("Die Lösung (Draft Model):", "Ein winziges Draft-Modell (z. B. 0.5B) generiert 5 Token-Vorschläge blitzschnell."),
        ("Verifikation im Pulk:", "Das große Zielmodell (z. B. 27B) prüft alle 5 Tokens in EINEM EINZIGEN Vorwärtsdurchlauf!"),
        ("Startflag in llama.cpp:", "./llama-server -m qwen27b.gguf -md qwen0.5b.gguf"),
        ("MTP (Multi-Token Prediction):", "Moderne Architekturen wie DeepSeek bringen eigene MTP-Heads mit – kein zweites Modell nötig!"),
        ("Ergebnis:", "1.5x bis 2.5x höhere Generierungsrate bei mathematisch exakt identischem Output!")
    ]
    for title, desc in spec_points:
        p = tf_s.add_paragraph()
        r1 = p.add_run()
        r1.text = title + "\n" if "./" in desc else title + " "
        r1.font.name = FONT_HEADING
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = TEXT_WHITE
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = FONT_CODE if "./" in desc else FONT_BODY
        r2.font.size = Pt(12)
        r2.font.color.rgb = ACCENT_AMBER if "./" in desc else TEXT_MUTED
        p.space_after = Pt(8)

    add_notes(slide15, """[ZEIT: 15:00 - 16:00 | 1 Minute]
• Multimodalität: Zeigen, dass man mit --mmproj einfach Bilder und Audio analysieren kann. Extrem wertvoll für DSGVO-konforme Rechnungs- und Beleganalyse.
• Nochmals betonen: Holt euch die FP8 mmproj-Dateien von AesSedai! Spart wertvollen VRAM.
• Speculative Decoding / MTP: Das Konzept erklären: Ein kleines Modell rät vor, das große bestätigt im Pulk.
• Ergebnis: 1.5x bis 2.5x Speedup ohne jeden Qualitätsverlust.""")
    slides.append(slide15)

    # =========================================================================
    # SLIDE 16: LIVE-DEMO: LLAMA-SERVER IN ACTION & API-DROP-IN
    # =========================================================================
    slide16 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide16)
    add_slide_title(slide16, "LIVE-DEMO: llama-server in Action & API-Drop-In")

    c_steps_demo = add_card(slide16, Inches(0.8), Inches(1.50), Inches(6.9), Inches(5.45))
    tb_sd = slide16.shapes.add_textbox(Inches(1.0), Inches(1.68), Inches(6.5), Inches(5.1))
    tf_sd = tb_sd.text_frame
    tf_sd.word_wrap = True

    p = tf_sd.paragraphs[0]
    p.text = "DER LIVE-DEMO ABLAUF (3 MINUTEN):"
    p.font.name = FONT_HEADING
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(14)

    demo_steps = [
        ("1. Terminal-Start:", "./llama-server -m qwen27b.gguf -c 8192 -ctk q8_0 -ctv q8_0"),
        ("2. Log-Inspektion:", "mmap Ladezeit (<1s!), VRAM-Allokation, Token-Timings in der Konsole."),
        ("3. WebUI im Browser:", "Aufruf von http://localhost:8080 – sofort fertige Chat-Oberfläche."),
        ("4. Prompt-Caching:", "Zweite Frage: Cache spart Prompt-Rechenzeit komplett ein!"),
        ("5. OpenAI Drop-In API:", "http://localhost:8080/v1 – Jedes Tool funktioniert sofort:"),
        ("  • Coding in IDEs:", "Continue.dev (VS Code & JetBrains), Cursor, Cline / Roo Code, Windsurf"),
        ("  • Chat & Knowledge:", "Open-WebUI, LibreChat, AnythingLLM, Jan.ai"),
        ("  • SDKs & Notizen:", "Python openai SDK (base_url), Obsidian Copilot, LangChain, LiteLLM")
    ]
    for title, desc in demo_steps:
        p = tf_sd.add_paragraph()
        r1 = p.add_run()
        r1.text = title + " "
        r1.font.name = FONT_HEADING
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = ACCENT_AMBER if "•" in title else TEXT_WHITE
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = FONT_CODE if ("./" in desc or "http" in desc) else FONT_BODY
        r2.font.color.rgb = ACCENT_GREEN if ("./" in desc or "http" in desc) else TEXT_MUTED
        r2.font.size = Pt(12)
        p.space_after = Pt(6 if "•" in title else 9)

    c_box_bet = add_card(slide16, Inches(7.9), Inches(1.50), Inches(4.633), Inches(5.45), border_color=ACCENT_AMBER)
    tb_b = slide16.shapes.add_textbox(Inches(8.1), Inches(1.68), Inches(4.233), Inches(5.1))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True

    p = tf_b.paragraphs[0]
    p.text = "DIE PUBLIKUMS-WETTE:"
    p.font.name = FONT_HEADING
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(14)

    bet_text = [
        ("Frage ans Publikum:", "Wie viele Tokens/s schafft das Modell auf dieser Maschine?"),
        ("Typische Schätzungen:", "„5–10 T/s? Ist ja lokal...“"),
        ("Die Realität:", "Auf modernem Laptop/GPU: 35–70+ Tokens/s! Schneller als das menschliche Auge lesen kann."),
        ("Prompt Processing vs. Gen:", "llama.cpp zeigt in den Logs genau an: Prompt eval time vs. Token generation time."),
        ("Takeaway für Skeptiker:", "Lokale Inferenz fühlt sich heute flotter an als viele überlastete Cloud-APIs zur Peak-Zeit!")
    ]
    for title, desc in bet_text:
        p = tf_b.add_paragraph()
        r1 = p.add_run()
        r1.text = title + "\n" if "Realität" in title else title + " "
        r1.font.name = FONT_HEADING
        r1.font.bold = True
        r1.font.size = Pt(14)
        r1.font.color.rgb = TEXT_WHITE
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.color.rgb = ACCENT_GREEN if "Realität" in title else TEXT_MUTED
        r2.font.size = Pt(13.5)
        if "Realität" in title: r2.font.bold = True
        p.space_after = Pt(12)

    add_notes(slide16, """[ZEIT: 16:00 - 18:30 | 2.5 Minuten Live-Demo]
• JETZT ZUM TERMINAL WECHSELN!
• Befehl ausführen, Terminal auf die linke Bildschirmhälfte, Browser auf die rechte.
• Vor dem Absenden des ersten Prompts kurz fragen: „Wer wettet mit? Wie viele Tokens pro Sekunde kriegen wir raus?“
• Frage eintippen, Enter drücken, Tokens streamen sehen.
• In der Konsole zeigen: „llama_print_timings: prompt eval time = 120 ms, eval time = 28 ms per token (35.7 T/s)“.
• Zeigen: Eingebautes WebUI auf Port 8080 hat sogar Settings für Temperatur, Top-P und Grammars!""")
    slides.append(slide16)

    # =========================================================================
    # SLIDE 17: DER ARCHITEKTUR-KOMPASS & DIE 5 GOLDENEN TAKEAWAYS
    # =========================================================================
    slide17 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide17)
    add_slide_title(slide17, "Der Architektur-Kompass & Die 5 Goldenen Takeaways")

    c_flow = add_card(slide17, Inches(0.8), Inches(1.50), Inches(5.75), Inches(5.45))
    tb_fl = slide17.shapes.add_textbox(Inches(1.0), Inches(1.68), Inches(5.35), Inches(5.1))
    tf_fl = tb_fl.text_frame
    tf_fl.word_wrap = True

    p = tf_fl.paragraphs[0]
    p.text = "DER ARCHITEKTUR-KOMPASS:"
    p.font.name = FONT_HEADING
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(16)

    flow_items = [
        ("Single-Stream / CPU / Mac / Lokale Tools:", "llama.cpp", "Der unangefochtene König für schlanken Betrieb ohne GPU-Zwang."),
        ("Riesen-MoE (DeepSeek) auf Heim-Hardware:", "K-Transformers", "Gewichte im DDR5-RAM, Rechenpfade auf 1-2 GPUs."),
        ("High-Throughput Production-APIs:", "vLLM", "Continuous Batching & PagedAttention für hunderte parallele Nutzer."),
        ("Agenten & Structured Output Multi-Turn:", "SGLang", "RadixAttention für extreme KV-Cache-Wiederverwendung.")
    ]
    for trigger, tool, note in flow_items:
        p = tf_fl.add_paragraph()
        r1 = p.add_run()
        r1.text = trigger + "\n"
        r1.font.name = FONT_HEADING
        r1.font.bold = True
        r1.font.size = Pt(13.5)
        r1.font.color.rgb = TEXT_WHITE
        r2 = p.add_run()
        r2.text = "➔ " + tool + "  "
        r2.font.name = FONT_HEADING
        r2.font.bold = True
        r2.font.size = Pt(14.5)
        r2.font.color.rgb = ACCENT_AMBER if tool == "llama.cpp" else ACCENT_GREEN
        r3 = p.add_run()
        r3.text = "(" + note + ")"
        r3.font.name = FONT_BODY
        r3.font.size = Pt(12)
        r3.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(16)

    c_take = add_card(slide17, Inches(6.78), Inches(1.50), Inches(5.75), Inches(5.45), border_color=ACCENT_GREEN)
    tb_t = slide17.shapes.add_textbox(Inches(6.98), Inches(1.68), Inches(5.35), Inches(5.1))
    tf_t = tb_t.text_frame
    tf_t.word_wrap = True

    p = tf_t.paragraphs[0]
    p.text = "5 ERKENNTNISSE ZUM MITNEHMEN:"
    p.font.name = FONT_HEADING
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(16)

    takeaways = [
        ("1. llama.cpp ist Production-Ready:", "Für Single-Stream, CPU, Mac und interne Tools die kostengünstigste Engine überhaupt."),
        ("2. Ollama meiden:", "Nutzt direkte Prebuilt-Binaries für volle Transparenz und planbare Latenz."),
        ("3. Immer 8-Bit statt 16-Bit:", "Q8_0 halbiert den RAM-Bedarf ohne messbaren Qualitätsverlust."),
        ("4. Größeres Modell @ 4-Bit > Kleineres @ 8-Bit:", "Lieber 27B Q4 als 14B Q8 – Intelligenz maximieren!"),
        ("5. Keine Angst vor C++:", "Download-Kompass nutzen, ZIP entpacken, GGUF reinlegen, ./llama-server starten!")
    ]
    for title, desc in takeaways:
        p = tf_t.add_paragraph()
        r1 = p.add_run()
        r1.text = title + " "
        r1.font.name = FONT_HEADING
        r1.font.bold = True
        r1.font.size = Pt(13.5)
        r1.font.color.rgb = TEXT_WHITE
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.size = Pt(12.5)
        r2.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(12)

    add_notes(slide17, """[ZEIT: 18:30 - 19:15 | 45 Sekunden]
• Die Quintessenz zusammenfassen:
  - Wer interne Tools baut: llama.cpp.
  - Wer tausende Cloud-Kunden bedient: vLLM / SGLang.
• Die 5 Goldenen Regeln noch einmal kurz im Raum nachhallen lassen.""")
    slides.append(slide17)

    # =========================================================================
    # SLIDE 18: HANDOUT, RESSOURCEN & GITHUB REPOSITORY
    # =========================================================================
    slide18 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide18)
    add_slide_title(slide18, "Handout, Ressourcen & GitHub Repository")

    # Card 1: Repo, Cheat Sheets & GGUF Sources (Left)
    c_repo = add_card(slide18, Inches(0.8), Inches(1.50), Inches(5.75), Inches(4.80), border_color=ACCENT_BLUE)
    tb_rep = slide18.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.35), Inches(4.50))
    tf_rep = tb_rep.text_frame
    tf_rep.word_wrap = True

    p = tf_rep.paragraphs[0]
    p.text = "GITHUB REPO, CHEAT SHEETS & GGUF-HUB"
    p.font.name = FONT_HEADING
    p.font.size = Pt(17.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(12)

    left_resources = [
        ("GitHub Repository:", "Vollständige Folien, Skripte, Benchmarks & Cheat Sheets als Open-Source Repo.", ACCENT_AMBER),
        ("Download-Kompass Handout:", "Druckfertiges A4-Querformat PDF: cheatsheets/handout.pdf im Repository.", TEXT_WHITE),
        ("GGUF & Quant-Cheat Sheet:", "Kompakte Übersicht für VRAM-Rechnung, Sweet-Spots (Q4_K_M vs Q8) und CLI-Flags.", TEXT_WHITE),
        ("Unsloth AI (Hugging Face):", "huggingface.co/unsloth – Erste Anlaufstelle für brandneue GGUF-Drops & optimierte Quants.", ACCENT_GREEN),
        ("AesSedai (Underdog-Tipp):", "huggingface.co/AesSedai – Exklusive FP8 mmproj-Dateien (Vision/Audio) & speichereffiziente Quants.", ACCENT_GREEN)
    ]
    for title, desc, col in left_resources:
        p = tf_rep.add_paragraph()
        r1 = p.add_run()
        r1.text = title + " "
        r1.font.name = FONT_HEADING
        r1.font.bold = True
        r1.font.size = Pt(13)
        r1.font.color.rgb = col
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.size = Pt(12)
        r2.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(12)

    # Card 2: Engines, Clients & Benchmarks (Right)
    c_tools = add_card(slide18, Inches(6.78), Inches(1.50), Inches(5.75), Inches(4.80), border_color=CARD_BORDER)
    tb_tol = slide18.shapes.add_textbox(Inches(6.98), Inches(1.65), Inches(5.35), Inches(4.50))
    tf_tol = tb_tol.text_frame
    tf_tol.word_wrap = True

    p = tf_tol.paragraphs[0]
    p.text = "OFFIZIELLE ENGINES, CLIENTS & QUELLEN"
    p.font.name = FONT_HEADING
    p.font.size = Pt(17.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(12)

    right_resources = [
        ("llama.cpp Releases:", "github.com/ggml-org/llama.cpp/releases – Offizielle Binaries für Windows, macOS, Linux.", TEXT_WHITE),
        ("ggml Core Library:", "github.com/ggml-org/ggml – Die Low-Level C/C++ Tensor-Engine hinter llama.cpp.", TEXT_WHITE),
        ("Coding IDEs & Agenten:", "Continue.dev (VS Code / JetBrains), Cursor, Cline / Roo Code, Windsurf.", ACCENT_BLUE),
        ("Lokale Web-UIs & Chat:", "Open-WebUI (openwebui.com), LibreChat (librechat.ai), AnythingLLM.", ACCENT_BLUE),
        ("Mobile Apps (GGUF offline):", "Pocket AI Lab (iOS) · LM Playground (Android).", ACCENT_AMBER),
        ("Benchmarks & Leaderboards:", "Artificial Analysis (artificialanalysis.ai) · LMSYS Arena (lmarena.ai).", TEXT_SOFT)
    ]
    for title, desc, col in right_resources:
        p = tf_tol.add_paragraph()
        r1 = p.add_run()
        r1.text = title + " "
        r1.font.name = FONT_HEADING
        r1.font.bold = True
        r1.font.size = Pt(12.5)
        r1.font.color.rgb = col
        r2 = p.add_run()
        r2.text = desc
        r2.font.name = FONT_BODY
        r2.font.size = Pt(11.5)
        r2.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(9)

    # Bottom Banner: Q&A
    c_qa = add_card(slide18, Inches(0.8), Inches(6.45), Inches(11.733), Inches(0.50), border_color=ACCENT_GREEN)
    tb_qa = slide18.shapes.add_textbox(Inches(0.95), Inches(6.49), Inches(11.433), Inches(0.42))
    tf_qa = tb_qa.text_frame
    tf_qa.word_wrap = True
    p_qa = tf_qa.paragraphs[0]
    p_qa.text = "VIELEN DANK FÜR EURE AUFMERKSAMKEIT!  ·  ZEIT FÜR FRAGEN & DISKUSSION"
    p_qa.font.name = FONT_HEADING
    p_qa.font.size = Pt(14)
    p_qa.font.bold = True
    p_qa.font.color.rgb = ACCENT_GREEN
    p_qa.alignment = PP_ALIGN.CENTER

    add_notes(slide18, """[ZEIT: 19:15 - 20:00 | 45 Sekunden + Q&A]
• Auf die bereitgestellten Ressourcen verweisen:
  - GitHub Repo mit allen Folien, Cheat Sheets und Beispielskripten.
  - Handout-PDF im Ordner cheatsheets/handout.pdf zum direkten Ausdrucken.
  - Empfohlene GGUF-Quellen: Unsloth für schnelle Drops & MoE-Quants; AesSedai für FP8 mmproj-Dateien.
  - Tools für den Alltag: Continue.dev in VS Code, Open-WebUI und Smartphone-Apps.
• Herzlicher Dank an das Publikum und Diskussion / Q&A eröffnen!""")
    slides.append(slide18)

    # =========================================================================
    # ADD CLICKABLE AGENDA NAVIGATION BAR TO ALL 18 SLIDES
    # =========================================================================
    section_targets = [slides[target_idx] for name, target_idx in SECTION_DEFS]

    bar_y = Inches(0.32)
    bar_h = Inches(0.34)
    x_start = Inches(0.8)
    box_w = Inches(1.85)
    gap = Inches(0.126)

    for slide_idx, slide in enumerate(slides):
        active_sec = SLIDE_SECTIONS[slide_idx]
        for sec_i, (sec_name, _) in enumerate(SECTION_DEFS):
            box_x = x_start + sec_i * (box_w + gap)
            is_active = (sec_i == active_sec)
            
            nav_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, box_x, bar_y, box_w, bar_h)
            nav_box.fill.solid()
            if is_active:
                nav_box.fill.fore_color.rgb = ACCENT_AMBER
                nav_box.line.color.rgb = ACCENT_AMBER
                nav_box.line.width = Pt(1.0)
            else:
                nav_box.fill.fore_color.rgb = CARD_BG
                nav_box.line.color.rgb = CARD_BORDER
                nav_box.line.width = Pt(0.75)
            
            # Interactive Click Action to target section slide
            nav_box.click_action.target_slide = section_targets[sec_i]

            tf = nav_box.text_frame
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf.word_wrap = False
            tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
            p = tf.paragraphs[0]
            p.text = sec_name
            p.font.name = FONT_HEADING
            p.font.size = Pt(9.5)
            p.font.bold = True
            p.font.color.rgb = RGBColor(16, 17, 21) if is_active else TEXT_MUTED
            p.alignment = PP_ALIGN.CENTER

    output_path = BASE_DIR / "llama_cpp_20min_praesentation.pptx"
    prs.save(str(output_path))
    print(f"SUCCESS: Created PowerPoint presentation with 18 slides at {output_path}")

if __name__ == "__main__":
    create_presentation()
