class CouplingCategory:

    CBO = 0
    MPC = 0

# Metrics getters
    def get_CBO(self):
        return self.CBO

    def get_MPC(self):
        return self.MPC

# Calculating the Metrics
    def set_CBO(self, value):
        self.CBO = value

    def set_MPC(self, value):
        self.MPC = value
