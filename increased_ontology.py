from TypicalMember import *
from itertools import *
from Scenario import *
import rational_closure_of_tbox

"""
Questo modulo fornisce una serie di metodi utilizzati per calcolare le probabilità da associare ad ogni TypicalMember,
generare tutti gli scenari possibili e associare ad ogni scenario la probabilità opportuna.
"""


def compute_probability_for_typical_members(ontology_manager, rank_assignment_dict):
    ontology_manager.typical_facts_list.sort(key=lambda typical_fact: typical_fact.t_class_identifier.name)
    ontology_manager.a_box_members_list.sort(key=lambda abox_member: abox_member.class_identifier.name)
    length = len(ontology_manager.typical_facts_list) - 1
    next_typical_fact_index = 0
    probability_to_assign_to_typical_member = 1.0
    while next_typical_fact_index <= length:
        t_class_identifier = ontology_manager.typical_facts_list[next_typical_fact_index].t_class_identifier
        for abox_member in ontology_manager.a_box_members_list:
            if abox_member.class_identifier.name == t_class_identifier.name and not already_assumed_as_typical_member(ontology_manager, abox_member):
                next_typical_fact_index_support = next_typical_fact_index
                if next_typical_fact_index == 2:
                    p = 1
                if rational_closure_of_tbox.classes_ranks.get(t_class_identifier.name) == rank_assignment_dict.get(abox_member.member_name):
                    while next_typical_fact_index_support < length and ontology_manager.typical_facts_list[next_typical_fact_index_support].t_class_identifier.name == ontology_manager.typical_facts_list[next_typical_fact_index_support + 1].t_class_identifier.name:
                        probability_to_assign_to_typical_member = float(probability_to_assign_to_typical_member * ontology_manager.typical_facts_list[next_typical_fact_index_support].probability)
                        next_typical_fact_index_support = next_typical_fact_index_support + 1
                    probability_to_assign_to_typical_member = float(probability_to_assign_to_typical_member * ontology_manager.typical_facts_list[next_typical_fact_index_support].probability)
                    __set_probability(
                        probability_to_assign_to_typical_member,
                        ontology_manager,
                        abox_member
                    )
        next_typical_fact_index = next_typical_fact_index + 1
        probability_to_assign_to_typical_member = 1.0


def already_assumed_as_typical_member(ontology_manager, abox_member):
    for typical_member in ontology_manager.typical_members_list:
        if typical_member.t_class_identifier.name == abox_member.class_identifier.name and typical_member.member_name == abox_member.member_name:
            return True
    return False


def __set_probability(probability_to_assign_to_typical_member, ontology_manager, abox_member):
    ontology_manager.typical_members_list.append(TypicalMember(
        abox_member.class_identifier,
        abox_member.member_name,
        probability_to_assign_to_typical_member
    ))


def generate_scenarios(ontology_manager):
    return chain(*map(lambda typical_member: combinations(
        ontology_manager.typical_members_list, typical_member), range(0, len(ontology_manager.typical_members_list) + 1))
                 )


def set_probability_for_each_scenario(scenarios, ontology_manager):
    num_scenario = 1
    for scenario in scenarios:
        scenario = list(scenario)
        probability_to_assign_to_each_scenario = 1
        for typical_member in scenario:
            probability_to_assign_to_each_scenario = probability_to_assign_to_each_scenario * typical_member.probability
        not_assumed_typical_members_keys_list = __get_not_assumed_typical_members_keys(scenario, ontology_manager.typical_members_list)
        for key in not_assumed_typical_members_keys_list:
            typical_member_not_assumed = __get_typical_member(key, ontology_manager)
            probability_to_assign_to_each_scenario = probability_to_assign_to_each_scenario * (
                    1 - typical_member_not_assumed.probability)
        ontology_manager.scenarios_list.append(Scenario(scenario,
                                                        probability_to_assign_to_each_scenario,
                                                        num_scenario))
        num_scenario += 1


def __get_not_assumed_typical_members_keys(scenario, typical_members_list):
    scenario_keys = list()
    typical_members_keys = list()
    for typical_member in scenario:
        scenario_keys.append(typical_member.key)
    for typical_member in typical_members_list:
        typical_members_keys.append(typical_member.key)
    not_assumed_typical_members_keys = [key for key in scenario_keys + typical_members_keys
                                        if key not in scenario_keys or key not in typical_members_keys]
    return not_assumed_typical_members_keys


def __get_typical_member(key, ontology_manager):
    for typical_member in ontology_manager.typical_members_list:
        if key == typical_member.key:
            return typical_member
