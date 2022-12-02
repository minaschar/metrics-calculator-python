from src.visitors.remote_methods_called_visitor import MethodsCalledNodeVisitor
from src.visitors.loc_counter import LOCNodeVisitor
from src.visitors.cc_visitor import CCNodeVisitor
from src.visitors.lcom_visitor import LCOMNodeVisitor
from src.visitors.hierarchy_visitor import HierarchyNodeVisitor


# In this class exists methods that calculates metrics for the whole project
class MetricsCalculator:

    def __init__(self, class_obj):
        self.class_obj = class_obj
        self.calc_wmpc2()
        self.calc_wmpc1()
        self.calc_nom()
        self.calc_size2()
        self.calc_wac()
        self.calc_mpc()
        self.calc_lcom()
        self.calc_loc()
        self.calc_rfc()
        self.calc_nocc()
        self.calc_dit(class_obj)
        self.calc_cbo()

    # Calculate NOC metric, by counting the Classes that exists in the whole project.
    # The method will called only once time when we want to print the results
    @staticmethod
    def calc_noc(project_files):
        noc = 0
        for python_file_obj in project_files:
            noc += len(python_file_obj.get_file_classes())

        return noc

    # Calculate NOM metric, by counting the number of methods a class
    def calc_nom(self):
        # We only need to get the length of the methods dictionary in the class object
        self.class_obj.get_size_category_metrics().set_nom(len(self.class_obj.get_methods()))

    # Calculate WMPC2 metric, by adding the number of the methods in the class + num of the parameters for each method in the class
    # The wmpc2 metrics based on that a method with more parameters in more complex that other with parameters
    def calc_wmpc2(self):
        num_of_params = 0

        # In params_size we have the count of parameters for each function in a class
        params_size = [len(args) for args in self.class_obj.get_methods().values()]

        # We count all parameters in the class
        for params in params_size:
            num_of_params += params

        # Store the sum of the nom and num_of_param
        self.class_obj.get_complexity_category_metrics().set_wmpc2(len(self.class_obj.get_methods()) + num_of_params)

    # Calculate SIZE2 metric, by counting the number of methods and fields for each class in the project
    def calc_size2(self):
        # We need to sum only the lengths of each data structure
        self.class_obj.get_size_category_metrics().set_size2(len(self.class_obj.get_methods()) + len(self.class_obj.get_fields()))

    # Calculate WAC metric, by counting the number of fields for each class
    def calc_wac(self):
        # We need to only get the length of the list that keeps all the fields of the class
        self.class_obj.get_size_category_metrics().set_wac(len(self.class_obj.get_fields()))

    # Calculate NOC metric, by subtracting coherent from non-cohesive pairs
    def calc_lcom(self):
        cohesive = 0
        non_cohesive = 0

        # A dictionary where keeps the method name and value a set with all the class and instance attributes that the method use
        uses_in_methods = LCOMNodeVisitor(self.class_obj).visit(self.class_obj.get_class_ast_node())

        # Get the intersection between the methods
        for i in range(0, len(uses_in_methods), 1):
            for j in range(i + 1, len(uses_in_methods), 1):
                if (len(list(set(list(uses_in_methods.values())[i]).intersection(list(uses_in_methods.values())[j])))) == 0:
                    non_cohesive += 1
                else:
                    cohesive += 1

        if (non_cohesive - cohesive < 0):
            self.class_obj.get_cohesion_category_metrics().set_lcom(0)
        else:
            self.class_obj.get_cohesion_category_metrics().set_lcom(non_cohesive - cohesive)

    # Calculate RFC Metric, by sum the nom and the method calls of other classes
    def calc_rfc(self):
        # We convert to set because we want to remove common method calls. We sum the methods that called, not the calls
        remote_methods_sum = len(set(MethodsCalledNodeVisitor(self.class_obj).visit_ClassDef(self.class_obj.get_class_ast_node())))
        self.class_obj.get_complexity_category_metrics().set_rfc(self.class_obj.get_size_category_metrics().get_nom() + remote_methods_sum)

    # Calculate NOCC Metric, by the sum of a Classes' children
    def calc_nocc(self):
        my_class_children_classes = len(self.return_children(self.class_obj))
        self.class_obj.get_size_category_metrics().set_nocc(my_class_children_classes)

    # Calculate DIT Metric, by the depth of the class in the max inheritance hierarchy
    def calc_dit(self, a_parent_class_object):
        self.curr_dit_class = a_parent_class_object
        # Class is not in any hierarchy
        if ((HierarchyNodeVisitor(self.curr_dit_class).visit_ClassDef(self.curr_dit_class.get_class_ast_node()) == []) and (len(self.return_children(self.curr_dit_class)) == 0)):
            self.curr_dit_class.get_complexity_category_metrics().set_dit(0)
            # set_hierarchy is needed for the calculation of potential children classes' DIT since their DIT is -> MaxParentDIT + 1
            self.curr_dit_class.set_hierarchy(0)
        # Class is in the root of an inheritance hierarchy
        elif ((HierarchyNodeVisitor(self.curr_dit_class).visit_ClassDef(self.curr_dit_class.get_class_ast_node()) == []) and (len(self.return_children(self.curr_dit_class)) != 0)):
            self.curr_dit_class.get_complexity_category_metrics().set_dit(1)
            # set_hierarchy is needed for the calculation of potential children classes' DIT since their DIT is -> MaxParentDIT + 1
            self.curr_dit_class.set_hierarchy(1)
        # Class is part of an inheritance hierarchy (not the root)
        else:
            my_parent_classes_names_only = HierarchyNodeVisitor(self.curr_dit_class).visit_ClassDef(self.curr_dit_class.get_class_ast_node())

            # Converting simple name pointers to actual object classes
            my_parent_classes_objects = self.convert_to_actual_parent_objects(self.curr_dit_class, my_parent_classes_names_only)
            # Finding the max depth of the parent classes since DIT takes into concideration the max parent class depth as input
            max_parent_depth = self.return_max_parent_depth(my_parent_classes_objects)
            self.curr_dit_class.get_complexity_category_metrics().set_dit(max_parent_depth + 1)
            # set_hierarchy is needed for the calculation of potential children classes' DIT since their DIT is -> MaxParentDIT + 1
            self.curr_dit_class.set_hierarchy(max_parent_depth + 1)

    # Calculate LOC metric, by counting lines of code for each class. Empty lines not added
    def calc_loc(self):
        self.class_obj.get_size_category_metrics().set_loc(LOCNodeVisitor(self.class_obj).visit_ClassDef(self.class_obj.get_class_ast_node()))

    # Calculate MPC Metric, by adding all the calls of methods that declared in other classes
    def calc_mpc(self):
        # We sum all the calls
        messages = len(MethodsCalledNodeVisitor(self.class_obj).visit_ClassDef(self.class_obj.get_class_ast_node()))

        self.class_obj.get_coupling_category_metrics().set_mpc(messages)

    # Calculate CBO Metric. As coupling between classes we consider the inheritance and the message passing between the classes
    # Classes in libraries not inluded in the calculation
    def calc_cbo(self):
        # We store all the methods that called, and belongs to other classes. Methods from libraries are not included
        methods_that_called = MethodsCalledNodeVisitor(self.class_obj).visit_ClassDef(self.class_obj.get_class_ast_node())
        # We store all the class name or instance names that used to call methods from other classes in the project. Classes and methods from libraries are not included
        # We use a set because we count each class and each instance only one time
        class_uses = set()
        for method in methods_that_called:
            parts = method.split(".", 2)
            # parts[0] will have the instance name or the class name that calls the method
            class_uses.add(parts[0])

        # In class_uses now we will have the union of parent class names and of classes that their methods are used in the current class
        class_uses = class_uses.union(set(HierarchyNodeVisitor(self.class_obj).visit_ClassDef(self.class_obj.get_class_ast_node())))

        self.class_obj.get_coupling_category_metrics().set_cbo(len(class_uses) + self.class_obj.get_size_category_metrics().get_nocc())

    # Calculate WMPC1 metric, by adding the cc of the whole class and divide by the nom
    def calc_wmpc1(self):
        class_nom = len(self.class_obj.get_methods())

        if (class_nom > 0):
            class_cc = CCNodeVisitor(self.class_obj).visit_ClassDef(self.class_obj.get_class_ast_node())
            self.class_obj.get_complexity_category_metrics().set_wmpc1(round(class_cc / class_nom, 2))
        else:
            # If there no methods, wmpcs1 is equal to 0
            self.class_obj.get_complexity_category_metrics().set_wmpc1(0.0)


##################### Methods necessary for NOCC and DIT calculation #####################

    # This method recieves a class and returns a list of its children (Classes in the list are presented by their names and not the actual objects)

    def return_children(self, class_in_question):
        all_parent_classes = list()
        my_class_children_classes = 0
        my_class_children_classes_list = list()
        # Iterating through each class in each file in the project to define all classes that parent some class
        for python_file_obj in class_in_question.get_python_file_obj().get_project_obj().get_files():
            for class_obj in python_file_obj.get_file_classes():
                all_parent_classes = all_parent_classes + HierarchyNodeVisitor(class_obj).visit_ClassDef(class_obj.get_class_ast_node())
        # We search the "class_in_question" as a parent in the list collected from above.
        # The amount of times the condition is met means how many classes the "class_in_question" fathers other classes and therefore "my_class_children_classes" is incremented.
        for my_class in all_parent_classes:
            if (my_class == class_in_question.get_class_name()):
                my_class_children_classes = my_class_children_classes + 1
                my_class_children_classes_list.append(my_class)
        return my_class_children_classes_list

    # This method converts a list of parent classes presented in simple name strings into the actual object classes
    def convert_to_actual_parent_objects(self, class_in_question, my_parent_classes_names_only):
        my_parent_classes_objects = list()
        # Iterating through each class in each file in the project
        for python_file_obj in class_in_question.get_python_file_obj().get_project_obj().get_files():
            for class_obj in python_file_obj.get_file_classes():
                for class_name_only in my_parent_classes_names_only:
                    if (class_obj.get_class_name() == class_name_only):
                        my_parent_classes_objects.append(class_obj)
        return my_parent_classes_objects

    # This method returns the max depth of a given parent class object
    def return_max_parent_depth(self, my_parent_classes_objects):
        # "max_parent_dit" is initialized to -2 because the default value of classObj.hierarchy is -1 and is set by the constructor
        max_parent_dit = -2
        for a_parent_class_object in my_parent_classes_objects:
            # This if clause makes sure that a parent has also calculated its DIT so that the children classes' DIT is -> MaxParentDIT + 1
            if (a_parent_class_object.get_hierarchy() == -1):
                # Recursion
                self.calc_dit(a_parent_class_object)
            else:
                if (a_parent_class_object.get_hierarchy() > max_parent_dit):
                    # Condition is met and the max value changes
                    max_parent_dit = a_parent_class_object.get_hierarchy()
        return max_parent_dit
