class Car:
    def __init__(self, car_type, Vexpected, Vcurrent, length, lane, position, visible_distance, index, stat):
        self.car_type = car_type
        self.Vexpected = Vexpected
        self.Vcurrent = Vcurrent
        self.length = length
        self.lane = lane
        self.position = position
        self.frontCar = None
        # need to change these into functions later
        self.safePassDistanceBack = self.length
        self.safeGoBackDistanceBack = self.length
        self.safeGoBackDistanceFront = self.length
        self.acceleration = 0
        self.DELTA_TIME = 0.05
        self.MAX_SPEED = 60
        self.goal = None
        self.targetSpeed = self.Vexpected
        self.index = index
        # need to change it to a function later
        self.reactionTime = 0.2

        self.visible_distance = visible_distance

        
        ''' this affects accident rate a lot'''
        self.expected_acceleration = self.Vexpected / 2

        self.stat = stat
        self.stat.increase("num_of_cars_generated", 1)

    def _getCarAtFront(self, all_cars, lane):
        minDistance = 100000
        result = None
        for each in all_cars:
            if each == None:
                continue
            if 0 < each.position - self.position < minDistance and each.lane == lane:
                minDistance = each.position - self.position
                result = each
        return result
                
            


    def _getCarAtBack(self, all_cars, lane):
        minDistance = 100000
        result = None
        for each in all_cars:
            if each == None:
                continue
            if 0 < self.position - each.position < minDistance and each.lane == lane:
                minDistance = self.position - each.position
                result = each
        return result

    def _shouldPassCars():
        pass

    def _haveIntentToPass(self, frontCar):
        ##            print("Oh I see front car: ", str(frontCar.position - self.position))
        if frontCar != None \
               and frontCar.position - frontCar.length - self.position < self.visible_distance \
               and self.Vexpected > frontCar.Vcurrent:
            self.stat.increase("passing_intents", 1)
            return True
        return False

    def move(self, all_cars):
        if self.lane == 'r':
            frontCar = self._getCarAtFront(all_cars, 'r')
            if self._haveIntentToPass(frontCar):
##                print("     I have intent to pass!")
##                print()
                # have intent to pass
                # check capability to pass

                if self._capableToPass(all_cars,frontCar):
##                    print("     I am on left lane!")
##                    print()
                    self.goal = frontCar
                    self.lane = 'l'
                    self.acceleration = self.expected_acceleration
                    self.targetSpeed = self.MAX_SPEED + 5
                    self._updateAttributes()
                    return
                else:
                    # have intent but no capability to pass
                    if self._haveAccident(frontCar):
##                        print("     Crap! Accident on right lane!")
                        all_cars[self.index] = None
                        all_cars[frontCar.index] = None
                    self.acceleration = -1 * self.expected_acceleration
                    self.targetSpeed = frontCar.Vcurrent
                    self._updateAttributes()
                    return
            else:
                # have no intent to pass
                self._updateAttributes()
                return

            #self.position += self.Vcurrent * self.DELTA_TIME
        elif self.lane == 'l':
            if self._capableToGoBack(all_cars):
                self.lane = 'r'
##                print("     Yay I am back!")
                self.goal = None
                self.acceleration = -1 * self.expected_acceleration
                self.targetSpeed = self.Vexpected
                if self.Vcurrent >= self.targetSpeed:
                    self.acceleration = -1 * self.expected_acceleration
                else:
                    self.acceleration = self.expected_acceleration
##                self.Vcurrent = self.Vexpected

            else:
                frontCar = self._getCarAtFront(all_cars, 'l')
                if frontCar != None:
                    if frontCar.position - self.position < self.visible_distance and \
                       frontCar.Vcurrent < self.Vcurrent:
                            self.targetSpeed = frontCar.Vcurrent
                            self.acceleration = -1 * self.expected_acceleration
                    else:
                        self.acceleration = self.expected_acceleration
                        self.targetSpeed = self.MAX_SPEED + 5

                if self._haveAccident(frontCar):
##                    print("     Crap! Accident!")
                    all_cars[self.index] = None
                    all_cars[frontCar.index] = None
                    
            self._updateAttributes()
            return

    def _haveAccident(self, frontCar):
        if frontCar == None or self.Vcurrent <= frontCar.Vcurrent:
            return False
        
        TTC = self._getTTC(frontCar)
        if TTC < self.reactionTime:
            self.stat.increase("num_of_accidents", 1)
            return True
        return False
        
    def _getTTC(self, frontCar):
        distance = frontCar.position - frontCar.length - self.position
##        print("with car", frontCar.index, " distance: ", distance, " speed difference: ", self.Vcurrent - frontCar.Vcurrent)
##        print("TTC: ", distance / (self.Vcurrent - frontCar.Vcurrent) )
        return distance / (self.Vcurrent - frontCar.Vcurrent)


        

    def _capableToPass(self, all_cars, frontCar):
        frontLeftCar = self._getCarAtFront(all_cars, 'l')
        backLeftCar = self._getCarAtBack(all_cars, 'l')
        if frontLeftCar == None and backLeftCar == None:
            return True
        elif frontLeftCar == None:
            if self.position - backLeftCar.position > self.safePassDistanceBack:
                return True
        elif backLeftCar == None:
            if frontLeftCar.position - frontLeftCar.length - self.position \
               > frontCar.position - frontCar.length - self.position:
                return True
        else:
            if self.position - backLeftCar.position > self.safePassDistanceBack and \
               frontLeftCar.position - frontLeftCar.length - self.position \
               > frontCar.position - frontCar.length - self.position:
                return True
        return False
               
    def _capableToGoBack(self, all_cars):
##        print("     Checking if capable to go back")
        capable = False
        if self.goal == None or self.goal.lane == 'l':
            capable = True
        elif self.position - self.length - self.goal.position - self.safeGoBackDistanceBack > 0:
            capable = True

        if capable == True:
            frontCar = self._getCarAtFront(all_cars, 'r')
            backCar = self._getCarAtBack(all_cars, 'r')
            if frontCar == None and backCar == None:
                self.stat.increase("successful_passings", 1)
                return True
            elif frontCar == None:
                if self.position - self.length - backCar.position > self.safeGoBackDistanceBack:
                    self.stat.increase("successful_passings", 1)
                    return True
            elif backCar == None:
                if frontCar.position - frontCar.length - self.position > self.safeGoBackDistanceFront:
                    self.stat.increase("successful_passings", 1)
                    return True
            elif frontCar.position - frontCar.length - self.position > self.safeGoBackDistanceFront and \
                 self.position - self.length - backCar.position > self.safeGoBackDistanceBack:
                self.stat.increase("successful_passings", 1)
                return True
        return False
    
    def _updateAttributes(self):
        # can update self.safePassDistanceBack
        # can update self.acceleration
        self.Vcurrent += self.acceleration * self.DELTA_TIME
        self.position += self.Vcurrent * self.DELTA_TIME

        if (self.Vcurrent > self.targetSpeed and self.acceleration > 0)\
           or (self.Vcurrent < self.targetSpeed and self.acceleration < 0):
            self.Vcurrent = self.targetSpeed
            self.acceleration = 0
        
