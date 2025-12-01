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
        syntax_errors.append(msg)

def p_error(p):
    if not p:
        register_error(None, "Erro de sintaxe próximo ao fim do arquivo.")
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
def p_class_header(p):
    """class_header : CLASS_STEREOTYPE CLASS_NAME opt_specializes"""
    global _current_class

    name = p[2]
    stereotype = p[1]
    superclasses = p[3]

    # registra a classe no resumo
    summary["classes"].append({
        "name": name,
        "stereotype": stereotype,
        "superclasses": superclasses,
        "attributes": []
    })

    # define a classe "dona" para as relações internas que vierem no corpo
    _current_class = name
    # devolve só o nome, para o class_decl usar
    p[0] = name

def p_class_decl(p):
    """class_decl : class_header opt_class_body"""
    class_name = p[1]
    members = p[2]

    if summary["classes"]:
        current_class_data = summary["classes"][-1]
        if members:
            attributes = [member_data for member_type, member_data in members if member_type == 'attribute']
            current_class_data["attributes"].extend(attributes)

    p[0] = ("class", class_name)

# Specializes (opcional)
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
    raw_attributes = p[4] 
    attributes = [attr_data for attr_type, attr_data in raw_attributes if attr_type == 'attribute']
   
    summary["datatypes"].append({
        "name": p[2],
        "superclasses": p[3],
        "attributes": attributes,
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

    # Pré-processamento para relações internas 
    rels_by_class = {}
    for r in internal:
        rels_by_class.setdefault(r["owner"], []).append(r)
    
    # Função auxiliar para formatar a relação 
    def format_relation(r, is_external=False):
        parts = []
        if r.get("stereotype"): 
            parts.append(f"@{r['stereotype']}")
        
        if is_external:
             parts.append("relation")
             parts.append(r["domain"])

        if r.get("card_from"): 
            parts.append(r["card_from"])
        parts.append(r["connector"])
        
        if r.get("name"):
            parts.append(r["name"])
            if not is_external:
                parts.append("--")
        
        if r.get("card_to"): 
            parts.append(r["card_to"])
        
        if not is_external:
            parts.append(r["target"])
        else:
            parts.append(r["range"])
            
        return " ".join(parts).strip()

    # Função para formatar o atributo 
    def format_attribute(attr):
        attr_name = attr.get('name', '(sem nome)')
        attr_type = attr.get('type', '(sem tipo)')
        attr_card = attr.get('cardinality', '')
        attr_flags = ", ".join(attr.get('flags', []))
        
        attr_str = f"{attr_name}: {attr_type}"
        if attr_card:
            attr_str += f" {attr_card}"
        if attr_flags:
            attr_str += f" {{{attr_flags}}}"
        return attr_str
    def get_branch_prefix(index, total):
        return "└── " if index == total - 1 else "├── "

    print("\n===================== RESUMO SINTÁTICO (ÁRVORE HIERÁRQUICA) =====================\n")
    
    print("🌳 ONTOLOGIA")

    major_components = []
    major_components.append({'type': 'IMPORTS', 'content': imports})
    
    if pkg:
        major_components.append({'type': 'PACOTE', 'content': pkg})
        
    package_declarations = []

    if classes: 
        package_declarations.append({'type': 'CLASSES', 'content': classes})
    if datatypes: 
        package_declarations.append({'type': 'DATATYPES', 'content': datatypes})
    if enums: 
        package_declarations.append({'type': 'ENUMS', 'content': enums})
    if gensets: 
        package_declarations.append({'type': 'GENSETS', 'content': gensets})
    if external: 
        package_declarations.append({'type': 'RELAÇÕES EXTERNAS', 'content': external})

    for major_index, major_comp in enumerate(major_components):
        is_last_major = major_index == len(major_components) - 1
        major_prefix = "└── " if is_last_major else "├── "
        major_indent = "    " if is_last_major else "│   "

        comp_type = major_comp['type']
        comp_content = major_comp['content']
        
        if comp_type == 'IMPORTS':
            print(f"{major_prefix} 📥 {comp_type}:")
            if comp_content:
                for i, imp in enumerate(comp_content):
                    prefix = major_indent + get_branch_prefix(i, len(comp_content))
                    print(f"{prefix}{imp}")
            else:
                print(f"{major_indent}└── (Nenhum pacote importado)")

        elif comp_type == 'PACOTE':
            print(f"{major_prefix} 📦 PACOTE: {comp_content}")

            for decl_index, decl_comp in enumerate(package_declarations):
                is_last_decl = decl_index == len(package_declarations) - 1
                decl_prefix = major_indent + get_branch_prefix(decl_index, len(package_declarations))
                decl_indent = major_indent + ("    " if is_last_decl else "│   ")
                
                decl_type = decl_comp['type']
                decl_content = decl_comp['content']

                if decl_type == 'CLASSES':
                    print(f"{decl_prefix} 📖 {decl_type}:")
                    for item_index, c in enumerate(decl_content):
                        is_last_item = item_index == len(decl_content) - 1
                        item_prefix = decl_indent + get_branch_prefix(item_index, len(decl_content))
                        
                        super_str = f" specializes {', '.join(c.get('superclasses', []))}" if c.get('superclasses') else ""
                        print(f"{item_prefix} <{c['stereotype']}> {c['name']}{super_str}")
                        
                        class_components = []
                        if c.get('attributes'):
                            class_components.append({'type': 'ATTRIBUTES', 'content': c['attributes']})
                        if c['name'] in rels_by_class:
                            class_components.append({'type': 'RELATIONS', 'content': rels_by_class[c['name']]})
                            
                        for comp_inner_index, comp_inner in enumerate(class_components):
                            is_last_inner = comp_inner_index == len(class_components) - 1
                            inner_prefix = decl_indent + ("    " if is_last_item else "│   ") + get_branch_prefix(comp_inner_index, len(class_components))
                            inner_indent = decl_indent + ("    " if is_last_item else "│   ") + ("    " if is_last_inner else "│   ")

                            # ATRIBUTOS (Sub-nível da Classe) 
                            if comp_inner['type'] == 'ATTRIBUTES':
                                attributes = comp_inner['content']
                                print(f"{inner_prefix} 📌 ATRIBUTOS:")
                                
                                for attr_index, attr in enumerate(attributes):
                                    is_last_attr = attr_index == len(attributes) - 1
                                    attr_prefix = inner_indent + get_branch_prefix(attr_index, len(attributes))
                                    
                                    attr_str = format_attribute(attr)
                                    print(f"{attr_prefix} {attr_str}")
                                    
                            # RELAÇÕES INTERNAS (Sub-nível da Classe) 
                            elif comp_inner['type'] == 'RELATIONS':
                                relations = comp_inner['content']
                                print(f"{inner_prefix} 🔗 RELAÇÕES INTERNAS:")
                                
                                for rel_index, r in enumerate(relations):
                                    is_last_rel = rel_index == len(relations) - 1
                                    rel_prefix = inner_indent + get_branch_prefix(rel_index, len(relations))
                                    rel_str = format_relation(r, is_external=False)
                                    print(f"{rel_prefix} {rel_str}")

                elif decl_type == 'DATATYPES':
                    print(f"{decl_prefix} 📊 {decl_type}:")
                    for item_index, d in enumerate(decl_content):
                        is_last_item = item_index == len(decl_content) - 1
                        item_prefix = decl_indent + get_branch_prefix(item_index, len(decl_content))
                        
                        super_str = f" specializes {', '.join(d.get('superclasses', []))}" if d.get('superclasses') else ""
                        print(f"{item_prefix}{d['name']}{super_str}")

                        # Atributos do Datatype (Sub-nível)
                        if d.get('attributes'):
                            attributes = d['attributes']
                            datatype_indent = decl_indent + ("    " if is_last_item else "│   ")
                            
                            print(f"{datatype_indent}└── 📌 ATRIBUTOS:")

                            for attr_index, attr in enumerate(attributes):
                                is_last_attr = attr_index == len(attributes) - 1
                                attr_prefix = datatype_indent + "    " + get_branch_prefix(attr_index, len(attributes))
                                
                                attr_str = format_attribute(attr)
                                print(f"{attr_prefix} {attr_str}")

                elif decl_type == 'ENUMS':
                    print(f"{decl_prefix} 🔢 {decl_type}:")
                    for item_index, e in enumerate(decl_content):
                        item_prefix = decl_indent + get_branch_prefix(item_index, len(decl_content))
                        elements_str = ", ".join(e['elements'])
                        print(f"{item_prefix}{e['name']}: {{{elements_str}}}")

                elif decl_type == 'GENSETS':
                    print(f"{decl_prefix} ➕ {decl_type}:")
                    for item_index, g in enumerate(decl_content):
                        is_last_item = item_index == len(decl_content) - 1
                        item_prefix = decl_indent + get_branch_prefix(item_index, len(decl_content))
                        
                        constraints_str = " ".join(g['constraints'])
                        general = g.get('general')
                        specifics_str = ", ".join(g['specifics'])
                        
                        print(f"{item_prefix} {constraints_str} {g['name']}")
                        
                        genset_indent = decl_indent + ("    " if is_last_item else "│   ")
                        
                        print(f"{genset_indent}├── GENERAL: {general}")
                        print(f"{genset_indent}└── SPECIFICS: {specifics_str}")

                elif decl_type == 'RELAÇÕES EXTERNAS':
                    print(f"{decl_prefix} 🌐 {decl_type}:")
                    for item_index, r in enumerate(decl_content):
                        item_prefix = decl_indent + get_branch_prefix(item_index, len(decl_content))
                        rel_str = format_relation(r, is_external=True)
                        print(f"{item_prefix} {rel_str}")
    
    print("\n\nRESUMO QUANTITATIVO:")
    print(f"- Classes..........: {len(classes)}")
    print(f"- Datatypes........: {len(datatypes)}")
    print(f"- Enums............: {len(enums)}")
    print(f"- GenSets..........: {len(gensets)}")
    print(f"- Rel. internas....: {len(internal)}")
    print(f"- Rel. externas....: {len(external)}")
    print("\n=================================================================================")

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
    print("\n========================================================")

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