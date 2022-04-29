import OntologyManager
import input_from_file
import rational_closure_of_tbox

"""
Questo modulo fornisce una serie di metodi utilizzati per interrogare l'ontologia.
In particolare le query in input sono dei fatti tipici del tipo Typical(Bird),Fly
oppure Typical(And(Bird_Black)),Fly.
L'output della query può essere:
    - appartenenza o meno di tale fatto tipico alla chiusura razionale della tbox
    - consistenza o meno dell'ontologia a seguito dell'aggiunta di tale fatto 
"""


def is_typical_fact_part_of_racl_of_tbox():
    file_object = open("query_input", "r")
    typical_fact = file_object.readline().rstrip("\n")
    file_object.close()
    rational_closure_of_tbox.compute_rational_closure_of_tbox(query_typical_fact_name=typical_fact)


def is_knowledge_base_consistent_with_new_typical_fact(ontology_manager):
    file_object = open("query_input", "r")
    typical_facts_list = input_from_file.process_set_typical_facts(file_object, ontology_manager)
    if "And" in typical_facts_list[0]:
        and_t_classes_identifiers_names = typical_facts_list[0].split(",")[0].replace("Typical(And(", "").replace(")", "").split("_")
        and_t_class_identifier_name = and_t_classes_identifiers_names[0] + "And" + and_t_classes_identifiers_names[1]
        perform_is_knowledge_base_consistent_with_new_typical_fact(typical_facts_list, and_t_class_identifier_name, ontology_manager)
    else:
        t_class_identifier_name = typical_facts_list[0].split(",")[0].replace("Typical(", "").replace(")", "")
        perform_is_knowledge_base_consistent_with_new_typical_fact(typical_facts_list, t_class_identifier_name, ontology_manager)
    file_object.close()


def perform_is_knowledge_base_consistent_with_new_typical_fact(typical_facts_list, t_class_identifier_name, ontology_manager):
    class_identifier_name = typical_facts_list[0].split(",")[1]
    typical_fact_name = "T" + t_class_identifier_name + "_" + class_identifier_name
    typical_fact = ontology_manager.get_typical_fact(typical_fact_name)
    print("FATTO AGGIUNTO ", typical_fact.typical_fact_name)
    # Questo controllo serve per vedere se nella Abox ci siano già dei membri appartenenti alla classe sotto
    # operatore di tipicalità; l'idea è che se si vuole verificare se un certo fatto tipico sia consistente o meno
    # con la base di conoscenza, se non ci sono membri allora si procede introducendo il membro x fittizio
    # altrimenti si ragiona con i membri già presenti.
    # Ad esempio se nella Abox si ha Typical(And(Bird_Black));opus e opus;Not(Fly) e la query è
    # Typical(And(Bird_Black)),Fly, il reasoner dirà che la base è inconsistente perchè si ha un controesempio
    # dove Typical(Bird_Black),Not(Fly) è vero.
    if not ontology_manager.has_members(typical_fact.t_class_identifier):
        rational_closure_of_tbox.add_member_to_knowledge_base_class(ontology_manager, typical_fact)
    else:
        for member_identifier in ontology_manager.get_members(typical_fact.t_class_identifier):
            rational_closure_of_tbox.add_member_to_knowledge_base_class(ontology_manager, typical_fact, member_identifier.name)
    ontology_manager.show_members_in_classes()
    ontology_manager.show_classes_iri()
    print("ESITO")
    print(ontology_manager.is_consistent())
