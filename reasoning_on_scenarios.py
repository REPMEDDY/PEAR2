from QueryResult import *
import input_from_file

"""
Questo modulo è composto da una serie di metodi che permettono di ragionare sugli scenari generati verificando se la 
query in input segue logicamente dalla base di conoscenza con l'aggiunta dello scenario corrente.
"""


def __translate_scenario(scenario, ontology_manager):
    for typical_member in scenario.list_of_typical_members:
        ontology_manager.set_as_typical_member(
            typical_member.member_name, typical_member.t_class_identifier, ontology_manager.onto[typical_member.t_class_identifier.name + "1"])
        ontology_manager.print_typical_member(typical_member.member_name, typical_member.t_class_identifier,
                                              ontology_manager.onto[typical_member.t_class_identifier.name + "1"])


def __query_hermit(ontology_manager):
    return ontology_manager.consistency()


def is_logical_consequence(ontology_manager, lower_probability_bound=0, higher_probability_bound=1):
    query_result = QueryResult()
    total_probability = 0
    if lower_probability_bound != 0 or higher_probability_bound != 1:
        filtered_scenarios = [scenario for scenario in ontology_manager.scenarios_list
                              if lower_probability_bound <= scenario.probability <= higher_probability_bound]
    else:
        filtered_scenarios = ontology_manager.scenarios_list
    for scenario in filtered_scenarios:
        ontology_manager_support = OntologyManager("https://test.org/onto.owl")
        input_from_file.build_ontology(ontology_manager_support)
        print("ONTOLOGIA PRIMA DELLA LETTURA DELLA QUERY\n"
              "=================================")
        ontology_manager_support.show_members_in_classes()
        ontology_manager_support.show_classes_iri()
        print("=================================\n"
              "FINE ONTOLOGIA PRIMA DELLA LETTURA DELLA QUERY\n\n"
              "LETTURA QUERY\n"
              "=================================")
        __read_query(ontology_manager_support)
        print("=================================\n"
              "LETTURA QUERY TERMINATA\n\n"
              "TRADUCENDO LO SCENARIO: \n"
              "=================================")
        OntologyManager.show_a_specific_scenario(scenario)
        __translate_scenario(scenario, ontology_manager_support)
        print("=================================\n"
              "FINE TRADUZIONE SCENARIO\n\n"
              "ONTOLOGIA CON SCENARIO E QUERY\n"
              "=================================")
        ontology_manager_support.show_classes_iri()
        ontology_manager_support.show_members_in_classes()
        print("=================================\n"
              "FINE ONTOLOGIA CON SCENARIO E QUERY\n\n")
        if __query_hermit(ontology_manager_support) == "The ontology is consistent":
            print("=====================\n"
                  "Il fatto non segue logicamente nel seguente scenario:")
            OntologyManager.show_a_specific_scenario(scenario)
            print("=====================\n")
        else:
            print("=====================\n"
                  "Il fatto segue logicamente nel seguente scenario:")
            OntologyManager.show_a_specific_scenario(scenario)
            print("=====================\n")
            query_result.list_of_logical_consequent_scenarios.append(scenario)
            total_probability = total_probability + scenario.probability
    query_result.probability = total_probability
    return query_result


def __read_query(ontology_manager):
    file_object = open("query_input", "r")
    line = file_object.readline().rstrip("\n")
    couple_member_class = line.split(";")
    # Caso in cui la query in input è m;Not(C)
    if couple_member_class[1].startswith("Not("):
        # Ottengo il nome della classe C
        couple_member_class[1] = couple_member_class[1].replace("Not(", "").replace("(", "").replace(")", "")
        # Creo la classe C
        class_identifier = ontology_manager.create_class(couple_member_class[1])
        # Creo la classe Not(C)
        not_class_identifier = ontology_manager.create_class("Not(" + couple_member_class[1] + ")")
        # Dico che Not(C) è equivalente al complementare di C
        not_class_identifier.equivalent_to = [ontology_manager.create_complementary_class(class_identifier)]
        # Aggiungo m come membro di C perchè la query in input è m;Not(C)
        print("Query aggiunta: " + couple_member_class[0] + " " + class_identifier.name)
        ontology_manager.add_member_to_class(couple_member_class[0], class_identifier)
    # Caso in cui la query in input è m;C
    else:
        # Creo la classe C
        class_identifier = ontology_manager.create_class(couple_member_class[1])
        # Creo la classe Not(C)
        not_class_identifier = ontology_manager.create_class("Not(" + couple_member_class[1] + ")")
        # Dico che Not(C) è equivalente al complementare di C
        not_class_identifier.equivalent_to = [ontology_manager.create_complementary_class(class_identifier)]
        # Aggiungo m come membro di Not(C) perchè la query in input è m;C
        print("Query aggiunta: " + couple_member_class[0] + " " + not_class_identifier.name)
        ontology_manager.add_member_to_class(couple_member_class[0], not_class_identifier)
    file_object.close()

