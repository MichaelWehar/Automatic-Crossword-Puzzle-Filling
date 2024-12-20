import time

class Timer:
    timerTotal = {}
    timerStart = {}
    @staticmethod
    def start(name):
        Timer.timerStart[name] = time.time()
        if name not in Timer.timerTotal:
            Timer.timerTotal[name] = 0.0
    @staticmethod
    def stop(name):
        Timer.timerTotal[name] += time.time() - Timer.timerStart[name]
    @staticmethod
    def total(name):
        return Timer.timerTotal[name]
    @staticmethod
    def output(name):
        print(name + ": " + str(Timer.total(name)))
    @staticmethod
    def outputAll():
        for name in Timer.timerTotal:
            Timer.output(name)
    @staticmethod
    def clearAll():
        timerTotal = {}
        timerStart = {}
