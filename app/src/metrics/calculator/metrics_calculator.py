from src.visitors.remote_methods_called_visitor import MethodsCalledNodeVisitor
from src.visitors.loc_counter import LOCNodeVisitor
from src.visitors.cc_visitor import CCNodeVisitor
from src.visitors.lcom_visitor import LCOMNodeVisitor
from src.visitors.hierarchy_visitor import HierarchyNodeVisitor
from src.entities.class_entity import Class


# In this class exists methods that calculates metrics for the whole project
class MetricsCalculator:

    def __init__(self, class_obj: Class):
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

    # Count the Classes that exists in the whole project.
    # The method will called only once time when we want to print the results
    @staticmethod
    def calc_noc(project_files):
        noc = 0
        for python_file_obj in project_files:
            noc += len(python_file_obj.get_file_classes())

        return noc

    # Count the number of methods a class
    def calc_nom(self):
        self.class_obj.get_size_category_metrics().set_nom(len(self.class_obj.get_methods()))

    # Calculate wmpc2 metric
    def calc_wmpc2(self):
        num_of_params = 0

        # In args_size we have the count of parameters for each function in a class
        params_size = [len(args) for args in self.class_obj.get_methods().values()]

        # We count all parameters in the class
        for params in params_size:
            num_of_params += params

        self.class_obj.get_complexity_category_metrics().set_wmpc2(len(self.class_obj.get_methods()) + num_of_params)

    # Count the number of methods and fields for each class in the project
    def calc_size2(self):
        self.class_obj.get_size_category_metrics().set_size2(len(self.class_obj.get_methods()) + len(self.class_obj.get_fields()))

    # Count the number of fields for each class
    def calc_wac(self):
        self.class_obj.get_size_category_metrics().set_wac(len(self.class_obj.get_fields()))

    # Calculate LCOM Metric
    def calc_lcom(self):
        cohesive = 0
        non_cohesive = 0

        uses_in_methods = LCOMNodeVisitor(self.class_obj).visit(self.class_obj.get_class_ast_node())

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

    # Calculate RFC Metric
    def calc_rfc(self):
        # We convert to set because we want to remove common method calls. We sum the methods, not the calls
        remote_methods_sum = len(set(MethodsCalledNodeVisitor(self.class_obj).visit_ClassDef(self.class_obj.get_class_ast_node())))
        self.class_obj.get_complexity_category_metrics().set_rfc(self.class_obj.get_size_category_metrics().get_nom() + remote_methods_sum)

    # Calculate NOCC Metric
    def calc_nocc(self):

        my_class_children_classes = len(self.return_children(self.class_obj))
        self.class_obj.get_size_category_metrics().set_nocc(my_class_children_classes)

    # Calculate DIT Metric
    def calc_dit(self, a_parent_class_object):
        self.curr_dit_class = a_parent_class_object
        # Class is not in any hierarchy
        if ((HierarchyNodeVisitor(self.curr_dit_class).visit_ClassDef(self.curr_dit_class.get_class_ast_node()) == []) and (len(self.return_children(self.curr_dit_class)) == 0)):
            self.curr_dit_class.get_complexity_category_metrics().set_dit(0)
            self.curr_dit_class.set_hierarchy(0)
        elif ((HierarchyNodeVisitor(self.curr_dit_class).visit_ClassDef(self.curr_dit_class.get_class_ast_node()) == []) and (len(self.return_children(self.curr_dit_class)) != 0)):
            self.curr_dit_class.get_complexity_category_metrics().set_dit(1)
            self.curr_dit_class.set_hierarchy(1)
        else:
            my_parent_classes_names_only = HierarchyNodeVisitor(self.curr_dit_class).visit_ClassDef(self.curr_dit_class.get_class_ast_node())

            # Converting simple name pointers to actually object classes
            my_parent_classes_objects = self.convert_to_actual_parent_objects(self.curr_dit_class, my_parent_classes_names_only)
            max_parent_depth = self.return_max_parent_depth(my_parent_classes_objects)
            self.curr_dit_class.get_complexity_category_metrics().set_dit(max_parent_depth + 1)
            self.curr_dit_class.set_hierarchy(max_parent_depth + 1)

    # Calculate LOC Metric
    def calc_loc(self):
        self.class_obj.get_size_category_metrics().set_loc(LOCNodeVisitor(self.class_obj).visit_ClassDef(self.class_obj.get_class_ast_node()))

    # Calculate MPC Metric
    def calc_mpc(self):
        # We sum all the calls
        messages = len(MethodsCalledNodeVisitor(self.class_obj).visit_ClassDef(self.class_obj.get_class_ast_node()))

        self.class_obj.get_coupling_category_metrics().set_mpc(messages)

    # Calculate CBO Metric
    def calc_cbo(self):
        # We store all the methods that called, and belongs to other classes. Methods from libraries are not included
        methods_that_called = MethodsCalledNodeVisitor(self.class_obj).visit_ClassDef(self.class_obj.get_class_ast_node())
        # We store all the class name or instance names that used to call methods from other classes in the project. Classes and methods from libraries are not included
        class_uses = set()
        for method in methods_that_called:
            part1 = method.split(".", 2)
            class_uses.add(part1[0])

        self.class_obj.get_coupling_category_metrics().set_cbo(len(class_uses) +
                                                               len(HierarchyNodeVisitor(self.class_obj).visit_ClassDef(self.class_obj.get_class_ast_node())) +
                                                               self.class_obj.get_size_category_metrics().get_nocc())

    def calc_wmpc1(self):
        class_nom = len(self.class_obj.get_methods())
        if (class_nom > 0):
            class_cc = CCNodeVisitor(self.class_obj).visit_ClassDef(self.class_obj.get_class_ast_node())
            self.class_obj.get_complexity_category_metrics().set_wmpc1(round(class_cc / class_nom, 2))
        else:
            self.class_obj.get_complexity_category_metrics().set_wmpc1(0.0)


##################### Methods necessary for NOCC and DIT calculation #####################


    def return_children(self, class_in_question):
        all_parent_classes = []
        my_class_children_classes = 0
        my_class_children_classes_list = []
        for python_file_obj in class_in_question.get_python_file_obj().get_project_obj().get_files():
            for class_obj in python_file_obj.get_file_classes():
                all_parent_classes = all_parent_classes + HierarchyNodeVisitor(class_obj).visit_ClassDef(class_obj.get_class_ast_node())
        for my_class in all_parent_classes:
            if (my_class == class_in_question.get_class_name()):
                my_class_children_classes = my_class_children_classes + 1
                my_class_children_classes_list.append(my_class)
        return my_class_children_classes_list

    def convert_to_actual_parent_objects(self, class_in_question, my_parent_classes_names_only):
        my_parent_classes_objects = []
        for python_file_obj in class_in_question.get_python_file_obj().get_project_obj().get_files():
            for class_obj in python_file_obj.get_file_classes():
                for class_name_only in my_parent_classes_names_only:
                    if (class_obj.get_class_name() == class_name_only):
                        my_parent_classes_objects.append(class_obj)
        return my_parent_classes_objects

    def return_max_parent_depth(self, my_parent_classes_objects):
        max_parent_dit = -2
        for a_parent_class_object in my_parent_classes_objects:
            if (a_parent_class_object.get_hierarchy() == -1):
                self.calc_dit(a_parent_class_object)
            else:
                if (a_parent_class_object.get_hierarchy() > max_parent_dit):
                    max_parent_dit = a_parent_class_object.get_hierarchy()
        return max_parent_dit
