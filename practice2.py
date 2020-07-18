class Car:
    def __init__(self,a):
        self.a = a

    @classmethod
    def from_csv(cls, a,b):
        print(a)
        return cls(a+b)

class Mercedes(Car):

    pass

m = Mercedes.from_csv(1,2)

print (m.a)