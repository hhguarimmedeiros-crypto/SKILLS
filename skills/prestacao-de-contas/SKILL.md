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

Monte um JSON no formato de `exemplo.json`:

- `contrato.percentual` e `contrato.clausula`: do contrato.
- `contrato.base`: `credito_cliente` (condenação atualizada, padrão), `valor_total` (tudo o que foi levantado) ou `condenacao_nominal` (sem correção), conforme a redação da cláusula.
- `contrato.atualizacao_destino`: omita (a atualização é do cliente e entra na base) ou `"escritorio"` só se o contrato destinar a atualização monetária ao escritório.
- `levantamento.sucumbencia`: preencha quando o alvará ou o cálculo trouxer o valor separado. Em branco, o script separa pelo percentual da decisão, supondo que o depósito cobre condenação atualizada + sucumbência sobre ela.
- `despesas`: custas, preparo, perícia adiantados pelo escritório e reembolsáveis pelo contrato.
- `cliente.tratamento`: "Olá," / "Prezada" / "Prezado".

## 3. Cálculo

```bash
python3 scripts/prestacao_contas.py caso.json /mnt/user-data/outputs
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
