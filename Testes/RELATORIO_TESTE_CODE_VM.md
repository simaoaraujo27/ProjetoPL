# Relatorio de Testes do Codigo VM

Ficheiro de testes:

- [test_code_vm.py](/home/francisco/Secretária/2Semestre3Ano/PL/ProjetoPL/testes/test_code_vm.py:1)

## Objetivo

Validar a traducao:

`IR -> codigo VM`

e a integracao final:

`Fortran -> AST -> semantica -> IR -> VM`

## Cobertura pratica

Os testes cobrem:

- offsets globais, locais, parametros e temporarios;
- atribuicoes e expressoes;
- saltos condicionais;
- `READ`, `WRITE`, `WRITELN`;
- arrays 1D;
- arrays multidimensionais;
- `DO`;
- `CALL` e `RETURN`;
- compilacao fim-a-fim para `.vm`;
- escrita de ficheiro `.vm`.

## Comando executado

```bash
python3 -m unittest testes/test_code_vm.py
```

## Resultado

- `Ran 12 tests`
- `OK`

## Estado

Todos os testes do codigo VM passaram.
