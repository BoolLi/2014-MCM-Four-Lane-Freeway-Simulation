class Statistics:
    def __init__(self):
        self.numbers = {}
        self.rates = {}
        self.list = {}

        
    def increase(self, type, num):
        if type in self.numbers:
            self.numbers[type] += num
        else:
            self.numbers[type] = num

    def getRate(self, type1, type2):
        if type2 not in self.numbers:
            return False
        elif type2 == 0:
            return type2 + " is 0"
        else:
            if type1 not in self.numbers:
                self.numbers[type1] = 0
            return self.numbers[type1] / self.numbers[type2]

    def getList(self, type):
        if type not in self.list:
            return False
        else:
            return self.list[type]
    
    def listIncrease(self, type, index, num):
        if type in self.list:
            l = self.list[type]
            if index < len(l):
                l[index] += num
            else:
                l += [num]
        else:
            self.list[type] = [num]

