from pypdf import PdfReader

pdf_path = input("Enter PDF path: ")

reader = PdfReader(pdf_path)

text = ""

for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
        text += page_text + "\n"

with open("data/content.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("✅ PDF content extracted to content.txt")
print("Characters:", len(text))