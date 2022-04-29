import OntologyManager
from OntologyManager import *
import input_from_file
import math

"""
Questo modulo fornisce una serie di metodi utilizzati per calcolare la chiusura razionale della tbox.
"""


member_x_classes_names_created_list = list()
# Il dizionario che viene inizializzato nel metodo initialize_classes_ranks_of_typical_facts_dict
classes_ranks_of_typical_facts_dict = dict()
# Il dizionario che viene inizializzato nel metodo update_classes_ranks_of_typical_facts_dict
classes_ranks = dict()


def initialize_classes_ranks_of_typical_facts_dict(ontology_manager_for_racl_of_tbox):
    """
    Inizializza un dizionario per tenere traccia dei rank dei concetti calcolati;
    questa mappa ha come chiave il fatto tipico e come valore una coppia di interi.
    Il primo intero è il rank del concetto argomento dell'operatore di tipicalità
    mentre il secondo intero è il rank del concetto C and not D (def 22 dell'articolo).
    Esempio di coppia chiave-valore: TPenguin_Not(Fly) --> [1, 2].
    :param ontology_manager_for_racl_of_tbox:
    :return:
    """
    for typical_fact in ontology_manager_for_racl_of_tbox.typical_facts_list:
        classes_ranks_of_typical_facts_dict[typical_fact.typical_fact_name] = [typical_fact.t_class_identifier.comment[0], math.inf]


def update_classes_ranks_of_typical_facts_dict(typical_fact_name, t_class_rank=math.nan, t_class_and_not_class_rank=math.nan):
    """
    Classes ranks è un dizionario in cui si tiene traccia dei rank di tutti i concetti che vengono
    calcoloti senza però memorizzare i fatti tipici corrispettivi; viene usato per sapere se è
    necessario ricalcolare il rank di un concetto.
    :param typical_fact_name: nome del fatto tipico i cui rank vengono aggiornati
    :param t_class_rank: rank del concetto presente come parametro dell'operatore di tipicalità di
    un fatto tipico non fittizio
    :param t_class_and_not_class_rank: rank del concetto presente come parametro dell'operatore di tipicalità di
    un fatto tipico fittizio
    :return:
    """
    if typical_fact_name in classes_ranks_of_typical_facts_dict.keys():
        if t_class_rank is not math.nan and t_class_and_not_class_rank is math.nan:
            classes_ranks_of_typical_facts_dict[typical_fact_name][0] = t_class_rank
        elif t_class_rank is math.nan and t_class_and_not_class_rank is not math.nan:
            classes_ranks_of_typical_facts_dict[typical_fact_name][1] = t_class_and_not_class_rank
        elif t_class_rank is not math.nan and t_class_and_not_class_rank is not math.nan:
            classes_ranks_of_typical_facts_dict[typical_fact_name][0] = t_class_rank
            classes_ranks_of_typical_facts_dict[typical_fact_name][1] = t_class_and_not_class_rank
        else:
            pass
    else:
        classes_ranks_of_typical_facts_dict[typical_fact_name] = [t_class_rank, t_class_and_not_class_rank]


def compute_rational_closure_of_tbox(query_typical_fact_name=""):
    """
    Metodo principale che permette il calcolo della chiusura razionale della Tbox; per funzionare
    crea un oggetto di tipo OntologyManager tramite cui viene letta la KB (o ontologia che di si voglia).
    Al termine della computazione, il metodo perform_compute_rational_closure_of_tbox stampa a video la
    chiusura razionale.
    :param query_typical_fact_name: parametro opzionale usato per memorizzare la query eventualmente fornita in input
    :return: rational_closure_of_tbox_list, ovvero una lista contenente tutti i fatti tipici che fanno parte della
    chiusura razionale della Tbox; max_rank, ovvero il rank più alto calcolato (serve per calcolare la chiusura
    razionale dell'Abox
    """
    ontology_manager_for_racl_of_tbox = OntologyManager("https://onto-racl-tbox.org/onto.owl")
    max_rank = compute_sequence_of_knowledge_bases(ontology_manager_for_racl_of_tbox, query_typical_fact_name)
    print("CHIUSURA RAZIONALE DELLA TBOX")
    rational_closure_of_tbox_list = perform_compute_rational_closure_of_tbox(ontology_manager_for_racl_of_tbox)
    return rational_closure_of_tbox_list, max_rank


def get_t_class_and_not_class_name(typical_fact):
    """
    Metodo che permette di ottenere il nome di un concetto appartenente ad un fatto tipico fittizio.
    :param typical_fact: fatto tipico da cui si ricava il nome del concetto
    :return: restituisce il nome del concetto
    """
    # Caso T(Penguin),Not(Fly) --> restituisce PenguinAndFly per il fatto tipico fittizio T(PenguinAndFly),c
    if "Not(" in typical_fact.class_identifier.name:
        return typical_fact.t_class_identifier.name + ":And:" + typical_fact.class_identifier.name.replace("Not(", "").replace(")", "")
    # Caso T(Bird),Fly --> restituisce BirdAndNot(Fly) per il fatto tipico fittizio T(BirdAndNot(Fly)),c
    else:
        return typical_fact.t_class_identifier.name + ":And:Not(" + typical_fact.class_identifier.name + ")"


def compute_sequence_of_knowledge_bases(ontology_manager_for_racl_of_tbox, query_typical_fact_name=""):
    """
    Metodo che permette di costruire la collezione di Ei necessarie per il calcolo della chiusura razionale
    della Tbox.
    :param ontology_manager_for_racl_of_tbox: oggetto utilizzato per gestire la costruzione della chiusura razionale
    :param query_typical_fact_name: parametro opzionale usato per memorizzare la query eventualmente fornita in input
    :return: e_counter, ovvero il numero dell'ultima Ei calcolata (corrisponde poi al max rank)
    """
    is_query_added = False
    query_typical_fact = None
    input_from_file.build_ontology(ontology_manager_for_racl_of_tbox)
    initialize_classes_ranks_of_typical_facts_dict(ontology_manager_for_racl_of_tbox)
    e_counter = 0
    typical_facts_exceptionality_dict = dict()
    non_exceptional_typical_facts_list = list()
    print("E" + str(e_counter))
    show_knowledge_base(ontology_manager_for_racl_of_tbox)
    non_exceptional_typical_facts = len(ontology_manager_for_racl_of_tbox.typical_facts_dict.values())
    # Il controllo che non_exceptional_typical_facts != 0 serve per evitare che il calcolo della racl inneschi un loop
    # infinito; questo succede quando tutti i fatti tipici presenti sono eccezionali e di conseguenza typical_facts_dict
    # non si svuota mai.
    while len(ontology_manager_for_racl_of_tbox.typical_facts_dict.values()) > 0 and non_exceptional_typical_facts != 0:
        for typical_fact in ontology_manager_for_racl_of_tbox.typical_facts_dict.values():
            process_exceptional_typical_fact(typical_fact, ontology_manager_for_racl_of_tbox, typical_facts_exceptionality_dict, non_exceptional_typical_facts_list, e_counter)
        if query_typical_fact_name != "":
            if is_query_added is False:
                query_typical_fact = input_from_file.add_query(ontology_manager_for_racl_of_tbox, query_typical_fact_name)
                print("QUERY AGGIUNTA: " + query_typical_fact.typical_fact_name)
                is_query_added = True
                update_classes_ranks_of_typical_facts_dict(query_typical_fact.typical_fact_name, t_class_rank=math.inf, t_class_and_not_class_rank=math.inf)
                # Ora la query è dentro typical_facts_list. Es: T(Bird),Giallo
            else:
                # Se non ricreo le classi della query, salta un errore interno di owlready
                t_class_identifier = ontology_manager_for_racl_of_tbox.create_class(query_typical_fact.t_class_identifier.name)
                class_identifier = ontology_manager_for_racl_of_tbox.create_class(query_typical_fact.class_identifier.name)
                ontology_manager_for_racl_of_tbox.add_typical_fact(t_class_identifier, class_identifier, add_to_dict=False, typical_fact_is_a_query=True)
                print("QUERY AGGIUNTA ELSE: " + query_typical_fact.typical_fact_name)
            process_query(ontology_manager_for_racl_of_tbox, non_exceptional_typical_facts_list, typical_facts_exceptionality_dict, query_typical_fact, e_counter)
        print("AGGIUNGO EVENTUALI NUOVI FATTI DELL'ABox")
        generate_possible_abox_facts_that_could_be_added_to_the_knowledge_base(ontology_manager_for_racl_of_tbox, non_exceptional_typical_facts_list, typical_facts_exceptionality_dict, e_counter)
        non_exceptional_typical_facts = len(non_exceptional_typical_facts_list)
        delete_non_exceptional_typical_facts(non_exceptional_typical_facts_list, ontology_manager_for_racl_of_tbox)
        e_counter = e_counter + 1
        if are_query_ranks_to_update(query_typical_fact_name, ontology_manager_for_racl_of_tbox, non_exceptional_typical_facts) is True:
            classes_ranks[ontology_manager_for_racl_of_tbox.query_typical_fact.t_class_identifier.name] = e_counter
            t_class_and_not_class_name = get_t_class_and_not_class_name(ontology_manager_for_racl_of_tbox.query_typical_fact)
            update_classes_ranks_of_typical_facts_dict(ontology_manager_for_racl_of_tbox.query_typical_fact.typical_fact_name,
                                                       t_class_rank=e_counter,
                                                       t_class_and_not_class_rank=classes_ranks.get(t_class_and_not_class_name))
        non_exceptional_typical_facts_list = list()
        print("E" + str(e_counter))
        show_knowledge_base(ontology_manager_for_racl_of_tbox)
    print("RANK COMPUTATI")
    print(classes_ranks_of_typical_facts_dict)
    print(classes_ranks)
    return e_counter


def process_exceptional_typical_fact(typical_fact, ontology_manager_for_racl_of_tbox, typical_facts_exceptionality_dict, non_exceptional_typical_facts_list, e_counter):
    """
    Metodo che si occupa di processare un fatto tipico eccezionale; in particolare si procede controllando se sia
    necessario ricalcolare il rank del concetto argomento dell'operatore di tipicalità. In caso affermativo si procede
    con il ricalcolo, altrimenti si procede solamente aggiornando classes_ranks_of_typical_facts_dict.
    Successivamente si controlla se sia necessario ricalcolare il rank del concetto argomento dell'operatore di
    tipicalità del fatto tipico fittizio procedendo al ricalcolo se necessario oppure aggiornando
    classes_ranks_of_typical_facts_dict.
    :param typical_fact: il fatto tipico da processare
    :param ontology_manager_for_racl_of_tbox:
    :param typical_facts_exceptionality_dict: dizionario che tiene traccia dello stato di eccezionalità dei fatti tipici
    :param non_exceptional_typical_facts_list: lista che tiene traccia dei fatti tipici che risultano essere non
    eccezionali
    :param e_counter: numero della Ei corrente
    :return:
    """
    print("FATTO TIPICO IN ESAME: " + typical_fact.typical_fact_name)
    print("CONTROLLO SE SIA NECESSARIO RICALCOLARE RANK(" + typical_fact.t_class_identifier.name + ")")
    abox_members_presents = False
    if classes_ranks.get(typical_fact.t_class_identifier.name) is None or classes_ranks.get(typical_fact.t_class_identifier.name) == math.inf:
        if typical_fact.t_class_identifier.name not in ontology_manager_for_racl_of_tbox.typical_members_dict.keys():
            compute_t_class_rank(ontology_manager_for_racl_of_tbox, typical_fact, non_exceptional_typical_facts_list, e_counter, typical_facts_exceptionality_dict)
        else:
            abox_members_presents = True
            compute_t_class_rank(ontology_manager_for_racl_of_tbox, typical_fact, non_exceptional_typical_facts_list, e_counter, typical_facts_exceptionality_dict, abox_members_presents=True)
    else:
        print("IL RANK DEL CONCETTO " + typical_fact.t_class_identifier.name + " É PARI A " + str(classes_ranks.get(typical_fact.t_class_identifier.name)) +
              " QUINDI NON LO RICALCOLO")
        non_exceptional_typical_facts_list.append(typical_fact)
        t_class_rank = classes_ranks.get(typical_fact.t_class_identifier.name)
        update_classes_ranks_of_typical_facts_dict(typical_fact.typical_fact_name, t_class_rank=t_class_rank)
    t_class_and_not_class_name = get_t_class_and_not_class_name(typical_fact)
    print("CONTROLLO SE SIA NECESSARIO RICALCOLARE RANK(" + t_class_and_not_class_name + ")")
    if classes_ranks.get(t_class_and_not_class_name) is None or classes_ranks.get(t_class_and_not_class_name) == math.inf:
        if not abox_members_presents:
            compute_t_class_and_not_class_rank(ontology_manager_for_racl_of_tbox, typical_fact, non_exceptional_typical_facts_list, e_counter, typical_facts_exceptionality_dict)
        else:
            compute_t_class_and_not_class_rank(ontology_manager_for_racl_of_tbox, typical_fact, non_exceptional_typical_facts_list, e_counter, typical_facts_exceptionality_dict, abox_members_presents=True)
    else:
        print("IL RANK DEL CONCETTO " + t_class_and_not_class_name + " É PARI A " + str(classes_ranks.get(t_class_and_not_class_name)) +
              " QUINDI NON LO RICALCOLO")
        t_class_and_not_class_rank = classes_ranks.get(t_class_and_not_class_name)
        update_classes_ranks_of_typical_facts_dict(typical_fact.typical_fact_name, t_class_and_not_class_rank=t_class_and_not_class_rank)


def process_query(ontology_manager_for_racl_of_tbox, non_exceptional_typical_facts_list, typical_facts_exceptionality_dict, query_typical_fact, e_counter):
    """
    Metodo che si occupa di processare la query fornita in input; procede sulla falsa riga del metodo
    process_exceptional_typical_fact
    :param ontology_manager_for_racl_of_tbox:
    :param non_exceptional_typical_facts_list: lista che tiene traccia dei fatti tipici che risultano essere non
    eccezionali
    :param typical_facts_exceptionality_dict: dizionario che tiene traccia dello stato di eccezionalità dei fatti tipici
    :param query_typical_fact: fatto tipico corrispondente alla query
    :param e_counter: numero della Ei corrente
    :return:
    """
    print("CONTROLLO SE SIA NECESSARIO RICALCOLARE RANK(" + ontology_manager_for_racl_of_tbox.query_typical_fact.t_class_identifier.name + ")")
    abox_members_presents = False
    # Qui controllo se il rank(Bird) sia nullo oppure se sia uguale a infinito
    if classes_ranks.get(ontology_manager_for_racl_of_tbox.query_typical_fact.t_class_identifier.name) is None or classes_ranks.get(ontology_manager_for_racl_of_tbox.query_typical_fact.t_class_identifier.name) == math.inf:
        if ontology_manager_for_racl_of_tbox.query_typical_fact.t_class_identifier.name not in ontology_manager_for_racl_of_tbox.typical_members_dict.keys():
            compute_t_class_rank(ontology_manager_for_racl_of_tbox, ontology_manager_for_racl_of_tbox.query_typical_fact, non_exceptional_typical_facts_list, e_counter, typical_facts_exceptionality_dict)
        else:
            abox_members_presents = True
            compute_t_class_rank(ontology_manager_for_racl_of_tbox, ontology_manager_for_racl_of_tbox.query_typical_fact, non_exceptional_typical_facts_list, e_counter, typical_facts_exceptionality_dict, abox_members_presents=True)
    else:
        print("IL RANK DEL CONCETTO " + ontology_manager_for_racl_of_tbox.query_typical_fact.t_class_identifier.name + " É PARI A " + str(
            classes_ranks.get(ontology_manager_for_racl_of_tbox.query_typical_fact.t_class_identifier.name)) +
              " QUINDI NON LO RICALCOLO")
        # Se entro qui vuol dire che il rank(Bird) è un valore finito, quindi aggiorno la mappa aggiungendo la
        # entry TBird_Giallo --> (rank(Bird), rank(BirdAndNot(Giallo))
        # Il rank(BirdAndNot(Giallo) lo valuto dopo, quando aggiungo il fatto fittizio
        t_class_rank = classes_ranks.get(ontology_manager_for_racl_of_tbox.query_typical_fact.t_class_identifier.name)
        update_classes_ranks_of_typical_facts_dict(query_typical_fact.typical_fact_name, t_class_rank=t_class_rank)
    # Rimuovo la query ma rimane presente in typical_facts_list
    delete_typical_fact(ontology_manager_for_racl_of_tbox, query_typical_fact.typical_fact_name)
    t_class_and_not_class_name = get_t_class_and_not_class_name(ontology_manager_for_racl_of_tbox.query_typical_fact)
    print("CONTROLLO SE SIA NECESSARIO RICALCOLARE RANK(" + t_class_and_not_class_name + ")")
    # Qui controllo se il rank(BirdAndNot(Giallo)) sia nullo oppure infinito
    if classes_ranks.get(t_class_and_not_class_name) is None or classes_ranks.get(t_class_and_not_class_name) == math.inf:
        if not abox_members_presents:
            compute_t_class_and_not_class_rank(ontology_manager_for_racl_of_tbox, ontology_manager_for_racl_of_tbox.query_typical_fact, non_exceptional_typical_facts_list, e_counter, typical_facts_exceptionality_dict)
        else:
            compute_t_class_and_not_class_rank(ontology_manager_for_racl_of_tbox, ontology_manager_for_racl_of_tbox.query_typical_fact, non_exceptional_typical_facts_list, e_counter, typical_facts_exceptionality_dict, abox_members_presents=True)
    # Il rank(BirdAndNot(Giallo)) ha un valore finito
    else:
        print("IL RANK DEL CONCETTO " + t_class_and_not_class_name + " É PARI A " + str(
            classes_ranks.get(t_class_and_not_class_name)) +
              "QUINDI NON LO RICALCOLO")
        # Aggiorno la mappa con il valore del rank(BirdAndNot(Giallo))
        t_class_and_not_class_rank = classes_ranks.get(t_class_and_not_class_name)
        update_classes_ranks_of_typical_facts_dict(query_typical_fact.typical_fact_name, t_class_and_not_class_rank=t_class_and_not_class_rank)


def are_query_ranks_to_update(query_typical_fact_name, ontology_manager_for_racl_of_tbox, non_exceptional_typical_facts):
    """
    Metodo che si occupa di controllare se sia necessario aggiornare i rank dei concetti della query; in particolare se
    esiste solo più un fatto tipico non eccezionale e la query fatta risulta ancora eccezionale nell'ultima Ei
    calcolata, allora si aggiorna il rank del concetto della query sotto l'operatore di tipicalità a e_counter in
    quanto sicuramente la query non risulterà eccezionale nella successiva Ei che si andrebbe a calcolare (infatti
    sarebbe presente solo la query come fatto tipico). In questo modo si evita di computare inutilmente un rank di
    cui si sa già il valore.
    :param query_typical_fact_name: nome del fatto tipico corrispondente alla query
    :param ontology_manager_for_racl_of_tbox:
    :param non_exceptional_typical_facts: corrisponde a len(non_exceptional_typical_facts_list)
    :return: True se è necessario aggiornare i rank, False altrimenti
    """
    if query_typical_fact_name != "" and \
                classes_ranks.get(ontology_manager_for_racl_of_tbox.query_typical_fact.t_class_identifier.name) == math.inf and \
                (len(ontology_manager_for_racl_of_tbox.typical_facts_dict.values()) == 0 or
                 (len(ontology_manager_for_racl_of_tbox.typical_facts_dict.values()) > 0 and non_exceptional_typical_facts == 0)):
        return True
    return False


def compute_t_class_rank(ontology_manager_for_racl_of_tbox, typical_fact, non_exceptional_typical_facts_list, e_counter, typical_facts_exceptionality_dict, abox_members_presents=False):
    """
    Metodo che si occupa di calcolare il rank del concetto argomento dell'operatore di tipicalità di un fatto tipico non
    fittizio; si procede controllando se nell'Abox siano presenti dei membri tipici. In caso negativo si procede
    introducendo un membro x fittizio, altrimenti si lavora direttamente con i membri tipici già presenti.
    :param ontology_manager_for_racl_of_tbox:
    :param typical_fact: fatto tipico non fittizio del concetto di cui si calcola il rank
    :param non_exceptional_typical_facts_list: lista che tiene traccia dei fatti tipici che risultano essere non
    eccezionali
    :param e_counter: numero della Ei corrente
    :param typical_facts_exceptionality_dict: dizionario che tiene traccia dello stato di eccezionalità dei fatti tipici
    :param abox_members_presents: booleano che indica se sono presenti o meno dei membri nell'Abox indicati come tipici
    :return:
    """
    print("KB PRIMA DI AGGIUNGERE IL MEMBRO FITTIZIO x")
    show_knowledge_base(ontology_manager_for_racl_of_tbox)
    # aggiungo il membro x
    if not abox_members_presents:
        add_member_to_knowledge_base_class(ontology_manager_for_racl_of_tbox, typical_fact)
    else:
        # Il metodo copy() per copiare il dizionario non funziona come dovrebbe,
        # quindi devo procedere alla vecchia maniera
        temp_typical_members_dict = copy_dict(ontology_manager_for_racl_of_tbox.typical_members_dict)
        for t_class_identifier_name in temp_typical_members_dict.keys():
            for typical_member_as_list in temp_typical_members_dict.get(t_class_identifier_name):
                add_member_to_knowledge_base_class(ontology_manager_for_racl_of_tbox, typical_fact, member_identifier_name=typical_member_as_list[3])
    print("KB DOPO AVER AGGIUNTO IL MEMBRO FITTIZIO x")
    show_knowledge_base(ontology_manager_for_racl_of_tbox)
    print("CONTROLLO SE IL FATTO TIPICO É ECCEZIONALE O NO")
    # controllo se il fatto tipico è eccezionale o no
    check_whether_the_typical_fact_is_exceptional_or_not(ontology_manager_for_racl_of_tbox, typical_fact,
                                                         non_exceptional_typical_facts_list, e_counter,
                                                         typical_facts_exceptionality_dict)
    delete_member_x_or_remove_classes_from_actual_members(abox_members_presents, ontology_manager_for_racl_of_tbox)


def compute_t_class_and_not_class_rank(ontology_manager_for_racl_of_tbox, typical_fact, non_exceptional_typical_facts_list, e_counter, typical_facts_exceptionality_dict, abox_members_presents=False):
    """
    Metodo che si occupa di calcolare il rank del concetto argomento dell'operatore di tipicalità di un fatto tipico
    fittizio; si procede controllando se nell'Abox siano presenti dei membri tipici. In caso negativo si procede
    introducendo un membro x fittizio, altrimenti si lavora direttamente con i membri tipici già presenti.
    :param ontology_manager_for_racl_of_tbox:
    :param typical_fact: fatto tipico non fittizio da cui si ricava il concetto argomento dell'operatore di tipicalità
    del fatto tipico fittizio
    :param non_exceptional_typical_facts_list: lista che tiene traccia dei fatti tipici che risultano essere non
    eccezionali
    :param e_counter: numero della Ei corrente
    :param typical_facts_exceptionality_dict: dizionario che tiene traccia dello stato di eccezionalità dei fatti tipici
    :param abox_members_presents: booleano che indica se sono presenti o meno dei membri nell'Abox indicati come tipici
    :return:
    """
    print("KB PRIMA DI AGGIUNGERE IL MEMBRO FITTIZIO x")
    show_knowledge_base(ontology_manager_for_racl_of_tbox)
    # Aggiungo il fatto t_class_and_not_class (sarebbe la def 22 a pagina 19)
    add_t_class_and_not_class_fact(ontology_manager_for_racl_of_tbox, typical_fact)
    # Aggiungo membro x come membro di t_class_and_not_class (Es: BirdAndNot(Fly));
    # internamente creo anche il fatto tipico con la classe fittizia c
    t_class_and_not_class_identifier = None
    c_class_identifier = None
    if not abox_members_presents:
        t_class_and_not_class_identifier, _, c_class_identifier = add_member_to_temporary_class(ontology_manager_for_racl_of_tbox, typical_fact)
        t_class_and_not_class_fact = ontology_manager_for_racl_of_tbox.typical_facts_support_dict.get("T" + t_class_and_not_class_identifier.name + "_" + c_class_identifier.name)
        add_member_to_knowledge_base_class(ontology_manager_for_racl_of_tbox, t_class_and_not_class_fact)
    else:
        temp_typical_members_dict = copy_dict(ontology_manager_for_racl_of_tbox.typical_members_dict)
        for t_class_identifier_name in temp_typical_members_dict.keys():
            for typical_member_as_list in temp_typical_members_dict.get(t_class_identifier_name):
                t_class_and_not_class_identifier, _, c_class_identifier = add_member_to_temporary_class(ontology_manager_for_racl_of_tbox, typical_fact, member_identifier_name=typical_member_as_list[3])
                t_class_and_not_class_fact = ontology_manager_for_racl_of_tbox.typical_facts_support_dict.get("T" + t_class_and_not_class_identifier.name + "_" + c_class_identifier.name)
                add_member_to_knowledge_base_class(ontology_manager_for_racl_of_tbox, t_class_and_not_class_fact, member_identifier_name=typical_member_as_list[3])
    print("KB DOPO AVER AGGIUNTO IL MEMBRO FITTIZIO x")
    show_knowledge_base(ontology_manager_for_racl_of_tbox)
    print("CONTROLLO SE IL FATTO TIPICO É ECCEZIONALE O NO")
    # controllo l'eccezionalità del membro x appartenente a t_class_and_not_class
    check_whether_the_typical_fact_is_exceptional_or_not(ontology_manager_for_racl_of_tbox, typical_fact, non_exceptional_typical_facts_list, e_counter, typical_facts_exceptionality_dict, temp_typical_fact_present=True)
    # Sono andato a creare un fatto tipico fittizio della forma T(C and Not(D)) < classe_fittizia per andare
    # a vedere se il membro x è un tipico top C and Not(D); questo fatto tipico però è solo funzionale a
    # tale scopo, quindi lo elimino dopo che non mi serve più; inolte elimino pure il membro x
    delete_member_x_or_remove_classes_from_actual_members(abox_members_presents, ontology_manager_for_racl_of_tbox)
    delete_typical_fact(ontology_manager_for_racl_of_tbox, "T" + t_class_and_not_class_identifier.name + "_" + c_class_identifier.name)


def delete_member_x_or_remove_classes_from_actual_members(abox_members_presents, ontology_manager_for_racl_of_tbox):
    """
    Metodo che, a seconda del fatto che la KB abbia o no membri nell'Abox, va ad eliminare il membro fittizio x oppure a
    rimuovere le classi a cui appartengono i membri tipici aggiunti che però non costituiscono una informazione
    persistente. (Es: tutti quei membri assunti come tipici per via della query)
    :param abox_members_presents: booleano che indica se sono presenti o meno dei membri nell'Abox indicati come tipici
    :param ontology_manager_for_racl_of_tbox:
    :return:
    """
    if not abox_members_presents:
        delete_member_x(ontology_manager_for_racl_of_tbox)
    else:
        for t_class_identifier_name in ontology_manager_for_racl_of_tbox.typical_members_dict.keys():
            for typical_member in ontology_manager_for_racl_of_tbox.typical_members_dict.get(t_class_identifier_name):
                if typical_member.remove_from_knowledge_base:
                    abox_member_found = next((abox_member for abox_member in ontology_manager_for_racl_of_tbox.a_box_members_list
                                              if abox_member.member_name == typical_member.member_name and
                                              abox_member.class_identifier.name == typical_member.t_class_identifier.name), None)
                    # Se il membro tipico non è presente in fatti del tipo opus;Fly (es di info persistente) allora
                    # posso anche rimuovere t_class_identifier
                    if abox_member_found is None:
                        if ontology_manager_for_racl_of_tbox.get_class(typical_member.t_class_identifier.name) in ontology_manager_for_racl_of_tbox.get_member(typical_member.member_name).is_a:
                            ontology_manager_for_racl_of_tbox.get_member(typical_member.member_name).is_a.remove(ontology_manager_for_racl_of_tbox.get_class(typical_member.t_class_identifier.name))
                    if ontology_manager_for_racl_of_tbox.get_class(typical_member.t_class_identifier_1.name) in ontology_manager_for_racl_of_tbox.get_member(typical_member.member_name).is_a:
                        ontology_manager_for_racl_of_tbox.get_member(typical_member.member_name).is_a.remove(ontology_manager_for_racl_of_tbox.get_class(typical_member.t_class_identifier_1.name))
                    if ontology_manager_for_racl_of_tbox.get_class(typical_member.t_class_intersection.name) in ontology_manager_for_racl_of_tbox.get_member(typical_member.member_name).is_a:
                        ontology_manager_for_racl_of_tbox.get_member(typical_member.member_name).is_a.remove(ontology_manager_for_racl_of_tbox.get_class(typical_member.t_class_intersection.name))


def copy_dict(typical_members_dict_to_copy):
    """
    Metodo che si occupa di copiare il dizionario di membri tipici fornito in input in un nuovo dizionario in cui
    ciascuna coppia è costituita da t_class_identifier_name --> array contenente i campi dell'oggetto typical_member.
    :param typical_members_dict_to_copy: il dizionario di membri tipici da copiare
    :return: copied_typical_members_dict, ovvero la copia formata da coppie
    t_class_identifier_name --> array contenente i campi dell'oggetto typical_member.
    """
    copied_typical_members_dict = dict()
    for t_class_identifier_name, typical_members_list in typical_members_dict_to_copy.items():
        values = list()
        for typical_member in typical_members_list:
            if typical_member.remove_from_knowledge_base is False:
                values.append([typical_member.t_class_identifier.name, typical_member.t_class_identifier_1.name,
                               typical_member.t_class_intersection.name, typical_member.member_name,
                               typical_member.probability, typical_member.key, typical_member.remove_from_knowledge_base])
        copied_typical_members_dict[t_class_identifier_name] = values
    return copied_typical_members_dict


def perform_compute_rational_closure_of_tbox(ontology_manager_for_racl_of_tbox):
    """
    Metodo che si occupa di stabilire quali fatti tipici fanno parte della chiusura razionale della Tbox. Viene seguita
    la definizione illustrata nell'articolo a pagina 22.
    :param ontology_manager_for_racl_of_tbox:
    :return: rational_closure_of_tbox_list, ovvero una lista contenente i fatti tipici che fanno parte della chiusura
    razionale della Tbox.
    """
    rational_closure_of_tbox_list = list()
    for typical_fact_name in classes_ranks_of_typical_facts_dict.keys():
        t_class_identifier_name = typical_fact_name.split("_")[0].replace("?", "").replace("T", "", 1)
        if ontology_manager_for_racl_of_tbox.get_class(t_class_identifier_name) is not None:
            members_list = ontology_manager_for_racl_of_tbox.get_members(ontology_manager_for_racl_of_tbox.get_class(t_class_identifier_name), return_as_list=True)
            if len(members_list) == 0:
                if classes_ranks_of_typical_facts_dict.get(typical_fact_name)[0] < classes_ranks_of_typical_facts_dict.get(typical_fact_name)[1] or classes_ranks_of_typical_facts_dict.get(typical_fact_name)[0] == math.inf:
                    rational_closure_of_tbox_list.append(typical_fact_name)
                    print(typical_fact_name)
            else:
                if classes_ranks_of_typical_facts_dict.get(typical_fact_name)[0] < classes_ranks_of_typical_facts_dict.get(typical_fact_name)[1]:
                    rational_closure_of_tbox_list.append(typical_fact_name)
                    print(typical_fact_name)
        else:
            if classes_ranks_of_typical_facts_dict.get(typical_fact_name)[0] < classes_ranks_of_typical_facts_dict.get(typical_fact_name)[1] or classes_ranks_of_typical_facts_dict.get(typical_fact_name)[0] == math.inf:
                rational_closure_of_tbox_list.append(typical_fact_name)
                print(typical_fact_name)
    ontology_manager_for_racl_of_tbox.show_strict_facts()
    return rational_closure_of_tbox_list


def add_member_to_knowledge_base_class(ontology_manager, typical_fact, member_identifier_name="x"):
    """
    Metodo che si occupa di aggiungere un membro (fittizio o non fittizio) come tipico di una classe della base di
    conoscenza.
    :param ontology_manager: a seconda di quale sia il chiamante di questo metodo, può essere quello usato per
    calcolare la chiusura razionale della tbox (ontology_manager_for_racl_of_tbox) oppure quello usato nel modulo
    query_ontology.py
    :param typical_fact: fatto tipico da cui si ricavano le classi necessarie per impostare come tipico il membro in
    questione
    :param member_identifier_name: nome del membro; se è uguale a "x" allora è il membro fittizio, altrimenti è un
    membro non fittizio
    :return:
    """
    perform_add_member_to_knowledge_base_class(ontology_manager, typical_fact, member_identifier_name)
    add_member_to_knowledge_base_superclasses(ontology_manager, typical_fact, member_identifier_name)
    if ":And:" in typical_fact.typical_fact_name.split("_")[0]:
        add_member_to_knowledge_base_and_classes(ontology_manager, typical_fact, member_identifier_name)


def perform_add_member_to_knowledge_base_class(ontology_manager, typical_fact, member_identifier_name):
    """
    Metodo che effettivamente aggiunge il membro (fittizio o non fittizio) come tipico di una classe della base di
    conoscenza.
    :param ontology_manager:
    :param typical_fact: fatto tipico da cui si ricavano le classi necessarie per impostare come tipico il membro in
    questione
    :param member_identifier_name: nome del membro che si vuole aggiungere come tipico
    :return:
    """
    if member_identifier_name != "x":
        ontology_manager.set_as_typical_member(member_identifier_name, typical_fact.t_class_identifier,
                                               ontology_manager.get_class(typical_fact.t_class_identifier.name + "1"), remove_from_knowledge_base=True)
    else:
        ontology_manager.set_as_typical_member("x", typical_fact.t_class_identifier,
                                               ontology_manager.get_class(typical_fact.t_class_identifier.name + "1"))


def add_member_to_knowledge_base_and_classes(ontology_manager, typical_fact, member_identifier_name):
    """
    Quando si passa in input una query del tipo Typical(And(Bird_Black)),Fly e si vuole verificare che la base di
    conoscenza sia consistente o no, bisogna procedere con l'aggiunta del membro.
    Questo metodo serve a far si che il membro venga aggiunto come tipico anche per le classi che compongono la
    classe BirdAndBlack; in particolare si va a controllare se esistano come fatti tipici (in questo esempio)
    Typical(Bird),C e Typical(Black),D dove C e D sono classi presenti nella base di conoscenza e rappresentano un
    possibile concetto (es: Fly oppure Not(Fly)). Se anche solo uno di essi è presente, allora il membro viene
    aggiunto come membro tipico di quella classe per cui il fatto tipico è presente.
    :param ontology_manager:
    :param typical_fact: fatto tipico da cui si ricavano le classi necessarie per impostare come tipico il membro in
    questione
    :param member_identifier_name: nome del membro che si vuole aggiungere come tipico
    :return:
    """
    if not typical_fact.typical_fact_is_a_query:
        and_t_classes_identifiers_names = typical_fact.typical_fact_name.split("_")[0].replace("T", "", 1).split(":And:")
    else:
        and_t_classes_identifiers_names = typical_fact.typical_fact_name.split("_")[0].replace("?T", "").split(":And:")
    for and_t_class_identifier_name in and_t_classes_identifiers_names:
        typical_facts = [typical_fact for (typical_fact_name, typical_fact) in ontology_manager.typical_facts_dict.items() if and_t_class_identifier_name == typical_fact_name.split("_")[0].replace("T", "", 1)]
        for typical_fact in typical_facts:
            if typical_fact is not None and ":And:" not in typical_fact.typical_fact_name.split("_")[0]:
                perform_add_member_to_knowledge_base_class(ontology_manager, typical_fact, member_identifier_name)
                add_member_to_knowledge_base_superclasses(ontology_manager, typical_fact, member_identifier_name)


def add_member_to_knowledge_base_superclasses(ontology_manager_for_racl_of_tbox, typical_fact, member_identifier_name):
    """
    Questo metodo si occupa di controllare se esistano delle superclassi per le quali il membro debba essere aggiunto
    come tipico top di quelle superclassi. Es: Penguin<Bird, Bird è una superclasse e quindi il membro sarà anche tipico
    top Bird oltre ad essere tipico top Penguin.
    :param ontology_manager_for_racl_of_tbox:
    :param typical_fact: fatto tipico da cui si ricavano le superclassi della classe argomento dell'operatore di
    tipicalità
    :param member_identifier_name: nome del membro che si vuole aggiungere come tipico
    :return:
    """
    for superclass in ontology_manager_for_racl_of_tbox.get_super_classes(typical_fact.t_class_identifier, exclude_owl_thing=True):
        if ontology_manager_for_racl_of_tbox.is_class_present(superclass.name + "1"):
            typical_fact_name_found = next((typical_fact_name for typical_fact_name in ontology_manager_for_racl_of_tbox.typical_facts_dict.keys()
                                            if superclass.name == typical_fact_name.split("_")[0].replace("T", "", 1)), None)
            # Se la superclasse è dentro l'operatore T di qualche fatto tipico della kb, allora procedo con l'assumere
            # il membro come tipico top and superclass.name
            if typical_fact_name_found is not None:
                if member_identifier_name != "x":
                    ontology_manager_for_racl_of_tbox.set_as_typical_member(member_identifier_name, superclass,
                                                                            ontology_manager_for_racl_of_tbox.onto[superclass.name + "1"], remove_from_knowledge_base=True)
                else:
                    ontology_manager_for_racl_of_tbox.set_as_typical_member("x", superclass,
                                                                            ontology_manager_for_racl_of_tbox.onto[superclass.name + "1"])
        else:
            typical_fact_name_found = next((typical_fact_name for typical_fact_name in ontology_manager_for_racl_of_tbox.typical_facts_dict.keys()
                                            if superclass.name == typical_fact_name.split("_")[0].replace("T", "", 1)), None)
            # Se la superclasse è dentro l'operatore T di qualche fatto tipico della kb, allora procedo con l'assumere
            # il membro come tipico top and superclass.name
            if typical_fact_name_found is not None:
                t_class_identifier_1 = ontology_manager_for_racl_of_tbox.create_class(superclass.name + "1")
                t_class_intersection = ontology_manager_for_racl_of_tbox.create_t_class_intersection(superclass,
                                                                                                     t_class_identifier_1)
                if member_identifier_name != "x":
                    ontology_manager_for_racl_of_tbox.set_as_typical_member(member_identifier_name, superclass,
                                                                            t_class_identifier_1, remove_from_knowledge_base=True)
                else:
                    ontology_manager_for_racl_of_tbox.set_as_typical_member("x", superclass, t_class_identifier_1)
                    member_x_classes_names_created_list.extend([t_class_identifier_1.name, t_class_intersection.name])


def add_member_to_temporary_class(ontology_manager_for_racl_of_tbox, typical_fact, member_identifier_name="x"):
    """
    Metodo che si occupa di aggiungere il membro come tipico di una classe non fittizia. Es: Bird and Not(Fly); per dire
    che è un tipico Bird and Not(Fly), si crea un fatto tipico farlocco con una classe fittizia c. Il reasoner poi
    verificherà se la kb sarà consistente o meno concludendo quindi che sia o no corretto assumere il membro come tipico
    Bird and Not(Fly). A seconda del risultato si ricava quindi il rank del concetto C and Not(D).
    :param ontology_manager_for_racl_of_tbox:
    :param typical_fact: fatto tipico da cui si ricava la classe t_class_and_not_class a cui il membro viene aggiunto
    come tipico; è una classe non fittizia ma temporanea perchè viene creata internamente dal reasoner per poter
    calcolare la chiusura razionale
    :param member_identifier_name: nome del membro; se è uguale a "x" allora è il membro fittizio, altrimenti è un
    membro non fittizio
    :return: t_class_and_not_class_identifier, ovvero l'identificatore della classe t_class_and_not_class;
    t_class_and_not_class_identifier1, ovvero l'identificatore della classe t_class_and_not_class1;
    c_class_identifier, ovvero l'identificatore della classe c
    """
    if typical_fact.class_identifier.name.startswith("Not("):
        # caso del concetto T(Penguin)_Not(Fly), quindi cerco PenguinAndFly
        t_class_and_not_class_identifier = ontology_manager_for_racl_of_tbox.get_class(typical_fact.t_class_identifier.name + ":And:" + typical_fact.class_identifier.name.replace("Not(", "").replace(")", ""))
    else:  # caso del concetto T(Bird)_Fly, quindi cerco il concetto BirdAndNot(Fly)
        t_class_and_not_class_identifier = ontology_manager_for_racl_of_tbox.get_class(typical_fact.t_class_identifier.name + ":And:Not(" + typical_fact.class_identifier.name + ")")
    c_class_identifier = ontology_manager_for_racl_of_tbox.create_class("c")
    ontology_manager_for_racl_of_tbox.add_typical_fact(t_class_and_not_class_identifier, c_class_identifier, add_to_dict=False)
    t_class_and_not_class_identifier1 = ontology_manager_for_racl_of_tbox.get_class(t_class_and_not_class_identifier.name + "1")
    # OntologyManager.set_as_typical_member(ontology_manager_for_racl_of_tbox, "x", t_class_and_not_class_identifier,
    # t_class_and_not_class_identifier1)
    if member_identifier_name == "x":
        ontology_manager_for_racl_of_tbox.set_as_typical_member(member_identifier_name, t_class_and_not_class_identifier, t_class_and_not_class_identifier1)
    else:
        pass
        # ontology_manager_for_racl_of_tbox.set_as_typical_member(member_identifier_name,
        # t_class_and_not_class_identifier, t_class_and_not_class_identifier1, remove_from_knowledge_base=True)
    return t_class_and_not_class_identifier, t_class_and_not_class_identifier1, c_class_identifier


def delete_member_x(ontology_manager_for_racl_of_tbox):
    """
    Metodo che si occupa dell'eliminazione del membro x dalla base di conoscenza.
    :param ontology_manager_for_racl_of_tbox:
    :return:
    """
    member_x_identifier = ontology_manager_for_racl_of_tbox.get_member("x")
    ontology_manager_for_racl_of_tbox.destroy_specific_entity(member_x_identifier)


def add_t_class_and_not_class_fact(ontology_manager_for_racl_of_tbox, typical_fact):
    """
    Metodo che si occupa dell'aggiunta della classe t_class_and_not_class nella base di conoscenza.
    :param ontology_manager_for_racl_of_tbox:
    :param typical_fact: fatto tipico da cui si ricavano le classi necessarie per poter creare ed aggiungere
    t_class_and_not_class
    :return:
    """
    # La classe non inizia per Not. Es: T(Bird) < Fly
    if not typical_fact.class_identifier.name.startswith("Not("):
        # Controllo che la complementare di Fly, ovvero Not(Fly), sia presente
        if ontology_manager_for_racl_of_tbox.is_class_present("Not(" + typical_fact.class_identifier.name + ")"):
            # ottengo classe Not(Fly)
            not_class_identifier = ontology_manager_for_racl_of_tbox.get_class("Not(" + typical_fact.class_identifier.name + ")")
        else:  # Non è presente la sua complementare, quindi la creo
            # ottengo la classe Fly, se presente, per poi crearne la complementare
            if ontology_manager_for_racl_of_tbox.get_class(typical_fact.class_identifier.name) is not None:
                class_identifier = ontology_manager_for_racl_of_tbox.get_class(typical_fact.class_identifier.name)
            # creo la classe Fly per poi crearne la complementare
            else:
                class_identifier = ontology_manager_for_racl_of_tbox.create_class(typical_fact.class_identifier.name)
                class_identifier.equivalent_to = typical_fact.class_identifier.equivalent_to
                class_identifier.is_a = typical_fact.class_identifier.is_a
            not_class_identifier = ontology_manager_for_racl_of_tbox.create_class("Not(" + typical_fact.class_identifier.name + ")")
            not_class_identifier.equivalent_to = [ontology_manager_for_racl_of_tbox.create_complementary_class(class_identifier)]
        # creo classe BirdAndNot(Fly)
        t_class_and_not_class_identifier = ontology_manager_for_racl_of_tbox.create_class(typical_fact.t_class_identifier.name + ":And:Not(" + typical_fact.class_identifier.name + ")")
        # ottengo classe Bird
        if ontology_manager_for_racl_of_tbox.get_class(typical_fact.t_class_identifier.name) is not None:
            t_class_identifier = ontology_manager_for_racl_of_tbox.get_class(typical_fact.t_class_identifier.name)
            t_class_and_not_class_identifier.equivalent_to = [t_class_identifier & not_class_identifier]
        # la classe Bird non c'è, quindi la creo per poter impostare t_class_and_not_class_identifier
        else:
            t_class_identifier = ontology_manager_for_racl_of_tbox.create_class(typical_fact.t_class_identifier.name)
            t_class_identifier.is_a = typical_fact.t_class_identifier.is_a
            t_class_identifier.equivalent_to = typical_fact.t_class_identifier.equivalent_to
            t_class_and_not_class_identifier.equivalent_to = [t_class_identifier & not_class_identifier]
        t_class_and_not_class_identifier.comment.append(math.inf)
    else:  # La classe inizia per Not Es: T(Penguin) < Not(Fly)
        # Controllo che la complementare di Not(Fly), ovvero Fly, sia presente
        if ontology_manager_for_racl_of_tbox.is_class_present(typical_fact.class_identifier.name.replace("Not(", "").replace(")", "")):
            # ottengo la classe Fly
            not_class_identifier = ontology_manager_for_racl_of_tbox.get_class(typical_fact.class_identifier.name.replace("Not(", "").replace(")", ""))
        else:  # Non è presente la sua complementare, quindi la creo
            # ottengo la classe Not(Fly) per poi crearne la sua complementare
            class_identifier = ontology_manager_for_racl_of_tbox.get_class(typical_fact.class_identifier.name)
            not_class_identifier = ontology_manager_for_racl_of_tbox.create_class(typical_fact.class_identifier.name.replace("Not(", "").replace(")", ""))
            not_class_identifier.equivalent_to = [ontology_manager_for_racl_of_tbox.create_complementary_class(class_identifier)]
        # creo classe PenguinAndFly
        t_class_and_not_class_identifier = ontology_manager_for_racl_of_tbox.create_class(typical_fact.t_class_identifier.name + ":And:" + typical_fact.class_identifier.name.replace("Not(", "").replace(")", ""))
        # ottengo classe Penguin
        if ontology_manager_for_racl_of_tbox.get_class(typical_fact.t_class_identifier.name) is not None:
            t_class_identifier = ontology_manager_for_racl_of_tbox.get_class(typical_fact.t_class_identifier.name)
            t_class_and_not_class_identifier.equivalent_to = [t_class_identifier & not_class_identifier]
        # la classe Penguin non c'è, quindi la creo per poter impostare t_class_and_not_class_identifier
        else:
            t_class_identifier = ontology_manager_for_racl_of_tbox.create_class(typical_fact.t_class_identifier.name)
            t_class_identifier.is_a = typical_fact.t_class_identifier.is_a
            t_class_identifier.equivalent_to = typical_fact.t_class_identifier.equivalent_to
            t_class_and_not_class_identifier.equivalent_to = [t_class_identifier & not_class_identifier]
        t_class_and_not_class_identifier.comment.append(math.inf)


def delete_non_exceptional_typical_facts(non_exceptional_typical_facts_list, ontology_manager_for_racl_of_tbox):
    """
    Metodo che si occupa della cancellazione dei fatti tipici che risultano essere non eccezionali; il procedimento
    prevede di ciclare su non_exceptional_typical_facts_list eliminando ogni fatto tipico. Successivamente si ricercano
    tutte le classi che dopo la cancellazione di tali fatti, risultano inutili.
    :param non_exceptional_typical_facts_list: lista dei fatti tipici non eccezionali
    :param ontology_manager_for_racl_of_tbox:
    :return:
    """
    for typical_fact in non_exceptional_typical_facts_list:
        delete_typical_fact(ontology_manager_for_racl_of_tbox, typical_fact.typical_fact_name)
        ontology_manager_for_racl_of_tbox.typical_facts_dict.pop(typical_fact.typical_fact_name)
    print("DOPO RIMOZIONE FATTO TIPICO NON ECCEZIONALE")
    ontology_manager_for_racl_of_tbox_classes = ontology_manager_for_racl_of_tbox.get_classes(return_as_list=True)
    # Normalmente questa lista è vuota perchè queste classi le cancello prima
    print("Classi create per aggiungerci il membro x ad esse")
    print(member_x_classes_names_created_list)
    print("Classi presenti in totale")
    print(ontology_manager_for_racl_of_tbox_classes)
    print("CLASSI ", list(ontology_manager_for_racl_of_tbox_classes))
    # Dopo aver eliminato i fatti tipici non eccezionali, potrebbero esserci ancora delle classi che non servono più,
    # di conseguenza ciclo sulle classi alla ricerca di classi inutili. In particolare queste classi o vengono
    # proprio distrutte o vengono rimosse da un certo membro dell'abox.
    for class_identifier in ontology_manager_for_racl_of_tbox_classes:
        # Caso in cui la classe corrisponde alla t_class_identifier della query
        if ontology_manager_for_racl_of_tbox.query_typical_fact is not None and class_identifier.name == ontology_manager_for_racl_of_tbox.query_typical_fact.t_class_identifier.name:
            typical_member_found = None
            # Se trovo un membro tipico che ha come classe class_identifier allora cerco il membro tipico
            if class_identifier.name in ontology_manager_for_racl_of_tbox.typical_members_dict.keys():
                typical_member_found = next((typical_member for typical_member in ontology_manager_for_racl_of_tbox.typical_members_dict.get(class_identifier.name)
                                             if typical_member.t_class_identifier.name == class_identifier.name and
                                             typical_member.remove_from_knowledge_base is False), None)
            # Cerco se esiste un fatto tipico che presenta class_identifier come sopraclasse del fatto stesso
            typical_fact_found = next((typical_fact_name for typical_fact_name in ontology_manager_for_racl_of_tbox.typical_facts_dict.keys()
                                       if typical_fact_name.split("_")[1] == class_identifier.name), None)
            # Cerco se esiste un fatto del tipo member_name;class_identifier
            abox_member_found = next((abox_member for abox_member in ontology_manager_for_racl_of_tbox.a_box_members_list
                                      if abox_member.class_identifier.name == class_identifier.name), None)
            # Il controllo sul fatto che la classe abbia o meno superclassi e/o sottoclassi serve perchè nel caso in cui
            # si abbia Penguin is_a Bird, T(Bird),Fly e ?T(Bird),Giallo, verrebbe cancellata la classe Bird perdendo
            # così l'informazione Penguin is_a Bird (rimarrebbe infatti solo che Penguin is_a owl.Thing)
            if typical_member_found == typical_fact_found == abox_member_found is None and \
                    len(ontology_manager_for_racl_of_tbox.get_sub_classes(class_identifier, exclude_self_and_owl_thing=True)) == 0 and \
                    len(ontology_manager_for_racl_of_tbox.get_super_classes(class_identifier, exclude_owl_thing=True)) == 0:
                ontology_manager_for_racl_of_tbox.destroy_specific_entity(class_identifier)
        # Caso in cui la classe non corrisponde alla t_class_identifier della query
        elif is_class_to_destroy(class_identifier, ontology_manager_for_racl_of_tbox) is True:
            ontology_manager_for_racl_of_tbox.destroy_specific_entity(class_identifier)
    show_knowledge_base(ontology_manager_for_racl_of_tbox)


def is_class_to_destroy(class_identifier, ontology_manager_for_racl_of_tbox):
    """
    Metodo che si occupa di stabilire se una classe è da eliminare dalla base di conoscenza oppure no; i casi in cui è
    possibile eliminare la classe sono 2:
    - la classe è una di quelle create per il membro x
    - la classe non presenta restrizioni tra le sue superclassi, non ha superclassi, non ha sottoclassi e non ha membri.
    :param class_identifier: identificatore della classe in esame
    :param ontology_manager_for_racl_of_tbox:
    :return: True, se la classe è da eliminare; False altrimenti
    """
    if class_identifier.name in member_x_classes_names_created_list or \
        (not any(isinstance(super_class, Restriction) for super_class in class_identifier.is_a) and
         len(ontology_manager_for_racl_of_tbox.get_sub_classes(class_identifier, exclude_self_and_owl_thing=True)) == 0
         and len(ontology_manager_for_racl_of_tbox.get_super_classes(class_identifier, exclude_owl_thing=True)) == 0 and
         not ontology_manager_for_racl_of_tbox.has_members(class_identifier)):
        return True
    return False


def delete_typical_fact(ontology_manager_for_racl_of_tbox, typical_fact_name):
    """
    Metodo che si occupa dell'eliminazione di un fatto tipico (può essere il fatto tipico della query).
    :param ontology_manager_for_racl_of_tbox:
    :param typical_fact_name: nome del fatto tipico da eliminare
    :return:
    """
    # Caso in cui il fatto tipico da cancellare è la query
    if "?" in typical_fact_name.split("_")[0]:
        perform_delete_query_typical_fact(ontology_manager_for_racl_of_tbox, typical_fact_name)
    # Caso in cui il fatto tipico da eliminare non è la query
    elif "?" not in typical_fact_name.split("_")[0]:
        perform_delete_typical_fact(ontology_manager_for_racl_of_tbox, typical_fact_name)


def perform_delete_query_typical_fact(ontology_manager_for_racl_of_tbox, typical_fact_name):
    """
    Metodo che effettivamente elimina il fatto tipico della query; il procedimento è il seguente:
    - se è presente almeno un fatto tipico nella Ei corrente con la stessa classe nell'operatore T non è possibile
    cancellare di netto l'intera query ma si elimina solo la caratteristica tipica della query. Es: se T(Bird),Giallo è la query e
    nella Ei ho T(Bird),Fly allora si elimina solo Giallo
    - è solo presente la query; se non ci sono membri tipici nella base di conoscenza allora si elimina tutto,
    altrimenti esiste almeno un membro tipico nella base di conoscenza e quindi dato che quell'informazione è
    persistente, si elimina solo not_t_class_identifier_1 in quanto le altre classi contribuiscono a definire
    il membro tipico.
    :param ontology_manager_for_racl_of_tbox:
    :param typical_fact_name: nome del fatto tipico della query
    :return:
    """
    typical_fact_object = ontology_manager_for_racl_of_tbox.typical_facts_support_dict.get(typical_fact_name)
    t_class_identifier = typical_fact_object.t_class_identifier
    typical_facts = [typical_fact for (typical_fact_name, typical_fact) in ontology_manager_for_racl_of_tbox.typical_facts_dict.items() if t_class_identifier.name == typical_fact_name.split("_")[0].replace("T", "", 1)]
    # Se è presente almeno 1 fatto tipico nella Ei corrente con la stessa classe nell'operatore T
    # non posso cancellare di netto l'intera query ma elimino solo la caratteristica tipica della query.
    # Es: se T(Bird),Giallo è la query e nella Ei ho T(Bird),Fly allora elimino solo Giallo
    if len(typical_facts) > 0:
        t_class_identifier_1 = ontology_manager_for_racl_of_tbox.get_class(t_class_identifier.name + "1")
        t_class_intersection = ontology_manager_for_racl_of_tbox.get_class("Intersection(" + typical_fact_object.t_class_identifier.name + t_class_identifier_1.name + ")")
        t_class_intersection.is_a.remove(typical_fact_object.class_identifier)
    # É solo presente la query
    else:
        typical_member_found = None
        if typical_fact_object.t_class_identifier.name in ontology_manager_for_racl_of_tbox.typical_members_dict.keys():
            typical_member_found = next((typical_member for typical_member in ontology_manager_for_racl_of_tbox.typical_members_dict.get(typical_fact_object.t_class_identifier.name)
                                         if typical_member.t_class_identifier.name == typical_fact_object.t_class_identifier.name and
                                         typical_member.remove_from_knowledge_base is False), None)
        # Se non ci sono membri tipici nella base di conoscenza, elimino tutto
        if typical_member_found is None:
            t_class_identifier_1 = ontology_manager_for_racl_of_tbox.get_class(t_class_identifier.name + "1")
            if t_class_identifier_1 is not None:
                not_t_class_identifier_1 = ontology_manager_for_racl_of_tbox.get_class("Not(" + t_class_identifier_1.name + ")")
                t_class_intersection = ontology_manager_for_racl_of_tbox.get_class("Intersection(" + typical_fact_object.t_class_identifier.name + t_class_identifier_1.name + ")")
                ontology_manager_for_racl_of_tbox.destroy_specific_entity(t_class_identifier_1)
                ontology_manager_for_racl_of_tbox.destroy_specific_entity(not_t_class_identifier_1)
                if len(ontology_manager_for_racl_of_tbox.get_super_classes(t_class_identifier, exclude_owl_thing=True)) == 0 and \
                        len(ontology_manager_for_racl_of_tbox.get_sub_classes(t_class_identifier, exclude_self_and_owl_thing=True)) == 0:
                    ontology_manager_for_racl_of_tbox.destroy_specific_entity(t_class_identifier)
                # In questo caso t_class_intersection la distruggo sempre perchè è presente solo la query
                ontology_manager_for_racl_of_tbox.destroy_specific_entity(t_class_intersection)
        # Esiste almeno un membro tipico nella base di conoscenza, quindi dato che quell'informazione è
        # persistente, elimino solo not_t_class_identifier_1 in quanto le altre classi contribuiscono a definire
        # il membro tipico.
        else:
            t_class_identifier_1 = ontology_manager_for_racl_of_tbox.get_class(t_class_identifier.name + "1")
            if t_class_identifier_1 is not None:
                delete_not_t_class_identifier_1(ontology_manager_for_racl_of_tbox, t_class_identifier_1, typical_fact_object)
        typical_fact_found = next((typical_fact_name for typical_fact_name in ontology_manager_for_racl_of_tbox.typical_facts_dict.keys()
                                   if typical_fact_name.split("_")[1] == typical_fact_object.class_identifier.name), None)
        abox_member_found = next((abox_member for abox_member in ontology_manager_for_racl_of_tbox.a_box_members_list
                                  if abox_member.class_identifier.name == typical_fact_object.class_identifier.name), None)
        if typical_fact_object.class_identifier.name not in ontology_manager_for_racl_of_tbox.typical_members_dict.keys() and \
                abox_member_found is None and typical_fact_found is None and \
                len(ontology_manager_for_racl_of_tbox.get_sub_classes(typical_fact_object.class_identifier, exclude_self_and_owl_thing=True)) == 0 and \
                len(ontology_manager_for_racl_of_tbox.get_super_classes(typical_fact_object.class_identifier, exclude_owl_thing=True)) == 0:
            ontology_manager_for_racl_of_tbox.destroy_specific_entity(typical_fact_object.class_identifier)


def perform_delete_typical_fact(ontology_manager_for_racl_of_tbox, typical_fact_name):
    """
    Metodo che effettivamente si occupa dell'eliminazione del fatto tipico.
    :param ontology_manager_for_racl_of_tbox:
    :param typical_fact_name: nome del fatto tipico
    :return:
    """
    typical_fact_object = ontology_manager_for_racl_of_tbox.typical_facts_support_dict.get(typical_fact_name)
    # Il fatto tipico da eliminare è quello fittizio creato per valutare il rank(C and Not(D))
    if "c" == typical_fact_object.class_identifier.name:
        delete_dummy_typical_fact(ontology_manager_for_racl_of_tbox, typical_fact_object)
    # Il fatto tipico da eliminare è uno di quelli presenti nella base di conoscenza
    else:
        typical_fact_object = ontology_manager_for_racl_of_tbox.typical_facts_support_dict.get(typical_fact_name)
        t_class_identifier = typical_fact_object.t_class_identifier
        typical_facts = [typical_fact for (typical_fact_name, typical_fact) in ontology_manager_for_racl_of_tbox.typical_facts_dict.items() if t_class_identifier.name == typical_fact_name.split("_")[0].replace("T", "", 1)]
        # Se sono presenti altri fatti tipici nella Ei corrente non posso cancellare di netto l'intero fatto tipico,
        # elimino solo la caratteristica tipica del fatto tipico. Es: se T(Bird),Fly allora elimino Fly
        if len(typical_facts) > 1:
            t_class_identifier_1 = ontology_manager_for_racl_of_tbox.get_class(t_class_identifier.name + "1")
            t_class_intersection = ontology_manager_for_racl_of_tbox.get_class("Intersection(" + typical_fact_object.t_class_identifier.name + t_class_identifier_1.name + ")")
            abox_member_found = next((abox_member for abox_member in ontology_manager_for_racl_of_tbox.a_box_members_list
                                      if abox_member.class_identifier.name == typical_fact_object.class_identifier.name), None)
            typical_fact_found = next((typical_fact_name for typical_fact_name in ontology_manager_for_racl_of_tbox.typical_facts_dict.keys()
                                       if typical_fact_name.split("_")[1] == typical_fact_object.class_identifier.name and
                                      typical_fact_name.split("_")[0].replace("T", "", 1) != typical_fact_object.t_class_identifier.name) , None)
            if typical_fact_object.class_identifier.name not in ontology_manager_for_racl_of_tbox.typical_members_dict.keys() and abox_member_found is None and typical_fact_found is None:
                ontology_manager_for_racl_of_tbox.destroy_specific_entity(typical_fact_object.class_identifier)
            else:
                t_class_intersection.is_a.remove(typical_fact_object.class_identifier)
        # É solo presente il fatto tipico
        else:
            typical_member_found = None
            if typical_fact_object.t_class_identifier.name in ontology_manager_for_racl_of_tbox.typical_members_dict.keys():
                typical_member_found = next((typical_member for typical_member in ontology_manager_for_racl_of_tbox.typical_members_dict.get(typical_fact_object.t_class_identifier.name)
                                             if typical_member.t_class_identifier.name == typical_fact_object.t_class_identifier.name and
                                             typical_member.remove_from_knowledge_base is False), None)
            # Se non ci sono membri tipici nella base di conoscenza, elimino tutto
            if typical_member_found is None:
                t_class_identifier_1 = ontology_manager_for_racl_of_tbox.get_class(t_class_identifier.name + "1")
                not_t_class_identifier_1 = ontology_manager_for_racl_of_tbox.get_class("Not(" + t_class_identifier_1.name + ")")
                t_class_intersection = ontology_manager_for_racl_of_tbox.get_class("Intersection(" + typical_fact_object.t_class_identifier.name + t_class_identifier_1.name + ")")
                ontology_manager_for_racl_of_tbox.destroy_specific_entity(t_class_identifier_1)
                ontology_manager_for_racl_of_tbox.destroy_specific_entity(not_t_class_identifier_1)
                ontology_manager_for_racl_of_tbox.destroy_specific_entity(t_class_intersection)
                abox_member_found = next((abox_member for abox_member in ontology_manager_for_racl_of_tbox.a_box_members_list
                                          if abox_member.class_identifier.name == typical_fact_object.class_identifier.name), None)
                # Se trovo anche un solo fatto tipico eccezionale che ha come class_identifier la medesima del
                # fatto tipico non eccezionale che sto per cancellare, allora class_identifier non deve essere
                # cancellata perché serve appunto almeno per il fatto tipico eccezionale trovato
                typical_fact_found = next((typical_fact_name for typical_fact_name in ontology_manager_for_racl_of_tbox.typical_facts_dict.keys()
                                           if typical_fact_name.split("_")[1] == typical_fact_object.class_identifier.name and
                                           typical_fact_name.split("_")[0].replace("T", "", 1) != typical_fact_object.t_class_identifier.name), None)
                if typical_fact_object.class_identifier.name not in ontology_manager_for_racl_of_tbox.typical_members_dict.keys() and \
                        abox_member_found is None and typical_fact_found is None:
                    ontology_manager_for_racl_of_tbox.destroy_specific_entity(typical_fact_object.class_identifier)
            # Esiste almeno un membro tipico nella base di conoscenza, quindi dato che quell'informazione è
            # persistente, elimino solo not_t_class_identifier_1 in quanto le altre classi contribuiscono a definire
            # il membro tipico.
            else:
                t_class_identifier_1 = ontology_manager_for_racl_of_tbox.get_class(t_class_identifier.name + "1")
                if t_class_identifier_1 is not None:
                    delete_not_t_class_identifier_1(ontology_manager_for_racl_of_tbox, t_class_identifier_1, typical_fact_object)
                abox_member_found = next((abox_member for abox_member in ontology_manager_for_racl_of_tbox.a_box_members_list
                                          if abox_member.class_identifier.name == typical_fact_object.class_identifier.name), None)
                if typical_fact_object.class_identifier.name not in ontology_manager_for_racl_of_tbox.typical_members_dict.keys() and abox_member_found is None:
                    ontology_manager_for_racl_of_tbox.destroy_specific_entity(typical_fact_object.class_identifier)


def delete_dummy_typical_fact(ontology_manager_for_racl_of_tbox, typical_fact_object):
    """
    Metodo che si occupa dell'eliminazione del fatto tipico fittizio.
    :param ontology_manager_for_racl_of_tbox:
    :param typical_fact_object: nome del fatto tipico fittizio
    :return:
    """
    t_class_identifier_1 = ontology_manager_for_racl_of_tbox.get_class(typical_fact_object.t_class_identifier.name + "1")
    not_t_class_identifier_1 = ontology_manager_for_racl_of_tbox.get_class("Not(" + t_class_identifier_1.name + ")")
    t_class_intersection = ontology_manager_for_racl_of_tbox.get_class("Intersection(" + typical_fact_object.t_class_identifier.name + t_class_identifier_1.name + ")")
    ontology_manager_for_racl_of_tbox.destroy_specific_entity(t_class_identifier_1)
    ontology_manager_for_racl_of_tbox.destroy_specific_entity(not_t_class_identifier_1)
    ontology_manager_for_racl_of_tbox.destroy_specific_entity(t_class_intersection)
    ontology_manager_for_racl_of_tbox.destroy_specific_entity(typical_fact_object.class_identifier)
    ontology_manager_for_racl_of_tbox.destroy_specific_entity(typical_fact_object.t_class_identifier)


def delete_not_t_class_identifier_1(ontology_manager_for_racl_of_tbox, t_class_identifier_1, typical_fact_object):
    """
    Questo metodo viene usato sia da perform_delete_query_typical_fact che da perform_delete_typical_fact.
    In entrambi infatti si procede ad eliminare not_t_class_identifier_1.
    :param ontology_manager_for_racl_of_tbox:
    :param t_class_identifier_1: identificatore di t_class_identifier_1 tramite cui si risale a not_t_class_identifier_1
    :param typical_fact_object: oggetto typical_fact tramite cui si riesce a rimuovere class_identifier dato che non
    serve più dopo l'eliminazione di not_t_class_identifier_1
    :return:
    """
    not_t_class_identifier_1 = ontology_manager_for_racl_of_tbox.get_class("Not(" + t_class_identifier_1.name + ")")
    ontology_manager_for_racl_of_tbox.destroy_specific_entity(not_t_class_identifier_1)
    # Capitava che ci fossero due Restriction uguali, in questo modo elimino i doppioni
    t_class_identifier_1.is_a = list(set(t_class_identifier_1.is_a))
    for superclass in t_class_identifier_1.is_a:
        if isinstance(superclass, Restriction):
            t_class_identifier_1.is_a.remove(superclass)
    t_class_intersection = ontology_manager_for_racl_of_tbox.get_class("Intersection(" + typical_fact_object.t_class_identifier.name + t_class_identifier_1.name + ")")
    # Capitava che ci fossero due classi uguali, in questo modo elimino i doppioni
    t_class_intersection.is_a = list(set(t_class_intersection.is_a))
    # Rimuovo class_identifier perchè rimarrebbe solo più l'info che il membro è un tipico membro senza
    # però esserci un fatto tipico con la stessa classe nell'operatore di tipicalità
    t_class_intersection.is_a.remove(ontology_manager_for_racl_of_tbox.get_class(typical_fact_object.class_identifier.name))


def check_whether_the_typical_fact_is_exceptional_or_not(ontology_manager_for_racl_of_tbox, typical_fact,
                                                         non_exceptional_typical_facts_list, e_counter,
                                                         typical_facts_exceptionality_dict, temp_typical_fact_present=False):
    """
    Metodo che si occupa di controllare se un fatto tipico è eccezionale oppure no; si procede andando a verificare la
    consistenza della base di conoscenza con quel fatto tipico. Se risulta consistente, allora quel fatto tipico non
    risulta eccezionale nella Ei corrente altrimenti è eccezionale nella Ei corrente. In entrambi i casi si va ad
    aggiornare classes_ranks e classes_ranks_of_typical_facts_dict. Si procede anche a tenere traccia dello stato di
    eccezionalità del fatto tipico in due casi:
    - se esso non risulta essere il fatto tipico della query
    - se non è presente il fatto tipico temporaneo e se esso non risulta essere il fatto tipico della query.
    :param ontology_manager_for_racl_of_tbox:
    :param typical_fact:
    :param non_exceptional_typical_facts_list:
    :param e_counter:
    :param typical_facts_exceptionality_dict:
    :param temp_typical_fact_present:
    :return:
    """
    if ontology_manager_for_racl_of_tbox.is_consistent() == "The ontology is consistent":
        print("OK, ALLORA " + typical_fact.typical_fact_name + " NON É ECCEZIONALE IN E" + str(e_counter))
        if not temp_typical_fact_present:  # il fatto tipico in esame è del tipo T(C) < D
            if not typical_fact.typical_fact_is_a_query:
                track_exceptionality_of_typical_facts(typical_facts_exceptionality_dict, typical_fact.typical_fact_name, "NotExceptional")
                # delete_member_x(ontology_manager_for_racl_of_tbox)
                non_exceptional_typical_facts_list.append(typical_fact)
            t_class_identifier = ontology_manager_for_racl_of_tbox.get_class(typical_fact.t_class_identifier.name)
            # qui vado ad aggiornare il rank del concetto C; per farlo sfrutto i comment di owlready2
            # t_class_identifier.comment[0] = e_counter
            t_class_identifier.comment = e_counter
            print("RANK(" + typical_fact.t_class_identifier.name + ") --> " + str(e_counter))
            classes_ranks[typical_fact.t_class_identifier.name] = e_counter
            print("RANK DEI CONCETTI ", classes_ranks)
            update_classes_ranks_of_typical_facts_dict(typical_fact.typical_fact_name, t_class_rank=e_counter)
            show_knowledge_base(ontology_manager_for_racl_of_tbox)
        else:  # il fatto tipico in esame è del tipo T(C And Not D) < temp
            # delete_member_x(ontology_manager_for_racl_of_tbox)
            # qui ottengo la classe C and Not(D). Es: Bird and Not(Fly)
            if typical_fact.class_identifier.name.startswith("Not("):
                t_class_identifier = ontology_manager_for_racl_of_tbox.get_class(typical_fact.t_class_identifier.name + ":And:" + typical_fact.class_identifier.name.replace("Not(", "").replace(")", ""))
            else:
                t_class_identifier = ontology_manager_for_racl_of_tbox.get_class(typical_fact.t_class_identifier.name + ":And:Not(" + typical_fact.class_identifier.name + ")")
            # qui vado ad aggiornare il rank del concetto C and Not(D); per farlo sfrutto i comment di owlready2
            # t_class_identifier.comment[0] = e_counter
            t_class_identifier.comment = e_counter
            print("RANK(" + t_class_identifier.name + ") --> " + str(e_counter))
            classes_ranks[t_class_identifier.name] = e_counter
            print("RANK DEI CONCETTI ", classes_ranks)
            update_classes_ranks_of_typical_facts_dict(typical_fact.typical_fact_name, t_class_and_not_class_rank=e_counter)
            show_knowledge_base(ontology_manager_for_racl_of_tbox)
    else:
        print("NO, ALLORA " + typical_fact.typical_fact_name + " É ECCEZIONALE IN E" + str(e_counter))
        if not temp_typical_fact_present and not typical_fact.typical_fact_is_a_query:
            track_exceptionality_of_typical_facts(typical_facts_exceptionality_dict, typical_fact.typical_fact_name,
                                                "Exceptional")
        # delete_member_x(ontology_manager_for_racl_of_tbox)
        if not temp_typical_fact_present:
            print("RANK(" + typical_fact.t_class_identifier.name + ") --> " + str(math.inf))
            classes_ranks[typical_fact.t_class_identifier.name] = math.inf
        else:
            t_class_and_not_class_name = get_t_class_and_not_class_name(typical_fact)
            print("RANK(" + t_class_and_not_class_name + ") --> " + str(math.inf))
            classes_ranks[t_class_and_not_class_name] = math.inf
        print("CLASSES RANKS ", classes_ranks)
        show_knowledge_base(ontology_manager_for_racl_of_tbox)


def track_exceptionality_of_typical_facts(typical_facts_exceptionality_dict, typical_fact_name, exceptionality):
    """
    Metodo che si occupa di tenere traccia dello stato di eccezionalità di un fatto tipico; tali informazioni vengono
    memorizzate in un dizionario le cui coppie sono del tipo typical_fact_name --> lista degli stati di eccezionalità
    nelle varie Ei.
    :param typical_facts_exceptionality_dict: dizionario che tiene traccia degli stati di eccezionalità dei fatti tipici
    :param typical_fact_name: nome del fatto tipico
    :param exceptionality: stato di eccezionalità (NotExceptional, Exceptional)
    :return:
    """
    if typical_facts_exceptionality_dict.get(typical_fact_name) is None:
        exceptionality_history = list()
        exceptionality_history.append(exceptionality)
        typical_facts_exceptionality_dict[typical_fact_name] = exceptionality_history
    else:
        typical_facts_exceptionality_dict[typical_fact_name].append(exceptionality)


def generate_possible_abox_facts_that_could_be_added_to_the_knowledge_base(ontology_manager_for_racl_of_tbox, non_exceptional_typical_facts_list, typical_facts_exceptionality_dict, e_counter):
    """
    Metodo che si occupa di generare tutti fatti dell'Abox che potrebbero essere aggiunti alla base di conoscenza
    (definizione 20 pagina 18 dell'articolo); l'implementazione segue passo passo la definizione 20 andando a
    considerare i fatti tipici che stanno nella differenza E(i-1) - E(i) e lo stato di eccezionalità di essi.
    :param ontology_manager_for_racl_of_tbox:
    :param non_exceptional_typical_facts_list: lista dei fatti tipici non eccezionali (corrispondono a quelli che stanno
    in E(i-1) - E(i))
    :param typical_facts_exceptionality_dict: dizionario che tiene traccia dello stato di eccezionalità dei fatti tipici
    :param e_counter: numero della Eì corrente
    :return:
    """
    # qui ho i fatti tipici dati dalla differenza E(i-1) - E(i)
    print("E(" + str(e_counter) + ") - E(" + str(e_counter + 1) + ")")
    print([item.typical_fact_name for item in non_exceptional_typical_facts_list])
    for non_exceptional_typical_fact in non_exceptional_typical_facts_list:
        # qui controllo che esista un membro tipico la cui classe è quella del fatto tipico
        if ontology_manager_for_racl_of_tbox.typical_members_dict.get(
                non_exceptional_typical_fact.t_class_identifier.name) is not None:
            # qui scorro i membri tipici per vedere se posso aggiungere il fatto (Not(C) OR D)(a) nell'abox
            for typical_member in ontology_manager_for_racl_of_tbox.typical_members_dict.get(
                    non_exceptional_typical_fact.t_class_identifier.name):
                if typical_member.remove_from_knowledge_base is False:
                    if typical_facts_exceptionality_dict.get(non_exceptional_typical_fact.typical_fact_name) is not None:
                        if typical_facts_exceptionality_dict.get(non_exceptional_typical_fact.typical_fact_name)[e_counter] == "NotExceptional":
                            while e_counter - 1 >= 0 and "Exceptional" == \
                                    typical_facts_exceptionality_dict.get(non_exceptional_typical_fact.typical_fact_name)[
                                        e_counter - 1]:
                                e_counter = e_counter - 1
                            if e_counter == 0:
                                ontology_manager_for_racl_of_tbox.create_not_t_class_or_class(typical_member.t_class_identifier, non_exceptional_typical_fact.class_identifier)
                                not_t_class_or_class_identifier = ontology_manager_for_racl_of_tbox.get_class("Not(" + typical_member.t_class_identifier.name + "):Or:" + non_exceptional_typical_fact.class_identifier.name)
                                ontology_manager_for_racl_of_tbox.add_member_to_class(typical_member.member_name, not_t_class_or_class_identifier)


def show_knowledge_base(ontology_manager_for_racl_of_tbox):
    """
    Metodo che stampa la base di conoscenza mostrando prima la parte dell'Abox e poi la parte della TBox.
    :param ontology_manager_for_racl_of_tbox:
    :return:
    """
    ontology_manager_for_racl_of_tbox.show_members_in_classes()
    ontology_manager_for_racl_of_tbox.show_classes_iri()
