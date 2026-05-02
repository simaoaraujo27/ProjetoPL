# Relatorio de Testes do Lexer

Ficheiro de testes:

- [test_lexer.py](/home/francisco/Secretária/2Semestre3Ano/PL/ProjetoPL/testes/test_lexer.py:1)

## Objetivo

Validar a fase lexica do compilador.

## Cobertura pratica

Os testes cobrem:

- keywords e identificadores;
- tokens compostos como `END IF` e `GO TO`;
- constantes inteiras, reais e strings;
- operadores relacionais e logicos;
- simbolos basicos da linguagem;
- comentarios;
- atualizacao do numero de linha;
- erro em caractere ilegal.

## Comando executado

```bash
python3 -m unittest testes/test_lexer.py
```

## Resultado

- `Ran 8 tests`
- `OK`

## Estado

Todos os testes do lexer passaram.
