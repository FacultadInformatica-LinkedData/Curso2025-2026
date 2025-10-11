from rdflib import Graph, Namespace, Literal, XSD
from rdflib.namespace import RDF, RDFS

VCARD = Namespace("http://www.w3.org/2001/vcard-rdf/3.0/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

class Report:
    def __init__(self):
        self.__report = ""

    def domain_and_range_correspond_to_input(self, g,propertyURI,correct_domain,correct_range):
        domain = g.value(subject=propertyURI, predicate=RDFS.domain)
        range = g.value(subject=propertyURI, predicate=RDFS.range)
        if domain is None or range is None:
            return False
        if domain != correct_domain or range != correct_range:
            return False
        return True

    def does_it_have_label(self, g, entity):
        label = g.value(subject=entity, predicate=RDFS.label)
        if label is None:
            return False
        return True

    def namespace_is_correct_class(self, entity):
        if entity is None:
            return False
        if "http://oeg.fi.upm.es/def/people#" not in entity:
            return False
        return True

    def namespace_is_correct_instance(self, entity):
        if entity is None:
            return False
        if "http://oeg.fi.upm.es/resource/person/" not in entity:
            return False
        return True

    def is_subClassOf(self, g, subClass, superClass):
        candidate = g.value(subject=subClass, predicate=RDFS.subClassOf, object=None)
        if candidate is None or superClass not in candidate:
            return False
        return True

    def __add_to_report(self, message):
        print(message)
        self.__report = self.__report + message + "\n"

    def validate_task_06_01(self, g):
        error = False
        professorURI = g.value(subject=None, predicate=RDFS.label, object=Literal("Professor", datatype=XSD.string))
        personURI = g.value(subject=None, predicate=RDFS.label, object=Literal("Person", datatype=XSD.string))
        associateProfessorURI = g.value(subject=None, predicate=RDFS.label, object=Literal("AssociateProfessor", datatype=XSD.string))
        interimURI = g.value(subject=None, predicate=RDFS.label, object=Literal("InterimAssociateProfessor", datatype=XSD.string))
        fProfessorURI = g.value(subject=None, predicate=RDFS.label, object=Literal("FullProfessor", datatype=XSD.string))
        classes = [professorURI,personURI,associateProfessorURI,interimURI, fProfessorURI]
        # check namespace and existence
        for i in classes:
            if i is None:
                self.__add_to_report("ERROR: One of the classes is missing its correct label! I cannot retrieve it")
                error = True
                return
            if self.namespace_is_correct_class(i):
                print("The namespace is correct for " + str(i))
            else:
                self.__add_to_report("ERROR: The namespace is not correct for " + str(i))
                error = True
        # check class hierarchy
        if self.is_subClassOf(g, professorURI, personURI) and \
            self.is_subClassOf(g, associateProfessorURI, professorURI) and \
            self.is_subClassOf(g, interimURI, associateProfessorURI) and \
            self.is_subClassOf(g, fProfessorURI, professorURI):
            self.__add_to_report("Hierarchy OK")
        else:
            self.__add_to_report("ERROR: Hierarchy is missing a subclassOf statement")
            error = True
        if error:
            self.__add_to_report("ERROR IN TASK 6.1")
        else:
            self.__add_to_report("TASK 6.1 OK")

    def validate_task_06_02(self, g):
        # check properties
        error = False
        hasColleague  = g.value(subject=None, predicate=RDFS.label, object=Literal("hasColleague", datatype=XSD.string))
        hasName = g.value(subject=None, predicate=RDFS.label, object=Literal("hasName", datatype=XSD.string))
        hasHomePage = g.value(subject=None, predicate=RDFS.label, object=Literal("hasHomePage", datatype=XSD.string))
        personURI = g.value(subject=None, predicate=RDFS.label, object=Literal("Person", datatype=XSD.string))
        fullProfessorURI = g.value(subject=None, predicate=RDFS.label, object=Literal("FullProfessor", datatype=XSD.string))
        properties = [hasColleague, hasName, hasHomePage]
        for i in properties:
            if i is None:
                self.__add_to_report("ERROR: One of the properties is missing its correct label! I cannot retrieve it")
                error = True
                return
        if not self.domain_and_range_correspond_to_input(g,hasColleague,personURI,personURI):
            self.__add_to_report("ERROR: hasColleague has an incorrect domain or range")
            error = True
        if not self.domain_and_range_correspond_to_input(g,hasName,personURI,RDFS.Literal):
            self.__add_to_report("ERROR: hasName has an incorrect domain or range")
            error = True
        if not self.domain_and_range_correspond_to_input(g,hasHomePage,fullProfessorURI,RDFS.Literal):
            self.__add_to_report("ERROR: hasHomePage has an incorrect domain or range")
            error = True
        if error:
            self.__add_to_report("ERROR IN TASK 6.2")
        else:
            self.__add_to_report("TASK 6.2 OK")

    def validate_task_06_03(self, g):
        # check all individuals can be retrieved through their label
        error = False
        oscar  = g.value(subject=None, predicate=RDFS.label, object=Literal("Oscar", datatype=XSD.string))
        asun  = g.value(subject=None, predicate=RDFS.label, object=Literal("Asun", datatype=XSD.string))
        raul  = g.value(subject=None, predicate=RDFS.label, object=Literal("Raul", datatype=XSD.string))
        if oscar is None or asun is None or raul is None:
            self.__add_to_report("ERROR: One of the individuals is missing its correct label! I cannot retrieve it")
            error = True
        # check all individuals have the correct namespace
        if not self.namespace_is_correct_instance(oscar):
            self.__add_to_report("ERROR: Oscar has an incorrect namespace")
            error = True
        if not self.namespace_is_correct_instance(asun):
            self.__add_to_report("ERROR: Asun has an incorrect namespace")
            error = True
        if not self.namespace_is_correct_instance(raul):
            self.__add_to_report("ERROR: Raul has an incorrect namespace")
            error = True
        # check all individuals have their properties
        oscar_properties = []
        for p in g.predicates(subject=oscar):
            oscar_properties.append(p)
        asun_properties = []
        for p in g.predicates(subject=asun):
            asun_properties.append(p)
        if oscar_properties is None or asun_properties is None:
            self.__add_to_report("ERROR: One of the individuals has no properties")
            error = True
        if len(oscar_properties) != 4 or len(asun_properties) != 4:
            # oscar: type, label, hasColleague, hasName.
            # asun: type, label, hasHomePage, hasColleague
            self.__add_to_report("ERROR: One of the individuals has the wrong number of properties")
            error = True
        if error:
            self.__add_to_report("ERROR IN TASK 6.3")
        else:
            self.__add_to_report("TASK 6.3 OK")

    def validate_task_06_04(self, g):
        error = False
        target_properties = [VCARD.Given, VCARD.Family, FOAF.email]
        #retrieve all triples from Oscar.
        oscar_properties = []
        oscar  = g.value(subject=None, predicate=RDFS.label, object=Literal("Oscar", datatype=XSD.string))
        for p in g.predicates(subject=oscar):
            oscar_properties.append(p)
        if oscar_properties is None:
            self.__add_to_report("ERROR: Oscar has no properties")
            error = True
        # do they have the correct ns?
        for i in target_properties:
            if i not in oscar_properties:
                self.__add_to_report("ERROR: One of the properties from Oscar has no correct namespace or does not exist. Please double check")
                error = True
        if error:
            self.__add_to_report("ERROR IN TASK 6.4")
        else:
            self.__add_to_report("TASK 6.4 OK")

    def save_report(self, task):
        report_name = "report_result" + task + ".txt"
        with open(report_name, "w", encoding="utf-8") as f:
            f.write(self.__report)

    def validate_07_01(self, result, task):
        error = False
        if len(result) != 7:
            self.__add_to_report("ERROR: The number of classes returned is not correct")
            error = True
        for c,sc in result:
            # Anything except Person and Animal must have a superclass
            if sc == None and "Person" not in str(c) and "Animal" not in str(c):
                self.__add_to_report("The class "+str(c)+" has no superclass")
                error = True
            if "Person" not in str(c) and "Animal" not in str(c) \
            and "Professor" not in str(c) and "Student" not in str(c) \
            and "FullProfessor" not in str(c) and "AssociateProfessor" not in str(c) \
            and "AssociateProfessor" not in str(c) and "Instructor" not in str(c) \
            and "InterimAssociateProfessor" not in str(c):
                self.__add_to_report("ERROR: incorrect class retrieved")
                error = True
        if not error:
            self.__add_to_report(task+" OK")

    def validate_07_1a(self, result):
        self.validate_07_01(result, "TASK 7.1a")

    def validate_07_1b(self, query, g):
        aux = g.query(query)
        aux_dict = []
        for r in g.query(query):
            aux_dict.append((r.c, r.sc))
        self.validate_07_01(aux_dict, "TASK 7.1b")

    def validate_07_02(self,result, task):
        error = False
        if len(result) != 3:
            self.__add_to_report("ERROR: The number of individuals returned is not correct")
            error = True
        for i in result:
            if "Asun" not in i and "Raul" not in i and "Oscar" not in i:
                self.__add_to_report("ERROR: The individual "+str(i)+" is not correct")
                error = True
        if error == False:
            self.__add_to_report(task+" OK")


    def validate_07_02a(self, individuals):
        self.validate_07_02(individuals, "TASK 7.2a")

    def validate_07_02b(self, g, query):
        error = False
        aux = g.query(query)
        aux_dict = []
        for r in g.query(query):
            if (r.ind is None):
                self.__add_to_report("ERROR: Variable used to retrieve the individuals is not correct!")
                error = True
            else:
                aux_dict.append(r.ind)
        self.validate_07_02(aux_dict, "TASK 7.2b")

    def validate_07_03(self, g, query):
        error = False
        entities = g.query(query)
        if len(list(entities)) != 3:
            self.__add_to_report("ERROR: The number of individuals returned is not correct")
            error = True
        for i in entities:
            if "Asun" not in i.name and "Raul" not in i.name and "Fantasma" not in i.name:
                self.__add_to_report("ERROR: An individual returned is not correct")
                error = True
        if not error:
            self.__add_to_report("TASK 7.3 OK")

    def validate_07_04(self, g, query):
        error = False
        entities = g.query(query)
        if len(list(entities)) != 3:
            self.__add_to_report("ERROR: The number of individuals returned is not correct")
            error = True
        for i in entities:
            if "Asun" not in i.name and "Raul" not in i.name and "Oscar" not in i.name:
                self.__add_to_report("ERROR: An individual returned is not correct")
                error = True
        if not error:
            self.__add_to_report("TASK 7.4 OK")
