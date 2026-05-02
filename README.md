# ProjetoPL

Compilador para uma subset da linguagem **Fortran 77 Standard**, desenvolvido no âmbito da unidade curricular de Processamento de Linguagens.

## Autores

- Francisco Barbosa (`a107286`)
- Pedro Morais (`a107319`)
- Simão Araújo (`a106855`)

## Visão Geral

O projeto implementa uma pipeline completa de compilação:

1. análise léxica
2. análise sintática
3. análise semântica
4. geração de representação intermédia (IR)
5. geração de código para a máquina virtual EWVM

O ponto de entrada principal é o ficheiro [`compiler.py`](./compiler.py), que recebe um programa Fortran e produz o respetivo ficheiro `.vm`.

## Estrutura do Projeto

- [`Lexer/`](./Lexer): analisador léxico
- [`Parser/`](./Parser): gramática, AST e parser
- [`Semantic/`](./Semantic): tabela de símbolos e validação semântica
- [`IR/`](./IR): representação intermédia e otimizações
- [`EWVM/`](./EWVM): geração de código para a máquina virtual
- [`Exemplos/`](./Exemplos): programas Fortran de exemplo e saídas `.vm`
- [`Testes/`](./Testes): suite de testes unitários e relatórios de teste
- [`Relatório-PL.pdf`](./Relatório-PL.pdf): relatório do projeto

## Requisitos

- Python 3
- biblioteca `ply`

Instalação da dependência:

```bash
pip install ply
```

## Como Executar

Compilar um ficheiro Fortran para código EWVM:

```bash
python3 compiler.py Exemplos/exemplo1.f
```

Por omissão, o compilador cria um ficheiro com o mesmo nome e extensão `.vm` no mesmo diretório do ficheiro de entrada.

Também é possível indicar explicitamente o ficheiro de saída:

```bash
python3 compiler.py Exemplos/exemplo1.f saida.vm
```

Uso geral:

```bash
python3 compiler.py <ficheiro.f> [ficheiro.vm]
```

## Testes

Para executar a suite de testes unitários:

```bash
python3 -m unittest discover -s Testes
```

Os testes cobrem as diferentes fases da pipeline:

- lexer
- parser
- semântica
- IR
- geração de código VM

## Exemplo de Fluxo

1. escolher um ficheiro em [`Exemplos/`](./Exemplos)
2. executar o compilador sobre esse ficheiro
3. inspecionar o `.vm` gerado

Exemplo:

```bash
python3 compiler.py Exemplos/exemplo7.f
```

## Notas

- O parser pode ser executado isoladamente com `python3 -m Parser <ficheiro>`.
- O compilador tenta resolver diferenças de capitalização no caminho do ficheiro de entrada.
