from OntologyManager import *

"""
Classe che rappresenta i risultati dell'interrogazione dell'ontologia
"""


class QueryResult:

    def __init__(self, list_of_logical_consequent_scenarios=None, probability=None):
        if list_of_logical_consequent_scenarios is None:
            list_of_logical_consequent_scenarios = []
        if probability is None:
            probability = 2
        self.list_of_logical_consequent_scenarios = list_of_logical_consequent_scenarios
        self.probability = probability

    def show_query_result(self):
        print("RISULTATI DELL'INTERROGAZIONE: ")
        print("SCENARI IN CUI LA QUERY SEGUE LOGICAMENTE")
        for scenario in self.list_of_logical_consequent_scenarios:
            OntologyManager.show_a_specific_scenario(scenario)
            print("\n")
        print("PROBABILITA' TOTALE: " + str(self.probability))
