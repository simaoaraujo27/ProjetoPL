# Plano da Parte 2: Valorizacao com Codigo Intermedio e VM

Este documento define o que falta fazer na parte 2 do projeto: traduzir Fortran 77 para um codigo intermédio e, a partir dele, gerar codigo para a linguagem da virtual machine.

Sequencia geral da fase 2:

`Fortran77 -> AST + tabela de simbolos -> IR -> codigo VM`

## 1. Sequencia de trabalho

1. fechar o subconjunto Fortran que vai ser suportado na primeira iteracao;
2. listar os nodes da AST e a informacao da tabela de simbolos que entram na traducao;
3. definir o formato do IR;
4. definir o layout de memoria da VM: `gp`, `fp`, arrays e strings;
5. implementar `AST + tabela de simbolos -> IR`;
6. implementar `IR -> VM`;
7. testar com programas pequenos e comparar `AST`, `IR` e `.vm`;
8. alargar para arrays, `DO`, funcoes e subrotinas;
9. documentar exemplos e integrar no relatorio.

## 2. Objetivo funcional

No fim desta fase, o compilador deve:

- receber um programa Fortran 77 dentro do subconjunto que ja suportamos;
- reutilizar a analise lexica, sintatica e semantica existente;
- reutilizar a tabela de simbolos produzida nessa analise;
- gerar uma representacao intermédia explicita;
- traduzir essa representacao para instrucoes da VM;
- produzir um ficheiro de saida executavel pela VM;
- ser validado com exemplos simples e representativos.

## 3. Detalhe de cada passo

### 3.1 Fechar o subconjunto inicial

Antes de tentar cobrir toda a gramatica, devemos fechar um subconjunto minimo executavel.

Primeira meta:

- `PROGRAM ... END`
- declaracoes `INTEGER`, `REAL`, `LOGICAL`
- atribuicoes escalares
- expressoes com `+`, `-`, `*`, `/`
- comparacoes `.LT.`, `.LE.`, `.GT.`, `.GE.`, `.EQ.`, `.NE.`
- `IF` logico
- `GOTO`
- `DO ... CONTINUE`
- `READ`
- `PRINT` e `WRITE`

So depois disso devemos alargar para:

- arrays;
- `Arithmetic IF`;
- `Computed GOTO`;
- `FUNCTION` e `SUBROUTINE`;
- `CHARACTER`;
- `PARAMETER`, `DATA`, `DIMENSION`;
- `STOP` e `RETURN` com politica clara de traducao.

### 3.2 Definir a arquitetura da traducao

Para esta parte, devemos separar a traducao em duas fases:

1. `AST + tabela de simbolos -> IR`
2. `IR -> VM`

Isto e melhor do que gerar VM diretamente a partir da AST porque:

- simplifica a traducao de expressoes e controlo de fluxo;
- evita misturar regras de Fortran com detalhes de baixo nivel da VM;
- permite usar a informacao semantica ja resolvida em vez de a recalcular;
- facilita testes intermédios;
- torna mais simples depurar erros de traducao.

### 3.3 Definir o papel da tabela de simbolos

A tabela de simbolos nao serve apenas para validacao semantica.

Na parte 2, ela continua a ser uma entrada da traducao e deve fornecer pelo menos:

- tipo de cada identificador;
- categoria do simbolo: variavel, array, parametro, funcao, subrotina;
- dimensoes dos arrays;
- parametros formais de funcoes e subrotinas;
- labels conhecidas no scope;
- separacao entre scope global e scopes locais.

Mais a frente, esta estrutura deve ser enriquecida com informacao de geracao de codigo, por exemplo:

- offset em `gp` para globais;
- offset em `fp` para parametros e locais;
- endereco base e tamanho de arrays;
- metadata para retorno de funcoes.

Em termos práticos, a AST diz a estrutura do programa, enquanto a tabela de simbolos diz o significado de cada nome. O IR deve ser gerado a partir das duas coisas em conjunto.

### 3.4 Definir o que o IR representa

O IR deve ser uma forma simples, linear e independente da sintaxe concreta do Fortran.

Deve conseguir representar:

- atribuicoes;
- leitura e escrita;
- operacoes aritmeticas;
- operacoes relacionais;
- operacoes logicas;
- labels;
- saltos incondicionais;
- saltos condicionais;
- ciclos `DO`;
- chamadas a funcoes e subrotinas, se decidirmos incluir essa parte na valorizacao;
- acessos a arrays;
- declaracoes de variaveis globais e locais.

Ao gerar estas instrucoes, o tradutor deve consultar a tabela de simbolos para saber:

- o tipo dos operandos;
- se um identificador e escalar, array ou funcao;
- quantos indices um acesso a array deve ter;
- que estrategia de acesso a memoria deve ser usada.

O IR nao precisa de ser sofisticado. Uma abordagem suficiente e usar instrucoes do genero:

- `LABEL L1`
- `JUMP L2`
- `JUMP_IF_FALSE t1 L3`
- `ASSIGN x t2`
- `BINOP t3 t1 + t2`
- `UNOP t4 NOT t3`
- `LOAD_ARRAY t5 A i`
- `STORE_ARRAY A i t5`
- `READ x`
- `WRITE x`
- `WRITE_LN`
- `CALL t6 F [a, b]`
- `RETURN x`

### 3.5 Definir a forma do IR

Convem definir classes ou dicionarios para estas entidades:

- `IRProgram`
- `IRFunction` ou `IRUnit`
- `IRInstruction`
- `IRLabel`
- `IRTemp`
- `IRConstant`
- `IRVariable`

Tambem precisamos de utilitarios para gerar:

- temporarios: `t1`, `t2`, `t3`, ...;
- labels internas: `L1`, `L2`, `L3`, ...;
- tabelas de offsets para variaveis globais e locais;
- metadados de tipo: `INTEGER`, `REAL`, `LOGICAL`, `CHARACTER`.

Convem distinguir duas estruturas:

- tabela de simbolos semantica, que ja existe;
- tabela de layout, usada na geracao de codigo.

A segunda pode ser derivada da primeira, sem duplicar validacoes.

### 3.6 Definir o mapeamento de tipos para a VM

Precisamos de fixar uma convencao simples:

- `INTEGER` -> inteiro da VM
- `LOGICAL` -> inteiro da VM (`0 = falso`, `1 = verdadeiro`)
- `REAL` -> real da VM
- `CHARACTER` -> endereco para String Heap da VM

Regras importantes:

- operacoes entre inteiros usam `ADD`, `SUB`, `MUL`, `DIV`, etc.;
- operacoes entre reais usam `FADD`, `FSUB`, `FMUL`, `FDIV`, etc.;
- comparacoes inteiras usam `INF`, `INFEQ`, `SUP`, `SUPEQ`, `EQUAL`;
- comparacoes reais usam `FINF`, `FINFEQ`, `FSUP`, `FSUPEQ`;
- negacao logica pode ser traduzida com `NOT`;
- quando houver mistura `INTEGER` / `REAL`, deve ser feita conversao explicita com `ITOF` ou `FTOI`.

### 3.7 Definir o layout de memoria na VM

Antes de gerar codigo, temos de decidir onde cada coisa vive.

Proposta:

- `gp` para variaveis globais do programa principal;
- `fp` para parametros e locais de funcoes/subrotinas;
- heap estruturada para arrays;
- string heap para literais e valores lidos com `READ`.

Temos de implementar:

- tabela de offsets globais;
- tabela de offsets locais por unidade de programa;
- tabela de arrays com base, dimensoes e estrategia de indexacao.

Esta informacao deve ser derivada da tabela de simbolos, nao descoberta de novo durante a traducao.

### 3.8 Implementar a traducao de expressoes

As expressoes devem ser traduzidas em pos-ordem para a pilha da VM.

Exemplo conceptual:

`X = A + B * C`

Passos:

1. gerar IR para `B * C`
2. gerar IR para `A + (resultado anterior)`
3. guardar o resultado em `X`

Na VM isto tende a ficar:

- carregar `A`
- carregar `B`
- carregar `C`
- `MUL`
- `ADD`
- guardar em `X`

Isto implica escrever um gerador de expressoes que devolva:

- instrucoes IR;
- o operando final onde ficou o resultado;
- o tipo inferido do resultado.

Esse tipo deve vir da tabela de simbolos e das regras semanticas ja fixadas, para decidir a operacao certa e eventuais conversoes.

### 3.9 Implementar a traducao de atribuicoes

Para escalares:

- avaliar a expressao;
- converter tipo, se necessario;
- armazenar no offset correto com `STOREG` ou `STOREL`.

Para arrays:

- calcular o endereco do elemento;
- avaliar a expressao;
- usar `STORE` ou `STOREN`, conforme a convencao adotada.

### 3.10 Implementar a traducao de controlo de fluxo

### `IF`

Estrategia:

- gerar a condicao;
- saltar para label `else` ou `end` se for falsa;
- emitir bloco `then`;
- se houver `else`, saltar para `end`;
- emitir labels finais.

### `GOTO`

- mapear diretamente para `JUMP label`.

### `DO`

O `DO` precisa de ser normalizado para labels e saltos.

Forma conceptual:

1. inicializar variavel de controlo;
2. criar label de teste;
3. comparar com limite;
4. saltar para fim se a condicao falhar;
5. emitir corpo;
6. atualizar contador com o passo;
7. voltar ao teste.

Temos de definir com cuidado:

- comportamento do passo omitido;
- comparacao correta quando o passo e negativo;
- forma de traduzir a label terminal `CONTINUE`.

### 3.11 Implementar a traducao de input/output

### `READ`

A VM fornece `READ`, mas devolve string. Por isso:

- `READ` + `ATOI` para `INTEGER`;
- `READ` + `ATOF` para `REAL`;
- para `CHARACTER`, manter o endereco da string;
- para `LOGICAL`, decidir uma convencao de entrada ou adiar suporte.

### `PRINT` / `WRITE`

Devemos escolher a instrucao conforme o tipo:

- `WRITEI`
- `WRITEF`
- `WRITES`
- `WRITECHR`, se for necessario imprimir caracteres isolados
- `WRITELN`, quando fizer sentido terminar linha

### 3.12 Implementar arrays

Esta e uma das partes que precisa de decisao tecnica antes de implementar.

Temos de decidir:

- se os arrays vao ser sempre alocados na heap com `ALLOC` ou `ALLOCN`;
- como converter indices Fortran para offsets lineares;
- como tratar limites nao iniciados em `1`;
- se vamos suportar ja arrays multidimensionais ou apenas 1D primeiro.

Proposta minima:

- implementar primeiro arrays 1D;
- guardar tamanho e endereco base;
- calcular `offset = indice - limite_inferior`;
- usar `PADD` e `LOAD` / `STORE`.

Depois disso, estender para multidimensionais.

### 3.13 Implementar funcoes e subrotinas

Se esta valorizacao incluir `FUNCTION` e `SUBROUTINE`, precisamos de definir:

- convencao de chamada;
- passagem de parametros;
- valor de retorno;
- layout de frame.

Pontos minimos:

- `PUSHA label`
- `CALL`
- `RETURN`

No caso de `FUNCTION`, o resultado pode seguir uma destas abordagens:

- ser devolvido no topo da pilha antes do `RETURN`;
- ou seguir a convencao Fortran de atribuir ao nome da funcao e, no fim, colocar esse valor no topo.

Como a analise semantica atual ja valida atribuicao ao nome da funcao, a segunda abordagem encaixa bem no projeto.

### 3.14 Criar os modulos necessarios

Sugestao de organizacao:

- `IR/ir.py`:
  definicoes das classes do codigo intermédio
- `IR/ir_generator.py`:
  traducao de AST para IR
- `vm_codegen.py`:
  traducao de IR para codigo da VM
- `compiler.py`:
  pipeline completa `lexer -> parser -> semantica -> IR -> VM`
- `test_codegen.py`:
  testes da traducao
- `EXEMPLOS_VM.md` ou equivalente:
  exemplos de saida esperada

Se preferirmos mexer menos na estrutura atual, o essencial e pelo menos separar:

- representacao IR;
- gerador IR;
- gerador VM.

### 3.15 Ordem de implementacao recomendada

### Fase A. Preparacao

- rever a AST atual e listar exatamente os tipos de nodes que vao entrar na traducao;
- rever a tabela de simbolos atual e confirmar que dados podem ser reutilizados diretamente;
- decidir o subconjunto inicial suportado;
- definir o formato interno do IR;
- definir como derivar a tabela de offsets a partir da tabela de simbolos.

### Fase B. IR minimo

- gerar IR para literais e identificadores;
- gerar IR para expressoes binarias e unarias;
- gerar IR para atribuicoes escalares;
- gerar IR para `READ`, `PRINT` e `WRITE`;
- gerar IR para `GOTO` e labels;
- gerar IR para `IF`.

### Fase C. VM minima

- traduzir IR de valores e carregamentos para `PUSHI`, `PUSHF`, `PUSHS`, `PUSHG`, `PUSHL`;
- traduzir operacoes para `ADD`, `SUB`, `MUL`, `DIV`, `FADD`, etc.;
- traduzir armazenamento para `STOREG` e `STOREL`;
- traduzir labels e saltos para `JUMP` e `JZ`.

### Fase D. Ciclos e arrays

- implementar traducao de `DO`;
- implementar arrays 1D;
- adicionar verificacoes simples de indexacao no codigo gerado, se fizer sentido usar `CHECK`.

### Fase E. Procedimentos

- implementar `SUBROUTINE`;
- implementar `FUNCTION`;
- definir e testar chamadas com parametros.

### Fase F. Fecho

- gerar um ficheiro final `.vm` por programa;
- documentar exemplos de traducao;
- escrever testes automatizados;
- integrar os resultados no relatorio.

### 3.16 Definir os testes

Temos de validar pelo menos estes casos:

- atribuicao inteira simples;
- atribuicao real simples;
- expressao com precedencia;
- `IF` sem `ELSE`;
- `IF` com `ELSE`;
- `GOTO` com label existente;
- ciclo `DO` com passo omitido;
- ciclo `DO` com passo explicito;
- `READ` para inteiro;
- `PRINT` de inteiro e real;
- array 1D com leitura e escrita;
- chamada a funcao ou subrotina, se essa parte for implementada.

Tambem convem comparar:

- AST esperada;
- IR esperado;
- codigo VM esperado.

### 3.17 Fechar decisoes antes de codar

Estas decisoes devem ser tomadas logo no inicio:

- qual e exatamente o subconjunto Fortran que a fase 2 vai suportar;
- se o IR vai ser baseado em classes ou em dicionarios simples;
- como mapear globais, locais e parametros para `gp` e `fp` a partir da tabela de simbolos;
- se arrays entram logo na primeira versao ou numa segunda iteracao;
- se `FUNCTION` e `SUBROUTINE` entram ja ou ficam como extensao final;
- como lidar com `LOGICAL` em `READ` e `WRITE`;
- como representar strings e `CHARACTER`.

### 3.18 Resultado esperado da fase

Quando esta parte estiver concluida, devemos ter:

- um documento com a especificacao do IR;
- uma ligacao clara entre AST, tabela de simbolos e traducao;
- codigo capaz de gerar IR a partir da AST;
- codigo capaz de traduzir IR para a VM;
- exemplos `.f` traduzidos para `.vm`;
- testes da traducao;
- material para escrever a secao do relatorio final sobre a valorizacao.

### 3.19 Proximo passo imediato

O primeiro passo recomendado e este:

1. listar os nodes da AST que vao ser suportados na primeira iteracao;
2. listar que informacao da tabela de simbolos entra em cada traducao;
3. desenhar o formato exato das instrucoes IR;
4. implementar um gerador IR minimo para atribuicoes, expressoes, `IF`, `READ` e `PRINT`;
5. so depois ligar esse IR ao gerador de codigo VM.

Assim evitamos tentar resolver arrays, chamadas e frames de ativacao demasiado cedo.
