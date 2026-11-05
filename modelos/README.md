# Modelos aprovados do escritório

## Cumprimento de sentença (Juizado Especial)

Arquivo: `MODELO PADRAO - CUMPRIMENTO DE SENTENCA - JEC.docx`, aprovado pelo escritório a partir do caso Eduardo Cesar Alves Lemes x SPE Mirante e WAM (7º JEC de Cuiabá, processo 1018572-93.2026.8.11.0001).

Sempre parta deste arquivo (`cp` para a pasta de saída e edite com python-docx). Nunca redija do zero.

### Estrutura que deve ser mantida

1. Endereçamento em caixa alta, centralizado.
2. **Caixa de teses vermelha** (tabela 1x2) com os cinco pontos do caso em tópicos.
3. Número do processo.
4. Qualificação: Exequente + **BRUNA CARLA GUARIM MEDEIROS** em nome próprio quanto à sucumbência (art. 23 da Lei 8.906/94 e art. 85, § 14, do CPC), com fundamento nos arts. 52 da Lei 9.099/95 e 523 a 527 do CPC.
5. Caixa do nome da ação: CUMPRIMENTO DE SENTENÇA, com a base legal embaixo.
6. I. DO TÍTULO EXECUTIVO JUDICIAL: sentença (Id e data), embargos, acórdão ou decisão monocrática (Id e data), trânsito em julgado.
7. II. DO DÉBITO E DA MEMÓRIA DE CÁLCULO: índices do título, **Quadro I** (verba, marcos, original, corrigido, juros, total, subtotal do Exequente, sucumbência, total da execução) e **Quadro II** (índices mensais). Abatimento de restituição administrativa e legitimidade da advogada para a sucumbência. Frase do total destacada.
8. III. DOS PEDIDOS: a) intimação na pessoa dos advogados (art. 513, § 2º, I) para pagar em 15 dias, separando o solidário da sucumbência; b) multa de 10% (art. 523, § 1º, e Enunciado 97 do FONAJE) e SISBAJUD; c) RENAJUD, INFOJUD e cadastro de inadimplentes (art. 782, § 3º); d) alvará eletrônico.
9. Fecho: "Cuiabá/MT, data do protocolo." e assinatura:
   BRUNA CARLA GUARIM MEDEIROS, ADVOGADA - OAB/MT nº 25.020, OAB/RJ nº 262.493.
10. **Nota interna amarela** ao final com as pendências do caso, apagada antes do protocolo.

### Regras de conteúdo

- No Juizado não se pede honorários de 10% do art. 523, § 1º, só a multa (Enunciado 97 do FONAJE).
- Sucumbência só contra o recorrente vencido (art. 55 da Lei 9.099/95).
- Correção e juros exatamente como o dispositivo manda; padrão TJMT pós-Lei 14.905/24: IPCA (série 433 do BCB) e taxa legal (série 29543 do BCB), juros simples, pro rata no mês corrente. O SisCalc (`siscalc.tjmt.jus.br`) usa as mesmas séries, mas exige o CPF do interessado.
- Premissas de data não confirmadas nos autos vão para a nota interna, nunca escondidas.

## Timbre e identidade visual

Arquivos em `modelos/marca/` (extraídos do pacote LOGOTIPO BRUNA GUARIM 2):

- `logotipo-horizontal-cor.png`: monograma dourado + nome em azul-petróleo. É o do cabeçalho das peças.
- `logotipo-horizontal-preto.png`: versão para impressão em preto e branco.
- `monograma-cor.png`: só o BG, para PDFs ao cliente e ícones.

Paleta do guia de marca: azul-noite `#061822`, azul-petróleo `#0F3849`, dourado `#987146` a `#F0C985`, gelo `#EEF7FC`. Tipografia da marca: Selk Serif e Raleway Extra Light (no corpo da peça segue Palatino Linotype 12).

Para pôr o timbre em qualquer peça: `python3 tools/aplica_timbre.py <entrada.docx> modelos/marca/logotipo-horizontal-cor.png <saida.docx>`. Logo de 7,5 cm centralizada no cabeçalho de todas as páginas, margem superior de 3,3 cm, e endereço do escritório no rodapé, em 8 pt azul-petróleo, sob filete dourado.

### Preenchimento por script

`tools/cumprimento_base.py` traz `par`, `cel`, `apaga_par` e `apaga_linhas`, que reescrevem o modelo mantendo a formatação. Fluxo: carregar o modelo, reescrever os parágrafos por índice, ajustar caixa de teses, Quadros I e II (apagar linhas de verbas que não existem) e nota interna, apagar parágrafos que não se aplicam (sucumbência, restituição administrativa, decisão recursal), procurar resíduos do caso anterior e olhar as páginas renderizadas. Se um quadro quebrar entre páginas, inserir quebra de página antes do título do quadro.

Para TJSP: endereçar à Vara do Juizado da comarca, assinar com OAB/SP nº 539.434 (seguida de OAB/MT e OAB/RJ), pedir levantamento por mandado de levantamento eletrônico (MLE) e lembrar que o cumprimento no JEC paulista não recolhe taxa judiciária, salvo má-fé.
