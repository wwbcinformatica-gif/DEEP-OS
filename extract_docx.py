import sys
import zipfile
from xml.etree import ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

docx_path = r'C:\DEEP-AUREA\relatorio.docx'
with zipfile.ZipFile(docx_path, 'r') as z:
    # Read document.xml
    xml_content = z.read('word/document.xml')
    root = ET.fromstring(xml_content)
    
    # Namespaces
    ns = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
        'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
        'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
        'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
    }
    
    # Extract all text
    paragraphs = root.findall('.//w:p', ns)
    for p in paragraphs:
        texts = []
        for t in p.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
            if t.text:
                texts.append(t.text)
        if texts:
            line = ''.join(texts)
            print(line)
        else:
            print()
    
    # Also look for tables
    tables = root.findall('.//w:tbl', ns)
    for tbl_idx, tbl in enumerate(tables):
        print(f'\n[TABELA {tbl_idx + 1}]')
        rows = tbl.findall('.//w:tr', ns)
        for row in rows:
            cells = row.findall('.//w:tc', ns)
            cell_texts = []
            for cell in cells:
                cell_paras = cell.findall('.//w:p', ns)
                para_texts = []
                for cp in cell_paras:
                    t_elems = cp.findall('.//w:t', ns)
                    ct = ''.join([t.text or '' for t in t_elems])
                    para_texts.append(ct)
                cell_texts.append(' | '.join(para_texts))
            print(' || '.join(cell_texts))
