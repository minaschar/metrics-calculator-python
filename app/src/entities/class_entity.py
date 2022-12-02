
class Class:

    def __init__(self, class_name, python_file_obj, class_ast_node, cohesion_category_metrics,
                 complexity_category_metrics, coupling_category_metrics, qmood_category_metrics, size_category_metrics):
        # The name of the class node we checking
        self.class_name = class_name
        # The object of the python file that the class declared to
        self.python_file_obj = python_file_obj
        # The ast node for the whole class block
        self.class_ast_node = class_ast_node
        # A dictionary with key the method name and value a list of the parameters of that method
        self.methods = dict()
        # All class attributes and instance attributes of the class
        self.fields = set()
        # The level of hierarchy of the class
        self.hierarchy = -1
        # Init objects that will keep the softawre quality metrics for the class
        self.cohesion_category_metrics = cohesion_category_metrics
        self.complexity_category_metrics = complexity_category_metrics
        self.coupling_category_metrics = coupling_category_metrics
        self.qmood_category_metrics = qmood_category_metrics
        self.size_category_metrics = size_category_metrics

    def get_class_name(self):
        return self.class_name

    def get_hierarchy(self):
        return self.hierarchy

    def get_python_file_obj(self):
        return self.python_file_obj

    # Method that returns the ast node for the specific class.
    # We need it so that we don't have to repeatedly access the python files to get the class nodes.
    def get_class_ast_node(self):
        return self.class_ast_node

    def get_methods(self):
        return self.methods

    def get_fields(self):
        return self.fields

    def get_cohesion_category_metrics(self):
        return self.cohesion_category_metrics

    def get_complexity_category_metrics(self):
        return self.complexity_category_metrics

    def get_coupling_category_metrics(self):
        return self.coupling_category_metrics

    def get_qmood_category_metrics(self):
        return self.qmood_category_metrics

    def get_size_category_metrics(self):
        return self.size_category_metrics

    def add_method(self, method_name, params):
        self.methods[method_name] = params

    def add_field(self, field):
        self.fields.add(field)

    # Setter for hierarchy property needed for DIT Metric
    def set_hierarchy(self, value):
        self.hierarchy = value
