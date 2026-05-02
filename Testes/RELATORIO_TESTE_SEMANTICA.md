# Relatorio de Testes da Semantica

Ficheiro de testes:

- [test_semantica.py](/home/francisco/Secretária/2Semestre3Ano/PL/ProjetoPL/testes/test_semantica.py:1)

## Objetivo

Validar a analise semantica e a construcao da tabela de simbolos.

## Cobertura pratica

Os testes cobrem:

- leitura dos ficheiros exemplo;
- construcao da tabela de simbolos;
- labels e referencias de labels;
- arrays e `DIMENSION`;
- funcoes, subrotinas e parametros;
- intrinseca `MOD`;
- casos validos da semantica;
- casos invalidos da semantica;
- multiplos erros no mesmo programa;
- mensagens de erro com numero de linha;
- alguns testes integrados de fase 1 para lexer, parser e semantica juntos.

## Comando executado

```bash
python3 -m unittest testes/test_semantica.py
```

## Resultado

- `Ran 17 tests`
- `OK`

## Estado

Todos os testes da semantica passaram.
