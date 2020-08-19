class Car:
    def __init__(self,a):
        self.a = a

    def add(self, b):
        return self.a + b

class Mercedes(Car):
    def __init__(self,c):
        self.c = c
        super().__init__(c)

m = Mercedes.from_csv(1,2)

print (m.a)