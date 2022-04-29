"""
Classe che rappresenta l'Abox dell'ontologia.
"""


class AboxMember:

    def __init__(self, class_identifier, member_name):
        self.class_identifier = class_identifier
        self.member_name = member_name
