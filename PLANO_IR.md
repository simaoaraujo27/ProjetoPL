# Plano Curto para a Parte do IR

Este ficheiro resume apenas o necessario para implementar a fase:

`AST + tabela de simbolos -> IR`

## 1. Objetivo

Transformar a AST do Fortran 77 numa representacao intermédia simples, que depois possa ser traduzida para a VM.

O IR deve servir para:

- simplificar a traducao;
- explicitar atribuicoes, saltos e operacoes;
- separar a logica do Fortran dos detalhes da VM.

## 2. O que entra

Para gerar IR, precisamos de:

- AST produzida pelo parser;
- tabela de simbolos produzida pela analise semantica.

A AST diz a estrutura.

A tabela de simbolos diz:

- tipo de cada identificador;
- se e variavel, array, funcao ou subrotina;
- dimensoes de arrays;
- scopes.

## 3. O que o IR deve ter

Neste momento, o IR ja suporta:

- `LABEL nome`
- `JUMP nome`
- `JUMP_IF_FALSE condicao nome`
- `ASSIGN destino valor`
- `BINOP temp op arg1 arg2`
- `UNOP temp op arg`
- `READ destino`
- `WRITE valor`
- `WRITE_LN`
- `LOAD_ARRAY temp array indice1 indice2 ...`
- `STORE_ARRAY array indice1 indice2 ... valor`
- `ARRAY_DECL array limite_inf1 limite_sup1 limite_inf2 limite_sup2 ...`
- `CALL label args...`
- `RETURN`

## 4. Subconjunto inicial

Ja existe geracao de IR para:

- declaracoes simples;
- literais;
- identificadores;
- expressoes binarias;
- expressoes unarias;
- atribuicoes;
- `IF`;
- `GOTO`;
- `DO`;
- `READ`;
- `PRINT` / `WRITE`;
- arrays;
- `FUNCTION`;
- `SUBROUTINE`;
- `CALL`;
- `RETURN`.

Deixar para depois:

- `Computed GOTO`;
- `Arithmetic IF`.

## 5. Passo a passo

1. listar os nodes da AST que vao ser traduzidos na primeira iteracao; `concluido`
2. criar um ficheiro `IR/ir.py` com as estruturas do IR; `concluido`
3. definir como representar temporarios: `t1`, `t2`, `t3`, ...; `concluido`
4. definir como representar labels internas: `L1`, `L2`, `L3`, ...; `concluido`
5. criar `IR/ir_generator.py`; `concluido`
6. implementar traducao de literais e identificadores; `concluido`
7. implementar traducao de expressoes binarias e unarias; `concluido`
8. implementar traducao de atribuicoes; `concluido`
9. implementar traducao de `READ`, `PRINT` e `WRITE`; `concluido`
10. implementar traducao de `IF`; `concluido`
11. implementar traducao de `GOTO`; `concluido`
12. imprimir o IR em texto para facilitar debug; `concluido`
13. testar com exemplos pequenos; `concluido`

### Estado atual dos passos 1 a 5

Nodes da AST ja suportados:

- `MainProgram`
- `FunctionDef`
- `SubroutineDef`
- `Statement`
- `Declaration`
- `Assignment`
- `ArrayAssignment`
- `Print`
- `Write`
- `Read`
- `Call`
- `If`
- `LogicalIf`
- `Goto`
- `Do`
- `Continue`
- `Return`
- `BinOp`
- `UnOp`
- `ID`
- `Literal`
- `ArrayAccess`
- `CallOrArrayAccess`

Ainda ficam fora:

- `ComputedGoto`
- `ArithmeticIf`
- `Slice`
- `Parameter`
- `Data`
- `Dimension`
- `Return`
- `Stop`
- `Pause`

Estruturas base do IR a criar:

- `IRProgram`
- `IRInstruction`
- `IRVariable`
- `IRTemp`
- `IRConstant`
- `IRLabelRef`

Convencoes base:

- temporarios: `t1`, `t2`, `t3`, ...;
- labels internas: `L1`, `L2`, `L3`, ...;
- operacoes guardadas como texto simples, por exemplo `+`, `-`, `.LT.`, `.AND.`.

## 6. Regras importantes

- o IR deve ser simples e linear;
- cada expressao mais complexa deve ser partida em temporarios;
- os tipos devem vir da tabela de simbolos;
- a traducao nao deve recalcular semantica;
- o IR deve ficar independente da sintaxe concreta do Fortran.

## 7. Exemplo simples

Fortran:

```fortran
X = A + B * C
```

IR possivel:

```text
BINOP t1 * B C
BINOP t2 + A t1
ASSIGN X t2
```

## 8. Resultado esperado

No fim desta etapa, devemos ter:

- um formato de IR definido;
- um gerador `AST + tabela de simbolos -> IR`;
- IR legivel para debug;
- testes simples a confirmar que a traducao esta correta.

## 9. Estado

O plano curto do IR ficou concluido para a fase atual.

Ja existe suporte para:

- `Literal` e `ID`;
- `BinOp` e `UnOp`;
- `Assignment`;
- `Read`;
- `Print` e `Write`;
- `If` e `LogicalIf`;
- `Goto`;
- `Do` com label terminal `CONTINUE`;
- arrays com `ARRAY_DECL`, `LOAD_ARRAY` e `STORE_ARRAY`, incluindo multiplas dimensoes;
- `FunctionDef` e `SubroutineDef`;
- `Call` e chamadas de funcao em expressao;
- `Return`;
- labels simples;
- renderizacao textual do IR;
- testes automatizados em `test_ir.py`.

Neste momento, o IR ja cobre o subconjunto principal do projeto e esta pronto para servir de entrada para a fase seguinte.

Podem ainda aparecer pequenos ajustes ao IR durante `IR -> VM`, mas isso ja sera refinamento, nao falta estrutural.

Ficam como extensoes opcionais ou refinamentos futuros:

- ajuste fino do formato de algumas instrucoes, se isso simplificar `IR -> VM`;
- melhoria da documentacao interna do IR;
- aumento da cobertura de testes com mais programas completos.

## 10. Fecho

A fase `AST + tabela de simbolos -> IR` pode ser considerada fechada.

O proximo passo do projeto passa a ser:

`IR -> VM`
