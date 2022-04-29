import rational_closure_of_tbox as racl_tbox
from OntologyManager import *
import input_from_file

"""
Questo modulo fornisce una serie di metodi utilizzati per calcolare la chiusura razionale della abox.
"""


def compute_rational_closure_of_abox():
    # Questo metodo implementa la chiusura razionale della abox (def 27 dell'articolo).
    # Il primo passo è calcolare μ; per farlo si cicla sui rank possibili (ottenuti dalla racl della tbox).
    rank_assignment_dict = dict()
    rational_closure_of_tbox_list, max_rank = racl_tbox.compute_rational_closure_of_tbox()
    ontology_manager_for_racl_of_abox = OntologyManager("https://onto-racl-abox.org/onto.owl")
    input_from_file.build_ontology(ontology_manager_for_racl_of_abox)
    rank_assignment = 0
    member_names = get_member_names(ontology_manager_for_racl_of_abox)
    number_of_members_with_rank_assigned = 0
    while rank_assignment <= max_rank and number_of_members_with_rank_assigned < len(member_names):
        for member_name in member_names:
            if member_name not in rank_assignment_dict.keys():
                print("PROVO AD ASSEGNARE A " + member_name + " IL RANK " + str(rank_assignment))
                not_t_class_or_class_identifiers_names_inferred_list = list()
                compute_first_part_of_mu(rational_closure_of_tbox_list, rank_assignment, ontology_manager_for_racl_of_abox, member_name, not_t_class_or_class_identifiers_names_inferred_list)
                compute_second_part_of_mu(ontology_manager_for_racl_of_abox, member_name, not_t_class_or_class_identifiers_names_inferred_list)
                number_of_members_with_rank_assigned = check_consistency_of_knowledge_base(ontology_manager_for_racl_of_abox, rank_assignment_dict, member_name, rank_assignment, number_of_members_with_rank_assigned, not_t_class_or_class_identifiers_names_inferred_list)
                not_t_class_or_class_identifiers_names_inferred_list.clear()
            else:
                print("AL MEMBRO " + member_name + " È GIÀ STATO ASSEGNATO UN RANK: rank(" + member_name + ") = " + str(rank_assignment_dict.get(member_name)))
        rank_assignment += 1
    print("RANK ASSIGNMENT: ", rank_assignment_dict)
    print("DOPO μ")
    show_knowledge_base(ontology_manager_for_racl_of_abox)
    return rank_assignment_dict


def compute_first_part_of_mu(rational_closure_of_tbox_list, rank_assignment, ontology_manager_for_racl_of_abox, member_name, not_t_class_or_class_identifiers_names_inferred_list):
    # Questo for costituisce la prima parte della definizione di μ; si aggiungono i fatti
    # not_t_class_or_class all'abox se rank del concetto del fatto tipico presente nella racl della tbox è
    # pari a rank_assignment e si aggiunge che il membro in esame è un not_t_class_or_class. Es: TBird_Fly
    # --> se rank(Bird) == rank_assignment --> aggiungo Not(Bird)OrFly e dico che il membro in esame vi
    # appartiene
    for typical_fact_name in racl_tbox.classes_ranks_of_typical_facts_dict.keys():
        if typical_fact_name in rational_closure_of_tbox_list and \
                racl_tbox.classes_ranks_of_typical_facts_dict.get(typical_fact_name)[0] >= rank_assignment:
            t_class_identifier = ontology_manager_for_racl_of_abox.get_class(typical_fact_name.split("_")[0].replace("?", "").replace("T", "", 1))
            class_identifier = ontology_manager_for_racl_of_abox.get_class(typical_fact_name.split("_")[1])
            ontology_manager_for_racl_of_abox.create_not_t_class_or_class(t_class_identifier, class_identifier)
            not_t_class_or_class_identifier_name = "Not(" + t_class_identifier.name + "):Or:" + class_identifier.name
            not_t_class_or_class_identifier = ontology_manager_for_racl_of_abox.get_class(not_t_class_or_class_identifier_name)
            ontology_manager_for_racl_of_abox.add_member_to_class(member_name, not_t_class_or_class_identifier)
            not_t_class_or_class_identifiers_names_inferred_list.append(not_t_class_or_class_identifier_name)


def compute_second_part_of_mu(ontology_manager_for_racl_of_abox, member_name, not_t_class_or_class_identifiers_names_inferred_list):
    # Questo for costituisce la seconda parte della definizione di μ; si aggiungono i fatti
    # not_t_class_or_class all'abox per ogni strict_fact presente nella kb e si aggiunge che il membro in
    # esame è un not_t_class_or_class. Es: Penguin is_a Bird --> aggiungo Not(Penguin)OrBird --> aggiungo il
    # membro in esame a Not(Penguin)OrBird
    for strict_fact in ontology_manager_for_racl_of_abox.strict_facts_list:
        t_class_identifier = strict_fact.sub_class_identifier
        class_identifier = strict_fact.super_class_identifier
        ontology_manager_for_racl_of_abox.create_not_t_class_or_class(t_class_identifier, class_identifier)
        not_t_class_or_class_identifier_name = "Not(" + t_class_identifier.name + "):Or:" + class_identifier.name
        not_t_class_or_class_identifier = ontology_manager_for_racl_of_abox.get_class(not_t_class_or_class_identifier_name)
        ontology_manager_for_racl_of_abox.add_member_to_class(member_name, not_t_class_or_class_identifier)
        not_t_class_or_class_identifiers_names_inferred_list.append(not_t_class_or_class_identifier_name)


def check_consistency_of_knowledge_base(ontology_manager_for_racl_of_abox, rank_assignment_dict, member_name, rank_assignment, number_of_members_with_rank_assigned, not_t_class_or_class_identifiers_names_inferred_list):
    if ontology_manager_for_racl_of_abox.is_consistent() == "The ontology is consistent":
        rank_assignment_dict[member_name] = rank_assignment
        number_of_members_with_rank_assigned += 1
        print("OK, L'ONTOLOGIA È CONSISTENTE")
        show_knowledge_base(ontology_manager_for_racl_of_abox)
        return number_of_members_with_rank_assigned
    else:
        print("NO, L'ONTOLOGIA È INCONSISTENTE")
        show_knowledge_base(ontology_manager_for_racl_of_abox)
        # Se l'ontologia non è consistente, devo rimuovere tutte le not_t_class_or_class aggiunte. In
        # teoria sarebbe sufficiente rimuovere la classe dall'is_a del membro in esame; tuttavia ho
        # riscontrato dei bug/funzionamenti di Hermit indesiderati. In particolare succede che in alcuni
        # casi, il programma aggiunge il membro alla not_t_class_or_class e successivamente quando si
        # verifica la consistenza, Hermit effettua un reparenting per cui tale membro non viene più visto
        # come appartenente a quella not_t_class_or_class. In aggiunta a ciò succede pure che se si va a
        # controllare le istanze di quella not_t_class_or_class (tramite instances()), tale membro ne
        # faccia parte. Di conseguenza nell'is_a del membro non risulterebbe quella not_t_class_or_class
        # ed in contemporanea quel membro figura come istanza di quella not_t_class_or_class. Per ovviare
        # a questo problema distruggo la not_t_class_or_class e la ricreo aggiungendo tutti i membri che
        # aveva precedentemente tranne il membro per cui l'ontologia risulta inconsistente.
        for not_t_class_or_class_identifier_name in not_t_class_or_class_identifiers_names_inferred_list:
            member_identifier = ontology_manager_for_racl_of_abox.get_member(member_name)
            not_t_class_or_class_identifier = ontology_manager_for_racl_of_abox.get_class(not_t_class_or_class_identifier_name)
            if not_t_class_or_class_identifier in member_identifier.is_a:
                if len(list(not_t_class_or_class_identifier.instances())) > 1:
                    member_identifier.is_a.remove(not_t_class_or_class_identifier)
                else:
                    if member_identifier in list(not_t_class_or_class_identifier.instances()):
                        ontology_manager_for_racl_of_abox.destroy_specific_entity(not_t_class_or_class_identifier)
            elif not_t_class_or_class_identifier not in member_identifier.is_a:
                if member_identifier in list(not_t_class_or_class_identifier.instances()):
                    not_t_class_or_class_identifier_name = not_t_class_or_class_identifier.name
                    not_t_class_or_class_identifier_members_list = list((member_identifier.name for member_identifier in not_t_class_or_class_identifier.instances()))
                    ontology_manager_for_racl_of_abox.destroy_specific_entity(not_t_class_or_class_identifier)
                    t_class_identifier = ontology_manager_for_racl_of_abox.get_class(not_t_class_or_class_identifier_name.split(":Or:")[0].replace("Not(", "").replace(")", ""))
                    class_identifier = ontology_manager_for_racl_of_abox.get_class(not_t_class_or_class_identifier_name.split(":Or:")[1])
                    ontology_manager_for_racl_of_abox.create_not_t_class_or_class(t_class_identifier, class_identifier)
                    not_t_class_or_class_identifier = ontology_manager_for_racl_of_abox.get_class(not_t_class_or_class_identifier_name)
                    for member_identifier_name in not_t_class_or_class_identifier_members_list:
                        if member_identifier_name != member_identifier.name:
                            ontology_manager_for_racl_of_abox.add_member_to_class(member_identifier_name, not_t_class_or_class_identifier)
        print("ONTOLOGIA DOPO RIMOZIONE FATTI")
        show_knowledge_base(ontology_manager_for_racl_of_abox)
        return number_of_members_with_rank_assigned


def get_member_names(ontology_manager_for_racl_of_abox):
    member_names = set()
    for abox_member in ontology_manager_for_racl_of_abox.a_box_members_list:
        member_names.add(abox_member.member_name)
    return member_names


def show_knowledge_base(ontology_manager_for_racl_of_abox):
    ontology_manager_for_racl_of_abox.show_members_in_classes()
    ontology_manager_for_racl_of_abox.show_classes_iri()
