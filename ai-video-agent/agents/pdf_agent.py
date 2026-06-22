import sys
import os
from pypdf import PdfReader

# Accept PDF path from command line or prompt
if len(sys.argv) > 1:
    pdf_path = sys.argv[1]
else:
    pdf_path = input("Enter PDF path: ").strip()

if not os.path.exists(pdf_path):
    print(f"❌ File not found: {pdf_path}")
    sys.exit(1)

print(f"📄 Reading: {pdf_path}")

reader = PdfReader(pdf_path)
text = ""

for i, page in enumerate(reader.pages):
    page_text = page.extract_text()
    if page_text:
        text += page_text + "\n"

os.makedirs("data", exist_ok=True)

with open("data/content.txt", "w", encoding="utf-8") as f:
    f.write(text)

print(f"✅ PDF content extracted → data/content.txt")
print(f"📊 Pages: {len(reader.pages)} | Characters: {len(text)}")