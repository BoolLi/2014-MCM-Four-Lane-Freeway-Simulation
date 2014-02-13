from Car import Car
from Statistics import Statistics
import random
import math

def writeToFile(l, fName):
    f = open(fName, 'w')
    s = ''
    for each in l:
        s += str(each) + "\n"
    f.write(s)
    f.close()
    print(fName + " complete")

class Road:
    def __init__(self):

        # all variables here
        self.TOTAL_TIME = 15000
        self.NUM_OF_CARS = 200000
        self.DELTA_TIME = 0.05
        self.PERCENT_OF_CARS = [0.3,0.7]

        # Units: m/delta_t
        self.AVG_SPEED_OF_CARS = {'s': 30, 'm': 25, 'b': 20}
        self.STD_DEV_OF_CARS = {'s': 10, 'm':10, 'b': 10}
        
        # Units: m
        self.LENGTHS_OF_CARS = {'s': 5, 'm': 7, 'b': 10}
        self.VISIBLE_DISTANCE_OF_CARS = {'s': 70, 'm': 80, 'b': 90}

        # Units: m/delta_t
        self.MIN_SPEED = 15
        self.MAX_SPEED = 60

        # Units: m
        self.ROAD_LENGTH = 5000
        self.SAFE_DISTANCE_BETWEEN_CARS = 20
        ''' this affects accident rate a lot'''
        self.INITIAL_DISTANCE_BETWEEN_CARS = 80

        self._recycledIndexes = set()
        
        self.all_cars = []

        self.current_num_of_cars = 0

        self.stat = Statistics()
        
        self.generateCar(self.generateIndex())
        for time in range(self.TOTAL_TIME):
            if self.needToGenerateCars():
                self.generateCar(self.generateIndex())
##                print("New Car generated")
##                print(self._recycledIndexes)
##                print()
                
            num_of_cars_on_r = 0
            num_of_cars_on_l = 0
            total_speed_on_r = 0
            total_speed_on_l = 0
            for i in range(len(self.all_cars)):
                each = self.all_cars[i]
                if each == None:
                    self._recycledIndexes.add(i)
                    continue
                if each.position > self.ROAD_LENGTH:
                    self.all_cars[i] = None
                    self._recycledIndexes.add(i)
##                    print(each.index, "th car reaches the end of the road!")
##                    print(self._recycledIndexes)
                    continue
##                print(each.index, "th car: ", each.position, " lane: ", each.lane)
##                print()
                each.move(self.all_cars)

###################################################Statistics################################
                if each.lane == 'r':
                    num_of_cars_on_r += 1
                    total_speed_on_r += each.Vcurrent
                elif each.lane == 'l':
                    num_of_cars_on_l += 1
                    total_speed_on_l += each.Vcurrent

            self.stat.listIncrease("density_of_r", time, num_of_cars_on_r / self.ROAD_LENGTH)
            self.stat.listIncrease("density_of_l", time, num_of_cars_on_l / self.ROAD_LENGTH)

            if num_of_cars_on_r == 0:
                    self.stat.listIncrease("avg_speed_on_r", time, 0)
            else:
                self.stat.listIncrease("avg_speed_on_r", time, total_speed_on_r / num_of_cars_on_r)
                    
            if num_of_cars_on_l == 0:
                    self.stat.listIncrease("avg_speed_on_l", time, 0)
            else:
                self.stat.listIncrease("avg_speed_on_l", time, total_speed_on_l / num_of_cars_on_l)
            
            time += self.DELTA_TIME


        print("accident rate: ", self.stat.getRate("num_of_accidents", "num_of_cars_generated"))
        print("succussful passing rate: ", self.stat.getRate("successful_passings", "passing_intents"))

        writeToFile(self.stat.getList("density_of_r"), "density_of_r.txt")
        writeToFile(self.stat.getList("density_of_l"), "density_of_l.txt")
        writeToFile(self.stat.getList("avg_speed_on_r"), "avg_speed_on_r.txt")
        writeToFile(self.stat.getList("avg_speed_on_l"), "avg_speed_on_l.txt")
##        print("density of lane r: ", self.stat.getList("density_of_r"))
##        print("density of lane l: ", self.stat.getList("density_of_l"))
##        print("Average speed on lane r: ", self.stat.getList("avg_speed_on_r"))
##        print("Average speed on lane l: ", self.stat.getList("avg_speed_on_l"))        

    #############
##        f.write(s)
##        f.close()
  ####################      

    def generateIndex(self):
        if len(self._recycledIndexes) > 0:
            return self._recycledIndexes.pop()
        else:
            return len(self.all_cars)

        
    def needToGenerateCars(self):
        # base cases
        if len(self.all_cars) == 0:
            return True
        if len(self.all_cars) >= self.NUM_OF_CARS:
            return False

        
        car = self.all_cars[len(self.all_cars) - 1]
        if car == None or car.position >= self.INITIAL_DISTANCE_BETWEEN_CARS:
            return True
        return False

    
    def generateRandomType(self):
        a = random.random()
        percent_of_cars = self.PERCENT_OF_CARS
        if a < percent_of_cars[0]:
            return 's'
        elif a >= percent_of_cars[0] and a < percent_of_cars[1]:
            return 'm'
        else:
            return 'b'

    def generateCar(self, index):
        typeOfCar = self.generateRandomType()
        Vcurrent = -1
        
        while(Vcurrent < self.MIN_SPEED or Vcurrent > self.MAX_SPEED):
            u = self.AVG_SPEED_OF_CARS[typeOfCar]
            std_dev = self.STD_DEV_OF_CARS[typeOfCar]
            u1 = random.random()
            u2 = random.random()
            z = (-2*math.log(u1))**(0.5)*math.cos(2*math.pi*u2)
            Vcurrent = u + std_dev*z
        
        Vexpected = Vcurrent
        length = self.LENGTHS_OF_CARS[typeOfCar]
        visible_distance = self.VISIBLE_DISTANCE_OF_CARS[typeOfCar]
        car = Car(typeOfCar, Vexpected, Vcurrent, length, 'r', 0, visible_distance, index, self.stat)
        if index >= len(self.all_cars):
            self.all_cars += [car]
        else:
            self.all_cars[index] = car
        

def calculateTrafficFlow(curDensity, curSpeed, otherDensity, otherSpeed, a, out):
    curDensityList = [float(line.strip()) for line in open(curDensity)]
    otherDensityList = [float(line.strip()) for line in open(otherDensity)]
    curSpeedList = [float(line.strip()) for line in open(curSpeed)]
    otherSpeedList = [float(line.strip()) for line in open(otherSpeed)]
    u = 26.83
    tau = 3
    dt = a.DELTA_TIME
    w = -6.67
    k = 0
    fOut = open(out, 'w')
    result = ""
    
    for i in range(len(curDensityList)):
        density = curDensityList[i]
        S = dt * u * density
        delta_V = max(0, otherSpeedList[i] - curSpeedList[i])
        L = S * delta_V / (u**2 * tau * dt)
        T = (S - L/u)/dt
        miu = w*(k - density)

        Sother = dt * u * otherDensityList[i]
        delta_V_other = max(0, curSpeedList[i] - otherSpeedList[i])
        Lother = Sother * delta_V_other / (u**2 * tau * dt)
        if T + u*dt*Lother == 0:
            gamma = 1
        else:
            gamma = min(1, miu/(T + u*dt*Lother))
        q = gamma * T
        result += str(q) + '\n'
    fOut.write(result)
    fOut.close()
    print(out + " complete")
        


def main():
    a = Road()
    calculateTrafficFlow("density_of_r.txt", "avg_speed_on_r.txt", "density_of_l.txt", "avg_speed_on_l.txt", a, "traffic_flow_of_r.txt")
    calculateTrafficFlow("density_of_l.txt", "avg_speed_on_l.txt", "density_of_r.txt", "avg_speed_on_r.txt", a, "traffic_flow_of_l.txt")
