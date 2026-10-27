#!/usr/bin/env python3
"""Insere imagens de prova logo abaixo de cada faixa cinza "DOC. Nº xx" de uma petição .docx.

Uso: python3 tools/insert_provas.py <entrada.docx> <saida.docx> <mapa.json>

mapa.json: {"05": {"images": [{"path": "...png", "height_cm": 9}], "gap_cm": 0.4}, ...}
A chave é o número do documento ("05", "10"...). Imagens do mesmo documento ficam lado a lado,
centralizadas, no mesmo parágrafo. O texto da petição não é alterado.
"""
import json
import re
import sys

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm
from docx.text.paragraph import Paragraph

USEFUL_CM = 16.0  # 9071 DXA


def main(src, dst, mapa_path):
    mapa = json.load(open(mapa_path, encoding="utf8"))
    d = docx.Document(src)
    feitos = set()
    for tbl in d.tables:
        txt = tbl.rows[0].cells[0].text.strip()
        m = re.match(r"DOC\. Nº (\d+)", txt)
        if not m or m.group(1) not in mapa or m.group(1) in feitos:
            continue
        num = m.group(1)
        spec = mapa[num]
        # a imagem entra numa 2ª linha da própria tabela da faixa, que não quebra de página,
        # e a faixa fica "junto com a próxima", para as duas nunca se separarem
        for p in tbl.rows[0].cells[0].paragraphs:
            p.paragraph_format.keep_with_next = True
        for row in tbl.rows:
            trPr = row._tr.get_or_add_trPr()
            if trPr.find(qn("w:cantSplit")) is None:
                trPr.append(OxmlElement("w:cantSplit"))
        nova = tbl.add_row()
        trPr = nova._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        cell = nova.cells[0]
        par = cell.paragraphs[0]
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.space_before = docx.shared.Pt(6)
        par.paragraph_format.space_after = docx.shared.Pt(6)
        imgs = spec["images"]
        for i, im in enumerate(imgs):
            run = par.add_run()
            if im.get("width_cm"):
                run.add_picture(im["path"], width=Cm(im["width_cm"]))
            else:
                run.add_picture(im["path"], height=Cm(im["height_cm"]))
            if i < len(imgs) - 1:
                par.add_run(" " * 2)
        feitos.add(num)
    faltam = set(mapa) - feitos
    if faltam:
        sys.exit("faixas não encontradas: " + ", ".join(sorted(faltam)))
    d.save(dst)
    print("ok", dst, "documentos com imagem:", len(feitos))


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
