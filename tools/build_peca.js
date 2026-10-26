#!/usr/bin/env node
// Gerador de petições na identidade visual do escritório Bruna Guarim.
// Uso: node tools/build_peca.js <conteudo.json> <saida.docx>
//
// O JSON traz a lista de blocos. Tipos de bloco:
//   {t:"addr", text}                       endereçamento
//   {t:"teses", items:[...]}               caixa de teses vermelha
//   {t:"acao", title, sub}                 caixa rosé do nome da ação
//   {t:"p", text}                          parágrafo de corpo
//   {t:"pn", text}                         parágrafo de corpo sem recuo de 1ª linha
//   {t:"h", text}                          título de seção (negrito, caixa alta)
//   {t:"juris", text}                      jurisprudência / transcrição legal (recuado, itálico 10)
//   {t:"prova", text}                      faixa cinza de prova
//   {t:"table", widths:[...], head:[...], rows:[[...]], lastBold:true}
//   {t:"fecho", city}                      fecho com assinatura
// Marcações inline no texto:
//   **negrito**      ==realce amarelo (negrito)==      {{pendência a conferir (amarelo)}}
const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  BorderStyle, ShadingType, AlignmentType, VerticalAlign, Header, Footer,
} = require('docx');

const FONT = 'Palatino Linotype';
const RED = 'C00000', ROSE = 'F2DCDB', WINE = '941717', GRAY = 'E8E8E8',
  GRAYBORDER = 'CCCCCC', YELLOW = 'F1F000', GOLD = 'C89800';
const USEFUL = 9071;

const FOOTER_ADDR =
  'Av. Dr. Hélio Ribeiro, Nº. 525 - Bairro Alvorada, Edifício Helbor Dual Business Office & Corporate, Sala 714, 7º andar, Cuiabá - MT, 78.048-250.';

const noB = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
const noBorders = { top: noB, bottom: noB, left: noB, right: noB };

// ---- inline: **negrito**, ==amarelo==, {{pendência}}
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|==[^=]+==|\{\{[^}]+\}\})/g;
  let last = 0, m;
  const push = (s, extra = {}) => {
    if (!s) return;
    out.push(new TextRun({ text: s, font: FONT, size: 24, ...base, ...extra }));
  };
  while ((m = re.exec(text))) {
    push(text.slice(last, m.index));
    const tok = m[0];
    if (tok.startsWith('**')) push(tok.slice(2, -2), { bold: true });
    else if (tok.startsWith('=='))
      push(tok.slice(2, -2), { bold: true, shading: { type: ShadingType.CLEAR, fill: YELLOW, color: 'auto' } });
    else
      push('[' + tok.slice(2, -2) + ']', { bold: true, shading: { type: ShadingType.CLEAR, fill: YELLOW, color: 'auto' } });
    last = m.index + tok.length;
  }
  push(text.slice(last));
  return out;
}

const body = (text, firstLine = 720) =>
  new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 360, lineRule: 'auto', before: 0, after: 160 },
    indent: firstLine ? { firstLine } : undefined,
    children: runs(text),
  });

const spacer = (after = 120, keepNext = false) =>
  new Paragraph({ keepNext, spacing: { before: 0, after }, children: [] });

function addr(text) {
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 0, after: 300 },
    children: [new TextRun({ text, font: FONT, size: 24, bold: true })],
  });
}

function teses(items) {
  const line = (t) =>
    new Paragraph({
      spacing: { before: 0, after: 60 },
      children: [new TextRun({ text: '●  ' + t, font: FONT, size: 22, bold: true, color: 'FFFFFF' })],
    });
  return [
    new Table({
      width: { size: USEFUL, type: WidthType.DXA },
      columnWidths: [4500, 4571],
      borders: { ...noBorders, insideHorizontal: noB, insideVertical: noB },
      rows: [
        new TableRow({
          children: [
            new TableCell({
              width: { size: 4500, type: WidthType.DXA },
              borders: noBorders,
              children: [new Paragraph('')],
            }),
            new TableCell({
              width: { size: 4571, type: WidthType.DXA },
              borders: noBorders,
              shading: { type: ShadingType.CLEAR, fill: RED, color: 'auto' },
              margins: { top: 120, bottom: 120, left: 160, right: 160 },
              children: items.map(line),
            }),
          ],
        }),
      ],
    }),
    spacer(200),
  ];
}

function acao(title, sub) {
  return [
    new Table({
      width: { size: USEFUL, type: WidthType.DXA },
      columnWidths: [USEFUL],
      borders: { ...noBorders, insideHorizontal: noB, insideVertical: noB },
      rows: [
        new TableRow({
          children: [
            new TableCell({
              width: { size: USEFUL, type: WidthType.DXA },
              borders: noBorders,
              shading: { type: ShadingType.CLEAR, fill: ROSE, color: 'auto' },
              margins: { top: 160, bottom: 160, left: 160, right: 160 },
              children: [
                new Paragraph({
                  alignment: AlignmentType.CENTER,
                  spacing: { after: 60 },
                  children: [new TextRun({ text: title, font: FONT, size: 28, bold: true, color: WINE })],
                }),
                new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: sub, font: FONT, size: 24, bold: true })],
                }),
              ],
            }),
          ],
        }),
      ],
    }),
    spacer(200),
  ];
}

function heading(text) {
  return new Paragraph({
    keepNext: true,
    spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, font: FONT, size: 24, bold: true })],
  });
}

function juris(text) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 276, before: 0, after: 40 },
    indent: { start: 3402, end: 0 },
    children: runs(text, { italics: true, size: 20 }),
  });
}

function prova(text) {
  const bd = { style: BorderStyle.SINGLE, size: 2, color: GRAYBORDER };
  return [
    new Table({
      width: { size: USEFUL, type: WidthType.DXA },
      columnWidths: [USEFUL],
      rows: [
        new TableRow({
          cantSplit: true,
          children: [
            new TableCell({
              width: { size: USEFUL, type: WidthType.DXA },
              borders: { top: bd, bottom: bd, left: bd, right: bd },
              shading: { type: ShadingType.CLEAR, fill: GRAY, color: 'auto' },
              verticalAlign: VerticalAlign.CENTER,
              margins: { top: 60, bottom: 60, left: 100, right: 100 },
              children: [
                new Paragraph({
                  alignment: AlignmentType.CENTER,
                  children: [new TextRun({ text: text.toUpperCase(), font: FONT, size: 22, bold: true })],
                }),
              ],
            }),
          ],
        }),
      ],
    }),
    spacer(240),
  ];
}

function table(spec) {
  const bd = { style: BorderStyle.SINGLE, size: 4, color: '000000' };
  const cb = { top: bd, bottom: bd, left: bd, right: bd };
  const W = spec.widths;
  const head = (t, w) =>
    new TableCell({
      width: { size: w, type: WidthType.DXA },
      borders: cb,
      shading: { type: ShadingType.CLEAR, fill: RED, color: 'auto' },
      verticalAlign: VerticalAlign.CENTER,
      margins: { top: 60, bottom: 60, left: 80, right: 80 },
      children: [
        new Paragraph({
          keepNext: true,
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: t, font: FONT, size: 20, bold: true, color: 'FFFFFF' })],
        }),
      ],
    });
  const cell = (t, w, bold, keepNext) =>
    new TableCell({
      width: { size: w, type: WidthType.DXA },
      borders: cb,
      verticalAlign: VerticalAlign.CENTER,
      margins: { top: 60, bottom: 60, left: 80, right: 80 },
      children: [
        new Paragraph({
          keepNext: !!keepNext,
          alignment: AlignmentType.CENTER,
          children: runs(t, { size: 20, bold: !!bold }),
        }),
      ],
    });
  const rows = [
    new TableRow({ tableHeader: true, cantSplit: true, children: spec.head.map((t, i) => head(t, W[i])) }),
    ...spec.rows.map(
      (r, ri) =>
        new TableRow({
          cantSplit: true,
          children: r.map((t, i) =>
            cell(t, W[i], spec.lastBold && ri === spec.rows.length - 1, ri === 0)
          ),
        })
    ),
  ];
  return [
    new Table({ width: { size: USEFUL, type: WidthType.DXA }, columnWidths: W, rows }),
    spacer(200),
  ];
}

function fecho(city) {
  const c = (t, bold) =>
    new Paragraph({
      alignment: AlignmentType.CENTER,
      keepNext: true,
      spacing: { after: 60 },
      children: [new TextRun({ text: t, font: FONT, size: 24, bold })],
    });
  return [
    spacer(200, true),
    c('Nestes termos,'),
    c('Pede deferimento.'),
    spacer(120, true),
    c(city + ', data do protocolo.'),
    spacer(240, true),
    c('BRUNA CARLA GUARIM', true),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: 'OAB – MT Nº 25020/O', font: FONT, size: 24 })],
    }),
  ];
}

function build(spec) {
  const kids = [];
  for (const b of spec.blocks) {
    switch (b.t) {
      case 'addr': kids.push(addr(b.text)); break;
      case 'teses': kids.push(...teses(b.items)); break;
      case 'acao': kids.push(...acao(b.title, b.sub)); break;
      case 'p': kids.push(body(b.text)); break;
      case 'pn': kids.push(body(b.text, 0)); break;
      case 'h': kids.push(heading(b.text)); break;
      case 'juris': kids.push(juris(b.text)); break;
      case 'prova': kids.push(...prova(b.text)); break;
      case 'table': kids.push(...table(b)); break;
      case 'fecho': kids.push(...fecho(b.city)); break;
      case 'gap': kids.push(spacer(b.after || 120)); break;
      default: throw new Error('bloco desconhecido: ' + b.t);
    }
  }
  const header = new Header({
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 0 },
        children: [new TextRun({ text: 'BRUNA GUARIM', font: FONT, size: 36, bold: true, color: GOLD })],
      }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 120 },
        children: [new TextRun({ text: 'ADVOCACIA & DIREITO DO PASSAGEIRO', font: FONT, size: 18, bold: true, color: GOLD })],
      }),
    ],
  });
  const footer = new Footer({
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: FOOTER_ADDR, font: FONT, size: 20, color: GOLD })],
      }),
    ],
  });
  return new Document({
    creator: 'Bruna Guarim Advocacia',
    title: spec.title || 'Petição inicial',
    styles: { default: { document: { run: { font: FONT, size: 24 } } } },
    sections: [
      {
        properties: {
          page: {
            size: { width: 11906, height: 16838 },
            margin: { top: 1701, left: 1701, right: 1134, bottom: 1879, header: 708, footer: 1134 },
          },
        },
        headers: { default: header },
        footers: { default: footer },
        children: kids,
      },
    ],
  });
}

const [, , inFile, outFile] = process.argv;
if (!inFile || !outFile) {
  console.error('uso: node tools/build_peca.js <conteudo.json> <saida.docx>');
  process.exit(1);
}
const spec = JSON.parse(fs.readFileSync(inFile, 'utf8'));
Packer.toBuffer(build(spec)).then((buf) => {
  fs.writeFileSync(outFile, buf);
  console.log('ok', outFile, buf.length, 'bytes');
});
