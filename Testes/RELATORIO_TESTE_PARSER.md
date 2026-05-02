# Relatorio de Testes do Parser

Ficheiro de testes:

- [test_parser.py](/home/francisco/Secretária/2Semestre3Ano/PL/ProjetoPL/testes/test_parser.py:1)

## Objetivo

Validar a fase sintatica do compilador.

## Cobertura pratica

Os testes cobrem:

- programa minimo;
- declaracoes e tipos basicos;
- `IF` logico;
- `IF ... THEN ... ELSE ... ENDIF`;
- `DO ... CONTINUE`;
- arrays e chamada a `MOD`;
- `ComputedGoto`;
- `ArithmeticIf`;
- `FUNCTION` e `SUBROUTINE`;
- `READ`, `WRITE`, `PRINT` e `STOP`;
- casos de erro sintatico.

## Comando executado

```bash
python3 -m unittest testes/test_parser.py
```

## Resultado

- `Ran 12 tests`
- `OK`

## Estado

Todos os testes do parser passaram.
