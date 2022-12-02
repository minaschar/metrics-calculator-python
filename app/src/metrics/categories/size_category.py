
class SizeCategory:

    nocc = 0
    nom = 0
    loc = 0
    size2 = 0
    wac = 0

    # Metrics getters
    def get_nocc(self):
        return self.nocc

    def get_nom(self):
        return self.nom

    def get_loc(self):
        return self.loc

    def get_size2(self):
        return self.size2

    def get_wac(self):
        return self.wac

    # Set value to the Metrics
    def set_nocc(self, value):
        self.nocc = value

    def set_nom(self, value):
        self.nom = value

    def set_loc(self, value):
        self.loc = value

    def set_size2(self, value):
        self.size2 = value

    def set_wac(self, value):
        self.wac = value
