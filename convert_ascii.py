import sys
import os
import re
from PIL import Image, ImageFilter
import numpy as np

ASCII_CHARS = " .:-=+*#%@"

def generate_ascii_art(image_path, width=42, height=25):
    try:
        img = Image.open(image_path).convert("L")
    except Exception as e:
        print(f"Error abriendo imagen: {e}")
        return None

    w, h = img.size

    # Crop to center face, glasses, hair and bust
    x1 = int(w * 0.12)
    x2 = int(w * 0.82)
    y1 = int(h * 0.10)
    y2 = int(h * 0.65)
    crop = img.crop((x1, y1, x2, y2))

    # Multi-scale edge detection to preserve thin glasses frames and eyes
    edges = crop.filter(ImageFilter.FIND_EDGES)
    edges_thick = edges.filter(ImageFilter.MaxFilter(7))

    # Resize edge map and base image to target grid
    e_arr = np.array(edges_thick.resize((width, height), Image.Resampling.BOX))
    b_arr = np.array(crop.resize((width, height), Image.Resampling.LANCZOS))

    lines = []
    for r in range(height):
        line = []
        for c in range(width):
            b = int(b_arr[r, c])
            e = int(e_arr[r, c])

            # Suppress outer corner artifacts (background wall)
            if r < 4 and (c < 8 or c > 32):
                char = " "
            elif r < 8 and (c < 4 or c > 37):
                char = " "
            elif c < 2 or c > 39:
                char = " "
            else:
                # Enhance glasses and facial lines
                if e > 65:
                    val = min(b, max(0, 255 - int(e * 1.2)))
                else:
                    val = b

                if val > 165:
                    char = " "
                else:
                    idx = int((1.0 - (val / 165.0)) * (len(ASCII_CHARS) - 1))
                    idx = max(0, min(len(ASCII_CHARS) - 1, idx))
                    char = ASCII_CHARS[idx]
            line.append(char)
        lines.append("".join(line))
    return lines

def format_svg_tspans(lines, x=15, start_y=30, step_y=20):
    tspans = []
    for i, line in enumerate(lines):
        y = start_y + (i * step_y)
        padded = f"{line:<44}"
        safe_line = padded.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        tspans.append(f'<tspan x="{x}" y="{y}">{safe_line}</tspan>')
    return "\n".join(tspans)

INFO_TSPAN_TEMPLATE = """<tspan x="390" y="30">anglsosa@dev</tspan> -———————————————————————————————————————————-—-
<tspan x="390" y="50" class="cc">. </tspan><tspan class="key">Role</tspan>:<tspan class="cc"> ............. </tspan><tspan class="value">Full-Stack &amp; iOS Engineer</tspan>
<tspan x="390" y="70" class="cc">. </tspan><tspan class="key">Uptime</tspan>:<tspan class="cc" id="age_data_dots"> ........... </tspan><tspan class="value" id="age_data">23 years, 2 months, 26 days</tspan>
<tspan x="390" y="90" class="cc">. </tspan><tspan class="key">Education</tspan>:<tspan class="cc"> ........ </tspan><tspan class="value">Computer Science @ BUAP</tspan>
<tspan x="390" y="110" class="cc">. </tspan><tspan class="key">Location</tspan>:<tspan class="cc"> ......... </tspan><tspan class="value">Puebla, Mexico</tspan>
<tspan x="390" y="130" class="cc">. </tspan>
<tspan x="390" y="150" class="cc">. </tspan><tspan class="key">Languages</tspan>:<tspan class="cc"> ........ </tspan><tspan class="value">Python, Swift, TypeScript</tspan>
<tspan x="390" y="170" class="cc">. </tspan><tspan class="key">Backend</tspan>:<tspan class="cc"> .......... </tspan><tspan class="value">FastAPI, PostgreSQL, Supabase</tspan>
<tspan x="390" y="190" class="cc">. </tspan><tspan class="key">Frontend</tspan>:<tspan class="cc"> ......... </tspan><tspan class="value">Next.js 14, React, Tailwind CSS</tspan>
<tspan x="390" y="210" class="cc">. </tspan><tspan class="key">Mobile</tspan>:<tspan class="cc"> ........... </tspan><tspan class="value">Native iOS (Swift), Flutter</tspan>
<tspan x="390" y="230" class="cc">. </tspan><tspan class="key">Apps</tspan>:<tspan class="cc"> ............. </tspan><tspan class="value">Librero, Jetzi Estimate (App Store)</tspan>
<tspan x="390" y="250" class="cc">. </tspan>
<tspan x="390" y="270" class="cc">. </tspan>
<tspan x="390" y="290">- Contact</tspan> -——————————————————————————————————————————————-—-
<tspan x="390" y="310" class="cc">. </tspan><tspan class="key">Email</tspan>:<tspan class="cc"> ............ </tspan><tspan class="value">angelsoatwork@gmail.com</tspan>
<tspan x="390" y="330" class="cc">. </tspan><tspan class="key">LinkedIn</tspan>:<tspan class="cc"> ......... </tspan><tspan class="value">linkedin.com/in/angel-sosa</tspan>
<tspan x="390" y="350" class="cc">. </tspan><tspan class="key">Project</tspan>:<tspan class="cc"> .......... </tspan><tspan class="value">Jetzi (jetzidigital.com)</tspan>
<tspan x="390" y="370" class="cc">. </tspan><tspan class="key">GitHub</tspan>:<tspan class="cc"> ........... </tspan><tspan class="value">anglsosa</tspan>
<tspan x="390" y="390" class="cc">. </tspan>
<tspan x="390" y="410" class="cc">. </tspan>
<tspan x="390" y="430" class="cc">. </tspan>
<tspan x="390" y="450">- GitHub Stats</tspan> -—————————————————————————————————————————-—-
<tspan x="390" y="470" class="cc">. </tspan><tspan class="key">Repos</tspan>:<tspan class="cc" id="repo_data_dots"> .... </tspan><tspan class="value" id="repo_data">--</tspan> {<tspan class="key">Contributed</tspan>: <tspan class="value" id="contrib_data">--</tspan>} | <tspan class="key">Stars</tspan>:<tspan class="cc" id="star_data_dots"> ........... </tspan><tspan class="value" id="star_data">--</tspan>
<tspan x="390" y="490" class="cc">. </tspan><tspan class="key">Commits</tspan>:<tspan class="cc" id="commit_data_dots"> ................. </tspan><tspan class="value" id="commit_data">--</tspan> | <tspan class="key">Followers</tspan>:<tspan class="cc" id="follower_data_dots"> ....... </tspan><tspan class="value" id="follower_data">--</tspan>
<tspan x="390" y="510" class="cc">. </tspan><tspan class="key">Lines of Code on GitHub</tspan>:<tspan class="cc" id="loc_data_dots">. </tspan><tspan class="value" id="loc_data">--</tspan> ( <tspan class="addColor" id="loc_add">--</tspan><tspan class="addColor">++</tspan>, <tspan id="loc_del_dots"> </tspan><tspan class="delColor" id="loc_del">--</tspan><tspan class="delColor">--</tspan> )"""

def update_svg_files(ascii_block):
    for filename in ["dark_mode.svg", "light_mode.svg"]:
        if not os.path.exists(filename):
            continue
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace ASCII art
        pattern_ascii = r'(<text x="15" y="30" fill="[^"]*" class="ascii">\n)([\s\S]*?)(</text>)'
        content = re.sub(pattern_ascii, rf"\g<1>{ascii_block}\n\3", content)

        # Replace right-side info
        pattern_info = r'(<text x="390" y="30" fill="[^"]*">\n)([\s\S]*?)(</text>)'
        content = re.sub(pattern_info, rf"\g<1>{INFO_TSPAN_TEMPLATE}\n\3", content)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Archivo actualizado: {filename}")

if __name__ == "__main__":
    img_path = sys.argv[1] if len(sys.argv) > 1 else "IMG_3879.JPG"
    lines = generate_ascii_art(img_path)
    if not lines:
        sys.exit(1)

    print("\n--- Vista Previa ASCII ---")
    for l in lines:
        print(l)
    print("--------------------------\n")

    ascii_block = format_svg_tspans(lines)
    update_svg_files(ascii_block)
