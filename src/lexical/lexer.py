import ply.lex as lex

tokens = [
    'CLASS_STEREOTYPE', 'RELATION_STEREOTYPE', 'KEYWORD', 'CLASS_NAME', 'RELATION_NAME',
    'INSTANCE_NAME', 'NATIVE_DATATYPE', 'NEW_DATATYPE','META_ATTRIBUTE','ATTRIBUTE', 
    'CARDINALITY', 'IMPORT', 'PACKAGE', 'SPECIALIZES', 'DATATYPE','ENUM', 'GENSET', 
    'DISJOINT', 'COMPLETE', 'GENERAL', 'SPECIFICS', 'WHERE', 'RELATION', 'AGGREGATION',
    'AGGREGATION_REV', 'COMPOSITION','COMPOSITION_REV', 'ASSOCIATION', 'LBRACE', 'RBRACE', 
    'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'AT', 'COLON','COMMA', 'DOTDOT', 'ASTERISK',
    'CATEGORIZER'
]

keywords = { 
    'functional-complexes', 'relators', 'intrinsic-modes', 'extrinsic-modes',
    'type', 'instanceOf', 'of', 'inverseOf'
} 

class_stereotypes = { 
    'event', 'situation', 'process', 'category', 'mixin','phaseMixin', 'roleMixin', 
    'historicalRoleMixin', 'kind', 'collective','quantity', 'quality', 'mode', 'intrisicMode', 
    'extrinsicMode', 'subkind','phase', 'role', 'historicalRole', 'relator', 'class'
}

relation_stereotypes = { 
    'material', 'derivation', 'comparative', 'mediation', 'characterization', 
    'externalDependence', 'subCollectionOf', 'subQualityOf', 'componentOf', 
    'instantiation', 'memberOf', 'termination', 'participational', 'participation', 
    'historicalDependence', 'creation', 'manifestation', 'bringsAbout', 'triggers', 
    'composition', 'aggregation', 'inherence', 'value', 'formal', 'constitution'
}

#  ====== Variáveis de Estado Léxico Globais ======
symbol_table = []
token_count = {token: 0 for token in tokens}
processed_tokens = [] 
error_tokens = []
# Flag para controlar se vai registrar tokens (modo léxico) ou não
collect_lex_info = True

# ====== Funções Auxiliares =======
def add_to_symbol_table(token):
    global collect_lex_info

    if not collect_lex_info:
        return # está no modo "sintático", não registrar nada

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

def add_to_error_list(token):
    data = token.lexer.lexdata
    start = token.lexer.lexpos
    i = start
    n = len(data)
    delimiters = set('{}()[]:@,.*-<>')

    while i < n and (not data[i].isspace()) and (data[i] not in delimiters):
        i += 1

    invalid_lexeme = data[start:i] if i > start else data[start:start+1]

    if collect_lex_info:
        error_tokens.append({
            'Token': 'ERRO',
            'Valor': invalid_lexeme,
            'Linha': token.lineno,
            'Posição': token.lexpos
        })

    return max(1, i - start)

# ===== EXPRESSÕES REGULARES  ===== 

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

# Cardinalidade [n], [n..m], [n..*], [*]
def t_CARDINALITY(t):
    r'\[\s*(\*|\d+)\s*(?:\.\.\s*(\*|\d+))?\s*\]'
    content = t.value[1:-1].strip()
    if '..' in content:
        a, b = [p.strip() for p in content.split('..', 1)]
        t.value = f'[{a}..{b}]'
    else:
        t.value = f'[{content}]'
    add_to_symbol_table(t)
    return t

def t_AGGREGATION(t):
    r'\<\>--'
    t.type = 'AGGREGATION'
    add_to_symbol_table(t)
    return t

def t_AGGREGATION_REV(t):
    r'--\<\>'
    t.type = 'AGGREGATION_REV'
    add_to_symbol_table(t)
    return t

def t_COMPOSITION(t):
    r'\<o\>--'
    t.type = 'COMPOSITION'
    add_to_symbol_table(t)
    return t

def t_COMPOSITION_REV(t):
    r'--\<o\>'
    t.type = 'COMPOSITION_REV'
    add_to_symbol_table(t)
    return t

def t_ASSOCIATION(t):
    r'--'
    t.type = 'ASSOCIATION'
    add_to_symbol_table(t)
    return t

# Símbolos Especiais
def t_LBRACKET(t):
    r'\['
    add_to_symbol_table(t)
    return t

def t_RBRACKET(t):
    r'\]'
    add_to_symbol_table(t)
    return t

def t_LBRACE(t):
    r'\{'
    add_to_symbol_table(t)
    return t

def t_RBRACE(t):
    r'\}'
    add_to_symbol_table(t)
    return t

def t_LPAREN(t):
    r'\('
    add_to_symbol_table(t)
    return t

def t_RPAREN(t):
    r'\)'
    add_to_symbol_table(t)
    return t

def t_AT(t):
    r'@'
    add_to_symbol_table(t)
    return t

def t_DOTDOT(t):
    r'\.\.'
    add_to_symbol_table(t)
    return t

def t_COMMA(t):
    r','
    add_to_symbol_table(t)
    return t

def t_COLON(t):
    r':'
    add_to_symbol_table(t)
    return t

def t_ASTERISK(t):
    r'\*'
    add_to_symbol_table(t)
    return t

# Palavras reservadas (tokens individuais)
def t_IMPORT(t): 
    r'\bimport\b'
    add_to_symbol_table(t)
    return t

def t_PACKAGE(t):
    r'\bpackage\b'
    add_to_symbol_table(t)
    return t

def t_SPECIALIZES(t): 
    r'\bspecializes\b'
    add_to_symbol_table(t)
    return t

def t_DATATYPE(t):
    r'\bdatatype\b'
    add_to_symbol_table(t)
    return t

def t_ENUM(t):
    r'\benum\b'
    add_to_symbol_table(t)
    return t

def t_GENSET(t):
    r'\bgenset\b'
    add_to_symbol_table(t)
    return t

def t_DISJOINT(t):
    r'\bdisjoint\b'
    add_to_symbol_table(t)
    return t

def t_COMPLETE(t):
    r'\bcomplete\b'
    add_to_symbol_table(t)
    return t

def t_GENERAL(t):
    r'\bgeneral\b'
    add_to_symbol_table(t)
    return t

def t_CATEGORIZER(t):
    r'\bcategorizer\b'
    add_to_symbol_table(t)
    return t

def t_SPECIFICS(t):
    r'\bspecifics\b'
    add_to_symbol_table(t)
    return t

def t_WHERE(t):
    r'\bwhere\b'
    add_to_symbol_table(t)
    return t

def t_RELATION(t):
    r'\brelation\b'
    add_to_symbol_table(t)
    return t

# Palavras reservadas 
def t_KEYWORD(t):
    r'\b(functional-complexes|relators|intrinsic-modes|extrinsic-modes|type|instanceOf|categorizer|of|inverseOf)\b'
    if t.value in keywords:
        t.type = 'KEYWORD'
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
    if t.value in relation_stereotypes:
        t.type = 'RELATION_STEREOTYPE'
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
    r'\r?\n+'
    t.lexer.lineno += t.value.count("\n")

# Ignorar espaços e tabulações
t_ignore = ' \t'

# Tratamento de erros
def t_error(t):
    consumed = add_to_error_list(t)
    t.lexer.skip(consumed)

# ====== Construção do Lexer ====== 
lexer = lex.lex()

# ====== Função para analisar o texto  ====== 
def analyze_text(data):
    global symbol_table, token_count, processed_tokens, error_tokens, collect_lex_info
    
    # Limpa completamente o contexto anterior
    symbol_table = []
    token_count = {token: 0 for token in tokens}
    processed_tokens = []
    error_tokens = []
    collect_lex_info = True
    
    lexer.lineno = 1
    lexer.input(data)
    while lexer.token():
        pass 
        
    # Retorna as listas de estado para o cli/main.py
    return processed_tokens, symbol_table, error_tokens