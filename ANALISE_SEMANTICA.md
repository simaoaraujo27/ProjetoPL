# Analise Semantica

Este ficheiro lista as validacoes semanticas alinhadas com o enunciado do projeto. O objetivo e verificar tipos de dados, declaracao de variaveis e coerencia do codigo, incluindo a validacao das labels dos ciclos `DO`.

## 1. Estrutura global do programa

- Validar que existe pelo menos uma unidade de programa.
- Validar que existe no maximo um `PROGRAM` principal.
- Criar um scope separado para cada unidade de programa.
- Validar que nomes sao case-insensitive, como em Fortran: `x` e `X` representam o mesmo identificador.

## 2. Declaracoes e tabela de simbolos

- Registar variaveis declaradas com o respetivo tipo.
- Registar arrays declarados com o respetivo tipo e dimensoes.
- Validar que uma variavel nao e declarada mais do que uma vez no mesmo scope.
- Validar que toda a variavel usada foi declarada antes de ser usada.
- Validar que uma variavel escalar nao e usada como array.
- Validar que um array nao e usado como variavel escalar, exceto em contextos permitidos.
- Validar que declaracoes `DIMENSION` so sao aplicadas a identificadores declarados.

## 3. Tipos de dados

- Inferir o tipo de cada expressao.
- Validar que atribuicoes respeitam tipos compativeis.
- Validar que operadores aritmeticos `+`, `-`, `*`, `/` e `**` recebem operandos numericos.
- Validar que operadores relacionais `.EQ.`, `.NE.`, `.GT.`, `.GE.`, `.LT.` e `.LE.` recebem operandos compativeis.
- Validar que operadores logicos `.AND.`, `.OR.` e `.NOT.` recebem operandos `LOGICAL`.
- Validar que condicoes de `IF` sao expressoes `LOGICAL`.
- Validar que os indices de arrays sao expressoes inteiras.
- Validar que um acesso a array usa o numero correto de indices.

## 4. Controlo de fluxo

- Registar todas as labels existentes em cada scope.
- Validar que nao existem labels repetidas no mesmo scope.
- Validar que `GOTO n` aponta para uma label existente.
- Validar que `GO TO n` e tratado da mesma forma que `GOTO n`.
- Validar que a label final de um ciclo `DO` existe.
- Validar que a label final de um ciclo `DO` corresponde a uma instrucao `CONTINUE`.
- Validar que a variavel de controlo de um `DO` foi declarada.
- Validar que a variavel de controlo de um `DO` e numerica, idealmente `INTEGER`.
- Validar que inicio, fim e passo do `DO` sao expressoes numericas.
- Validar que o passo do `DO` nao e zero quando e constante.

## 5. IF-THEN-ELSE

- Validar que a condicao do `IF` foi semanticamente analisada.
- Validar que a condicao do `IF` tem tipo `LOGICAL`.
- Validar semanticamente os blocos `THEN` e `ELSE`.

## 6. Input/Output basico

- Validar que itens em `READ` sao atribuiveis: variaveis escalares ou posicoes de arrays.
- Validar que `READ` nao tenta escrever para simbolos que nao podem receber valor.
- Validar que variaveis/arrays usados em `READ` e `PRINT` foram declarados.
- Validar semanticamente as expressoes usadas em `PRINT`.

## 7. Erros e mensagens

- Produzir mensagens com o nome do simbolo ou label e o tipo de erro.
- Continuar a analise depois de encontrar um erro, quando for razoavel, para reportar varios erros numa execucao.
- Exemplos de erros esperados:
  - `Variavel 'X' usada mas nao declarada`
  - `Simbolo 'N' ja declarado no scope 'MAIN'`
  - `Array 'A' usado com 2 indices, mas foi declarado com 1 dimensao`
  - `GOTO para label inexistente: 20`
  - `DO usa label 10, mas a label nao corresponde a CONTINUE`
  - `Atribuicao incompativel: INTEGER recebe LOGICAL`

## 8. Valorizacao: funcoes e subrotinas

O enunciado indica `SUBROUTINE` e `FUNCTION` como valorizacao. Se forem suportadas, validar tambem:

- Registar cada `FUNCTION` com nome, tipo de retorno e lista de parametros.
- Registar cada `SUBROUTINE` com nome e lista de parametros.
- Criar um scope separado para cada `FUNCTION` e `SUBROUTINE`.
- Validar que parametros formais sao declarados com tipo.
- Validar que nenhum parametro formal e repetido.
- Validar que chamadas a funcoes/subrotinas usam simbolos declarados.
- Validar que `CALL NOME(...)` refere uma subrotina.
- Validar que uma `FUNCTION` usada em expressao tem retorno conhecido.
- Validar que uma `FUNCTION` atribui valor ao seu proprio nome antes de terminar.

## 9. Ordem sugerida de implementacao

1. Construir scopes e registar simbolos.
2. Registar declaracoes, arrays e labels.
3. Validar usos de identificadores.
4. Inferir e validar tipos de expressoes.
5. Validar atribuicoes.
6. Validar `IF`, `DO`, `GOTO`, `READ` e `PRINT`.
7. Validar a regra especifica do enunciado: labels de ciclos `DO` devem corresponder a `CONTINUE`.
8. Implementar validacoes de `FUNCTION` e `SUBROUTINE`, se a valorizacao for mantida.
