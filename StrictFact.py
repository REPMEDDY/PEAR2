class StrictFact:

    def __init__(self, sub_class_identifier, super_class_identifier):
        self.sub_class_identifier = sub_class_identifier
        self.super_class_identifier = super_class_identifier
        self.strict_fact_name = sub_class_identifier.name + " is_a " + super_class_identifier.name

