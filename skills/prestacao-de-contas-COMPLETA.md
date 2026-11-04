---
name: prestacao-de-contas
description: Calcula e redige a prestação de contas ao cliente quando o processo termina e o valor é levantado, no padrão do escritório Bruna Guarim Advocacia & Direito do Passageiro. Use SEMPRE que receber sentença, acórdão, alvará ou comprovante de depósito junto com o contrato de honorários e for preciso dizer quanto o cliente recebe. Desconta honorários de sucumbência, honorários contratuais (percentual e base tirados do contrato) e atualização monetária quando o contrato a destina ao escritório. Entrega texto para WhatsApp/e-mail e PDF com demonstrativo e termo de quitação. Ativa para "prestação de contas", "quanto o cliente recebe", "repasse ao cliente", "alvará levantado", "pagamento do processo", "calcular honorários do êxito".
---

# Prestação de contas ao cliente

Entram: **sentença ou acórdão** (e a decisão que fixou o valor final, se houver), **contrato de honorários** e, quando houver, **alvará ou comprovante do levantamento**. Saem: texto para o cliente e PDF com demonstrativo e termo de quitação.

## 1. Leitura dos documentos

Leia tudo antes de calcular (`pdftotext -layout`; se não sair texto, `pdftoppm -r 70 -png` e leia a imagem; `.docx` com python-docx).

| Documento | O que extrair |
|---|---|
| Sentença / acórdão | tipo e data; cada condenação com valor; percentual de sucumbência e sua base; marcos de correção e juros. **O acórdão prevalece sobre a sentença no que reformou**: majoração da sucumbência (art. 85, § 11, do CPC), redução do dano moral, exclusão de pedido. No Juizado, a sentença de 1º grau não tem sucumbência (art. 55 da Lei 9.099/95); ela só aparece no acórdão contra o recorrente vencido. |
| Contrato | **percentual dos honorários contratuais**, **base de cálculo** e número da cláusula; destino da atualização monetária; despesas reembolsáveis. **O percentual sempre sai do contrato enviado, nunca se presume.** Sem contrato, pare e peça. |
| Alvará / comprovante | valor total levantado, data, origem; se separa a sucumbência, use esse valor. |

## 2. Montagem do caso

Monte um JSON no formato do **Anexo A**:

- `contrato.percentual` e `contrato.clausula`: do contrato.
- `contrato.base`: `credito_cliente` (condenação atualizada, padrão), `valor_total` (tudo o que foi levantado) ou `condenacao_nominal` (sem correção), conforme a redação da cláusula.
- `contrato.atualizacao_destino`: omita (a atualização é do cliente e entra na base) ou `"escritorio"` só se o contrato destinar a atualização monetária ao escritório.
- `levantamento.sucumbencia`: preencha quando o alvará ou o cálculo trouxer o valor separado. Em branco, o script separa pelo percentual da decisão, supondo que o depósito cobre condenação atualizada + sucumbência sobre ela.
- `despesas`: custas, preparo, perícia adiantados pelo escritório e reembolsáveis pelo contrato.
- `cliente.tratamento`: "Olá," / "Prezada" / "Prezado".

## 3. Cálculo

```bash
cat > /tmp/prestacao_contas.py <<'PY'
(cole aqui o script do Anexo B)
PY
python3 /tmp/prestacao_contas.py caso.json /mnt/user-data/outputs
```

Ordem: valor levantado, (-) honorários de sucumbência (art. 23 da Lei 8.906/94), (=) crédito do cliente (condenação + atualização monetária e juros), (-) honorários contratuais, (-) atualização se do escritório, (-) despesas, (=) líquido do cliente. A última linha impressa confere escritório + cliente + despesas = total levantado.

O script **para com erro** se o levantamento menos a sucumbência for menor que a condenação nominal: indica valor digitado errado, pagamento parcial ou condenação reduzida no acórdão. Investigue, não force.

Sem ambiente de código: faça a mesma conta à mão, arredondando cada linha em centavos, e mostre a soma de conferência.

## 4. Conferência antes de entregar

- condenações batem com o dispositivo da **decisão final**, não com os pedidos da inicial;
- percentual e base batem com a cláusula citada;
- depósito parcial: diga que a prestação é parcial e que o saldo segue em cumprimento de sentença;
- abra o PDF renderizado e olhe a página;
- texto sem travessões, com valores em R$ 0.000,00.

## 5. Entrega

1. texto pronto para colar no WhatsApp (negrito com `*`);
2. PDF do demonstrativo com termo de quitação;
3. no retorno: os números usados e de onde saiu cada um (folha da decisão, cláusula do contrato, alvará) e qualquer divergência encontrada.

Antes do primeiro cálculo da conversa, grave o script do **Anexo B** em `/tmp/prestacao_contas.py`, exatamente como está, e grave o JSON do caso em `caso.json`.

---

## Anexo A. Modelo do caso (`caso.json`)

```json
{
  "numero": "00",
  "processo": "0000000-00.2025.8.11.0003",
  "juizo": "Juizado Especial Cível de Rondonópolis/MT",
  "re": "Companhia Aérea Exemplo S.A.",
  "cliente": {"nome": "Maria Exemplo da Silva", "cpf": "000.000.000-00", "tratamento": "Olá,"},
  "decisao": {
    "tipo": "acórdão da Turma Recursal",
    "data": "10/08/2026",
    "condenacoes": [
      {"descricao": "Danos morais", "valor": 6000},
      {"descricao": "Danos materiais (restituição da passagem)", "valor": 1250.40}
    ],
    "sucumbencia_percentual": 15
  },
  "levantamento": {"valor_total": 9480.62, "data": "28/10/2026", "origem": "alvará eletrônico"},
  "contrato": {"percentual": 30, "base": "credito_cliente", "clausula": "3ª"},
  "despesas": [],
  "pagamento": {"destino": "PIX na chave informada pela cliente", "prazo": "06/11/2026"}
}
```

## Anexo B. Script de cálculo (`prestacao_contas.py`)

```python
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


def linhas(caso, r):
    con = caso["contrato"]
    clausula = f", cláusula {con['clausula']}" if con.get("clausula") else ""
    L = [("Valor total levantado", r["total"], "")]
    if r["suc"]:
        q = f"{pct(r['p_suc'])} fixados na decisão; " if r["p_suc"] else ""
        L.append(("(-) Honorários de sucumbência", r["suc"],
                  f"{q}pagos pela parte contrária, pertencem ao advogado (art. 23 da Lei 8.906/94)"))
    L.append(("(=) Crédito do cliente", r["credito"],
              f"condenação {brl(r['nominal'])} + atualização monetária e juros {brl(r['atualizacao'])}"))
    L.append(("(-) Honorários contratuais", r["hon"],
              f"{pct(r['p_con'])} {BASE_TXT[r['base_tipo']]}, conforme contrato{clausula}"))
    if r["atu_ret"]:
        L.append(("(-) Atualização monetária", r["atu_ret"], f"conforme contrato{clausula}"))
    for desc, v in r["despesas"]:
        L.append((f"(-) {desc}", v, "despesa adiantada pelo escritório"))
    L.append(("(=) VALOR LÍQUIDO DO CLIENTE", r["liquido"], ""))
    return L


def texto(caso, r):
    dec, lev, cli = caso["decisao"], caso["levantamento"], caso["cliente"]
    trat = cli.get("tratamento", "Prezado(a)")
    t = [f"*PRESTAÇÃO DE CONTAS*", f"Processo nº {caso['processo']}",
         f"{cli['nome']} x {caso['re']}", "", f"{trat} {cli['nome'].split()[0]},", "",
         f"Temos uma ótima notícia: o seu processo contra {caso['re']} foi concluído e o valor já foi "
         f"levantado. Segue a prestação de contas, com cada valor explicado.", "",
         f"*1. O que a Justiça decidiu*",
         f"Por {dec['tipo']} de {dec['data']}, {caso['re']} foi condenada a pagar:"]
    t += [f"• {c['descricao']}: {brl(c['valor'])}" for c in dec["condenacoes"]]
    t += ["", "*2. O que foi recebido*",
          f"Em {lev['data']}, foi levantado {brl(r['total'])}"
          + (f" ({lev['origem']})" if lev.get("origem") else "")
          + ". Esse valor inclui a correção monetária e os juros do período"
          + (" e os honorários de sucumbência fixados pelo juiz." if r["suc"] else "."),
          "", "*3. Demonstrativo*"]
    for rot, v, obs in linhas(caso, r):
        neg = rot.startswith("(=) VALOR")
        t.append(f"{'*' if neg else ''}{rot}: {brl(v)}{'*' if neg else ''}")
        if obs:
            t.append(f"   _{obs}_")
    t += ["", "*4. Entenda os descontos*"]
    if r["suc"]:
        t.append("• Os honorários de sucumbência não saem do seu bolso: são pagos pela empresa "
                 "condenada e a lei os destina ao advogado.")
    t.append("• Os honorários contratuais são os combinados no contrato que você assinou, "
             "calculados sobre o que você efetivamente recebeu.")
    pag = caso.get("pagamento", {})
    t += ["", "*5. Pagamento*",
          f"Vamos transferir *{brl(r['liquido'])}* "
          + (f"para {pag['destino']}" if pag.get("destino") else "para a conta que você indicar")
          + (f" até {pag['prazo']}" if pag.get("prazo") else "") + ".",
          "Ao receber, pedimos que assine o termo de quitação em anexo.", "",
          "Foi uma alegria cuidar do seu caso. Qualquer dúvida, estamos à disposição!", "",
          caso.get("assinatura", "Bruna Guarim Advocacia & Direito do Passageiro")]
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
    E = [Paragraph("PRESTAÇÃO DE CONTAS", h), Spacer(1, 10),
         Paragraph(f"<b>Processo:</b> {caso['processo']}<br/><b>Juízo:</b> {caso.get('juizo', '')}"
                   f"<br/><b>Cliente:</b> {cli['nome']}"
                   + (f" (CPF {cli['cpf']})" if cli.get("cpf") else "")
                   + f"<br/><b>Parte contrária:</b> {caso['re']}", n), Spacer(1, 8),
         Paragraph(f"Por {dec['tipo']} de {dec['data']}, a parte contrária foi condenada a pagar "
                   + "; ".join(f"{c['descricao'].lower()}, {brl(c['valor'])}" for c in dec["condenacoes"])
                   + f". Em {lev['data']} foi levantado o valor de {brl(r['total'])}"
                   + (f" ({lev['origem']})" if lev.get("origem") else "") + ".", n), Spacer(1, 10)]
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
          Paragraph("Honorários de sucumbência: art. 23 da Lei 8.906/94. Honorários contratuais conforme "
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
    print(f"\n[conferência] escritório {brl(r['escritorio'])} + cliente {brl(r['liquido'])} + despesas "
          f"{brl(sum((v for _, v in r['despesas']), Decimal('0')))} = {brl(r['total'])}")


if __name__ == "__main__":
    main()
```
