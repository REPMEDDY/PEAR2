"""
Classe che assieme alla classe TypicalFact costituisce la Tbox dell'ontologia
"""


class TypicalMember:
    counter = 0

    def __init__(self, t_class_identifier, member_name, probability=None, t_class_identifier_1=None, t_class_intersection=None, remove_from_knowledge_base=False):
        self.t_class_identifier = t_class_identifier
        self.t_class_identifier_1 = t_class_identifier_1
        self.t_class_intersection = t_class_intersection
        self.member_name = member_name
        self.probability = probability
        self.key = TypicalMember.counter
        self.remove_from_knowledge_base = remove_from_knowledge_base
        TypicalMember.counter += 1
