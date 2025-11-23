import ply.lex as lex

# Lista de tokens
tokens = [
    'CLASS_STEREOTYPE', 'RELATION_STEREOTYPE', 'KEYWORD', 'SPECIAL_SYMBOL', 'CLASS_NAME', 
    'RELATION_NAME','INSTANCE_NAME', 'NATIVE_DATATYPE', 'NEW_DATATYPE','META_ATTRIBUTE',
    'ENUM_NAME', 'ATTRIBUTE', 'CARDINALITY'
]

# Palavras reservadas
keywords = { 
    'specializes', 'genset', 'disjoint', 'complete', 'general', 'specifics', 'where', 
    'package', 'import', 'functional-complexes', 'relators', 'intrinsic-modes', 'extrinsic-modes', 
    'datatype', 'enum', 'type', 'instanceOf', 'categorizer', 'of', 'relation', 'inverseOf'
}

# Estereótipos de classe
class_stereotypes = { 
    'event', 'situation', 'process', 'category', 'mixin','phaseMixin', 'roleMixin', 
    'historicalRoleMixin', 'kind', 'collective','quantity', 'quality', 'mode', 'intrisicMode', 
    'extrinsicMode', 'subkind','phase', 'role', 'historicalRole', 'relator', 'class'
}

# Estruturas de dados
symbol_table = []
token_count = {token: 0 for token in tokens}
processed_tokens = [] 
error_tokens = []
last_keyword = None  # Armazena a última palavra-chave processada

# Adiciona o token à tabela de símbolos e atualiza o contador
def add_to_symbol_table(token):
    if any(entry['Valor'] == token.value for entry in symbol_table):
        token_count[token.type] += 1
        processed_tokens.append(token)
        return  # Não adiciona duplicatas
    symbol_table.append({
        'Token': token.type,
        'Valor': token.value
    })
    token_count[token.type] += 1
    processed_tokens.append(token)

# Função para adicionar erros (captura o lexema inválido completo e retorna o tamanho consumido)
def add_to_error_list(token):
    data = token.lexer.lexdata
    start = token.lexer.lexpos
    i = start
    n = len(data)
    # Delimitadores conhecidos (não consumir para não perder tokens válidos seguintes)
    delimiters = set('{}()[]:@,.*-<>')
    while i < n and (not data[i].isspace()) and (data[i] not in delimiters):
        i += 1
    invalid_lexeme = data[start:i] if i > start else data[start:start+1]
    error_tokens.append({
        'Token': 'ERRO',
        'Valor': invalid_lexeme,
        'Linha': token.lineno,
        'Posição': token.lexpos
    })
    return max(1, i - start)

# Expressões regulares para os tokens

# Atributos de Classes e DataTypes
def t_ATTRIBUTE(t):
    r'\b[a-z][a-zA-Z]*:'
    t.value = t.value[:-1]  
    add_to_symbol_table(t)
    return t

# Novos tipos de dados
def t_NEW_DATATYPE(t):
    r'\b[A-Za-z]+DataType\b'
    add_to_symbol_table(t)
    return t

# Enumerações
def t_ENUM_NAME(t):
    r'\b[A-Za-z]+Enum\b'
    add_to_symbol_table(t)
    return t

# Cardinalidade [n], [n..m], [n..*], [*]
def t_CARDINALITY(t):
    r'\[\s*(\*|\d+)\s*(?:\.\.\s*(\*|\d+))?\s*\]'
    # remove espaços internos
    content = t.value[1:-1].strip()
    if '..' in content:
        a, b = [p.strip() for p in content.split('..', 1)]
        t.value = f'[{a}..{b}]'
    else:
        t.value = f'[{content}]'
    add_to_symbol_table(t)
    return t

# Símbolos especiais restantes
# Observação: o caractere ":" também é usado em atributos, mas lá é consumido por t_ATTRIBUTE.
# Aqui tratamos apenas ocorrências de ':' que não façam parte de um atributo.
def t_SPECIAL_SYMBOL(t):
    r'(\{|\}|\(|\)|<>--|--<>|--|--<o>|<o>--|@|:|,|\.)'
    add_to_symbol_table(t)
    return t

# Palavras reservadas
def t_KEYWORD(t):
    r'\b(specializes|genset|disjoint|complete|general|specifics|where|package|import|functional-complexes|relators|intrinsic-modes|extrinsic-modes|datatype|enum|type|instanceOf|categorizer|of|relation|inverseOf)\b'
    global last_keyword
    if t.value in keywords:
        t.type = 'KEYWORD'
        last_keyword = t.value  # Armazena a palavra-chave processada
    add_to_symbol_table(t)
    return t

# Tipos de dados nativos: number, string, boolean, date, time, datetime
def t_NATIVE_DATATYPE(t):
    r'\b(number|string|boolean|date|time|datetime)\b'
    add_to_symbol_table(t)
    return t

# Meta-atributos: ordered, const, derived, subsets, redefines
def t_META_ATTRIBUTE(t):
    r'\b(ordered|const|derived|subsets|redefines)\b'
    add_to_symbol_table(t)
    return t

# Estereótipos de Classe
def t_CLASS_STEREOTYPE(t):
    r'\b(event|situation|process|category|mixin|phaseMixin|roleMixin|historicalRoleMixin|kind|collective|quantity|quality|mode|intrisicMode|extrinsicMode|subkind|phase|role|historicalRole|relator|class)\b'
    if t.value in class_stereotypes:
        t.type = 'CLASS_STEREOTYPE'
    add_to_symbol_table(t)
    return t

# Estereótipos de relações
def t_RELATION_STEREOTYPE(t):
    r'\b(material|derivation|comparative|mediation|characterization|externalDependence|subCollectionOf|subQualityOf|componentOf|instantiation|memberOf|termination|participational|participation|historicalDependence|creation|manifestation|bringsAbout|triggers|composition|aggregation|inherence|value|formal|constitution)\b'
    add_to_symbol_table(t)
    return t

# Nomes de Instâncias
def t_INSTANCE_NAME(t):
    r'\b[A-Za-z][A-Za-z_]*\d+\b'
    add_to_symbol_table(t)
    return t

# Convenção para nomes de relações
def t_RELATION_NAME(t):
    r'\b[a-z][a-zA-Z]*(?:_[a-zA-Z]+)*\b'
    add_to_symbol_table(t)
    return t

# Convenção para nomes de Classes (também usado para Packages e GenSets)
def t_CLASS_NAME(t):
    r'\b[A-Z][a-zA-Z]*(?:_[a-zA-Z][a-zA-Z]*)*\b'
    add_to_symbol_table(t)
    return t

# Atualizar contagem de linhas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignorar espaços e tabulações
t_ignore = ' \t'

# Tratamento de erros
def t_error(t):
    consumed = add_to_error_list(t)
    t.lexer.skip(consumed)

# Construção do Lexer
lexer = lex.lex()

# Função para processar o arquivo
def process_file(file_path):
    global symbol_table, token_count, processed_tokens, error_tokens, last_keyword
    # Limpa completamente o contexto anterior
    symbol_table = []
    token_count = {token: 0 for token in tokens}
    processed_tokens = []
    error_tokens = []
    last_keyword = None  # Reseta a última palavra-chave

    try:
        with open(file_path, 'r') as file:
            data = file.read()
            # Reinicia contagem de linhas do lexer
            lexer.lineno = 1
            lexer.input(data)

            # Processa os tokens
            while lexer.token():
                pass  # Apenas preenche os dados na tabela e contador
    except FileNotFoundError:
        print(f"Arquivo {file_path} não encontrado.")
        return False
    except Exception as e:
        print(f"Erro ao processar o arquivo: {e}")
        return False
    return True

# Função para exibir os tokens processados
def show_tokens():
    print("\n====================== Tokens Processados =======================\n")
    header = f"{'Token':<20} {'Valor':<28} {'Linha':<6} {'Posição':<5}"
    print(header)
    print("-" * len(header))

    for token in processed_tokens:
        print(f"{token.type:<20} {str(token.value):<30} {token.lineno:<6} {token.lexpos:<6}")

    if error_tokens:
        header = f"{'Token':<20} {'Valor':<28} {'Linha':<6} {'Posição':<5}"

        print("\n=========================== Erros ===============================\n")
        print(header)
        print("-" * len(header))
        for error in error_tokens:
            print(f"{error['Token']:<20} {error['Valor']:<30} {error['Linha']:<6} {error['Posição']:<5}")

# Função para exibir a tabela de símbolos
def show_symbol_table():
    print("\n================= Tabela de Símbolos =================\n")
    print(f"{'Token':<20} {'Valor':<30}")
    print("-" * 55)
    for entry in symbol_table:
        print(f"{entry['Token']:<20} {entry['Valor']:<30}")

# Função para exibir a contagem de tokens
def show_token_count():
    print("\n======= Contagem de Tokens =======\n")
    print(f"{'Token':<20} {'Quantidade':<10}")
    print("-" * 35)
    for token, count in token_count.items():
        print(f"{token:<25} {count:<10}")