#!/usr/bin/env python3
"""Calcula e redige a prestação de contas de um processo encerrado.

Uso: python3 tools/prestacao_contas.py <caso.json> [pasta_saida]

Gera, na pasta de saída (padrão: prestacao-contas/saida/):
  <nº> - PRESTACAO DE CONTAS - <Cliente>.txt   texto para WhatsApp/e-mail
  <nº> - PRESTACAO DE CONTAS - <Cliente>.pdf   demonstrativo com termo de quitação

Ordem do cálculo (ver prestacao-contas/README.md):
  1. valor total levantado (alvará / depósito / RPV)
  2. (-) honorários de sucumbência, que pertencem ao advogado (art. 23 da Lei 8.906/94)
  3. (=) crédito do cliente = condenação + atualização monetária e juros
  4. (-) honorários contratuais, percentual e base tirados do CONTRATO
  5. (-) despesas adiantadas pelo escritório, quando houver
  6. (=) valor líquido a repassar ao cliente
"""
import json
import os
import sys
from decimal import ROUND_HALF_UP, Decimal

C = Decimal("0.01")


def d(v):
    return Decimal(str(v or 0)).quantize(C, ROUND_HALF_UP)


def brl(v):
    s = f"{d(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def pct(v):
    s = f"{Decimal(str(v)).normalize():f}".replace(".", ",")
    return f"{s}%"


def calcula(caso):
    lev = caso["levantamento"]
    dec = caso["decisao"]
    con = caso["contrato"]
    total = d(lev["valor_total"])
    nominal = sum((d(c["valor"]) for c in dec["condenacoes"]), Decimal("0"))

    # Sucumbência: valor informado no alvará/cálculo prevalece; senão, separa pelo percentual,
    # supondo que o depósito cobre condenação atualizada + sucumbência sobre ela.
    suc = lev.get("sucumbencia")
    p_suc = Decimal(str(dec.get("sucumbencia_percentual") or 0))
    if suc is not None:
        suc = d(suc)
    elif p_suc:
        suc = d(total - total / (1 + p_suc / 100))
    else:
        suc = d(0)

    credito = total - suc
    atualizacao = credito - nominal  # correção monetária + juros embutidos no levantamento

    base_tipo = con.get("base", "credito_cliente")
    base = {
        "credito_cliente": credito,          # condenação atualizada (padrão)
        "valor_total": total,                # tudo o que foi levantado
        "condenacao_nominal": nominal,       # sem atualização
    }[base_tipo]
    p_con = Decimal(str(con["percentual"]))
    hon = d(base * p_con / 100)

    # Atualização monetária retida pelo escritório, só se o contrato mandar (ex.: cláusula que
    # destina a correção de valores adiantados). Padrão: fica com o cliente e integra a base.
    atu_ret = d(atualizacao) if con.get("atualizacao_destino") == "escritorio" else d(0)

    despesas = [(x["descricao"], d(x["valor"])) for x in caso.get("despesas", [])]
    liquido = credito - hon - atu_ret - sum((v for _, v in despesas), Decimal("0"))

    if atualizacao < 0:
        raise SystemExit(
            f"Levantamento menos sucumbência ({brl(credito)}) é menor que a condenação nominal "
            f"({brl(nominal)}). Confira o valor do alvará, a sucumbência e as condenações."
        )
    return dict(total=total, suc=suc, p_suc=p_suc, credito=credito, nominal=nominal,
                atualizacao=d(atualizacao), base=d(base), base_tipo=base_tipo, p_con=p_con,
                hon=hon, atu_ret=atu_ret, despesas=despesas, liquido=d(liquido),
                escritorio=d(suc + hon + atu_ret))


BASE_TXT = {
    "credito_cliente": "sobre o valor da condenação atualizado",
    "valor_total": "sobre o valor total levantado",
    "condenacao_nominal": "sobre o valor da condenação",
}


def sep(caso, r):
    """Padrão do escritório: a sucumbência fica fora da prestação de contas do cliente."""
    return bool(r["suc"]) and caso.get("sucumbencia_separada", True)


def linhas(caso, r):
    con = caso["contrato"]
    clausula = f", cláusula {con['clausula']}" if con.get("clausula") else ""
    if sep(caso, r):   # sucumbência fora do documento do cliente
        L = [("Valor da condenação atualizada", r["credito"],
              f"condenação {brl(r['nominal'])} + atualização monetária e juros {brl(r['atualizacao'])}")]
    else:
        L = [("Valor total levantado", r["total"], "")]
    if r["suc"] and not sep(caso, r):
        q = f"{pct(r['p_suc'])} fixados na decisão; " if r["p_suc"] else ""
        L.append(("(-) Honorários de sucumbência", r["suc"],
                  f"{q}pagos pela parte contrária, pertencem ao advogado (art. 23 da Lei 8.906/94)"))
    if not sep(caso, r):
        L.append(("(=) Crédito do cliente", r["credito"],
                  f"condenação {brl(r['nominal'])} + atualização monetária e juros {brl(r['atualizacao'])}"))
    L.append(("(-) Honorários contratuais", r["hon"],
              f"{pct(r['p_con'])} {BASE_TXT[r['base_tipo']]}, conforme contrato{clausula}"))
    if r["atu_ret"]:
        ca = f", cláusula {con['clausula_atualizacao']}" if con.get("clausula_atualizacao") else clausula
        L.append(("(-) Atualização monetária e juros", r["atu_ret"],
                  f"correção e juros do período, devidos à advogada conforme contrato{ca}"))
    for desc, v in r["despesas"]:
        L.append((f"(-) {desc}", v, "despesa adiantada pelo escritório"))
    L.append(("(=) VALOR LÍQUIDO DO CLIENTE", r["liquido"], ""))
    return L


def texto(caso, r):
    """Texto curto para WhatsApp (padrão do escritório). O detalhamento completo fica no PDF."""
    dec, cli = caso["decisao"], caso["cliente"]
    re_ = caso.get("re_curto") or caso["re"]
    pag = caso.get("pagamento", {})
    conds = [f"*{brl(c['valor'])}* de {c['descricao'][0].lower() + c['descricao'][1:]}" for c in dec["condenacoes"]]
    conds = conds[0] if len(conds) == 1 else ", ".join(conds[:-1]) + " e " + conds[-1]
    base = {"condenacao_nominal": f"sobre os {brl(r['nominal'])}",
            "credito_cliente": f"sobre o valor atualizado de {brl(r['credito'])}",
            "valor_total": f"sobre o total levantado de {brl(r['total'])}"}[r["base_tipo"]]
    t = [f"Olá, {cli['nome'].split()[0]}! Tudo bem? 😊", "",
         "Ótima notícia: seu processo contra a " + re_ + " terminou e o valor já foi liberado! ✅", "",
         f"A Justiça condenou a {re_} a pagar {conds}. Com a correção e os juros, o valor ficou em "
         f"*{brl(r['credito'])}*.", "", "Como combinado no contrato:"]
    if r["suc"] and not sep(caso, r):
        t.append(f"• Honorários de sucumbência, pagos pela {re_} ao escritório: {brl(r['suc'])}")
    t.append(f"• {pct(r['p_con'])} de honorários {base}: {brl(r['hon'])}")
    if r["atu_ret"]:
        t.append(f"• Correção e juros, que ficam com o escritório: {brl(r['atu_ret'])}")
    for desc, v in r["despesas"]:
        t.append(f"• {desc}, adiantado pelo escritório: {brl(v)}")
    t += ["", f"💰 *Você recebe: {brl(r['liquido'])}*", ""]
    # padrão do escritório: a mensagem vai junto com o contrato e o comprovante do PIX já feito
    t.append(pag.get("mensagem", "Segue o contrato e o comprovante do PIX. 📎"))
    t += ["", "Foi um prazer cuidar do seu caso! Qualquer dúvida, é só chamar. 🙏", "",
          caso.get("assinatura", "Bruna Guarim Advocacia")]
    return "\n".join(t)


def pdf(caso, r, dst):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    VERM = colors.HexColor("#8B1A1A")
    n = ParagraphStyle("n", fontName="Times-Roman", fontSize=11, leading=15, alignment=4)
    h = ParagraphStyle("h", parent=n, fontName="Times-Bold", fontSize=14, alignment=1, textColor=VERM)
    s = ParagraphStyle("s", parent=n, fontSize=8.5, leading=11, textColor=colors.HexColor("#555555"))
    cli, dec, lev = caso["cliente"], caso["decisao"], caso["levantamento"]
    E = []
    logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "modelos", "marca", "logotipo-horizontal-cor.png")
    if os.path.exists(logo):
        from reportlab.platypus import Image as RLImage
        E += [RLImage(logo, width=7.5 * cm, height=7.5 * cm * 516 / 3621), Spacer(1, 14)]
    E += [Paragraph("PRESTAÇÃO DE CONTAS", h), Spacer(1, 10),
         Paragraph(f"<b>Processo:</b> {caso['processo']}<br/><b>Juízo:</b> {caso.get('juizo', '')}"
                   f"<br/><b>Cliente:</b> {cli['nome']}"
                   + (f" (CPF {cli['cpf']})" if cli.get("cpf") else "")
                   + f"<br/><b>Parte contrária:</b> {caso['re']}", n), Spacer(1, 8),
         Paragraph(f"Por {dec['tipo']} de {dec['data']}, a parte contrária foi condenada a pagar "
                   + "; ".join(f"{c['descricao'].lower()}, {brl(c['valor'])}" for c in dec["condenacoes"])
                   + (f". Em {lev['data']} foi levantado o valor da condenação"
                      + (f" ({lev['origem']})" if lev.get("origem") else "")
                      + f", que, atualizado, soma {brl(r['credito'])}." if sep(caso, r) else
                      f". Em {lev['data']} foi levantado o valor de {brl(r['total'])}"
                      + (f" ({lev['origem']})" if lev.get("origem") else "") + "."), n), Spacer(1, 10)]
    rows = [["Descrição", "Valor"]]
    for rot, v, obs in linhas(caso, r):
        txt = f"<b>{rot}</b>" + (f"<br/><font size=8.5 color='#555555'>{obs}</font>" if obs else "")
        rows.append([Paragraph(txt, n), Paragraph(f"<b>{brl(v)}</b>" if rot.startswith("(=)") else brl(v), n)])
    tb = Table(rows, colWidths=[12.5 * cm, 3.5 * cm], repeatRows=1)
    tb.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), VERM), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"), ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#999999")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F2E6E6")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    pag = caso.get("pagamento", {})
    E += [tb, Spacer(1, 14),
          Paragraph("<b>TERMO DE QUITAÇÃO.</b> Declaro que recebi a quantia líquida de "
                    f"<b>{brl(r['liquido'])}</b>"
                    + (f", por {pag['destino']}" if pag.get("destino") else "")
                    + ", conferi o demonstrativo acima e dou plena e irrevogável quitação ao escritório "
                    "quanto aos valores recebidos no processo indicado, nada mais tendo a reclamar.", n),
          Spacer(1, 40),
          Paragraph("_______________________________________<br/>" + cli["nome"],
                    ParagraphStyle("c", parent=n, alignment=1)),
          Spacer(1, 6), Paragraph("Local e data: ____________________________", n), Spacer(1, 18),
          Paragraph(("" if sep(caso, r) else "Honorários de sucumbência: art. 23 da Lei 8.906/94. ")
                    + "Honorários contratuais conforme "
                    "contrato firmado entre as partes. Valores conferidos com a decisão e o comprovante "
                    "de levantamento.", s)]
    SimpleDocTemplate(dst, pagesize=A4, leftMargin=2.5 * cm, rightMargin=2.5 * cm,
                      topMargin=2.5 * cm, bottomMargin=2 * cm,
                      title=f"Prestação de contas - {cli['nome']}").build(E)


def main():
    caso = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2] if len(sys.argv) > 2 else "prestacao-contas/saida"
    os.makedirs(out, exist_ok=True)
    r = calcula(caso)
    nome = f"{caso.get('numero', '00')} - PRESTACAO DE CONTAS - {caso['cliente']['nome']}"
    txt = texto(caso, r)
    open(os.path.join(out, nome + ".txt"), "w", encoding="utf-8").write(txt)
    pdf(caso, r, os.path.join(out, nome + ".pdf"))
    print(txt)
    if sep(caso, r):   # demonstrativo interno da sucumbência, que não vai ao cliente
        q = f"{pct(r['p_suc'])} fixados na decisão" if r["p_suc"] else "conforme alvará"
        interno = "\n".join([
            f"DEMONSTRATIVO INTERNO - NÃO ENVIAR AO CLIENTE", f"Processo nº {caso['processo']} - {caso['cliente']['nome']} x {caso['re']}", "",
            f"Valor total levantado ............ {brl(r['total'])}",
            f"(-) Honorários de sucumbência ..... {brl(r['suc'])}  ({q}; art. 23 da Lei 8.906/94)",
            f"(=) Condenação atualizada ......... {brl(r['credito'])}  (base da prestação de contas do cliente)",
            f"(-) Honorários contratuais ........ {brl(r['hon'])}",
            f"(-) Atualização retida ............ {brl(r['atu_ret'])}",
            f"(=) Líquido do cliente ............ {brl(r['liquido'])}", "",
            f"Total do escritório: sucumbência {brl(r['suc'])} + contratuais {brl(r['hon'])} + atualização {brl(r['atu_ret'])} = {brl(r['escritorio'])}"])
        open(os.path.join(out, nome.replace("PRESTACAO DE CONTAS", "SUCUMBENCIA INTERNO") + ".txt"), "w", encoding="utf-8").write(interno)
        print("\n" + interno)
    print(f"\n[conferência] escritório {brl(r['escritorio'])} + cliente {brl(r['liquido'])} + despesas "
          f"{brl(sum((v for _, v in r['despesas']), Decimal('0')))} = {brl(r['total'])}")


if __name__ == "__main__":
    main()
