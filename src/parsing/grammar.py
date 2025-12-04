import ply.yacc as yacc

from ..lexical import lexer as lexer_module
from .summary import ModelBuilder 

class TontoParser:
    def __init__(self, model_builder):
        self.model_builder = model_builder
        self.syntax_errors = []
        self.tokens = lexer_module.tokens 
        
        # Constrói o parser
        self.parser = yacc.yacc(module=self, start="model", debug=False)
        
    def register_error(self, token, msg):
        if token:
            self.syntax_errors.append(f"Erro de sintaxe na linha {token.lineno}: {msg} (token: '{token.value}')")
        else:
            self.syntax_errors.append(msg)

    def p_error(self, p):
        if not p:
            self.register_error(None, "Erro de sintaxe próximo ao fim do arquivo.")
            return
        self.register_error(p, "Token inesperado")
        self.parser.errok() # não para a validação se achar erro 

    # ======  DEFINIÇÃO DA GRAMÁTICA =======
    # Símbolo inicial
    def p_model(self, p):
        """model : opt_imports package_decl declarations_opt"""
        p[0] = {"imports": p[1], "package": p[2], "declarations": p[3]}

    # Imports
    def p_opt_imports(self, p):
        """opt_imports :
                       | imports"""
        p[0] = p[1] if len(p) > 1 else []

    def p_imports(self, p):
        """imports : import_stmt
                   | imports import_stmt"""
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[2]]

    def p_import_stmt(self, p):
        """import_stmt : IMPORT CLASS_NAME"""
        self.model_builder.register_import(p[2])
        p[0] = ("import", p[2])

    # Package
    def p_package_decl(self, p):
        """package_decl : PACKAGE CLASS_NAME"""
        self.model_builder.register_package(p[2])
        p[0] = p[2]

    # Declarações
    def p_declarations_opt(self, p):
        """declarations_opt :
                            | declarations"""
        p[0] = p[1] if len(p) > 1 else []

    def p_declarations(self, p):
        """declarations : declaration
                        | declarations declaration"""
        if len(p) == 2:
            p[0] = [] if p[1] is None else [p[1]]
        else:
            if p[2] is None:
                p[0] = p[1]
            else:
                p[0] = p[1] + [p[2]]

    def p_declaration(self, p):
        """declaration : class_decl
                       | datatype_decl
                       | enum_decl
                       | genset_short
                       | genset_long
                       | external_relation_decl"""
        p[0] = p[1]

    # Classes
    def p_class_header(self, p):
        """class_header : CLASS_STEREOTYPE CLASS_NAME opt_specializes"""
        name = p[2]
        stereotype = p[1]
        superclasses = p[3]
        self.model_builder.register_class_header(name, stereotype, superclasses)
        p[0] = name

    def p_class_decl(self, p):
        """class_decl : class_header opt_class_body"""
        class_name = p[1]
        members = p[2]
        self.model_builder.register_class_members(class_name, members)
        p[0] = ("class", class_name)

    # Specializes (opcional)
    def p_opt_specializes(self, p):
        """opt_specializes :
                           | SPECIALIZES class_list"""
        p[0] = [] if len(p) == 1 else p[2]

    def p_class_list(self, p):
        """class_list : CLASS_NAME
                      | class_list COMMA CLASS_NAME"""
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

    def p_opt_class_body(self, p):
        """opt_class_body :
                          | LBRACE class_members RBRACE"""
        p[0] = [] if len(p) == 1 else p[2]

    def p_class_members(self, p):
        """class_members : 
                         | class_members class_member"""
        p[0] = [] if len(p) == 1 else p[1] + [p[2]]

    def p_class_member(self, p):
        """class_member : attribute_decl
                        | internal_relation_decl"""
        p[0] = p[1]

    # Atributos
    def p_attribute_decl(self, p):
        """attribute_decl : ATTRIBUTE type opt_cardinality opt_meta_attrs"""
        p[0] = ("attribute", {
            "name": p[1],
            "type": p[2],
            "cardinality": p[3],
            "flags": p[4]
        })

    def p_type(self, p):
        """type : NATIVE_DATATYPE
                | NEW_DATATYPE
                | CLASS_NAME"""
        p[0] = p[1]

    def p_opt_cardinality(self, p):
        """opt_cardinality :
                           | CARDINALITY"""
        p[0] = p[1] if len(p) > 1 else None

    def p_opt_meta_attrs(self, p):
        """opt_meta_attrs :
                          | LBRACE meta_attr_list RBRACE"""
        p[0] = [] if len(p) == 1 else p[2]

    def p_meta_attr_list(self, p):
        """meta_attr_list : META_ATTRIBUTE
                          | meta_attr_list COMMA META_ATTRIBUTE"""
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

    # Datatypes
    def p_datatype_decl(self, p):
        """datatype_decl : DATATYPE NEW_DATATYPE opt_dt_specializes opt_datatype_body"""
        self.model_builder.register_datatype(p[2], p[3], p[4])
        p[0] = ("datatype", p[2])

    def p_opt_dt_specializes(self, p):
        """opt_dt_specializes :
                              | SPECIALIZES dt_super_list"""
        p[0] = [] if len(p) == 1 else p[2]

    def p_dt_super_list(self, p):
        """dt_super_list : type
                         | dt_super_list COMMA type"""
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

    def p_opt_datatype_body(self, p):
        """opt_datatype_body :
                             | LBRACE opt_datatype_fields RBRACE"""
        p[0] = [] if len(p) == 1 else p[2]

    def p_opt_datatype_fields(self, p):
        """opt_datatype_fields :
                               | opt_datatype_fields attribute_decl"""
        p[0] = [] if len(p) == 1 else p[1] + [p[2]]

    # Enums
    def p_enum_decl(self, p):
        """enum_decl : ENUM CLASS_NAME LBRACE opt_enum_elements RBRACE"""
        self.model_builder.register_enum(p[2], p[4])
        p[0] = ("enum", p[2])

    def p_opt_enum_elements(self, p):
        """opt_enum_elements :
                             | enum_elements"""
        p[0] = [] if len(p) == 1 else p[1]

    def p_enum_elements(self, p):
        """enum_elements : enum_element
                         | enum_elements COMMA enum_element"""
        p[0] = [p[1]] if len(p) == 2 else p[1] + [p[3]]

    def p_enum_element(self, p):
        """enum_element : INSTANCE_NAME"""
        p[0] = p[1]

    # Gensets 
    def p_genset_short(self, p):
        """genset_short : opt_constraints GENSET CLASS_NAME WHERE class_list SPECIALIZES CLASS_NAME"""
        constraints = p[1]
        name = p[3]        
        specifics = p[5]  
        general = p[7]     
        categorizer = None 

        self.model_builder.register_genset(name, constraints, general, specifics, categorizer, data=None)
        p[0] = ("genset_inline", specifics, general)

    def p_genset_long(self, p):
        """genset_long : opt_constraints GENSET CLASS_NAME LBRACE genset_body RBRACE"""
        constraints = p[1] 
        name = p[3]        
        data = p[5]       

        self.model_builder.register_genset(name, constraints, None, None, None, data=data)
        p[0] = ("genset_long", data)

    def p_genset_body(self, p):
        """genset_body : genset_general opt_genset_categorizer genset_specifics"""
        p[0] = {
            "general": p[1],
            "categorizer": p[2],
            "specifics": p[3],
        }

    def p_genset_general(self, p):
        """genset_general : GENERAL CLASS_NAME"""
        p[0] = p[2]

    def p_opt_genset_categorizer(self, p):
        """opt_genset_categorizer :
                                  | CATEGORIZER CLASS_NAME"""
        p[0] = None if len(p) == 1 else p[2]

    def p_genset_specifics(self, p):
        """ genset_specifics : SPECIFICS class_list"""
        p[0] = p[2]

    def p_opt_constraints(self, p):
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
    def p_internal_relation_decl(self, p):
        """internal_relation_decl : opt_stereo opt_cardinality rel_connector opt_relname opt_cardinality CLASS_NAME"""
        stereo = p[1]
        card_from = p[2]
        connector = p[3]
        name = p[4]
        self.model_builder.register_internal_relation(stereo, card_from, connector, name, p[5], p[6])
        p[0] = ("internal_relation", name)

    def p_opt_stereo(self, p):
        """opt_stereo :
                      | AT RELATION_STEREOTYPE"""
        p[0] = None if len(p) == 1 else p[2]

    def p_rel_connector(self, p):
        """rel_connector : ASSOCIATION
                         | AGGREGATION
                         | COMPOSITION"""
        p[0] = p[1]

    def p_opt_relname(self, p):
        """opt_relname :
                       | RELATION_NAME ASSOCIATION"""
        p[0] = None if len(p) == 1 else p[1]

    def p_external_relation_decl(self, p):
        """
        external_relation_decl : opt_stereo RELATION CLASS_NAME opt_cardinality rel_connector opt_relname opt_cardinality CLASS_NAME"""
        stereo    = p[1]
        domain    = p[3]
        card_from = p[4]
        connector = p[5]
        name      = p[6]
        card_to   = p[7]
        range_    = p[8]

        self.model_builder.register_external_relation(stereo, domain, card_from, connector, name, card_to, range_)
        p[0] = ("external_relation", domain, range_)

# Função principal de parse que encapsula a lógica
def parse_text(data):
    model_builder_instance = ModelBuilder()
    parser_instance = TontoParser(model_builder_instance)

    lexer_module.collect_lex_info = False # desliga a coleta léxica durante o parse (para evitar duplicatas)
    lexer_module.lexer.lineno = 1
    lexer_module.lexer.input(data)
    ast = parser_instance.parser.parse(lexer=lexer_module.lexer)
    lexer_module.collect_lex_info = True # reativa, se precisar de outra análise léxica no futuro

    # Retorna a AST, o summary preenchido pelo builder e os erros sintáticos
    return ast, model_builder_instance.get_summary(), parser_instance.syntax_errors