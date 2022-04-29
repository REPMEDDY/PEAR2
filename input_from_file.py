import math

import owlready2.util

import increased_ontology
import query_ontology
import reasoning_on_scenarios
import rational_closure_of_tbox
import rational_closure_of_abox
from OntologyManager import *

"""
Il seguente metodo prendendo in input un oggetto di tipo OntologyManager
ha il compito di costruire l'ontologia leggendo i dati forniti dal file
"ontology_input"
"""


def add_query(ontology_manager_object, query_typical_fact_name):
    # Caso in cui la query presenta due classi in And nell'operatore di tipicalità
    if "And(" in query_typical_fact_name.split(",")[0]:
        query_typical_fact_name_splitted = query_typical_fact_name.split(",")
        query_typical_fact_name_splitted[0] = query_typical_fact_name_splitted[0].replace("?Typical(And(", "").replace(")", "")
        typical_fact = process_typical_fact_with_and_classes(query_typical_fact_name_splitted, ontology_manager_object, typical_fact_is_a_query=True)
    # Caso in cui la query non presenta due classi in And nell'operatore di tipicalità
    else:
        query_typical_fact_name_splitted = query_typical_fact_name.split(",")
        query_typical_fact_name_splitted[0] = query_typical_fact_name_splitted[0].replace("?Typical(", "").replace(")", "")
        typical_fact = process_typical_fact_without_and_classes(ontology_manager_object, query_typical_fact_name_splitted, typical_fact_is_a_query=True)
    return typical_fact


def build_ontology(ontology_manager_object):
    file_object = open("ontology_input", "r")
    for line in file_object:
        if line[:-1] == "Classes:":
            process_classes_names(file_object, ontology_manager_object)
        if line[:-1] == "Set_as_sub_class:":
            process_set_as_sub_class(file_object, ontology_manager_object)
        if line[:-1] == "Add_members_to_class:":
            process_add_members_to_class(file_object, ontology_manager_object)
        if line[:-1] == "Set_typical_facts:":
            process_set_typical_facts(file_object, ontology_manager_object)
        if line[:-1] == "Add_typical_member:":
            process_add_typical_member(file_object, ontology_manager_object)
    file_object.close()


def process_classes_names(file_object, ontology_manager_object):
    line = file_object.readline().rstrip("\n")
    class_names_list = line.split()
    for class_name in class_names_list:
        ontology_manager_object.create_class(class_name)


def process_set_as_sub_class(file_object, ontology_manager_object):
    line = file_object.readline().rstrip("\n")
    sub_class_list = line.split()
    for classes_couple in sub_class_list:
        split_classes_couple = classes_couple.split(",")
        sub_class = ontology_manager_object.get_class(split_classes_couple[0])
        super_class = ontology_manager_object.get_class(split_classes_couple[1])
        ontology_manager_object.add_sub_class(sub_class, super_class)


def process_add_members_to_class(file_object, ontology_manager_object):
    line = file_object.readline().rstrip("\n")
    list_couple_member_classes = line.split(" ")
    for couple_member_classes in list_couple_member_classes:
        couple_splitted = couple_member_classes.split(";")
        member_name = couple_splitted[0]
        classes_identifiers_names = couple_splitted[1].split(",")
        for class_identifier_name in classes_identifiers_names:
            if "Not(" in class_identifier_name:
                not_class_identifier = process_class_startswith_not(class_identifier_name, ontology_manager_object)
                ontology_manager_object.add_member_to_class(member_name, not_class_identifier)
            else:
                class_identifier = ontology_manager_object.get_class(class_identifier_name)
                ontology_manager_object.add_member_to_class(member_name, class_identifier)


def process_add_typical_member(file_object, ontology_manager_object):
    line = file_object.readline().rstrip("\n")
    couple_typical_class_member_list = line.split(" ")
    for couple_typical_class_member in couple_typical_class_member_list:
        couple_splitted = couple_typical_class_member.split(";")
        member_names = couple_splitted[1].split(",")
        # typical_class = couple_splitted[0].replace("Typical", "").replace("(", "").replace(")", "")
        # Caso in cui il membro tipico è del tipo Typical(And(Bird_Black));opus
        if "And(" in couple_splitted[0]:
            and_t_classes_identifiers_names = couple_splitted[0].replace("Typical(And(", "").replace(")", "").split("_")
            # Caso in cui la classe tipica è già stata creata
            if ontology_manager_object.get_class(and_t_classes_identifiers_names[0] + ":And:" + and_t_classes_identifiers_names[1]) is not None:
                for member_name in member_names:
                    t_class_identifier = ontology_manager_object.get_class(and_t_classes_identifiers_names[0] + ":And:" + and_t_classes_identifiers_names[1])
                    t_class_identifier_1 = ontology_manager_object.get_class(and_t_classes_identifiers_names[0] + ":And:" + and_t_classes_identifiers_names[1] + "1")
                    ontology_manager_object.set_as_typical_member(member_name, t_class_identifier, t_class_identifier_1)
            # Caso in cui la classe tipica non è stata ancora creata; capita quando si usa il modulo query_ontology.py
            else:
                # Es: creo BirdAndBlack
                t_class_identifier_name = and_t_classes_identifiers_names[0] + ":And:" + and_t_classes_identifiers_names[1]
                # Bird
                class_identifier = ontology_manager_object.get_class(and_t_classes_identifiers_names[0])
                # Black
                class_identifier_1 = ontology_manager_object.get_class(and_t_classes_identifiers_names[1])
                # Ottengo le classi BirdAndBlack, BirdAndBlack1
                t_class_identifier, t_class_identifier_1 = ontology_manager_object.create_classes_to_set_a_member_as_typical_member(t_class_identifier_name, [class_identifier, class_identifier_1])
                for member_name in member_names:
                    ontology_manager_object.set_as_typical_member(member_name, t_class_identifier, t_class_identifier_1)
        # Caso in cui il membro tipico è del tipo Typical(Bird);opus
        else:
            # Caso in cui la classe tipica è già stata creata
            typical_class = couple_splitted[0].replace("Typical(", "").replace(")", "")
            if ontology_manager_object.get_class(typical_class) is not None:
                for member_name in member_names:
                    t_class_identifier = ontology_manager_object.get_class(typical_class)
                    t_class_identifier_1 = ontology_manager_object.get_class(typical_class + "1")
                    ontology_manager_object.set_as_typical_member(member_name, t_class_identifier, t_class_identifier_1)
            # Caso in cui la classe tipica non è stata ancora creata; capita quando si usa il modulo query_ontology.py
            else:
                # Es: creo Penguin
                t_class_identifier_name = typical_class
                # Penguin
                class_identifier = ontology_manager_object.get_class(t_class_identifier_name)
                t_class_identifier, t_class_identifier_1 = ontology_manager_object.create_classes_to_set_a_member_as_typical_member(t_class_identifier_name, [class_identifier])
                for member_name in member_names:
                    ontology_manager_object.set_as_typical_member(member_name, t_class_identifier, t_class_identifier_1)


def process_set_typical_facts(file_object, ontology_manager_object):
    line = file_object.readline().rstrip("\n")
    # i fatti tipici sono separati da uno spazio, perciò splitto sullo spazio
    fact_list = line.split(" ")
    # qui ho una lista di fatti tipici
    for fact in fact_list:
        # caso in cui ho due classi in And all'interno dell'operatore di tipicalità
        if "And(" in fact.split(",")[0]:
            # splitto il fatto tipico in esame sulla virgola per separare la parte con l'operatore di tipicalità dal resto
            splitted_fact = fact.split(",")
            splitted_fact[0] = splitted_fact[0].replace("Typical(And(", "").replace(")", "")
            if "?" not in splitted_fact[0]:
                process_typical_fact_with_and_classes(splitted_fact, ontology_manager_object)
            else:
                process_typical_fact_with_and_classes(splitted_fact, ontology_manager_object, typical_fact_is_a_query=True)
        # caso in cui il fatto tipico non presenta classi in And all'interno dell'operatore di tipicalità
        else:
            # splitto il fatto tipico in esame sulla virgola per separare la parte con l'operatore di tipicalità dal resto
            splitted_fact = fact.split(",")
            splitted_fact[0] = splitted_fact[0].replace("Typical(", "").replace(")", "")
            if "?" not in splitted_fact[0]:
                process_typical_fact_without_and_classes(ontology_manager_object, splitted_fact)
            else:
                process_typical_fact_without_and_classes(ontology_manager_object, splitted_fact, typical_fact_is_a_query=True)
    return fact_list


def process_typical_fact_with_and_classes(splitted_fact, ontology_manager_object, typical_fact_is_a_query=False):
    # Caso in cui il fatto tipico non è una query
    if not typical_fact_is_a_query:
        and_t_classes_identifiers_names = splitted_fact[0].split("_")
        t_class_identifier = ontology_manager_object.get_class(and_t_classes_identifiers_names[0])
        t_class_identifier_1 = ontology_manager_object.get_class(and_t_classes_identifiers_names[1])
        and_equivalent_t_class_identifier = ontology_manager_object.create_and_class(t_class_identifier, t_class_identifier_1)
        and_equivalent_t_class_identifier.comment = math.inf
        # caso in cui il fatto tipico presenta una classe con l'operatore Not
        # fuori dall'operatore di tipicalità. es: Typical(And(Bird_Black)),Not(Fly)
        if "Not(" in splitted_fact[1]:
            not_class_identifier = process_class_startswith_not(splitted_fact[1], ontology_manager_object)
            if len(splitted_fact) > 2:
                typical_fact = ontology_manager_object.add_typical_fact(and_equivalent_t_class_identifier, not_class_identifier, float(splitted_fact[2]))
            else:
                typical_fact = ontology_manager_object.add_typical_fact(and_equivalent_t_class_identifier, not_class_identifier)
        # caso in cui il fatto tipico non presenta una classe con l'operatore Not
        # fuori dall'operatore di tipicalità. es: Typical(And(Bird_Black)),Fly
        else:
            class_identifier = ontology_manager_object.get_class(splitted_fact[1])
            if len(splitted_fact) > 2:
                typical_fact = ontology_manager_object.add_typical_fact(and_equivalent_t_class_identifier, class_identifier, float(splitted_fact[2]))
            else:
                typical_fact = ontology_manager_object.add_typical_fact(and_equivalent_t_class_identifier, class_identifier)
    # Caso in cui il fatto tipico è una query
    else:
        and_t_classes_identifiers_names = splitted_fact[0].split("_")
        t_class_identifier = ontology_manager_object.get_class(and_t_classes_identifiers_names[0])
        t_class_identifier_1 = ontology_manager_object.get_class(and_t_classes_identifiers_names[1])
        and_equivalent_t_class_identifier = ontology_manager_object.create_and_class(t_class_identifier, t_class_identifier_1)
        and_equivalent_t_class_identifier.comment = math.inf
        # caso in cui il fatto tipico presenta una classe con l'operatore Not
        # fuori dall'operatore di tipicalità. es: Typical(And(Bird_Black)),Not(Fly)
        if "Not(" in splitted_fact[1]:
            not_class_identifier = process_class_startswith_not(splitted_fact[1], ontology_manager_object)
            if len(splitted_fact) > 2:
                typical_fact = ontology_manager_object.add_typical_fact(and_equivalent_t_class_identifier, not_class_identifier, float(splitted_fact[2]), add_to_dict=False, typical_fact_is_a_query=True)
            else:
                typical_fact = ontology_manager_object.add_typical_fact(and_equivalent_t_class_identifier, not_class_identifier, add_to_dict=False, typical_fact_is_a_query=True)
        # caso in cui il fatto tipico non presenta una classe con l'operatore Not
        # fuori dall'operatore di tipicalità. es: Typical(And(Bird_Black)),Fly
        else:
            class_identifier = ontology_manager_object.get_class(splitted_fact[1])
            if len(splitted_fact) > 2:
                typical_fact = ontology_manager_object.add_typical_fact(and_equivalent_t_class_identifier, class_identifier, float(splitted_fact[2]), add_to_dict=False, typical_fact_is_a_query=True)
            else:
                typical_fact = ontology_manager_object.add_typical_fact(and_equivalent_t_class_identifier, class_identifier, add_to_dict=False, typical_fact_is_a_query=True)
    return typical_fact


def process_typical_fact_without_and_classes(ontology_manager_object, splitted_fact, typical_fact_is_a_query=False):
    # Caso in cui il fatto tipico non è una query
    if not typical_fact_is_a_query:
        t_class_identifier = ontology_manager_object.get_class(splitted_fact[0])
        t_class_identifier.comment.append(math.inf)
        # caso in cui il fatto tipico presenta una classe con l'operatore Not
        # fuori dall'operatore di tipicalità. es: T(Penguin),Not(Fly)
        if splitted_fact[1].startswith("Not("):
            not_class_identifier = process_class_startswith_not(splitted_fact[1], ontology_manager_object)
            # caso in cui il fatto tipico ha anche una probabilità associata. es: T(Bird),Fly,0.90
            if len(splitted_fact) > 2:
                typical_fact = ontology_manager_object.add_typical_fact(t_class_identifier, not_class_identifier, float(splitted_fact[2]))
            else:
                typical_fact = ontology_manager_object.add_typical_fact(t_class_identifier, not_class_identifier)
        # caso in cui il fatto tipico non presenta una classe con l'operatore Not
        # fuori dall'operatore di tipicalità. es: T(Bird),Fly
        else:
            class_identifier = ontology_manager_object.get_class(splitted_fact[1])
            if len(splitted_fact) > 2:
                typical_fact = ontology_manager_object.add_typical_fact(t_class_identifier, class_identifier, float(splitted_fact[2]))
            else:
                typical_fact = ontology_manager_object.add_typical_fact(t_class_identifier, class_identifier)
    # Caso in cui il fatto tipico è una query
    else:
        t_class_identifier = ontology_manager_object.get_class(splitted_fact[0])
        t_class_identifier.comment.append(math.inf)
        # caso in cui il fatto tipico presenta una classe con l'operatore Not
        # fuori dall'operatore di tipicalità. es: T(Penguin),Not(Fly)
        if splitted_fact[1].startswith("Not("):
            not_class_identifier = process_class_startswith_not(splitted_fact[1], ontology_manager_object)
            # caso in cui il fatto tipico ha anche una probabilità associata. es: T(Bird),Fly,0.90
            if len(splitted_fact) > 2:
                typical_fact = ontology_manager_object.add_typical_fact(t_class_identifier, not_class_identifier,
                                                         float(splitted_fact[2]), add_to_dict=False,
                                                         typical_fact_is_a_query=True)
            else:
                typical_fact = ontology_manager_object.add_typical_fact(t_class_identifier, not_class_identifier,
                                                                        add_to_dict=False, typical_fact_is_a_query=True)
        # caso in cui il fatto tipico non presenta una classe con l'operatore Not
        # fuori dall'operatore di tipicalità. es: T(Bird),Fly
        else:
            class_identifier = ontology_manager_object.get_class(splitted_fact[1])
            if len(splitted_fact) > 2:
                typical_fact = ontology_manager_object.add_typical_fact(t_class_identifier, class_identifier,
                                                                        float(splitted_fact[2]), add_to_dict=False,
                                                                        typical_fact_is_a_query=True)
            else:
                typical_fact = ontology_manager_object.add_typical_fact(t_class_identifier, class_identifier,
                                                                        add_to_dict=False, typical_fact_is_a_query=True)
    return typical_fact


def process_class_startswith_not(splitted_fact, ontology_manager_object):
    splitted_fact = splitted_fact.replace("Not(", "").replace("(", "").replace(")", "")
    not_class_identifier = ontology_manager_object.create_class("Not(" + splitted_fact + ")")
    not_class_identifier.equivalent_to = [ontology_manager_object.create_complementary_class(
        ontology_manager_object.get_class(splitted_fact))]
    return not_class_identifier


if __name__ == '__main__':
    """
    # Task di PEAR
    ontology_manager = OntologyManager()
    build_ontology(ontology_manager)
    increased_ontology.compute_probability_for_typical_members(ontology_manager)
    increased_ontology.set_probability_for_each_scenario(
        increased_ontology.generate_scenarios(ontology_manager),
        ontology_manager)
    ontology_manager.show_scenarios()
    query_result = reasoning_on_scenarios.is_logical_consequence(ontology_manager)
    query_result.show_query_result()"""

    # Task per controllare se la chiusura razionale della Tbox viene fatta bene

    """query_ontology.is_typical_fact_part_of_racl_of_tbox()"""

    # Task primario con gli scenari di PEAR2
    ontology_manager = OntologyManager()
    build_ontology(ontology_manager)
    rank_assignment_dict = rational_closure_of_abox.compute_rational_closure_of_abox()
    increased_ontology.compute_probability_for_typical_members(ontology_manager, rank_assignment_dict)
    increased_ontology.set_probability_for_each_scenario(
        increased_ontology.generate_scenarios(ontology_manager),
        ontology_manager)
    ontology_manager.show_scenarios()
    query_result = reasoning_on_scenarios.is_logical_consequence(ontology_manager)
    query_result.show_query_result()
