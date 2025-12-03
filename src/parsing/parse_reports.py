# ====== Funções auxiliares para formatação e impressão ======
def _format_relation(r, is_external=False):
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

def _format_attribute(attr):
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
    
def _get_branch_prefix(index, total):
    return "└── " if index == total - 1 else "├── "

def _print_imports(comp_content, major_indent):
    if comp_content:
        for i, imp in enumerate(comp_content):
            prefix = major_indent + _get_branch_prefix(i, len(comp_content))
            print(f"{prefix}{imp}")
    else:
        print(f"{major_indent}└── (Nenhum pacote importado)")

def _print_class_attributes(attributes, inner_prefix, inner_indent):
    print(f"{inner_prefix} 📌 ATRIBUTOS:")
    for attr_index, attr in enumerate(attributes):
        attr_prefix = inner_indent + _get_branch_prefix(attr_index, len(attributes))
        attr_str = _format_attribute(attr)
        print(f"{attr_prefix} {attr_str}")

def _print_class_relations(relations, inner_prefix, inner_indent):
    print(f"{inner_prefix} 🔗 RELAÇÕES INTERNAS:")
    for rel_index, r in enumerate(relations):
        rel_prefix = inner_indent + _get_branch_prefix(rel_index, len(relations))
        rel_str = _format_relation(r, is_external=False)
        print(f"{rel_prefix} {rel_str}")

def _print_class_components(class_components, decl_indent, is_last_item):
    for comp_inner_index, comp_inner in enumerate(class_components):
        is_last_inner = comp_inner_index == len(class_components) - 1
        inner_prefix = decl_indent + ("    " if is_last_item else "│   ") + _get_branch_prefix(comp_inner_index, len(class_components))
        inner_indent = decl_indent + ("    " if is_last_item else "│   ") + ("    " if is_last_inner else "│   ")

        if comp_inner['type'] == 'ATTRIBUTES':
            _print_class_attributes(comp_inner['content'], inner_prefix, inner_indent)
        elif comp_inner['type'] == 'RELATIONS':
            _print_class_relations(comp_inner['content'], inner_prefix, inner_indent)

def _print_classes(decl_content, decl_indent, rels_by_class):
    for item_index, c in enumerate(decl_content):
        is_last_item = item_index == len(decl_content) - 1
        item_prefix = decl_indent + _get_branch_prefix(item_index, len(decl_content))
        
        super_str = f" specializes {', '.join(c.get('superclasses', []))}" if c.get('superclasses') else ""
        print(f"{item_prefix} <{c['stereotype']}> {c['name']}{super_str}")
        
        class_components = []
        if c.get('attributes'):
            class_components.append({'type': 'ATTRIBUTES', 'content': c['attributes']})
        if c['name'] in rels_by_class:
            class_components.append({'type': 'RELATIONS', 'content': rels_by_class[c['name']]})
        
        _print_class_components(class_components, decl_indent, is_last_item)

def _print_datatype_attributes(attributes, datatype_indent):
    print(f"{datatype_indent}└── 📌 ATRIBUTOS:")
    for attr_index, attr in enumerate(attributes):
        attr_prefix = datatype_indent + "    " + _get_branch_prefix(attr_index, len(attributes))
        attr_str = _format_attribute(attr)
        print(f"{attr_prefix} {attr_str}")

def _print_datatypes(decl_content, decl_indent):
    for item_index, d in enumerate(decl_content):
        is_last_item = item_index == len(decl_content) - 1
        item_prefix = decl_indent + _get_branch_prefix(item_index, len(decl_content))
        
        super_str = f" specializes {', '.join(d.get('superclasses', []))}" if d.get('superclasses') else ""
        print(f"{item_prefix}{d['name']}{super_str}")

        if d.get('attributes'):
            datatype_indent = decl_indent + ("    " if is_last_item else "│   ")
            _print_datatype_attributes(d['attributes'], datatype_indent)

def _print_enums(decl_content, decl_indent):
    for item_index, e in enumerate(decl_content):
        item_prefix = decl_indent + _get_branch_prefix(item_index, len(decl_content))
        elements_str = ", ".join(e['elements'])
        print(f"{item_prefix}{e['name']}: {{{elements_str}}}")

def _print_gensets(decl_content, decl_indent):
    for item_index, g in enumerate(decl_content):
        is_last_item = item_index == len(decl_content) - 1
        item_prefix = decl_indent + _get_branch_prefix(item_index, len(decl_content))
        
        constraints_str = " ".join(g['constraints'])
        general = g.get('general')
        specifics_str = ", ".join(g['specifics'])
        
        print(f"{item_prefix} {constraints_str} {g['name']}")
        
        genset_indent = decl_indent + ("    " if is_last_item else "│   ")
        print(f"{genset_indent}├── GENERAL: {general}")
        print(f"{genset_indent}└── SPECIFICS: {specifics_str}")

def _print_external_relations(decl_content, decl_indent):
    for item_index, r in enumerate(decl_content):
        item_prefix = decl_indent + _get_branch_prefix(item_index, len(decl_content))
        rel_str = _format_relation(r, is_external=True)
        print(f"{item_prefix} {rel_str}")

def _print_package_declaration(decl_comp, decl_prefix, decl_indent, rels_by_class):
    decl_type = decl_comp['type']
    decl_content = decl_comp['content']

    if decl_type == 'CLASSES':
        print(f"{decl_prefix} 📖 {decl_type}:")
        _print_classes(decl_content, decl_indent, rels_by_class)
    elif decl_type == 'DATATYPES':
        print(f"{decl_prefix} 📊 {decl_type}:")
        _print_datatypes(decl_content, decl_indent)
    elif decl_type == 'ENUMS':
        print(f"{decl_prefix} 🔢 {decl_type}:")
        _print_enums(decl_content, decl_indent)
    elif decl_type == 'GENSETS':
        print(f"{decl_prefix} ➕ {decl_type}:")
        _print_gensets(decl_content, decl_indent)
    elif decl_type == 'RELAÇÕES EXTERNAS':
        print(f"{decl_prefix} 🌐 {decl_type}:")
        _print_external_relations(decl_content, decl_indent)

def _print_package_declarations(package_declarations, major_indent, rels_by_class):
    for decl_index, decl_comp in enumerate(package_declarations):
        is_last_decl = decl_index == len(package_declarations) - 1
        decl_prefix = major_indent + _get_branch_prefix(decl_index, len(package_declarations))
        decl_indent = major_indent + ("    " if is_last_decl else "│   ")
        _print_package_declaration(decl_comp, decl_prefix, decl_indent, rels_by_class)

def _print_quantitative_summary(classes, datatypes, enums, gensets, internal, external):
    rows = [
        ("Classes", len(classes)),
        ("Datatypes", len(datatypes)),
        ("Enums", len(enums)),
        ("GenSets", len(gensets)),
        ("Rel. internas", len(internal)),
        ("Rel. externas", len(external)),
    ]

    label_width = max(max(len(r[0]) for r in rows), len('Item'))
    count_width = max(max(len(str(r[1])) for r in rows), len('Qtd'))

    print("\n\n📊 RESUMO QUANTITATIVO")
    top = "┌" + "─" * (label_width + 2) + "┬" + "─" * (count_width + 2) + "┐"
    header = f"│ {'Construto'.ljust(label_width)} │ {'Qtd'.center(count_width)} │"
    sep = "├" + "─" * (label_width + 2) + "┼" + "─" * (count_width + 2) + "┤"

    print(top)
    print(header)
    print(sep)

    for label, count in rows:
        print(f"│ {label.ljust(label_width)} │ {str(count).rjust(count_width)} │")
    bottom = "└" + "─" * (label_width + 2) + "┴" + "─" * (count_width + 2) + "┘"
    print(bottom)

# ====== Exibir Resumo Sintático ====== 
def show_syntax_summary(summary_data):
    pkg = summary_data.get("package")
    imports = summary_data.get("imports", [])
    classes = summary_data.get("classes", [])
    datatypes = summary_data.get("datatypes", [])
    enums = summary_data.get("enums", [])
    gensets = summary_data.get("gensets", [])
    internal = summary_data.get("internal_relations", [])
    external = summary_data.get("external_relations", [])

    # Pré-processamento para relações internas 
    rels_by_class = {}
    for r in internal:
        rels_by_class.setdefault(r["owner"], []).append(r)
    
    print("\n=========================== RESUMO SINTÁTICO ===========================\n")
    print("🌳 ONTOLOGIA")

    major_components = [{'type': 'IMPORTS', 'content': imports}]
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
            _print_imports(comp_content, major_indent)
        elif comp_type == 'PACOTE':
            print(f"{major_prefix} 📦 PACOTE: {comp_content}")
            _print_package_declarations(package_declarations, major_indent, rels_by_class)
    
    _print_quantitative_summary(classes, datatypes, enums, gensets, internal, external)
    print("\n=================================== ## ===================================")

# ====== Exibir Erros Sintáticos ====== 
def show_syntax_errors(errors):
    print("\n====================== ERROS SINTÁTICOS =====================\n")
    if not errors:
        print("✅ Nenhum erro sintático encontrado.")
        print("\n=========================== ## ==============================")
        return
    for e in errors:
        print("❌", e)
    print("\n=========================== ## ==============================")