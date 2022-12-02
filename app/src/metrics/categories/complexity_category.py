class ComplexityCategory:

    dit = 0
    rfc = 0
    wmpc1 = 0.0
    wmpc2 = 0

    # Metrics getters
    def get_dit(self):
        return self.dit

    def get_rfc(self):
        return self.rfc

    def get_wmpc1(self):
        return self.wmpc1

    def get_wmpc2(self):
        return self.wmpc2

    # Set value to the Metrics
    def set_dit(self, value):
        self.dit = value

    def set_rfc(self, value):
        self.rfc = value

    def set_wmpc1(self, value):
        self.wmpc1 = value

    def set_wmpc2(self, value):
        self.wmpc2 = value
