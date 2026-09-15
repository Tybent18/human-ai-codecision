"""Generate the repository demo GIF deterministically."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def generate_demo(path: Path = Path("demos/codecision-lab.gif")) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    frames = []
    modes = [
        ("DEFER", "Human authority retained", "#93a9b8"),
        ("RECOMMEND", "AI evidence displayed", "#55a8ff"),
        ("ASSIST", "Uncertainty threshold crossed", "#55e2b4"),
        ("OVERRIDE", "Critical risk · contestable", "#ff788c"),
    ]
    for active, (mode, reason, color) in enumerate(modes):
        for pulse in range(3):
            image = Image.new("RGB", (960, 540), "#07101b")
            draw = ImageDraw.Draw(image)
            draw.text((45, 35), "HUMAN × AI CODECISION", fill="#55e2b4", font=font)
            draw.text((45, 61), "SHARED AUTHORITY LABORATORY", fill="#e1edf3", font=font)
            draw.text((45, 85), "Cybersecurity event · trial 14 / 24", fill="#829baa", font=font)
            draw.rounded_rectangle((45, 125, 565, 425), 12, fill="#0d1b2b", outline="#1c3952")
            draw.text((68, 150), "SECURITY EVENT", fill="#e1edf3", font=font)
            signals = [
                ("Failed logins", 72),
                ("Geo velocity", 41),
                ("Privilege change", 88),
                ("Exfiltration", 79),
            ]
            for idx, (name, value) in enumerate(signals):
                y = 195 + idx * 48
                draw.text((68, y), name, fill="#829baa", font=font)
                draw.rounded_rectangle((205, y, 520, y + 12), 5, fill="#10243a")
                draw.rounded_rectangle(
                    (205, y, 205 + int(315 * value / 100), y + 12), 5, fill="#55a8ff"
                )
            draw.rounded_rectangle((590, 125, 915, 425), 12, fill="#0d1b2b", outline="#1c3952")
            draw.text((615, 150), "AUTHORITY POLICY", fill="#e1edf3", font=font)
            for idx, (label, _detail, row_color) in enumerate(modes):
                y = 192 + idx * 50
                fill = "#17344d" if idx <= active else "#0a1725"
                draw.rounded_rectangle((615, y, 890, y + 37), 7, fill=fill)
                marker = (
                    row_color
                    if idx == active and pulse % 2 == 0
                    else ("#526b7d" if idx > active else row_color)
                )
                draw.text((630, y + 12), label, fill=marker, font=font)
            draw.rounded_rectangle((45, 455, 915, 505), 9, fill="#10243a", outline=color)
            draw.text((65, 472), f"{mode} · {reason}", fill=color, font=font)
            frames.append(image)
    frames[0].save(
        path, save_all=True, append_images=frames[1:], duration=260, loop=0, optimize=True
    )
    return path


if __name__ == "__main__":
    print(generate_demo())
