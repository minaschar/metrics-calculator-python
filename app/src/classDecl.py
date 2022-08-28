

class Class:

    def __init__(self, className, pyFileObj, cohesionCategoryMetrics, complexityCategoryMetrics, couplingCategoryMetrics, qmoodCategoryMetrics, sizeCategoryMetrics):
        self.name = className
        self.pyFileObj = pyFileObj
        self.methods = []
        self.fields = []
        self.cohesionCategoryMetrics = cohesionCategoryMetrics
        self.complexityCategoryMetrics = complexityCategoryMetrics
        self.couplingCategoryMetrics = couplingCategoryMetrics
        self.qmoodCategoryMetrics = qmoodCategoryMetrics
        self.sizeCategoryMetrics = sizeCategoryMetrics

    def get_name(self):
        return self.name

    def get_methods(self):
        return self.methods

    def get_fields(self):
        return self.fields

    def add_method(self, method):
        self.methods.append(method)

    def add_field(self, field):
        self.fields.append(field)

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
