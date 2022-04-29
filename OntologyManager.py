from owlready2 import *
import types

from functools import singledispatchmethod
from TypicalMember import *
from TypicalFact import *
from StrictFact import *
from AboxMember import *

"""
Classe che rappresenta l'ontologia, fornisce vari metodi per gestirla.
"""


class OntologyManager:
    def __init__(self, iri="https://www.example.org/onto.owl"):
        self.query_typical_fact = None
        self.typical_facts_dict = dict()
        self.typical_facts_support_dict = dict()
        self.typical_members_dict = dict()
        self.typical_facts_list = list()
        self.strict_facts_list = list()
        self.a_box_members_list = list()
        self.typical_members_list = list()
        self.scenarios_list = list()
        self.my_world = World()
        if iri != "https://www.example.org/onto.owl":
            self.onto = self.my_world.get_ontology(iri)
        else:
            self.onto = self.my_world.get_ontology("https://www.example.org/onto.owl")

    def create_complementary_class(self, class_identifier):
        with self.onto:
            complementary_class = Not(class_identifier)
        return complementary_class

    def get_complementary_class(self, class_identifier_name):
        with self.onto:
            # Es: Not(Fly)
            if "Not(" in class_identifier_name:
                return self.get_class(class_identifier_name.replace("Not(", "").replace(")", ""))
            # Es: Fly
            else:
                return self.get_class("Not(" + class_identifier_name + ")")

    def create_class(self, class_identifier_name):
        with self.onto:
            new_class = types.new_class(class_identifier_name, (Thing,))
        return new_class

    def create_not_t_class_or_class(self, t_class_identifier, class_identifier):
        with self.onto:
            not_t_class_or_class_identifier = self.create_class("Not(" + t_class_identifier.name + "):Or:" + class_identifier.name)
            if self.get_class("Not(" + t_class_identifier.name + ")") is not None:
                not_t_class_identifier = self.get_class("Not(" + t_class_identifier.name + ")")
                not_t_class_or_class_identifier.equivalent_to = [not_t_class_identifier | class_identifier]
            else:
                not_t_class_identifier = self.create_class("Not(" + t_class_identifier.name + ")")
                not_t_class_identifier.equivalent_to = [self.create_complementary_class(t_class_identifier)]
                not_t_class_or_class_identifier.equivalent_to = [not_t_class_identifier | class_identifier]

    def create_t_class_intersection(self, t_class_identifier, t_class_identifier_1):
        with self.onto:
            t_class_intersection = self.create_class("Intersection(" + t_class_identifier.name + t_class_identifier_1.name + ")")
            t_class_intersection.equivalent_to = [t_class_identifier & t_class_identifier_1]
        return t_class_intersection

    def create_and_class(self, class_identifier, class_identifier_1):
        with self.onto:
            and_class = self.create_class(
                class_identifier.name + ":And:" + class_identifier_1.name)
            and_class.equivalent_to = [class_identifier & class_identifier_1]
        return and_class

    @singledispatchmethod
    def create_property(self, property_name):
        with self.onto:
            new_property = types.new_class(property_name, (ObjectProperty,))
        return new_property

    @create_property.register
    def _(self, property_name: list):
        with self.onto:
            new_property = types.new_class(property_name[0], (ObjectProperty,))
            new_property.domain = [self.onto[property_name[1]]]
            new_property.range = [self.onto[property_name[2]]]
        return new_property

    def create_relation(self, domain_member_name, range_member_name, property_name):
        with self.onto:
            domain_member = self.get_member(domain_member_name)
            range_member = self.get_member(range_member_name)
            setattr(domain_member, property_name, [range_member])

    def destroy_specific_entity(self, entity_identifier):
        with self.onto:
            destroy_entity(entity_identifier)

    def add_sub_class(self, sub_class_identifier, super_class_identifier, add_to_strict_facts_list=True):
        with self.onto:
            sub_class_identifier.is_a.append(super_class_identifier)
            if add_to_strict_facts_list:
                self.strict_facts_list.append(StrictFact(sub_class_identifier, super_class_identifier))

    def add_typical_fact(self, t_class_identifier, class_identifier, probability="No probability", add_to_dict=True, typical_fact_is_a_query=False):
        with self.onto:
            t_class_identifier_1 = self.create_class(t_class_identifier.name + "1")
            t_class_intersection = self.create_class("Intersection(" + t_class_identifier.name + t_class_identifier_1.name + ")")
            t_class_intersection.equivalent_to = [t_class_identifier & t_class_identifier_1]
            self.add_sub_class(t_class_intersection, class_identifier, add_to_strict_facts_list=False)

            r1 = self.create_property("r1")
            t_class_identifier_1.is_a.append(r1.only(Not(t_class_identifier) & t_class_identifier_1))

            not_t_class_identifier_1 = self.create_class("Not(" + t_class_identifier_1.name + ")")
            not_t_class_identifier_1.is_a.append(r1.some(t_class_identifier & t_class_identifier_1))

            if typical_fact_is_a_query:
                typical_fact = TypicalFact(t_class_identifier, class_identifier, probability, typical_fact_is_a_query=True)
                self.query_typical_fact = typical_fact
                self.typical_facts_support_dict["?T" + t_class_identifier.name + "_" + class_identifier.name] = typical_fact
            else:
                typical_fact = TypicalFact(t_class_identifier, class_identifier, probability)
                self.typical_facts_support_dict["T"+t_class_identifier.name+"_"+class_identifier.name] = typical_fact
            if add_to_dict:
                self.typical_facts_dict["T"+t_class_identifier.name+"_"+class_identifier.name] = typical_fact
                self.typical_facts_list.append(typical_fact)
        return typical_fact

    def get_typical_fact(self, typical_fact_name):
        return self.typical_facts_dict.get(typical_fact_name)

    def show_scenarios(self):
        for scenario in self.scenarios_list:
            print("INIZIO SCENARIO " + str(scenario.num_scenario))
            record = ""
            if len(scenario.list_of_typical_members) == 0:
                print("Scenario vuoto" + "\n" + "Probabilità scenario: " + str(scenario.probability))
            else:
                for typical_member in scenario.list_of_typical_members:
                    record = record + "Typical(" + typical_member.t_class_identifier.name + ")" + "," + typical_member.member_name + "," + str(
                        typical_member.probability) + "\n"
                record = record + "Probabilità scenario: " + str(scenario.probability)
                print(record)
            print("FINE SCENARIO " + str(scenario.num_scenario))
            print("\n")

    @staticmethod
    def show_a_specific_scenario(scenario):
        print("INIZIO SCENARIO " + str(scenario.num_scenario))
        record = ""
        if len(scenario.list_of_typical_members) == 0:
            print("Scenario vuoto; " + str(scenario.probability))
        else:
            for typical_member in scenario.list_of_typical_members:
                record = record + "Typical(" + typical_member.t_class_identifier.name + ")," + typical_member.member_name + "," + str(typical_member.probability) + "\n"
            record = record + "Probabilità scenario: " + str(scenario.probability)
            print(record)
        print("FINE SCENARIO " + str(scenario.num_scenario))

    @staticmethod
    def set_classes_as_disjoint(classes_identifier_list):
        AllDisjoint(classes_identifier_list)

    def add_member_to_class(self, member_name, class_identifier):
        self.a_box_members_list.append(AboxMember(class_identifier, member_name))
        return class_identifier(member_name)

    def create_classes_to_set_a_member_as_typical_member(self, t_class_identifier_name, class_identifiers: list = None):
        t_class_identifier = self.create_class(t_class_identifier_name)
        self.create_class("Intersection(" + t_class_identifier_name + t_class_identifier_name + "1)")
        t_class_identifier_1 = self.create_class(t_class_identifier_name + "1")
        if class_identifiers is not None:
            t_class_identifier.equivalent_to = [class_identifiers[0] & class_identifiers[1]]
        return t_class_identifier, t_class_identifier_1

    def set_as_typical_member(self, member_name, t_class_identifier, t_class_identifier_1, remove_from_knowledge_base=False):
        with self.onto:
            t_class_identifier(member_name)
            t_class_identifier_1(member_name)
            t_class_intersection = self.get_class("Intersection(" + t_class_identifier.name + t_class_identifier_1.name + ")")
            t_class_intersection(member_name)
            if member_name != "x":
                if self.typical_members_dict.get(t_class_identifier.name) is None:
                    temp = list()
                    temp.append(TypicalMember(t_class_identifier, member_name, probability=None, t_class_identifier_1=t_class_identifier_1, t_class_intersection=t_class_intersection, remove_from_knowledge_base=remove_from_knowledge_base))
                    self.typical_members_dict[str(t_class_identifier.name)] = temp
                else:
                    typical_member_found = next((typical_member for typical_member in self.typical_members_dict.get(str(t_class_identifier.name))
                                                if typical_member.t_class_identifier.name == t_class_identifier.name and
                                                typical_member.member_name == member_name), None)
                    if typical_member_found is None:
                        self.typical_members_dict[str(t_class_identifier.name)].append(TypicalMember(t_class_identifier, member_name, probability=None, t_class_identifier_1=t_class_identifier_1, t_class_intersection=t_class_intersection, remove_from_knowledge_base=remove_from_knowledge_base))

    def print_typical_member(self, member_name, t_class_identifier, t_class_identifier_1):
        t_class_intersection = self.get_class("Intersection(" + t_class_identifier.name + t_class_identifier_1.name + ")")
        print("Membro tipico:")
        print(member_name + " ∈ " + t_class_identifier.name)
        print(member_name + " ∈ " + t_class_identifier_1.name)
        print(member_name + " ∈ " + t_class_intersection.name)

    def add_member_to_multiple_classes(self, member_identifier, class_list):
        for c in class_list:
            member_identifier.is_a.append(c)
            self.a_box_members_list.append(AboxMember(c, member_identifier.name))

    def is_class_present(self, class_name):
        if self.get_class(class_name) is not None:
            return True
        return False

    def get_class(self, class_name):
        return self.onto[class_name]

    def get_classes(self, return_as_list=False):
        if return_as_list:
            return list(self.onto.classes())
        else:
            return self.onto.classes()

    def is_consistent(self):
        return self.consistency()

    def consistency(self):
        try:
            with self.onto:
                sync_reasoner(self.my_world)
                return "The ontology is consistent"
        except OwlReadyInconsistentOntologyError:
            return "The ontology is inconsistent"

    def show_strict_facts(self):
        for strict_fact in self.strict_facts_list:
            print(strict_fact.strict_fact_name)

    def show_classes_iri(self):
        for c in self.onto.classes():
            print(str(c.name) + " ⊑ " + str(c.is_a))

    def show_members_in_classes(self):
        for class_identifier in self.onto.classes():
            for member_identifier in class_identifier.instances():
                print(member_identifier.name + " ∈ " + class_identifier.name)

    @staticmethod
    def show_super_classes(super_class_identifier):
        print(super_class_identifier.is_a)

    def get_super_classes(self, class_identifier, exclude_owl_thing=False):
        if exclude_owl_thing is False:
            return self.onto[class_identifier.name].is_a
        else:
            return [super_class for super_class in self.onto[class_identifier.name].ancestors() if super_class.name != "Thing" and super_class.name != class_identifier.name]

    def get_sub_classes(self, class_identifier, exclude_self_and_owl_thing=False):
        if exclude_self_and_owl_thing is False:
            return self.onto[class_identifier.name].descendants()
        else:
            return [sub_class for sub_class in self.onto[class_identifier.name].descendants() if sub_class.name != "Thing" and sub_class.name != class_identifier.name]

    def get_member(self, member_name):
        for class_identifier in self.onto.classes():
            for member_identifier in class_identifier.instances():
                if member_identifier.name == member_name:
                    return member_identifier
        return "Member " + member_name + " not found"

    def get_members(self, class_identifier, return_as_list=False):
        if return_as_list:
            return list(self.onto[class_identifier.name].instances())
        else:
            return self.onto[class_identifier.name].instances()

    def has_members(self, class_identifier):
        if len(list(self.onto[class_identifier.name].instances())) == 0:
            return False
        return True
