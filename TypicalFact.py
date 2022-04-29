"""
Classe che assieme alla classe TypicalMember costituisce la Tbox dell'ontologia
"""


class TypicalFact:

    def __init__(self, t_class_identifier, class_identifier, probability, already_examined=False, typical_fact_is_a_query=False):
        self.t_class_identifier = t_class_identifier
        self.class_identifier = class_identifier
        self.probability = probability
        self.already_examined = already_examined
        self.typical_fact_is_a_query = typical_fact_is_a_query
        if not self.typical_fact_is_a_query:
            self.typical_fact_name = "T" + t_class_identifier.name + "_" + class_identifier.name
        else:
            self.typical_fact_name = "?T" + t_class_identifier.name + "_" + class_identifier.name

