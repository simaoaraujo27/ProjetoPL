# Plano de Trabalho

Este ficheiro resume a ordem de trabalho proposta para fechar o projeto de PL.

## 1. Relatorio da parte lexica, sintatica e semantica

Estado:
- Concluido

Objetivo:
- Rever o que ja esta implementado nas fases lexica, sintatica e semantica.
- Corrigir erros, lacunas e inconsistencias encontradas.
- Consolidar essa parte num relatorio tecnico claro.

Checklist:
- Confirmar tokens, regras lexicas e casos especiais no `lexer.py`.
- Confirmar gramatica, precedencias e cobertura de construcoes no `parser.py`.
- Rever validacoes semanticas, tabela de simbolos e mensagens de erro.
- Atualizar a documentacao existente com o estado real da implementacao.

Fecho da fase:
- Foi criado e atualizado o `RELATORIO_FINAL.md` com as secoes de analise lexica, sintatica e semantica.
- Foi feita revisao da implementacao atual das tres fases.
- Foi criado o ficheiro `testes_fase1.py` para validar pontos mais sensiveis da fase 1.
- Foi criado o `RESUMO_TESTES_FASE1.md` com o resultado da execucao dos testes.
- Os testes executados para a fase 1 passaram sem falhas.

## 2. Traducao de codigo com valorizacao

Estado:
- Por fazer

Objetivo:
- Passar para a fase de traducao de codigo.
- Implementar a traducao com a valorizacao pedida no enunciado.

Checklist:
- Rever no `enunciado.pdf` exatamente qual e a valorizacao exigida.
- Definir formato de saida da traducao.
- Implementar a traducao principal.
- Implementar a parte adicional da valorizacao.
- Validar a traducao com exemplos representativos.

## 3. Relatorio da parte de traducao de codigo

Estado:
- Por fazer

Objetivo:
- Documentar a abordagem usada na traducao.
- Explicar decisoes, limitacoes e exemplos de entrada/saida.

Checklist:
- Descrever a estrategia de traducao.
- Explicar a valorizacao implementada.
- Incluir exemplos concretos.
- Registar limitacoes conhecidas e trabalho futuro, se fizer sentido.

## 4. Testes e integracao no relatorio

Estado:
- Em aberto

Objetivo:
- Garantir que as fases implementadas estao testadas.
- Integrar os resultados dos testes no relatorio final.

Checklist:
- Criar ou completar testes para analise lexica, sintatica, semantica e traducao.
- Executar testes com exemplos validos e invalidos.
- Registar resultados relevantes.
- Incluir os testes e as conclusoes no relatorio.

## Ordem de execucao

1. Fechar e documentar a analise lexica, sintatica e semantica.
2. Implementar a traducao de codigo com valorizacao.
3. Escrever o relatorio da traducao.
4. Fechar testes e integrar tudo no relatorio final.
