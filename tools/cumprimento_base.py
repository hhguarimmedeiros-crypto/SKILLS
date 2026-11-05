#!/usr/bin/env python3
"""Funções para preencher o modelo padrão de cumprimento de sentença (modelos/MODELO PADRAO - ...docx).

par(p, '...**negrito**...')  reescreve o parágrafo mantendo a formatação do primeiro run
cel(cell, ['linha 1', '**linha 2**'])  reescreve as linhas de uma célula
apaga_par(p), apaga_linhas(tabela, [índices])
"""
import copy, re

def _seg(txt):
    return [(s[2:-2], True) if s.startswith('**') else (s, None) for s in re.split(r'(\*\*.+?\*\*)', txt) if s]

def par(p, txt, bold_padrao=None):
    tpl = copy.deepcopy(p.runs[0]._r)
    for r in list(p.runs): r._r.getparent().remove(r._r)
    for s, b in _seg(txt):
        r = copy.deepcopy(tpl); p._p.append(r)
        from docx.text.run import Run
        run = Run(r, p); run.text = s; run.bold = b if b else bold_padrao

def cel(c, linhas):
    ps = c.paragraphs
    while len(ps) < len(linhas):
        novo = copy.deepcopy(ps[-1]._p); ps[-1]._p.addnext(novo); ps = c.paragraphs
    for p in ps[len(linhas):]: p._p.getparent().remove(p._p)
    for p, t in zip(c.paragraphs, linhas):
        b = p.runs[0].bold if p.runs else None
        par(p, t, bold_padrao=b)

def apaga_par(p): p._p.getparent().remove(p._p)

def apaga_linhas(t, idx):
    rows = t.rows
    for i in sorted(idx, reverse=True): t._tbl.remove(rows[i]._tr)
