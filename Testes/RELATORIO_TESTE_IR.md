# Relatorio de Testes do IR

Ficheiro de testes:

- [test_ir.py](/home/francisco/Secretária/2Semestre3Ano/PL/ProjetoPL/testes/test_ir.py:1)

## Objetivo

Validar a traducao:

`AST + tabela de simbolos -> IR`

## Cobertura pratica

Os testes cobrem:

- atribuicoes e precedencia de expressoes;
- `constant folding`;
- simplificacao de unarios;
- simplificacao de comparacoes constantes;
- `IF`, `LogicalIf`, `ArithmeticIf`;
- `GOTO` e `ComputedGoto`;
- `DO`;
- `READ`, `PRINT`, `WRITE`;
- arrays 1D e multidimensionais;
- `FUNCTION`, `SUBROUTINE`, `CALL`, `RETURN`;
- labels e fluxo de controlo no IR.

## Comando executado

```bash
python3 -m unittest testes/test_ir.py
```

## Resultado

- `Ran 22 tests`
- `OK`

## Estado

Todos os testes do IR passaram.
