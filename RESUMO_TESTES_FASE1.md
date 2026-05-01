# Resumo dos Testes da Fase 1

## Ficheiro de testes

Foi criado o ficheiro `testes_fase1.py` para validar pontos mais sensíveis da análise léxica, sintática e semântica.

## Comando executado

```bash
python3 testes_fase1.py
```

## Resultado global

- Total de testes executados: `10`
- Resultado: `OK`
- Falhas: `0`
- Erros: `0`

## O que foi testado

### Análise léxica

- Comentários inline com `!`
- Deteção de carácter ilegal

### Análise sintática

- `logical IF`
- `IF ... THEN ... ELSE ... ENDIF`
- Distinção entre chamada de função e acesso a array

### Análise semântica

- Ciclo `DO` válido com label final em `CONTINUE`
- Rejeição de `DO` com label final numa instrução inválida
- Rejeição de uso de variável não inicializada
- Suporte a `FUNCTION` e `SUBROUTINE`
- Rejeição de dois `PROGRAM` principais no mesmo ficheiro

## Conclusão

Os testes executados não revelaram problemas imediatos nas três análises para os casos escolhidos. Em particular, os pontos que pareciam mais sensíveis à leitura do código comportaram-se de acordo com a implementação atual.

## Observações

- Estes testes não provam que a fase 1 esteja totalmente fechada; apenas confirmam que os casos críticos testados estão a funcionar.
- A regra semântica de rejeitar variáveis não inicializadas está ativa e foi confirmada por teste. Esta decisão é mais restritiva do que o mínimo pedido no enunciado, por isso convém mantê-la explícita no relatório e nos testes.
- Continuam a faltar testes mais largos com programas completos e combinações maiores de construções da linguagem.
