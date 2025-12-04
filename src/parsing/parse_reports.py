# ====== Funções auxiliares para formatação e impressão ======

# Função que formata a string de uma relação interna ou externa
def _format_relation(r, is_external=False):
    parts = []
    
    if r.get("stereotype"): 
        parts.append(f"@{r['stereotype']}")

    if is_external:
        parts.append(f"{r['domain']}")  # Domínio da relação 

    if r.get("card_from"): 
        parts.append(r["card_from"])
        
    parts.append(r["connector"])
    
    if r.get("name"):
        parts.append(r["name"])
        # Se nomeada, o segundo conector é obrigatoriamente "--"
        parts.append("--") 
    
    if r.get("card_to"): 
        parts.append(r["card_to"])
    
    if not is_external:
        parts.append(r["target"]) # Classe de destino
    else:
        parts.append(f"{r['range']}") # Imagem da relação 
        
    return " ".join(parts).strip()

# Função que formata a string de um atributo
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

# Retorna '└── ' para o último item ou '├── ' para outros
def _get_branch_prefix(index, total):
    return "└── " if index == total - 1 else "├── "

# Agrupa as relações internas para serem exibidas aninhadas em suas classes
def _group_internal_relations_by_class(internal_relations):
    grouped = {}
    for r in internal_relations:
        owner = r["owner"]
        if owner not in grouped:
            grouped[owner] = []
        grouped[owner].append(r)
    return grouped

# ====== Funções de Impressão de Construtos (Item Único) ======
def _print_imports(imports, parent_indent):
    if imports:
        for i, imp_name in enumerate(imports):
            prefix = parent_indent + _get_branch_prefix(i, len(imports))
            print(f"{prefix}{imp_name}")
    else:
        print(f"{parent_indent}└── (Nenhum pacote importado)")

# DATATYPE ou ENUM
def _print_simple_declaration(comp_data, comp_type, decl_indent, item_index, total_items):
    item_prefix = decl_indent + _get_branch_prefix(item_index, total_items)
    
    if comp_type == 'ENUM':
        enum_members = comp_data.get('elements', [])
        member_names = f" [Elementos: {', '.join(enum_members)}]" if enum_members else ""
        # Format: ENUM: Nome [Elementos: ...]
        print(f"{item_prefix}🔢 ENUM: {comp_data['name']}{member_names}")
    else: 
        # Specializes
        superclasses = comp_data.get('superclasses', [])
        specializes_str = f" [specializes: {', '.join(superclasses)}]" if superclasses else ""

        # Format: DATATYPE: Nome [specializes: Superclasse]
        print(f"{item_prefix}📊 DATATYPE: {comp_data['name']}{specializes_str}")        

        attributes = comp_data.get("attributes", [])

        if attributes:
            # Verifica se é o último item para definir a indentação dos filhos
            is_last_item = (item_index == total_items - 1)
            fields_indent = decl_indent + ("    " if is_last_item else "│   ")
            
            # Cabeçalho dos campos
            print(f"{fields_indent}└── 📌 ATRIBUTOS:")
            
            attr_indent = fields_indent + "    "
            for i, field in enumerate(attributes):
                attr_prefix = _get_branch_prefix(i, len(attributes))
                print(f"{attr_indent}{attr_prefix}{_format_attribute(field)}")

def _print_external_relation_declaration(r, decl_indent, item_index, total_items):
    item_prefix = decl_indent + _get_branch_prefix(item_index, total_items)
    relation_str = _format_relation(r, is_external=True)
    print(f"{item_prefix}🌐 RELAÇÃO EXTERNA: {relation_str}")

def _print_genset_declaration(g, decl_indent, item_index, total_items):
    is_last_item = item_index == total_items - 1
    item_prefix = decl_indent + _get_branch_prefix(item_index, total_items)
    genset_indent = decl_indent + ("    " if is_last_item else "│   ")

    constraints = g.get('constraints', [])
    general = g.get('general', '(Nenhum)')
    specifics = g.get('specifics', [])
    categorizer = g.get('categorizer')

    print(f"{item_prefix}➕ GENSET: {g['name']}")
    
    # Componentes para iteração (Restrições, General, Categorizer, Specifics)
    components = []

    # 1. Restrições
    constraints_str = ", ".join(constraints) if constraints else "<nenhuma>"
    components.append({'type': 'Restrições', 'content': [constraints_str]})

    # 2. Generalização
    components.append({'type': 'General', 'content': [general]})
    
    # 3. Categorizer (se existir)
    if categorizer:
        components.append({'type': 'Categorizer', 'content': [categorizer]})

    # 4. Especificações (Specifics)
    if specifics:
        components.append({'type': 'Specifics', 'content': specifics})

    for comp_index, comp in enumerate(components):
        is_last_comp = comp_index == len(components) - 1
        comp_prefix = genset_indent + _get_branch_prefix(comp_index, len(components))
        
        # Tipos simples (Restrições, General, Categorizer)
        if comp['type'] in ['Restrições', 'General', 'Categorizer']:
            print(f"{comp_prefix}{comp['type']}: {comp['content'][0]}")

        # Specifics (hierarquia aninhada)
        elif comp['type'] == 'Specifics':
            print(f"{comp_prefix}Specifics:")
            
            specifics_indent = genset_indent + ("    " if is_last_comp else "│   ")
            
            for spec_index, specific in enumerate(comp['content']):
                spec_prefix = specifics_indent + _get_branch_prefix(spec_index, len(comp['content']))
                print(f"{spec_prefix}{specific}")

def _print_class_declaration(c, rels_by_class, decl_indent, item_index, total_items):
    is_last_item = item_index == total_items - 1
    item_prefix = decl_indent + _get_branch_prefix(item_index, total_items)
    
    # 1. Imprime o Cabeçalho da Classe no formato:
    # CLASSE: Child [estereótipo: subkind | specializes: Person]
    stereotype_str = f"estereótipo: {c['stereotype']}"
    superclasses_list = c.get('superclasses', [])
    specializes_str = f" | specializes: {', '.join(superclasses_list)}" if superclasses_list else ""
    
    # Título principal
    print(f"{item_prefix}🧱 CLASSE: {c['name']} [{stereotype_str}{specializes_str}]")

    # Componentes internos (atributos e relações internas)
    members = []

    if c.get('attributes'):
        members.append({'type': 'ATRIBUTOS', 'content': c['attributes']})
    
    internal_relations = rels_by_class.get(c['name'], [])

    if internal_relations:
        members.append({'type': 'RELAÇÕES INTERNAS', 'content': internal_relations})

    if not members:
        return

    # 2. Imprime os Membros Hierarquicamente
    members_indent = decl_indent + ("    " if is_last_item else "│   ")

    for member_index, member in enumerate(members):
        is_last_member = member_index == len(members) - 1
        member_prefix = members_indent + _get_branch_prefix(member_index, len(members))
        
        # Imprime o Cabeçalho do Grupo de Membros (ex: Atributos:)
        member_type = member['type']
        header = f"{member_type}:"

        if member_type == 'ATRIBUTOS':
            header = f"📌 {header}"
        elif member_type == 'RELAÇÕES INTERNAS':
            header = f"🔗 {header}"
        
        print(f"{member_prefix}{header}")

        content_list = member['content']
        content_indent = members_indent + ("    " if is_last_member else "│   ")
        
        for content_index, content_data in enumerate(content_list):
            content_prefix = content_indent + _get_branch_prefix(content_index, len(content_list))
            
            # Formatação do conteúdo
            if member_type == 'ATRIBUTOS':
                content_str = _format_attribute(content_data)
                print(f"{content_prefix}{content_str}")
            elif member_type == 'RELAÇÕES INTERNAS':
                content_str = _format_relation(content_data, is_external=False)
                print(f"{content_prefix}{content_str}")

# ====== Lógica de Iteração Ordenada) ======
def _print_package_contents(declarations, parent_indent, rels_by_class):
    
    if not declarations:
        return
        
    for comp_index, comp in enumerate(declarations):
        comp_type = comp['type'] 
        comp_data = comp['data'] 
        total_comps = len(declarations)
        
        # Construtos de Classe (incluindo todos os estereótipos)
        if comp_type in ['kind', 'phase', 'role', 'subkind', 'relator', 'category', 'mixin', 'roleMixin', 'phaseMixin', 'historicalRole', 'historicalRoleMixin', 'collective', 'quantity', 'quality', 'mode', 'intrisicMode', 'extrinsicMode', 'event', 'situation', 'process', 'class']: 
             _print_class_declaration(comp_data, rels_by_class, parent_indent, comp_index, total_comps)
             
        # Tipos Simples (Ex: DATATYPE, ENUM)
        elif comp_type in ['DATATYPE', 'ENUM']:
             _print_simple_declaration(comp_data, comp_type, parent_indent, comp_index, total_comps)
             
        # GenSet
        elif comp_type == 'GENSET':
             _print_genset_declaration(comp_data, parent_indent, comp_index, total_comps)
             
        # Relação Externa
        elif comp_type == 'EXTERNAL_RELATION':
             _print_external_relation_declaration(comp_data, parent_indent, comp_index, total_comps)

# ====== Resumo Quantitativo ======
def _print_quantitative_summary(imports, package, classes, datatypes, enums, gensets, internal, external):
    rows = [
        ("Imports", len(imports)),
        ("Packages", 1 if package else 0),
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
def show_syntax_summary(summary):
    classes = summary.get('classes', [])
    datatypes = summary.get('datatypes', [])
    enums = summary.get('enums', [])
    gensets = summary.get('gensets', [])
    internal = summary.get('internal_relations', [])
    external = summary.get('external_relations', [])
    
    # Recupera a lista ordenada de declarações
    ordered_declarations = summary.get('ordered_declarations', [])
    
    imports = summary.get('imports', [])
    package_name = summary.get('package')

    print("\n=========================== RESUMO SINTÁTICO ===========================\n")
    print("🌳 ONTOLOGIA")
    
    #  Componentes de Nível Superior (ONTOLOGIA)
    major_components = [{'type': 'IMPORTS', 'content': imports}]
    
    if package_name:
        major_components.append({
            'type': 'PACOTE', 
            'content': package_name, 
            'declarations': ordered_declarations 
        })

    for major_index, major_comp in enumerate(major_components):
        is_last_major = major_index == len(major_components) - 1
        major_prefix = _get_branch_prefix(major_index, len(major_components))
        major_indent = "    " if is_last_major else "│   "

        comp_type = major_comp['type']
        comp_content = major_comp.get('content')
        
        if comp_type == 'IMPORTS':
            print(f"{major_prefix}📥 IMPORTS:")
            _print_imports(comp_content, major_indent)

        elif comp_type == 'PACOTE':
            print(f"{major_prefix}📦 PACOTE: {comp_content}")
            
            # Chama a função que imprime o conteúdo na ordem
            rels_by_class = _group_internal_relations_by_class(internal)
            _print_package_contents(major_comp['declarations'], major_indent, rels_by_class)
    
    _print_quantitative_summary(imports, package_name, classes, datatypes, enums, gensets, internal, external)
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