# WBC PDV Premium v4.0 - Dicionário de Dados do Banco de Dados Relacional (Firebird)

Este arquivo serve como mapa de referência obrigatório para operações de leitura (SELECT), inserção (INSERT) e atualização (UPDATE) de dados no sistema de vendas.

---

## 1. Módulo de Vendas e Pedidos (Faturamento / Balcão)

### Tabela: `DAV` (Documento de Auxílio à Venda - Cabeçalho)
Guarda as informações consolidadas da venda.
* **`ID`** (Integer, PK, Generator Auto): Código identificador único do DAV.
* **`DATA_EMISSAO`** (Date, NOT NULL): Data da venda. Fallback: `CURRENT_DATE`.
* **`HORA_EMISSAO`** (Time, NOT NULL): Hora da venda. Fallback: `CURRENT_TIME`.
* **`ID_CLIENTE`** (Integer): ID do cliente vinculado (Tabela `CLIENTES`). Obrigatório para Vendas a Prazo.
* **`NOME_CLIENTE`** (Varchar): Nome do cliente/consumidor gravado de forma descritiva.
* **`CPF_CNPJ_CLIENTE`** (Varchar): Documento do cliente para impressão no cupom.
* **`VALOR_TOTAL`** (Numeric, NOT NULL): Somatório bruto dos itens.
* **`DESCONTO`** (Numeric, Default 0): Valor absoluto de desconto aplicado na venda.
* **`ACRESCIMO`** (Numeric, Default 0): Valor absoluto de acréscimo aplicado na venda.
* **`VALOR_FINAL`** (Numeric, NOT NULL): Valor líquido (`VALOR_TOTAL - DESCONTO + ACRESCIMO`).
* **`ID_FORMA_PAGAMENTO`** (Integer, NOT NULL): ID da forma selecionada na modal de fechamento.
* **`ID_MOVIMENTO`** (Integer, NOT NULL): ID do movimento de caixa ativo. **Garantir busca por caixa aberto (`STATUS='A'`) antes do insert.**
* **`CFOP`** (Varchar, NOT NULL): CFOP da operação global. **Fallback obrigatório: '5102' se nulo.**
* **`STATUS_VENDA`** (Varchar, Default 'FECHADO'): Situação atual da venda ('ABERTO' para Prazo/Pendente, 'FECHADO' para Concluída).

### Tabela: `DAV_ITENS` (Produtos Vinculados ao DAV)
Guarda o carrinho de compras detalhado de cada venda.
* **`ID`** (Integer, PK, Generator Auto): Identificador único do item.
* **`ID_DAV`** (Integer, FK, NOT NULL): Vinculação com o ID da tabela `DAV`.
* **`ID_PRODUTO`** (Integer, FK, NOT NULL): Vinculação com a tabela `PRODUTOS`.
* **`QUANTIDADE`** (Numeric, NOT NULL): Quantidade vendida.
* **`VALOR_UNITARIO`** (Numeric, NOT NULL): Preço unitário praticado.
* **`TOTAL_ITEM`** (Numeric, NOT NULL): Subtotal (`QUANTIDADE * VALOR_UNITARIO`).
* **`CFOP`** (Varchar, NOT NULL): CFOP individual do item. **Fallback obrigatório: '5102' se nulo ou em branco.**
* **`DESCONTO_RATEIO`** (Numeric, Default 0): Fração do desconto geral rateada para este item.

---

## 2. Módulo Financeiro e Crediário (Contas a Receber)

### Tabela: `CONTAS_RECEBER`
Gerada automaticamente quando o `ID_FORMA_PAGAMENTO` resolve para `'PRAZO'`.
* **`ID`** (Integer, PK, Generator Auto): Identificador da parcela/duplicata.
* **`ID_CLIENTE`** (Integer, FK, NOT NULL): **Obrigatório.** Não permite inserção se o cliente não for identificado.
* **`NUMERO_DOCUMENTO`** (Varchar): Geralmente preenchido com o número do DAV correspondente.
* **`PARCELA`** (Varchar, NOT NULL): Identificador da parcela no formato string (ex: "1/3", "2/3", "3/3").
* **`VLR_CONTA`** (Numeric, NOT NULL): Valor líquido desta parcela individual (`VALOR_FINAL / TOTAL_PARCELAS`).
* **`DT_CONTA`** (Date, Default CURRENT_DATE): Data em que a dívida foi gerada.
* **`DT_VENC`** (Date, NOT NULL): Data de vencimento da parcela. **Mapeamento padrão: de 30 em 30 dias (`CURRENT_DATE + 30 * i`).**
* **`HISTORICO`** (Varchar): Descrição da origem da conta. Padrão: `"Venda a Prazo - DAV n. {ID_DAV}"`.
* **`SITUACAO`** (Varchar, Default 'ABERTO'): Status financeiro da cobrança ('ABERTO', 'QUITADO').
* **`ID_OPERADOR`** (Integer): ID do usuário do sistema que efetuou o lançamento.

### Tabela: `FINANCEIRO_MOV` (Fluxo de Caixa e Lançamentos)
Guarda as entradas financeiras imediatas (Dinheiro, Entrada do Prazo, Pix, Cartões).
* **`ID`** (Integer, PK, Generator Auto): Identificador do lançamento de caixa.
* **`ID_MOVIMENTO`** (Integer, FK, NOT NULL): Vinculado ao movimento de caixa aberto.
* **`TIPO_LANC`** (Varchar, NOT NULL): Origem do recurso ('DINHEIRO', 'PIX', 'CARTAO_CREDITO', 'CARTAO_DEBITO', 'ENTRADA_PRAZO').
* **`VALOR`** (Numeric, NOT NULL): Valor exato que entrou fisicamente no caixa.

---

## 3. Módulo de Cadastros Base

### Tabela: `PRODUTOS`
* **`ID_PRODUTO`** (Integer, PK): Código interno do produto.
* **`BARRAS`** (Varchar): Código de barras (EAN/GTIN) para busca rápida por leitor.
* **`PRODUTO`** (Varchar, NOT NULL): Descrição/Nome comercial do item.
* **`ESTOQUE`** (Numeric, Default 0): Saldo físico atual em estoque.
* **`VALOR_VENDA`** (Numeric, NOT NULL): Preço de venda padrão praticado no balcão.
* **`CUSTO`** (Numeric, Default 0): Preço de custo do produto para cálculo de margem.
* **`UNIDADE_COMECIAL`** (Varchar, Default 'UN'): Sigla da unidade de medida para venda.

### Tabela: `CLIENTES`
* **`ID_CLIENTE`** (Integer, PK): Identificador único do cliente.
* **`CLIENTE`** (Varchar, NOT NULL): Nome completo ou Razão Social.
* **`CPF_CNPJ`** (Varchar): Documento de identificação física ou jurídica.
* **`STATUS`** (Varchar, Default 'ATIVO'): Situação do cadastro ('ATIVO', 'BLOQUEADO').
* **`VENDE_APRAZO`** (Varchar, Default 'SIM'): Trava de segurança comercial ('SIM', 'NAO'). **Validar antes de liberar a Modal de Crediário.**

---

## 4. Regras de Ouro para os Agentes de IA (Prompts do Sistema)
1. **Trava de Campos Nulos:** As colunas `CFOP`, `ID_MOVIMENTO` e `ID_CLIENTE` (em caso de prazo) **nunca** devem receber valores `null` ou vazios em blocos de `INSERT`. Sempre aplique as validações preventivas e fallbacks descritos neste mapa.
2. **Controle de Caching:** Ao injetar URLs de imagens de logotipos (`logoLateralUrl`, `logoImpressaoUrl`), controle a re-renderização do React utilizando chaves de tickets numéricos (`Date.now()`) controlados via estado, concatenando com tratamento de query params (`.includes('?')`).
