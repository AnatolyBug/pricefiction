from Instruments import *

class Portfolio():

    number_of_portfolios = 0

    def __init__(self, args, name = ''):
        self.name = name
        self.products = list(args)
        Portfolio.number_of_portfolios += 1

    def mtm(self, t, scenario=None, md=None, pr_md=None):
        mtm = 0
        for product in self.products:
            mtm += product.price(t,scenario=scenario,md=md, pr_md=pr_md)
        return mtm

    def delta(self, t, scenario=None, md=None, pr_md=None):
        dlt = 0
        for product in self.products:
            dlt += product.delta(t,scenario=scenario,md=md, pr_md=pr_md)
        return dlt

    def rho(self, t, scenario=None, md=None, pr_md=None):
        _rho = 0
        for product in self.products:
            _rho += product.rho(t,scenario=scenario,md=md, pr_md=pr_md)
        return _rho

    def add_product(self,product):
        print(self.name, ' added', str(product))
        self.products.append(product)

    def __repr__(self):
        return 'Portfolio' + self.name

    @classmethod
    def from_csv(cls, file, name=''):
        products = []
        with open(file, 'r') as file:
            for line in file:
                trade_econ = line.strip().split(',')
                instrument = trade_econ.pop(0)
                cls_inst = globals()[instrument]
                products.append(cls_inst.from_csv(trade_econ))
        file.close()
        return cls(products, name)





