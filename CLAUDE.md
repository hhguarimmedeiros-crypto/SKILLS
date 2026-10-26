# Da pasta do caso ao protocolo

Este projeto trata da produção jurídica do escritório Bruna Guarim Advocacia & Direito do Passageiro. Sempre que eu enviar uma pasta ou zip de um caso (relato, inicial da equipe Farol, procuração, provas) e pedir análise, revisão da peça ou organização dos documentos, siga o procedimento abaixo.

## 1. Inventário antes de qualquer coisa

Extraia o zip em diretório próprio e liste todos os arquivos, **inclusive subpastas como DIVERSOS**, onde costumam estar as provas mais fortes que a equipe não juntou.

Leia tudo antes de opinar:

- `pdftotext -layout` nos PDFs; quando não sai texto, `pdftoppm -r 70 -png` e leia a imagem.
- `.docx` com python-docx, percorrendo parágrafos e tabelas.
- `.txt` de conversa de WhatsApp: leia inteiro, inclusive o fim.
- `.html` de transcrição de chat (Air New Zealand, Zendesk, LiveChat): o conteúdo está num JSON embutido, extraia com `re.search(r'=\s*(\[\{.{200,}\}\]);', t, re.S)` e ordene por `createdDateTime`.
- Procuração assinada por gov.br: os certificados PKCS#7 guardam o **e-mail de cada signatário**, que não aparece no texto impresso. Extraia com pypdf (`get_fields()['Signature1']['/V']['/Contents']`) e `strings | grep @`.
- `.ogg` / `.mp4`: não há transcrição neste ambiente, diga isso.

## 2. Análise crítica

Confronte o que a inicial afirma com o que os documentos provam. Erros recorrentes:

- afirmar fato que o próprio documento desmente (data de compra, natureza do recibo);
- pedir restituição integral quando cabe abatimento proporcional (art. 20, III, do CDC);
- deixar de fora a prova decisiva que está em DIVERSOS;
- comprovante de endereço em nome de terceiro, risco de emenda;
- não juntar prova do pagamento pelo próprio autor;
- litisconsorte ativo sem tópico de legitimidade.

Sempre termine a análise com **conclusão explícita de viabilidade**, sem evasiva.

## 3. Competência

Nunca confie no nome do município. Verifique se ele tem comarca própria ou pertence a outra; a relação de comarcas do tribunal resolve (ex.: Santa Terezinha de Itaipu integra a Comarca de Foz do Iguaçu). Em São Paulo, use `https://www.tjsp.jus.br/app/CompetenciaTerritorial` e pesquise **pelo logradouro, não só pelo CEP**: a base divide ruas em faixas de numeração que compartilham o mesmo CEP. Informe também o sistema de protocolo (PJe, e-SAJ, eproc, Projudi).

Antes de numerar a peça nova, confira se o mesmo cliente já tem peça revisada: pode haver divergência de comarca ou de valor a conciliar.

## 4. Reescrita da peça

Trabalhe sobre um esqueleto já aprovado, nunca do zero:

- adulto em Juizado: `83 - INICIAL - Amir Gil Sessim x LATAM - REVISADA.docx`
- menor em Vara Cível: `85 - INICIAL - Jessika Araujo (menor) x LATAM - VARA CIVEL.docx`

```bash
cp "<esqueleto>" "/mnt/user-data/outputs/<nº> - INICIAL - <Autor> x <Ré> - <JUÍZO> - REVISADA.docx"
sed -e "s#^DST = .*#DST = '<novo caminho>'#" -e "s#^IMG = .*#IMG = '<pasta de imagens>/'#" jo_base.py > xx_base.py
```

`xx_base.py` traz `ache`, `set_runs`, `novo_par`, `imagem`, `apaga`, `apaga_imagens`, `preenche`, `arredonda_ind`. Divida a edição em quatro scripts: cabeçalho e preliminares, fatos, fundamentação, danos e pedidos. Cada um ancora por trecho inicial de parágrafo e salva no fim.

Armadilhas:

- não existe o estilo `Table Grid`; bordas só via XML `w:tblBorders`;
- repita o cabeçalho da tabela com `w:tblHeader` na primeira linha;
- `keep_with_next` em todo parágrafo terminado em `:` e nas duas primeiras linhas de cada tabela;
- `ache` falha se o parágrafo não existir, o que é bom: corrija a âncora em vez de forçar;
- rode com `python3` simples, sem `-I`, senão o `from xx_base import *` quebra.

Depois de montar, **procure resíduos do caso-modelo** com regex (nomes de voos, cidades, valores, "o Autor" quando a parte é mulher) em parágrafos e células. Valide com `python3 /mnt/skills/public/docx/scripts/office/validate.py`, converta com `run_soffice` e **olhe as páginas renderizadas** em montagem 3x3 antes de entregar.

## 5. Provas em PDF

Conversa de WhatsApp e transcrição de chat viram PDF em tabela de três colunas (data e hora, de, mensagem), com reportlab, cabeçalho repetido, linhas da empresa em cinza e nota de rodapé dizendo que o documento foi gerado do arquivo original sem supressão. Remova caracteres fora do Latin-1, senão emojis viram quadrados pretos:

```python
t = ''.join(c for c in t if ord(c) < 0x2000 or c in '‘’“”…')
```

Para os prints no corpo da peça, renderize o PDF a 150 dpi e recorte por frações da altura com PIL, conferindo cada recorte antes de inserir.

## 6. Pasta de protocolo

- tudo em PDF, imagens convertidas com `Image.save(dst, 'PDF', resolution=150.0)`;
- numeração na ordem de juntada, nomes **sem pontos, traços ou acentos**: `03 DOCUMENTO PESSOAL DA AUTORA.pdf`;
- a procuração entra só assinada;
- o contrato de honorários **nunca** entra;
- entregue os PDFs **soltos**, um a um, não em zip.

Quando faltar declaração de residência (comprovante em nome de terceiro), gere o modelo em PDF para assinatura, com fundamento no art. 2º da Lei 7.115/83 e a advertência do art. 299 do Código Penal, e entregue fora da numeração até voltar assinada.

## 7. Jurisprudência

Só julgado real e verificável. O portal de jurisprudência do TJPR e o Jusbrasil não são acessíveis deste ambiente; o STJ é (`scon.stj.jus.br`, informativos e notícias). Quando não conseguir confirmar uma ementa trazida pela equipe, mantenha com a referência completa e **avise que precisa ser conferida antes do protocolo**, nomeando o número do processo.

## 8. Entrega

Docx e PDF da peça, documentos soltos, e no retorno: o que mudou e por quê, o que ficou pendente e a conclusão de viabilidade. Para gravar na pasta do Google Drive, o conector aceita só arquivos de poucos KB (o conteúdo vai codificado na própria chamada); peça maior que isso eu arrasto do chat, ou conecto o computador pelo app desktop para gravação direta.
