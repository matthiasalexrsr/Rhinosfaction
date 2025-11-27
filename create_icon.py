#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Icon-Generator für Rhinoplastik-Anwendung
Erstellt ein einfaches medizinisches Icon
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_icon():
    """Erstellt ein medizinisches Icon für die Anwendung"""
    
    # Verzeichnis erstellen
    icon_dir = "/workspace/rhinoplastik_app/assets/icons"
    os.makedirs(icon_dir, exist_ok=True)
    
    # 64x64 Icon mit transparentem Hintergrund
    size = 64
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Medizinisches Kreuz (blau)
    cross_size = 32
    cross_x = (size - cross_size) // 2
    cross_y = (size - cross_size) // 2
    
    # Kreuz-Form
    # Horizontaler Balken
    draw.rectangle([
        cross_x - 4, cross_y - 4, 
        cross_x + cross_size + 4, cross_y + 12
    ], fill=(59, 130, 246, 255))  # Blau
    
    # Vertikaler Balken
    draw.rectangle([
        cross_x + 12, cross_y - 4, 
        cross_x + 20, cross_y + cross_size + 4
    ], fill=(59, 130, 246, 255))  # Blau
    
    # Äußerer Kreis (grau)
    margin = 4
    draw.ellipse([
        margin, margin, 
        size - margin, size - margin
    ], fill=(75, 85, 99, 255), outline=(59, 130, 246, 255), width=2)
    
    # Icon speichern
    icon_path = os.path.join(icon_dir, "app.ico")
    img.save(icon_path, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64)])
    
    print(f"✅ Icon erstellt: {icon_path}")
    return icon_path

if __name__ == "__main__":
    create_icon()