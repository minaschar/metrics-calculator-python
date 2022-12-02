class CouplingCategory:

    cbo = 0
    mpc = 0

    # Metrics getters
    def get_cbo(self):
        return self.cbo

    def get_mpc(self):
        return self.mpc

    # Set value to the Metrics
    def set_cbo(self, value):
        self.cbo = value

    def set_mpc(self, value):
        self.mpc = value
