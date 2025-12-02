# Analisador Sintático para a Linguagem TONTO

Este projeto implementa um **Analisador Sintático** (Parser) para a linguagem [*TONTO*](https://matheuslenke.github.io/tonto-docs/docs/intro), utilizando **Python** e a biblioteca **PLY (Python Lex-Yacc)**. O objetivo é validar a estrutura sintática de uma ontologia descrita nessa linguagem, produzindo um **resumo sintático** que representa a estrutura do programa.

---

## 📋 Tabela de Conteúdos
<!--ts-->
   * [A Linguagem TONTO](#-a-linguagem-tonto)
   * [Sobre o Projeto](#-sobre-o-projeto)
   * [Tecnologias Utilizadas](#-tecnologias-utilizadas)
   * [Estrutura de Pastas](#-estrutura-de-pastas)
   * [Funcionalidades](#-funcionalidades)
   * [Construtos Reconhecidos](#-construtos-reconhecidos)
   * [Como Usar](#-como-usar)
   * [Exemplo de Uso](#-exemplo-de-uso)
   * [Autores](#%E2%80%8D-autores)
   * [Licença](#-licença)
<!--te-->

---

## 🧩 A Linguagem TONTO

A **TONTO** (*Textual Ontology Language*) é uma linguagem textual para modelagem de ontologias, desenvolvida por **Matheus Lenke Coutinho**. Criada com o objetivo de superar limitações das linguagens de modelagem puramente visuais, ela permite a **edição**, **validação** e **versionamento** de ontologias por meio de **código textual** e também a **conversão** para outros para outros formatos como:

- *OntoUML*
- *gUFO (OWL)*
- *JSON*

Também possui extensão para o *VSCode*, permitindo criar módulos `.tonto`, gerenciar dependências com o *Tonto Package Manager* e gerar modelos interoperáveis com o *Protégé* e o *Visual Paradigm*.

> [!TIP]
> Para mais informações sobre a linguagem, consulte a [documentação oficial](https://matheuslenke.github.io/tonto-docs/docs/intro), a [monografia completa](https://matheuslenke.github.io/tonto-docs/pdf/Tonto.pdf) e o [repositório oficial no GitHub](https://github.com/matheuslenke/Tonto).

---

## 📖 Sobre o Projeto

O **Analisador Sintático para a Linguagem TONTO** foi desenvolvido como parte de um estudo prático sobre a construção de compiladores e ferramentas de análise sintática. O projeto complementa o **Analisador Léxico** (documentação completa pode ser acessada [aqui](https://github.com/geyseevelyn/lexical_analyzer)) previamente desenvolvido e consome diretamente os *tokens* produzidos por ele. O objetivo é verificar a corretude da especificação textual de uma ontologia nos seguintes casos:

- **Declaração de importações**;
- **Declaração de pacotes**;
- **Declaração de classes**;
- **Declaração de tipos de dados**;
- **Declaração de classes enumeradas**;
- **Declaração de generalizações (*generalization sets*)**;
- **Declarações de relações (internas e externas)**.

---

## 🛠 Tecnologias Utilizadas

- **Python 3.10+**;
- **PLY** (Python Lex-Yacc)
- **TONTO** (Extensão do *VS Code*, *Tonto CLI* e *Tonto Package Manager*).

---

## 📂 Estrutura de Pastas

```shell
syntactic_analyzer/
├── docs/                      
│   └── tonto_constructs.md     # Detalhes sobre as construções da linguagem TONTO
│
├── examples/                   # Arquivos TONTO de entrada para testes
├── src/                        
│   ├── cli/
│   │   ├── __init__.py         # Indica que 'cli' é um pacote Python.
│   │   └── main.py             # Ponto de entrada da aplicação. Contém o CLI e o menu principal.
│   │
│   ├── lexical/
│   │   ├── __init__.py         # Indica que 'lexical' é um pacote Python
│   │   ├── lexer.py            # Definições do Lexer (PLY) e regras léxicas (tokens) 
│   │   └── reports.py          # Funções para exibir relatórios léxicos (Tokens, Tabela de Símbolos, Contagem)
│   │
│   ├── parsing/
│   │   ├── __init__.py         # Indica que 'parsing' é um pacote Python
│   │   ├── grammar.py          # Definições do Parser (PLY) e regras de gramática
│   │   ├── reports.py          # Funções para exibir relatórios sintáticos (Resumo e Erros)
│   │   └── summary.py          # Classe ModelBuilder para coletar o resumo sintático
│   │
│   └── __init__.py             # Define 'src' como o pacote raiz.
│
├── .gitignore                  # Arquivo para ignorar pastas e arquivos gerados (padrão Git)
├── LICENSE                     # Informações sobre a licença de uso do código.
└── README.md                   # Documentação principal do projeto.

```

---

## ✨ Funcionalidades

Além de manter todas funcionalidades do [**analisador léxico**](https://github.com/geyseevelyn/lexical_analyzer), o **Analisador Sintático** oferece: 

* **Validação Sintática**: verifica a corretude estrutural de ontologias escritas em **TONTO**;

* **Geração de Resumo Sintático**: exibe uma representação hierárquica da estrutura do programa e a quantidade de construtos válidos encontrados;

* **Detecção de Erros**: identifica e reporta erros sintáticos com detalhes de linha e *token*;

* **Integração com Lexer**: usa os *tokens* gerados pelo analisador léxico;

* **Menu Interativo:** permite a navegação por arquivos `.tonto` e a visualização de resultados.

---

## 🔤 Construtos Reconhecidos  

A **especificação detalhada** dos construtos da linguagem **TONTO** reconhecidas pelo **analisador sintático** pode ser encontrada nesse [documento](docs/tonto_constructs.md).

---

## 🚀 Como Usar

### Pré-requisitos 

- [Python 3.10+](https://www.python.org/downloads/)
- [PLY (Python Lex-Yacc)](https://www.dabeaz.com/ply/)

### Instalação

1. Clone o repositório ou baixe o arquivo ZIP:

   ```bash
   git clone https://github.com/geyseevelyn/syntactic_analyzer.git
   ```

2. Acesse a pasta do projeto:

   ```bash
   cd syntactic_analyzer
   ```

3. Instale a dependência necessária (PLY):

   ```bash
   pip install ply
   ```

### Execução

1. Já na pasta do projeto, execute o código:

   ```bash
   python -m src.cli.main
   ```

2. Na **menu interativo**, escolha uma opção:
   - **Opção 1**: Digitar o caminho completo do arquivo `.tonto` no seu computador.
   - **Opção 2**: Listar e escolher um arquivo `.tonto` da pasta `examples`.

3. Após selecionar o arquivo, o programa vai processá-lo e exibir o **menu principal** com opções para:

   * Exibir Tokens Processados (léxico)
   * Exibir Tabela de Símbolos (léxico)
   * Exibir Contagem de Tokens (léxico)
   * **Exibir Resumo Sintático**
   * **Exibir Erros Sintáticos**
   * Analisar outro arquivo (`.tonto`)
   * Sair

### Usando os exemplos prontos

* O projeto já inclui exemplos na pasta`\examples`. Você pode escolher a **Opção 2** quando o programa pedir e selecionar um arquivo da lista, por exemplo:
  * `CarExample\src\car.tonto`
  * `FoodAllergyExample\src\alergiaalimentar.tonto`
  * `TDAHExample\src\TDAH.tonto`

### Usando seu próprio arquivo

1. Tenha um arquivo com a extensão `.tonto` salvo no seu computador.
2. Execute o programa (`python -m src.cli.main`).
3. Escolha a **Opção 1** e cole o caminho completo do arquivo, por exemplo:
   - `C:\Users\seu_usuario\Documents\meu_arquivo.tonto`

---

## 💻 Exemplo de Uso

### Entrada

   ```tonto
   package CarOwnership 

   kind Organization
   subkind CarAgency specializes Organization
   kind Car

   relator CarOwnership {
      @mediation
      -- involvesOwner -- [1] CarAgency

      @mediation
      -- involvesProperty -- [1] Car
   }
   ```
### Saída Esperada

- **Resumo Sintático** (*Opção 4* do menu principal):

   <details>
   <summary>Clique para expandir</summary>
   <br>

   ```
   =========================== RESUMO SINTÁTICO ===========================

   🌳 ONTOLOGIA
   ├──  📥 IMPORTS:
   │   └── (Nenhum pacote importado)
   └──  📦 PACOTE: CarOwnership
      └──  📖 CLASSES:
         ├──  <kind> Organization
         ├──  <subkind> CarAgency specializes Organization
         ├──  <kind> Car
         └──  <relator> CarOwnership
               └──  🔗 RELAÇÕES INTERNAS:
                  ├──  @mediation -- involvesOwner -- [1] CarAgency
                  └──  @mediation -- involvesProperty -- [1] Car


   📊 RESUMO QUANTITATIVO
   ┌───────────────┬─────┐
   │ Construto     │ Qtd │
   ├───────────────┼─────┤
   │ Classes       │   4 │
   │ Datatypes     │   0 │
   │ Enums         │   0 │
   │ GenSets       │   0 │
   │ Rel. internas │   2 │
   │ Rel. externas │   0 │
   └───────────────┴─────┘

   =================================== ## ===================================
   ```

   </details>

- **Erros Sintáticos** (*Opção 5* do  principal):

  <details>
  <summary>Clique para expandir</summary>
  <br>

   ```
   ====================== ERROS SINTÁTICOS =====================

   ✅ Nenhum erro sintático encontrado.

   =========================== ## ==============================
   ```

  </details>

---

## 👨‍💻 Autores

* [Geyse Evelyn](https://github.com/geyseevelyn)
* [Ivanildo Junior](https://github.com/jrsilva95)

---

## 📜 Licença
Este projeto está sob a licença *MIT*. Consulte o arquivo [LICENSE](./LICENSE) para mais detalhes.

---

<div align="center">
    <a href="https://github.com/geyseevelyn/syntactic_analyzer/tree/geyse?tab=readme-ov-file#analisador-sint%C3%A1tico-para-a-linguagem-tonto">Voltar ao topo</a>
</div>