# 🔤 Construtos Reconhecidos  

Esta seção descreve detalhadamente todos os construtos reconhecidos pelo **analisador sintático**, conforme a especificação apresentada na documentação do trabalho e na [monografia](https://matheuslenke.github.io/tonto-docs/pdf/Tonto.pdf) oficial da linguagem **TONTO** (*APPENDIX A – Tonto Grammar*).

> [!TIP]
> As regras para escrever os nomes de *classes* (*pacotes*, *enumerações* e *generalization sets* seguem o mesmo padrão), *novos tipos de dados*, *instâncias* e *relações* foram especificadas no [Analisador Léxico](https://github.com/geyseevelyn/lexical_analyzer/blob/main/docs/tokens_tonto_details.md).

---

## 1. Declarações de Importação 

**TONTO** permite importar outros módulos **antes** da declaração do pacote principal através da palavra-chave `import`. Essas importações funcionam como **dependências externas** ou **bibliotecas de tipos**.

#### Estrutura:
```tonto
import <NomeDoMódulo>
```

#### Exemplos:
```tonto
import CoreDatatypes
import PersonPhases

package University
```

---

## 2. Declaração de Pacotes

Todo arquivo **TONTO** deve começar pela declaração de um `package`, que funciona como um *namespace* ou um contêiner lógico de classes, seus respectivos atributos e
relações.

#### Estrutura:

```tonto
package <NomeDoPacote>
```

#### Exemplo:

```tonto
package University
```

---

## 3. Declaração de Classes

As classes em **TONTO** podem assumir três formas distintas: simples, com generalização ou estruturada. Todas seguem o padrão *OntoUML*, e utilizam estereótipos específicos como: `kind`, `subkind`, `role`, `phase`, `collective`, `roleMixin`, `relator`, entre outros.


### 3.1. Classe Simples

#### Estrutura:

```tonto
<estereótipo> <NomeDaClasse>
```

#### Exemplo:

```tonto
role Employer
kind Room
phase FormerStudent
```

### 3.2. Classe com Generalização (*specializes*)

Define herança entre classes.

#### Estrutura:

```tonto
<estereótipo> <NomeDaClasse> specializes <NomeDaSuperClasse>
```

#### Exemplos:

```tonto
subkind JuniorStaff specializes Staff
subkind SeniorStaff specializes Staff
role UniversityEmployer specializes Employer, University
```

### 3.3. Classe Estruturada (com corpo)

Inclui atributos próprios e/ou relações internas.

#### Estrutura:

```tonto
<estereótipo> <NomeDaClasse> {
    <atributos>        [opcional]
    <relações internas>  [opcional]
    ...
}
```

#### Exemplos:

* Classe contendo atributo e relação interna:

   ```tonto
   kind University {
      address: AddressDataType
      @componentOf [1] <>-- has -- [1..*] Department
   }
   ```

* Classe apenas com atributos:

   ```tonto
   kind Person {
      name: string
      birthDate: date {const}
   }
   ```

---

## 4. Declaração de Tipos de Dados

**TONTO** permite construir ou derivar novos tipos de dados mais complexos a partir dos seis tipos nativos:  `number`, `string`, `boolean`, `date`, `time`, `datetime`. A declaração desse tipo de construto é precedida pela palavra reservada `datatype`.

### 4.1. Tipos de Dados com Atributos

#### Estrutura:

```tonto
datatype <NomeDoTipoDataType> {
    <atributo>: <TipoNativo> ou <NovoTipo> <CardinalidadeOpcional> <MetaAtributoOpcional>
    ...
}
```

#### Exemplos:

* Tipo de dado apenas com atributos:

   ```tonto
   datatype AddressDataType {
      street: string
      number: number
   }
   ```

* Tipo de dado com atributos e cardinalidade:

   ```tonto
   datatype PhoneNumberDataType { 
      countryCode: intDataType [1]
      bodyNumber: intDataType [1]
   }
   ```

### 4.2. Tipos de Dados com Generalização (*specializes*)

#### Estrutura:

```tonto
datatype <NomeDoTipoDataType> specializes <TipoNativo> ou <NovoTipo> ou <NomeDaClasse>
```

#### Exemplo:

```tonto
datatype intDataType specializes number
```

---

## 5. Declaração de Classes Enumeradas

Utilizadas para definir conjuntos finitos e pré-definidos de instâncias (ou indivíduos). A declaração desse tipo de classe é precedida pela palavra reservada `enum`.

#### Estrutura:

```tonto
enum <NomeDaEnum> {
     <NomeDaInstancia1>
     <NomeDaInstancia2>
    ...
}
```

#### Exemplo:

```tonto
enum EyeColor {
    Blue1
    Green1
    Brown1
    Grey1
}
```

---

## 6. Declaração de Generalizações (*Generalization Sets*)

**TONTO** fornece duas formas de declarar grupos de generalizações (*generalization sets*). Ambas são definidas pela palavra-chave `genset` e podem incluir **restrições disjunção ou completude** opcionais (`disjoint`, `complete`, etc.)

### 6.1. Forma Estruturada

Utiliza um bloco `{ }` para declarar explicitamente os elementos do *generalization set*.
Nesta abordagem, tanto a classe mãe quanto as classes filhas são listadas em linhas separadas dentro do corpo do `genset`, garantindo maior legibilidade em taxonomias mais complexas.

#### Estrutura:

```tonto
<RestriçõesOpcionais> genset <NomeDoGenset> {
    general <ClasseMae>
    categorizer <NomeDaClasse>   [opcional]
    specifics <ClasseFilha1>, <ClasseFilha2>,...
}
```

#### Exemplos:

* Sem restrições: 

    ```tonto
    genset PersonAgeGroup {
        general Person
        specifics Child, Adult
    }
    ```
    
* Com restrições: 

    ```tonto
    disjoint complete genset AgePhase {
        general LivingPerson
        specifics Child, Teenager, Adult
    }
    ```

### 6.2. Forma Compacta

Permite declarar um *generalization set* em uma única linha, utilizando a palavra-chave `where` sem bloco `{ }`. Nessa forma, as subclasses aparecem diretamente após o `where`, seguidas pela palavra reservada `specializes` indicando a classe mãe.

#### Estrutura:

```tonto
<RestriçõesOpcionais> genset <NomeDoGenset> where <ClasseFilha1>, <ClasseFilha2>, ... specializes <ClasseMae> 
```

#### Exemplo:

```tonto
disjoint complete genset PersonAgeGroup where Child, Adult specializes Person
```

---

## 7. Declarações de Relações

As relações em **TONTO** podem ser **internas** (dentro de classes) ou **externas** (fora de classes). Elas podem ou não ser nomeadas e seus estereótipos são **opcionais**.

### 7.1 Relações Internas

Declaradas **dentro** do corpo de uma classe.

#### Exemplos:

* Relação interna **com nome**: 

    ```tonto
    kind University {
        @componentOf [1] <>-- has -- [1..*] Department
    }
    ```

* Relação interna **sem nome**: 

    ```tonto
    kind Department {
        name: string
        @componentOf [1] <>-- [1] JuniorStaff
        @componentOf [1] <>-- [1] SeniorStaff
    }
    ```

### 7.2 Relações Externas

Declaradas **fora do escopo** de qualquer classe, usando a palavra-chave `relation`.

#### Exemplos:

* Relação externa **com nome**:

    ```tonto
    relation Person [0..*] -- hasFriend -- [0..] Person 
    ```

* Relação externa **sem nome**:

    ```tonto
    @mediation relation EmploymentContract [1..*] -- [1] Employee
    ```

