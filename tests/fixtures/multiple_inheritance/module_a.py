class Flyer:
    def fly(self):
        return "flying"


class Swimmer:
    def swim(self):
        return "swimming"


class Duck(Flyer, Swimmer):
    def quack(self):
        return "quack"
