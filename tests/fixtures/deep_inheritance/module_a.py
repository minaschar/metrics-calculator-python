class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        raise NotImplementedError


class Mammal(Animal):
    def __init__(self, name, fur_color):
        super().__init__(name)
        self.fur_color = fur_color


class Dog(Mammal):
    def speak(self):
        return "Woof"


class Puppy(Dog):
    def speak(self):
        return "Yip"
