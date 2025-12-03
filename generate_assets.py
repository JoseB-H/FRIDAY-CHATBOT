from PIL import Image, ImageDraw, ImageFont
import os

def create_avatar(filename, color, text, text_color="white"):
    size = (100, 100)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    
    draw.ellipse([0, 0, 100, 100], fill=color)
    
    
    try:  
        draw.text((35, 35), text, fill=text_color, font_size=40)
    except:
        draw.text((40, 40), text, fill=text_color)
        
    img.save(f"assets/{filename}")
    print(f"Created {filename}")

if not os.path.exists("assets"):
    os.makedirs("assets")

create_avatar("avatar_friday.png", "#00A8E8", "F")

create_avatar("avatar_user.png", "#4A4A4A", "U")
