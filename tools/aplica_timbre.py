#!/usr/bin/env python3
"""Aplica o timbre do escritório (logo no cabeçalho, endereço no rodapé com filete dourado) a um .docx.

Uso: python3 tools/aplica_timbre.py <entrada.docx> modelos/marca/logotipo-horizontal-cor.png <saida.docx>
"""
import sys, docx
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
src, logo, dst = sys.argv[1:4]
d = docx.Document(src)
for s in d.sections:
    s.header_distance = Cm(1.0); s.footer_distance = Cm(0.8)
    s.top_margin = Cm(3.3); s.bottom_margin = Cm(2.2)
    s.different_first_page_header_footer = False
    h = s.header; h.is_linked_to_previous = False
    p = h.paragraphs[0]; p.text = ''; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(logo, width=Cm(7.5))
    f = s.footer; f.is_linked_to_previous = False
    fp = f.paragraphs[0]; fp.text = ''; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # filete dourado acima do rodapé
    pPr = fp._p.get_or_add_pPr(); bd = OxmlElement('w:pBdr'); top = OxmlElement('w:top')
    for k, v in (('val','single'),('sz','4'),('space','4'),('color','987146')): top.set(qn('w:'+k), v)
    bd.append(top)
    jc = pPr.find(qn('w:jc'))  # pBdr precisa vir antes de jc no esquema
    (jc.addprevious(bd) if jc is not None else pPr.append(bd))
    r = fp.add_run('Av. Dr. Hélio Ribeiro, nº 525, Bairro Alvorada, Edifício Helbor Dual Business Office & Corporate, Sala 714, 7º andar, Cuiabá/MT, CEP 78.048-250')
    r.font.size = Pt(8); r.font.name = 'Palatino Linotype'; r.font.color.rgb = RGBColor(0x0F, 0x38, 0x49)
d.save(dst)
