import ply.yacc as yacc
import lexer 

tokens = lexer.tokens
base_lexer = lexer.lexer

syntax_errors = []

summary = {
    "package": None,
    "imports": [],
    "classes": [],
    "datatypes": [],
    "enums": [],
    "gensets": [],
    "internal_relations": [],
    "external_relations": []
}

_current_class = None  # classe "dona" da relação interna atual

def register_error(token, msg):
    if token:
        syntax_errors.append(f"Erro de sintaxe na linha {token.lineno}: {msg} (token: '{token.value}')")
    else:
        syntax_errors.append("Erro de sintaxe próximo ao fim do arquivo.")

def p_error(p):
    if not p:
        register_error(None, "Erro próximo ao fim do arquivo")
        return
    register_error(p, "Token inesperado")
    parser.errok() # não para a validação se achar erro 

# ======  DEFINIÇÃO DA GRAMÁTICA =======

# Símbolo inicial
def p_model(p):
    """model : opt_imports package_decl declarations_opt"""
    p[0] = {"imports": p[1], "package": p[2], "declarations": p[3]}

# Imports
def p_opt_imports(p):
    """opt_imports :
                   | imports"""
    p[0] = p[1] if len(p) > 1 else []

def p_imports(p):
    """imports : import_stmt
               | imports import_stmt"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

def p_import_stmt(p):
    """import_stmt : IMPORT CLASS_NAME"""
    summary["imports"].append(p[2])
    p[0] = ("import", p[2])

# Package
def p_package_decl(p):
    """package_decl : PACKAGE CLASS_NAME"""
    summary["package"] = p[2]
    p[0] = p[2]

# Declarações
def p_declarations_opt(p):
    """declarations_opt :
                        | declarations"""
    p[0] = p[1] if len(p) > 1 else []

def p_declarations(p):
    """declarations : declaration
                    | declarations declaration"""
    if len(p) == 2:
        p[0] = [] if p[1] is None else [p[1]]
    else:
        if p[2] is None:
            p[0] = p[1]
        else:
            p[0] = p[1] + [p[2]]

def p_declaration(p):
    """declaration : class_decl
                   | datatype_decl
                   | enum_decl
                   | genset_short
                   | genset_long
                   | external_relation_decl"""
    p[0] = p[1]

# Classes
def p_class_decl(p):
    """class_decl : CLASS_STEREOTYPE CLASS_NAME class_tail"""
    global _current_class
    name = p[2]
    stereotype = p[1]

    summary["classes"].append({
        "name": name,
        "stereotype": stereotype,
        "superclasses": p[3]["superclasses"]
    })

    _current_class = name  # dono das relações internas
    p[0] = ("class", name)

def p_class_tail(p):
    """class_tail : opt_specializes opt_class_body"""
    p[0] = {"superclasses": p[1], "body": p[2]}

# Speializes (opcional)
def p_opt_specializes(p):
    """opt_specializes :
                       | SPECIALIZES class_list"""
    p[0] = [] if len(p) == 1 else p[2]

def p_class_list(p):
    """class_list : CLASS_NAME
                  | class_list COMMA CLASS_NAME"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

def p_opt_class_body(p):
    """opt_class_body :
                      | LBRACE class_members RBRACE"""
    p[0] = [] if len(p) == 1 else p[2]

def p_class_members(p):
    """class_members : 
                     | class_members class_member"""
    p[0] = [] if len(p) == 1 else p[1] + [p[2]]

def p_class_member(p):
    """class_member : attribute_decl
                    | internal_relation_decl"""
    p[0] = p[1]

# Atributos
def p_attribute_decl(p):
    """attribute_decl : ATTRIBUTE type opt_cardinality opt_meta_attrs"""
    p[0] = ("attribute", {
        "name": p[1],
        "type": p[2],
        "cardinality": p[3],
        "flags": p[4]
    })

def p_type(p):
    """type : NATIVE_DATATYPE
            | NEW_DATATYPE
            | CLASS_NAME"""
    p[0] = p[1]

def p_opt_cardinality(p):
    """opt_cardinality :
                       | CARDINALITY"""
    p[0] = p[1] if len(p) > 1 else None

def p_opt_meta_attrs(p):
    """opt_meta_attrs :
                      | LBRACE meta_attr_list RBRACE"""
    p[0] = [] if len(p) == 1 else p[2]

def p_meta_attr_list(p):
    """meta_attr_list : META_ATTRIBUTE
                      | meta_attr_list COMMA META_ATTRIBUTE"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

# Datatypes
def p_datatype_decl(p):
    """datatype_decl : DATATYPE NEW_DATATYPE opt_dt_specializes opt_datatype_body"""
    summary["datatypes"].append({
        "name": p[2],
        "superclasses": p[3],
        "attributes": p[4],
    })
    p[0] = ("datatype", p[2])

def p_opt_dt_specializes(p):
    """opt_dt_specializes :
                          | SPECIALIZES dt_super_list"""
    p[0] = [] if len(p) == 1 else p[2]

def p_dt_super_list(p):
    """dt_super_list : type
                     | dt_super_list COMMA type"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

def p_opt_datatype_body(p):
    """opt_datatype_body :
                         | LBRACE opt_datatype_fields RBRACE"""
    p[0] = [] if len(p) == 1 else p[2]

def p_opt_datatype_fields(p):
    """opt_datatype_fields :
                           | opt_datatype_fields attribute_decl"""
    p[0] = [] if len(p) == 1 else p[1] + [p[2]]

# Enums
def p_enum_decl(p):
    """enum_decl : ENUM CLASS_NAME LBRACE opt_enum_elements RBRACE"""
    summary["enums"].append({
        "name": p[2],
        "elements": p[4]
    })
    p[0] = ("enum", p[2])

def p_opt_enum_elements(p):
    """opt_enum_elements :
                         | enum_elements"""
    p[0] = [] if len(p) == 1 else p[1]

def p_enum_elements(p):
    """enum_elements : enum_element
                     | enum_elements COMMA enum_element"""
    p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

def p_enum_element(p):
    """enum_element : INSTANCE_NAME"""
    p[0] = p[1]

# Gensets 

def p_genset_short(p):
    """genset_short : opt_constraints GENSET CLASS_NAME WHERE class_list SPECIALIZES CLASS_NAME"""
    summary["gensets"].append({
        "name": p[3],
        "specifics": p[5],
        "general": p[7],
        "categorizer": None,
        "constraints": p[1],
    })
    p[0] = ("genset_short", p[3])

def p_genset_long(p):
    """genset_long : opt_constraints GENSET CLASS_NAME LBRACE genset_body RBRACE"""
    data = p[5]

    summary["gensets"].append({
        "name": p[3],
        "general": data["general"],
        "specifics": data["specifics"],
        "categorizer": data["categorizer"],
        "constraints": p[1],
    })
    p[0] = ("genset_long", p[3])

def p_genset_body(p):
    """genset_body : genset_general opt_genset_categorizer genset_specifics"""
    p[0] = {
        "general": p[1],
        "categorizer": p[2],
        "specifics": p[3],
    }

def p_genset_general(p):
    """genset_general : GENERAL CLASS_NAME"""
    p[0] = p[2]

def p_opt_genset_categorizer(p):
    """opt_genset_categorizer :
                              | CATEGORIZER CLASS_NAME"""
    p[0] = None if len(p) == 1 else p[2]

def p_genset_specifics(p):
    """ genset_specifics : SPECIFICS class_list"""
    p[0] = p[2]

def p_opt_constraints(p):
    """opt_constraints :
                       | DISJOINT
                       | COMPLETE
                       | DISJOINT COMPLETE
                       | COMPLETE DISJOINT"""
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1], p[2]]

# Relação Interna 
def p_internal_relation_decl(p):
    """internal_relation_decl : opt_stereo opt_left_card rel_connector opt_relname CARDINALITY CLASS_NAME"""
    stereo = p[1]
    card_from = p[2]
    connector = p[3]
    # opt_relname retorna (name ou None)
    name = p[4]

    summary["internal_relations"].append({
        "owner": _current_class,
        "stereotype": stereo,
        "card_from": card_from,
        "connector": connector,
        "name": name,
        "card_to": p[5],
        "target": p[6],
    })

    p[0] = ("internal_relation", name)

def p_opt_stereo(p):
    """opt_stereo :
                  | AT RELATION_STEREOTYPE"""
    p[0] = None if len(p) == 1 else p[2]

def p_opt_left_card(p):
    """opt_left_card :
                     | CARDINALITY"""
    p[0] = p[1] if len(p) > 1 else None

def p_rel_connector(p):
    """rel_connector : ASSOCIATION
                     | AGGREGATION
                     | COMPOSITION"""
    p[0] = p[1]

def p_opt_relname(p):
    """opt_relname :
                   | RELATION_NAME ASSOCIATION"""
    p[0] = None if len(p) == 1 else p[1]

def p_external_relation_decl(p):
    """
    external_relation_decl : opt_stereo RELATION CLASS_NAME opt_left_card rel_connector opt_relname CARDINALITY CLASS_NAME"""
    stereo    = p[1]
    domain    = p[3]
    card_from = p[4]
    connector = p[5]
    name      = p[6]
    card_to   = p[7]
    range_    = p[8]

    summary["external_relations"].append({
        "stereotype": stereo,
        "domain": domain,
        "card_from": card_from,
        "connector": connector,
        "name": name,
        "card_to": card_to,
        "range": range_,
    })

    p[0] = ("external_relation", domain, range_)

# ====== Resumo Sintático ====== 
def show_syntax_summary(summary_data=None):
    if summary_data is None:
        summary_data = summary

    pkg = summary_data["package"]
    imports = summary_data["imports"]
    classes = summary_data["classes"]
    datatypes = summary_data["datatypes"]
    enums = summary_data["enums"]
    gensets = summary_data["gensets"]
    internal = summary_data["internal_relations"]
    external = summary_data["external_relations"]

    print("\n===================== RESUMO SINTÁTICO =====================\n")
    
    print(" QUANTIDADE DE CONSTRUTOS DECLARADOS:")
    print(f"  - Classes..........: {len(classes)}")
    print(f"  - Datatypes........: {len(datatypes)}")
    print(f"  - Enums............: {len(enums)}")
    print(f"  - GenSets..........: {len(gensets)}")
    print(f"  - Rel. internas....: {len(internal)}")
    print(f"  - Rel. externas....: {len(external)}")
    print()

    print("PACOTES IMPORTADOS:")
    if imports:
        for imp in imports:
            print(f"  - {imp}")
        print()
    else:
        print("  (nenhum pacote importado)\n")
    
    print("PACOTE PRINCIPAL:")
    print(f"  - {pkg if pkg else '(nenhum)'}\n")

    print("CLASSES POR PACOTE:")
    if not classes:
        print("  (nenhuma classe declarada)\n")
    else:
        for c in classes:
            print(f"  - {c['name']}")
        print()

    print("RELAÇÕES INTERNAS POR CLASSE:")
    if not internal:
        print("  (nenhuma relação interna declarada)\n")
    else:
        rels_by_class = {}
        for r in internal:
            rels_by_class.setdefault(r["owner"], []).append(r)

        for owner, rels in rels_by_class.items():
            print(f"  {owner}:")
            for r in rels:
                p = []
                if r["stereotype"]: p.append(f"@{r['stereotype']}")
                if r["card_from"]:  p.append(r["card_from"])
                p.append(r["connector"])
                if r["name"]:
                    p.append(r["name"])
                    p.append("--")
                p.append(r["card_to"])
                p.append(r["target"])
                print("     " + " ".join(p))
        print()
    
    print("RELAÇÕES EXTERNAS:")
    if not external:
        print("  (nenhuma relação externa declarada)\n")
    else:
        for r in external:
            p = []
            if r["stereotype"]: p.append(f"@{r['stereotype']}")
            p.append("relation")
            p.append(r["domain"])
            if r["card_from"]: p.append(r["card_from"])
            p.append(r["connector"])
            if r["name"]:
                p.append(r["name"])
                p.append("--")
            p.append(r["card_to"])
            p.append(r["range"])
            print("   " + " ".join(p))
        print()

    print("DATATYPES:")
    if datatypes:
        for d in datatypes:
            print(f"  - {d['name']}")
    else:
        print("  (nenhum DATATYPE declarado)")
    print()

    print("ENUMS:")
    if enums:
        for e in enums:
            print(f"  - {e['name']}")
    else:
        print("  (nenhuma ENUM declarada)")
    print()

    print("GENSETS:")
    if gensets:
        for g in gensets:
            print(f"  - {g['name']}")
    else:
        print("  (nenhum GENSET declarado)") 
    print()

# ====== Erros Sintáticos ====== 
def show_syntax_errors(errors=None):
    if errors is None:
        errors = syntax_errors

    print("\n===================== ERROS SINTÁTICOS =====================\n")
    if not errors:
        print("Nenhum erro sintático encontrado.")
        return
    for e in errors:
        print(" -", e)

# ====== Construção do Parser ====== 
parser = yacc.yacc(start="model")

def parse_file(file_path):
    global summary, syntax_errors, _current_class

    summary = {
        "package": None,
        "imports": [],
        "classes": [],
        "datatypes": [],
        "enums": [],
        "gensets": [],
        "internal_relations": [],
        "external_relations": []
    }

    syntax_errors = []
    _current_class = None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read()
    except FileNotFoundError:
        return None, summary, ["Arquivo não encontrado."]

    # desliga a coleta léxica durante o parse
    lexer.collect_lex_info = False

    base_lexer.lineno = 1
    base_lexer.input(data)
    ast = parser.parse(lexer=base_lexer)

    # reativa, se precisar de outra análise léxica no futuro
    lexer.collect_lex_info = True

    return ast, summary, syntax_errors