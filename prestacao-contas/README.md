# Assistente de pagamento e prestação de contas

Usado quando o processo termina e o dinheiro é levantado. Entram a **sentença ou o acórdão** (e a decisão que fixou o valor final, se houver), o **contrato de honorários** e, quando houver, o **alvará ou comprovante do levantamento**. Saem o texto para o cliente (WhatsApp ou e-mail) e o PDF com o demonstrativo e o termo de quitação.

## 1. Leitura dos documentos

Leia tudo antes de calcular (`pdftotext -layout`; se não sair texto, `pdftoppm -r 70 -png` e leia a imagem).

| Documento | O que extrair |
|---|---|
| Sentença / acórdão | tipo e data; cada condenação com valor; percentual de sucumbência e sobre qual base incide; marcos de correção e juros. **O acórdão prevalece sobre a sentença no que reformou**: majoração de sucumbência (art. 85, § 11, do CPC), redução do dano moral, exclusão de pedido. No Juizado, sentença de 1º grau não tem sucumbência (art. 55 da Lei 9.099/95); ela só aparece no acórdão contra o recorrente vencido. |
| Contrato | **percentual dos honorários contratuais**, **base de cálculo** e número da cláusula; se a atualização monetária tem destino próprio; despesas que o cliente reembolsa. O percentual sempre sai do contrato, nunca se presume. |
| Alvará / comprovante | valor total levantado, data, origem; se o alvará separa a sucumbência, use esse valor. |

## 2. Montagem do caso

Crie `prestacao-contas/<nº>-<cliente>.json` no formato de `exemplo.json`:

- `contrato.base`: `credito_cliente` (condenação atualizada, padrão), `valor_total` (tudo o que foi levantado) ou `condenacao_nominal` (sem correção), conforme a redação da cláusula.
- `contrato.atualizacao_destino`: omita (a atualização é do cliente e entra na base) ou `"escritorio"` só se o contrato destinar a atualização ao escritório.
- `levantamento.sucumbencia`: preencha quando o alvará ou o cálculo trouxer o valor separado. Se ficar em branco, o script separa pelo percentual, supondo que o depósito cobre condenação atualizada + sucumbência sobre ela.
- `despesas`: custas, preparo, perícia adiantados pelo escritório e reembolsáveis pelo contrato.

## 3. Cálculo

```bash
python3 tools/prestacao_contas.py prestacao-contas/<nº>-<cliente>.json /mnt/user-data/outputs
```

Ordem: valor levantado, (-) sucumbência (art. 23 da Lei 8.906/94), (=) crédito do cliente (condenação + atualização), (-) honorários contratuais, (-) despesas, (=) líquido do cliente. A última linha impressa confere escritório + cliente + despesas = total levantado.

O script **para com erro** se o levantamento menos a sucumbência for menor que a condenação nominal (indica valor errado, pagamento parcial ou condenação reduzida no acórdão).

## 4. Conferência antes de entregar

- os valores da condenação batem com o dispositivo da decisão final (não com o pedido da inicial);
- o percentual e a base batem com a cláusula do contrato citada;
- se a ré depositou só parte, avise: a prestação é parcial e o saldo segue em cumprimento de sentença;
- abra o PDF renderizado e olhe a página.

## 5. Entrega

Texto pronto para colar, PDF do demonstrativo com termo de quitação e, no retorno: os números usados, de onde saiu cada um (folha ou cláusula) e qualquer divergência encontrada.

## 6. Sucumbência separada (padrão do escritório)

A prestação de contas do cliente **não mostra a sucumbência**. O demonstrativo começa pela condenação atualizada (levantado menos sucumbência), e o termo de quitação cobre só isso. A sucumbência vai num arquivo à parte, `<nº> - SUCUMBENCIA INTERNO - <Cliente>.txt`, que **não se envia ao cliente**: ele mostra o levantado total, a sucumbência, o total do escritório e a conferência com o alvará. Para voltar ao formato antigo num caso específico, use `"sucumbencia_separada": false` no JSON.

## 7. Texto do WhatsApp (padrão do escritório)

Sempre curto: saudação, notícia, condenação e valor atualizado, os descontos do contrato em tópicos, "💰 *Você recebe: R$ X*", "Segue o comprovante do PIX. 📎" e o fecho "Foi um prazer cuidar do seu caso!". O detalhamento completo e o termo de quitação ficam no PDF. Campos opcionais no JSON: `recado` (aviso extra, como o andamento de outro processo do cliente), `re_curto` (ex.: "Azul") e `pagamento.mensagem` para trocar a linha do PIX.


## 8. O que vai ao cliente

Só o texto do WhatsApp, com o comprovante do PIX. O PDF com demonstrativo e termo de quitação não é gerado por padrão; use `"pdf": true` no JSON quando precisar dele. O demonstrativo interno da sucumbência é sempre gerado e fica no escritório.
