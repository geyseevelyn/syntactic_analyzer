# ====== Classe para Construção do Resumo Sintático =======
class ModelBuilder:
    def __init__(self):
        self.summary = {
            "package": None,
            "imports": [],
            "classes": [],
            "datatypes": [],
            "enums": [],
            "gensets": [],
            "internal_relations": [],
            "external_relations": [],
            "ordered_declarations": []
        }
        self._current_class = None

    def get_summary(self):
        return self.summary
    
    def _register_ordered(self, type, data):
        """Registra uma declaração de pacote na ordem em que é encontrada."""
        self.summary["ordered_declarations"].append({
            "type": type,
            "data": data
        })
    
    def register_import(self, name):
        self.summary["imports"].append(name)

    def register_package(self, name):
        self.summary["package"] = name
        
    def register_class_header(self, name, stereotype, superclasses):
        class_data = {
            "name": name,
            "stereotype": stereotype,
            "superclasses": superclasses,
            "attributes": []
        }
        self.summary["classes"].append(class_data)
        self._current_class = name
        self._register_ordered(stereotype, class_data)

    def register_class_members(self, class_name, members):
        if self.summary["classes"] and self.summary["classes"][-1]["name"] == class_name:
            current_class_data = self.summary["classes"][-1]
            if members:
                attributes = [m[1] for m in members if m[0] == 'attribute']
                current_class_data["attributes"].extend(attributes)

    def register_attribute(self, name, type, cardinality, flags):
        # Esta função é chamada *antes* de register_class_members (para coleta temporária)
        pass

    def register_datatype(self, name, superclasses, raw_attributes):
        attributes = [f[1] for f in raw_attributes if f and isinstance(f, tuple) and f[0] == 'attribute']
        
        datatype_data = {
            "name": name, 
            "superclasses": superclasses if superclasses else [],
            "attributes": attributes
        }
        self.summary["datatypes"].append(datatype_data)
        self.summary["ordered_declarations"].append({
            "type": "DATATYPE",
            "data": datatype_data
        })
        
    def register_enum(self, name, elements):
        enum_data = {
            "name": name,
            "elements": elements
        }
        self.summary["enums"].append(enum_data)
        self._register_ordered("ENUM", enum_data)

    def register_genset(self, name, constraints, general, specifics, categorizer, data=None):
        if data: # Formato longo
            genset_data = {
                "name": name,
                "general": data["general"],
                "specifics": data["specifics"],
                "categorizer": data["categorizer"],
                "constraints": constraints,
            }
        else: # Formato inline
            genset_data = {
                "name": name,
                "specifics": specifics,
                "general": general,
                "categorizer": categorizer,
                "constraints": constraints,
            }
        self.summary["gensets"].append(genset_data)
        self._register_ordered("GENSET", genset_data)
            
    def register_internal_relation(self, stereo, card_from, connector, name, card_to, target):
        self.summary["internal_relations"].append({
            "owner": self._current_class,
            "stereotype": stereo,
            "card_from": card_from,
            "connector": connector,
            "name": name,
            "card_to": card_to,
            "target": target,
        })
        
    def register_external_relation(self, stereo, domain, card_from, connector, name, card_to, range_):
        relation_data = {
            "stereotype": stereo,
            "domain": domain,
            "card_from": card_from,
            "connector": connector,
            "name": name,
            "card_to": card_to,
            "range": range_
        }
        self.summary["external_relations"].append(relation_data)
        self._register_ordered("EXTERNAL_RELATION", relation_data)