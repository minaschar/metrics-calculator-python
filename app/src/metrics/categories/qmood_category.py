class QMOODCategory:

    reusability = 0.0
    flexibility = 0.0
    understandability = 0.0
    functionality = 0.0
    extendability = 0.0
    effectiveness = 0.0

    # Metrics getters
    def get_reusability(self):
        return self.reusability

    def get_flexibility(self):
        return self.flexibility

    def get_understandability(self):
        return self.understandability

    def get_functionality(self):
        return self.functionality

    def get_extendability(self):
        return self.extendability

    def get_effectiveness(self):
        return self.effectiveness

    # Set value to the Metrics
    def set_reusability(self, value):
        self.reusability = value

    def set_flexibility(self, value):
        self.flexibility = value

    def set_understandability(self, value):
        self.understandability = value

    def set_functionality(self, value):
        self.functionality = value

    def set_extendability(self, value):
        self.extendability = value

    def set_effectiveness(self, value):
        self.effectiveness = value
