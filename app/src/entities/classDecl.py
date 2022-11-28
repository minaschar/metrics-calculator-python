
class Class:

    def __init__(self, className, pyFileObj, classAstNode, cohesionCategoryMetrics, complexityCategoryMetrics, couplingCategoryMetrics, qmoodCategoryMetrics, sizeCategoryMetrics):
        self.name = className
        self.pyFileObj = pyFileObj
        self.classAstNode = classAstNode
        self.methods = dict()
        self.fields = set()  # All class attributes and instance attributes
        self.hierarchy = -1
        self.cohesionCategoryMetrics = cohesionCategoryMetrics
        self.complexityCategoryMetrics = complexityCategoryMetrics
        self.couplingCategoryMetrics = couplingCategoryMetrics
        self.qmoodCategoryMetrics = qmoodCategoryMetrics
        self.sizeCategoryMetrics = sizeCategoryMetrics

    def get_name(self):
        return self.name

    def get_hierarchy(self):
        return self.hierarchy

    def getPyFileObj(self):
        return self.pyFileObj

    # Method that returns the ast node for the specific class.
    # We need it so that we don't have to repeatedly access the python files to get the class nodes.
    def getClassAstNode(self):
        return self.classAstNode

    def get_methods(self):
        return self.methods

    def get_fields(self):
        return self.fields

    def add_method(self, methodName, params):
        self.methods[methodName] = params

    def add_field(self, field):
        self.fields.add(field)

    def getCohesionCategoryMetrics(self):
        return self.cohesionCategoryMetrics

    def getComplexityCategoryMetrics(self):
        return self.complexityCategoryMetrics

    def getCouplingCategoryMetrics(self):
        return self.couplingCategoryMetrics

    def getQMOODCategoryMetrics(self):
        return self.qmoodCategoryMetrics

    def getSizeCategoryMetrics(self):
        return self.sizeCategoryMetrics

    # Setter for hierarchy property needed for DIT Metric
    def set_hierarchy(self, value):
        self.hierarchy = value
