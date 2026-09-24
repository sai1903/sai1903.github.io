"""Regenerate contact.vcf. Run with your live card URL once deployed:

    python tools/make-vcard.py https://your-domain.com/card.html

A real .vcf file is used (rather than one built in JS) because iOS Safari
opens it straight into "Add to Contacts", and it still works with JS off.
"""
import base64, io, sys, datetime
from PIL import Image

ME = dict(
    last="Baratam", first="Sai Surya Kiran",
    full="Baratam Sai Surya Kiran",
    title="AI & Data Engineer",
    org="Commbricks",
    tel="+918919274754",
    email="saisuryakiranbaratam@gmail.com",
    city="Hyderabad", country="India",
    note="AI and data engineering, 10+ years. PhD research on quantum "
         "computing for AI, AGI and ASI models.",
)

url = sys.argv[1] if len(sys.argv) > 1 else ""

src = Image.open("assets/6vgicdie_surya-professional.png").convert("RGBA")
head = src.crop((178, 6, 478, 306))
flat = Image.new("RGB", head.size, (252, 249, 245))
flat.paste(head, (0, 0), head)
buf = io.BytesIO()
flat.resize((280, 280), Image.LANCZOS).save(buf, "JPEG", quality=78, optimize=True)
photo = base64.b64encode(buf.getvalue()).decode()

lines = [
    "BEGIN:VCARD", "VERSION:3.0",
    f"N:{ME['last']};{ME['first']};;;",
    f"FN:{ME['full']}",
    f"TITLE:{ME['title']}",
    f"ORG:{ME['org']}",
    f"TEL;TYPE=CELL,VOICE:{ME['tel']}",
    f"EMAIL;TYPE=INTERNET,PREF:{ME['email']}",
    f"ADR;TYPE=WORK:;;;{ME['city']};;;{ME['country']}",
]
if url:
    lines.append(f"URL:{url}")
lines += [
    f"NOTE:{ME['note']}",
    f"PHOTO;ENCODING=b;TYPE=JPEG:{photo}",
    "REV:" + datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "END:VCARD",
]

def fold(line):
    if len(line) <= 74:
        return line
    out, rest = line[:74], line[74:]
    while rest:
        out += "\r\n " + rest[:73]
        rest = rest[73:]
    return out

vcf = "\r\n".join(fold(l) for l in lines) + "\r\n"
with open("contact.vcf", "w", encoding="utf-8", newline="") as f:
    f.write(vcf)
print(f"contact.vcf written — {len(vcf)} bytes, url={url or '(none set)'}")
