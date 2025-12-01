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
            "external_relations": []
        }
        self._current_class = None

    def get_summary(self):
        return self.summary
    
    def register_import(self, name):
        self.summary["imports"].append(name)

    def register_package(self, name):
        self.summary["package"] = name
        
    def register_class_header(self, name, stereotype, superclasses):
        self._current_class = name
        self.summary["classes"].append({
            "name": name,
            "stereotype": stereotype,
            "superclasses": superclasses,
            "attributes": []
        })

    def register_class_members(self, class_name, members):
        if self.summary["classes"] and self.summary["classes"][-1]["name"] == class_name:
            current_class_data = self.summary["classes"][-1]
            if members:
                attributes = [member_data for member_type, member_data in members if member_type == 'attribute']
                current_class_data["attributes"].extend(attributes)

    def register_datatype(self, name, superclasses, raw_attributes):
        attributes = [attr_data for attr_type, attr_data in raw_attributes if attr_type == 'attribute']
        self.summary["datatypes"].append({
            "name": name,
            "superclasses": superclasses,
            "attributes": attributes,
        })
        
    def register_enum(self, name, elements):
        self.summary["enums"].append({
            "name": name,
            "elements": elements
        })

    def register_genset(self, name, constraints, general=None, specifics=None, categorizer=None, data=None):
        if data: # Formato longo
            self.summary["gensets"].append({
                "name": name,
                "general": data["general"],
                "specifics": data["specifics"],
                "categorizer": data["categorizer"],
                "constraints": constraints,
            })
        else: # Formato inline
            self.summary["gensets"].append({
                "name": name,
                "specifics": specifics,
                "general": general,
                "categorizer": categorizer,
                "constraints": constraints,
            })
            
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
        self.summary["external_relations"].append({
            "stereotype": stereo,
            "domain": domain,
            "card_from": card_from,
            "connector": connector,
            "name": name,
            "card_to": card_to,
            "range": range_,
        })