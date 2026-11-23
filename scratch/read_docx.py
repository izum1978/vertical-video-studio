import zipfile
import xml.etree.ElementTree as ET

z = zipfile.ZipFile('Промпты_и_план_обучения_Qwen.docx')
tree = ET.fromstring(z.read('word/document.xml'))
ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

paras = []
for p in tree.iter(f'{ns}p'):
    texts = [node.text for node in p.iter(f'{ns}t') if node.text]
    if texts:
        paras.append(''.join(texts))

with open('scratch/plan_qwen_text.txt', 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(paras))

print(f"Total paragraphs: {len(paras)}")
for i, p in enumerate(paras[:25]):
    print(f"--- P{i} ---")
    print(p[:150])
