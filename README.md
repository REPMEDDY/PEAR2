# PEAR2
PEAR2 is a reasoner based on the ALC Descriptive Logic and it’s able to perform non-monotonic reasoning by implementing a non-monotonic extension of ALC.\
The tool is implemented in Python 3.9 and uses Owlready2 0.34, a library to create, manage and query ontologies.
## How it works
PEAR2 is able to query a knowledge base specified as input with a specific syntax. The output of the tool is a list of scenarios equipped with a probability and it’s also possible to specify a certain range of probability so that the tool will return (if they exists) only the scenarios where the query logically follows whose probability is in the specified range.
## How to create a knowledge base
To create a knowledge base it’s necessary to edit the ontology_input.txt file.\
The file is already edited with a simple knowledge base that describes the typical characteristics of CardPlayers and Students.
### Classes:
The keyword “Classes:” specify that in the following row are presents the classes to create. It’s necessary to separate with a space every class name it is provided.
##### Example
Classes:\
Bird Penguin Fly
### Set_as_sub_class:
They keyword “Set_as_sub_class:” allows to specify that in the following row a class is subclass of another class. It’s necessary to separate with a space every couple class,sub_class.
##### Example
Set_as_sub_class:\
Penguin,Bird Dog,Mammal
### Set_typical_facts:
The keyword “Set_typical_facts:” allows to model in the following row the typical properties of a certain class, in other words, the so called typical facts. It’s necessary to separate every typical fact with a space. A typical fact follows this syntax: Typical(C),D,p or Typical(And(C_E)),F,p.
##### Example
Set_typical_facts:\
Typical(Bird),Fly,0.80 Typical(Penguin),Not(Fly),0.90 Typical(And(Bird_Black)),Fly,0.80
### Add_members_to_class:
The keyword “Add_members_to_class:” allows to specify in the following row to which class an individual belongs. It’s necessary to separate with a space every couple “individual_name;class_name”.
##### Example
Add_members_to_class:\
Tweety;Bird Tux;Penguin Tux;Not(Fly)
##### Example
Add_members_to_class:\
Tweety;Bird Tux;Penguin,Not(Fly)
### Not
The keyword Not is used to refer to the complementary of a certain class. In the previous examples was used to say that Tux do not fly (Tux,Not(Fly)) and to say typically/normally penguins do not fly (Typical(Penguin),Not(Fly),0.90).\
\
It’s also possible to write classes names on multiple rows.
##### Example 
Classes:\
FirstClass SecondClass\
Classes:\
ThirdClass FourthClass\
\
This logic is also valid for all the other keywords except for the Not keyword.
## How to create a query
To create a query it’s necessary to edit the query_input.txt file. A query has this syntax: individual_name;class_name
##### Example
Tux;Penguin
## How to run PEAR2
After providing the knowledge base and the query, to run the tool it’s sufficient to run the main present in the input_from_file.py file.
