# Estado da Analise Semantica

Este ficheiro resume o que ja esta implementado na analise semantica do projeto.
A implementacao esta dividida em:

- `symbol_table.py`: tabela de simbolos, simbolos e `SemanticError`.
- `semantic_table_builder.py`: construcao da tabela de simbolos a partir da AST.
- `semantic.py`: validacoes semanticas feitas depois da tabela estar construida.

## 1. Estrutura global do programa

### O que ja valida

- Existe pelo menos uma unidade de programa.
- Existe no maximo um `PROGRAM` principal.
- E criado um scope separado para cada `PROGRAM`, `FUNCTION` e `SUBROUTINE`.
- Os nomes sao tratados de forma case-insensitive.

### Exemplo valido

```fortran
PROGRAM MAIN
END
```

Este programa cria:

```text
global
  MAIN
```

### Exemplo invalido

```fortran
PROGRAM A
END
PROGRAM B
END
```

Falha porque existem dois programas principais.

## 2. Declaracoes e tabela de simbolos

### O que ja regista

- Variaveis declaradas com o respetivo tipo.
- Arrays declarados com tipo e dimensoes.
- Parametros formais de `FUNCTION` e `SUBROUTINE`.
- Funcoes, subrotinas, programa principal e intrinsecas no scope global.
- Labels definidas e referencias a labels usadas por `DO` e `GOTO`.

### O que ja valida

- Uma variavel nao pode ser declarada duas vezes no mesmo scope.
- Uma variavel tem de ser declarada antes de ser usada.
- Uma variavel tem de ser inicializada antes de ser usada em expressoes.
- Declaracoes de tipo e `DIMENSION` tem de aparecer antes de comandos executaveis.
- Uma variavel escalar nao pode ser usada como array.
- Um array nao pode ser usado como variavel escalar.
- `DIMENSION` so pode ser aplicado a identificadores ja declarados.
- Um acesso a array tem de usar o numero correto de indices.

### Exemplo valido

```fortran
PROGRAM ARR
INTEGER A(5), I
I = 1
A(I) = 10
END
```

`A` fica registado como array `INTEGER` com uma dimensao.
`I` fica registado como variavel `INTEGER` e e inicializado antes de ser usado como indice.

### Exemplo invalido: variavel nao declarada

```fortran
PROGRAM A
X = 1
END
```

Falha porque `X` foi usada sem declaracao.

### Exemplo invalido: declaracao duplicada

```fortran
PROGRAM A
INTEGER X
INTEGER X
END
```

Falha porque `X` ja existe no mesmo scope.

### Exemplo invalido: variavel nao inicializada

```fortran
PROGRAM A
INTEGER X, Y
Y = X
END
```

Falha porque `X` foi declarada, mas ainda nao recebeu valor.

### Exemplo valido: `READ` inicializa variavel

```fortran
PROGRAM A
INTEGER X
READ *, X
PRINT *, X
END
```

Passa porque `READ *, X` conta como inicializacao de `X`.

### Exemplo invalido: declaracao depois de comando executavel

```fortran
PROGRAM A
PRINT *, 'OLA'
INTEGER X
END
```

Falha porque declaracoes devem aparecer antes de comandos executaveis.

### Exemplo invalido: `DIMENSION` sem declaracao previa

```fortran
PROGRAM A
DIMENSION X(3)
END
```

Falha porque `X` nao foi declarado antes do `DIMENSION`.

### Exemplo invalido: escalar usado como array

```fortran
PROGRAM A
INTEGER X
X(1) = 10
END
```

Falha porque `X` foi declarado como variavel escalar.

### Exemplo invalido: array usado como escalar

```fortran
PROGRAM A
INTEGER A(5), X
X = A
END
```

Falha porque `A` e array e esta a ser usado como variavel escalar.

## 3. Tipos de dados

### O que ja infere

- Literais inteiros como `INTEGER`.
- Literais reais como `REAL`.
- Strings como `CHARACTER`.
- `.TRUE.` e `.FALSE.` como `LOGICAL`.
- Variaveis e arrays pelo tipo guardado na tabela de simbolos.
- Chamadas a funcoes pelo `return_type`.
- `MOD` como intrinseca com retorno `INTEGER`.
- Expressoes aritmeticas, relacionais e logicas.

### O que ja valida

- Atribuicoes respeitam tipos compativeis.
- Operadores aritmeticos `+`, `-`, `*`, `/` e `**` recebem operandos numericos.
- Operadores relacionais recebem operandos compativeis.
- Operadores logicos `.AND.`, `.OR.` e `.NOT.` recebem operandos `LOGICAL`.
- Condicoes de `IF` sao expressoes `LOGICAL`.
- Indices de arrays sao expressoes `INTEGER`.

### Exemplo valido: atribuicao numerica

```fortran
PROGRAM A
INTEGER X
REAL R
R = X + 1
END
```

Passa porque `INTEGER` e `REAL` sao tipos numericos compativeis.

### Exemplo invalido: atribuicao incompativel

```fortran
PROGRAM A
INTEGER X
LOGICAL L
X = L
END
```

Falha porque `INTEGER` nao pode receber `LOGICAL`.

### Exemplo invalido: operador aritmetico com `LOGICAL`

```fortran
PROGRAM A
INTEGER X
LOGICAL L
X = L + 1
END
```

Falha porque `+` exige operandos numericos.

### Exemplo valido: condicao logica

```fortran
PROGRAM A
INTEGER X
IF (X .GT. 0) THEN
ENDIF
END
```

Passa porque `X .GT. 0` produz uma expressao `LOGICAL`.

### Exemplo invalido: condicao de `IF` nao logica

```fortran
PROGRAM A
INTEGER X
IF (X) THEN
ENDIF
END
```

Falha porque a condicao do `IF` tem tipo `INTEGER`, nao `LOGICAL`.

### Exemplo invalido: indice de array nao inteiro

```fortran
PROGRAM A
INTEGER A(5)
REAL R
A(R) = 1
END
```

Falha porque indices de arrays devem ser `INTEGER`.

## 4. Controlo de fluxo

### O que ja valida

- Labels repetidas no mesmo scope falham.
- `GOTO` tem de apontar para uma label existente.
- `DO` tem de apontar para uma label existente.
- A label final de um `DO` tem de corresponder a uma instrucao `CONTINUE`.
- A variavel de controlo do `DO` tem de estar declarada.
- A variavel de controlo do `DO` tem de ser numerica.
- Inicio, fim e passo do `DO` tem de ser numericos.
- O passo do `DO` nao pode ser zero quando e constante.
- `computed GOTO` e `arithmetic IF` validam as labels usadas.

### Exemplo valido: ciclo `DO`

```fortran
PROGRAM A
INTEGER I
DO 10 I = 1, 5
10 CONTINUE
END
```

Passa porque a label `10` existe e aponta para `CONTINUE`.

### Exemplo invalido: `GOTO` para label inexistente

```fortran
PROGRAM A
GOTO 20
END
```

Falha porque a label `20` nao existe no scope do programa.

### Exemplo invalido: label final do `DO` nao e `CONTINUE`

```fortran
PROGRAM A
INTEGER I
DO 10 I = 1, 5
10 PRINT *, I
END
```

Falha porque a label final do ciclo `DO` aponta para `PRINT`, nao para `CONTINUE`.

### Exemplo invalido: passo zero no `DO`

```fortran
PROGRAM A
INTEGER I
DO 10 I = 1, 5, 0
10 CONTINUE
END
```

Falha porque o passo constante do `DO` e zero.

## 5. IF-THEN-ELSE

### O que ja valida

- A condicao do `IF` e analisada semanticamente.
- A condicao do `IF` tem de ter tipo `LOGICAL`.
- Os blocos `THEN` e `ELSE` tambem sao validados semanticamente.
- O `IF` logico de uma linha tambem exige condicao `LOGICAL`.

### Exemplo valido

```fortran
PROGRAM A
INTEGER X
IF (X .GT. 0) THEN
X = X + 1
ELSE
X = 0
ENDIF
END
```

Passa porque a condicao produz `LOGICAL` e os dois blocos usam simbolos declarados.

### Exemplo invalido: condicao nao logica

```fortran
PROGRAM A
INTEGER X
IF (X) THEN
ENDIF
END
```

Falha porque `X` tem tipo `INTEGER`, nao `LOGICAL`.

### Exemplo invalido: erro dentro do bloco `THEN`

```fortran
PROGRAM A
IF (.TRUE.) THEN
X = 1
ENDIF
INTEGER X
END
```

Falha porque `X` e usado antes de ser declarado dentro do bloco `THEN`.

## 6. Input/Output basico

### O que ja valida

- Itens em `READ` tem de ser variaveis escalares ou posicoes de arrays.
- `READ` nao pode escrever para arrays inteiros usados como escalares.
- Variaveis e arrays usados em `READ`, `PRINT` e `WRITE` tem de estar declarados.
- Expressoes usadas em `PRINT` e `WRITE` sao analisadas semanticamente.

### Exemplo valido: `READ` para variavel e posicao de array

```fortran
PROGRAM A
INTEGER X, A(5), I
READ *, X
READ *, A(I)
END
```

Passa porque `X` e variavel escalar e `A(I)` e uma posicao valida de array.

### Exemplo invalido: `READ` para array como escalar

```fortran
PROGRAM A
INTEGER A(5)
READ *, A
END
```

Falha porque `A` e array e nao uma variavel escalar.

### Exemplo invalido: `PRINT` com variavel nao declarada

```fortran
PROGRAM A
PRINT *, X
END
```

Falha porque `X` nao foi declarado.

## 7. Erros e mensagens

### O que ja valida

- Os erros semanticos usam `SemanticError`.
- As mensagens indicam a linha, simbolo, label ou tipo que causou o erro, quando a linha esta disponivel na AST.
- Quando a tabela de simbolos ja foi construida, o validador tenta continuar a analise e juntar varios erros na mesma execucao.
- A inicializacao segue o mesmo criterio geral do exemplo da aula: declarar nao basta; a variavel tem de receber valor antes de ser usada.

### Exemplo invalido com varios erros

```fortran
PROGRAM A
X = 1
PRINT *, Y
END
```

Pode reportar os dois usos invalidos: `X` e `Y`.

### Exemplo de mensagem com linha

```text
Linha 4: Variável 'X' usada antes de ser inicializada
```

## 8. Funcoes e subrotinas

### O que ja regista

- Cada `FUNCTION` e registada no scope global com tipo de retorno e lista de parametros.
- Cada `SUBROUTINE` e registada no scope global com lista de parametros.
- Cada funcao/subrotina tem o seu proprio scope.
- Parametros formais sao registados no scope da unidade.

### O que ja valida

- Parametros formais nao podem ser repetidos.
- Parametros formais tem de ser declarados com tipo.
- `CALL NOME(...)` tem de referir uma subrotina.
- Chamadas a funcoes/subrotinas validam o numero de argumentos.
- Chamadas a funcoes/subrotinas validam tipos de argumentos quando os parametros tem tipo conhecido.
- Uma `FUNCTION` usada em expressao tem de ter tipo de retorno conhecido.
- Uma `FUNCTION` tem de atribuir valor ao proprio nome antes de terminar.

### Exemplo valido: funcao com retorno

```fortran
PROGRAM A
INTEGER F, X
X = F(1)
END

INTEGER FUNCTION F(N)
INTEGER N
F = N
END
```

Passa porque `F` tem retorno `INTEGER`, parametro `N` tipado e atribui valor a `F`.

### Exemplo valido: subrotina

```fortran
PROGRAM A
      CALL S(1)
END

SUBROUTINE S(X)
INTEGER X
RETURN
END
```

Passa porque `S` e subrotina e recebe um argumento compativel com `INTEGER`.

### Exemplo invalido: parametro formal repetido

```fortran
INTEGER FUNCTION F(X, X)
INTEGER X
F = X
END
```

Falha porque `X` aparece duas vezes na lista de parametros formais.

### Exemplo invalido: parametro formal sem tipo

```fortran
INTEGER FUNCTION F(X)
F = 1
END
```

Falha porque `X` nao foi declarado com tipo no corpo da funcao.

### Exemplo invalido: funcao sem atribuir retorno

```fortran
INTEGER FUNCTION F(X)
INTEGER X
RETURN
END
```

Falha porque a funcao termina sem atribuir valor a `F`.

### Exemplo invalido: `CALL` para funcao

```fortran
PROGRAM A
      CALL F(1)
END

INTEGER FUNCTION F(X)
INTEGER X
F = X
END
```

Falha porque `CALL` so pode chamar subrotinas.

### Exemplo invalido: tipo de argumento errado

```fortran
PROGRAM A
LOGICAL L
      CALL S(L)
END

SUBROUTINE S(X)
INTEGER X
RETURN
END
```

Falha porque `S` espera `INTEGER`, mas recebe `LOGICAL`.

## 9. Ordem de implementacao

A ordem sugerida no plano foi seguida na implementacao:

1. Construir scopes e registar simbolos.
2. Registar declaracoes, arrays e labels.
3. Validar usos de identificadores.
4. Inferir e validar tipos de expressoes.
5. Validar atribuicoes.
6. Validar `IF`, `DO`, `GOTO`, `READ` e `PRINT`.
7. Validar labels de ciclos `DO` contra `CONTINUE`.
8. Implementar validacoes de `FUNCTION` e `SUBROUTINE`.


