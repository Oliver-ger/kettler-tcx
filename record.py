#!/usr/bin/env python

from time import sleep,strftime

from kettler import *
from tcx import *
from display import *

class recorder():

    ergo=kettler()
    workout=tcx()
    anzeige=display()

    intervall=5
    timeout=600
    
    #Durchschnittsberechnung Watt und Puls
    zaehler=0
    Wattsumme=0
    Pulssumme=0

    def start(self):
        self.ergo.reset()
        if (self.wait_for_workout()):
            self.record_workout()

    def wait_for_workout(self):
        starttime=time() # aktuelle Zeit holen
        while True:
            print ("\rWaiting for workout: "+ str(round(time()-starttime)) + "s", end="")
            if self.ergo.is_active():
                print()
                return True
            if time()-starttime > self.timeout: # Abbruch bei > 600s
                print()
                return False
            sleep(self.intervall)
            
            
    def values_display(self,Zeit,Watt,Puls):
        self.zaehler = self.zaehler + 1
        # Zeit-Ausgabe auf Display 
        self.anzeige.untereZeile(Zeit)
        # Watt-Ausgabe auf Display ( Durchschnitt )
        self.Wattsumme = self.Wattsumme + Watt
        Wattf = self.Wattsumme / self.zaehler #float
        self.anzeige.mittlereZeile(str(round(Wattf)))
        # Puls-Augabe auf Display
        self.Pulssumme = self.Pulssumme + Puls
        Pulsf = self.Pulssumme / self.zaehler #float
        self.anzeige.obereZeile(str(round(Pulsf)))
    
    
    def record_workout(self):
        starttime=self.ergo.starttime # aktuelle Zeit holen
        self.workout.add_activity(start=starttime) 

        #start recording
        while True:
            print("\rRecording: " + str(round(time()-starttime)) + "s",end='')
            #Letzten State holen und dazu TCX-Punkt generieren
            tcxpoint=self.kettler_to_tcx(self.ergo.get_state())
            #TCX-Punkt hinzufügen
            self.workout.add_trackpoint(tcxpoint)
            # Werte an Display
            Zeit = str(round(time()-starttime))
            Watt = int(tcxpoint['Watts'])
            Puls = int(tcxpoint['HeartRateBpm'])
            self.values_display(Zeit,Watt,Puls)
            
            sleep(self.intervall) # 5s Pause
            #is_active reads the state
            if not self.ergo.is_active():
                print()
                break # Abbruch while-loop

    def kettler_to_tcx(self,kettlerstate):
        #convert kettler state to tcx trackpoint
        tcxpoint={
            "Time"        :     kettlerstate['time'],
            "TimeDiff"  :   kettlerstate['timediff'], # Zeitdifferenz in [s]
            "HeartRateBpm"    :    kettlerstate['pulse'],
            "Cadence"    :    kettlerstate['rpm'],
            "Speed"        :    kettlerstate['speed']*100/3600,    # 0.1km/h in m/s
            "DistanceMeters":    kettlerstate['distance']*100,        # 0.1 km in m
            "AltitudeMeters":    kettlerstate['my_altitude'],            # my altitude
            "Calories"    :    int(kettlerstate['energy']*0.239006),    # kJ in kcal
            "TotalTimeSeconds":    kettlerstate['runtime'],        # in seconds
            "Watts" :   kettlerstate['power'] # in Watts, Sollwert statt Istwert
            }
        return tcxpoint


    def test_workout(self):
        self.workout.add_activity()
        self.workout.set_starttime(time())
        self.workout.add_trackpoint({"workouttime":5,"DistanceMeters":100,"Speed":10,"Watts":200})
        self.workout.add_trackpoint({"workouttime":7,"DistanceMeters":200,"Speed":20,"Calories":100})

    def save(self,filename="Ergo_"+strftime("%Y_%m_%d_%H-%M-%S")+".tcx"): # write filename with date & time
        self.workout.write_xml(filename)


def main():
    print("Wait for key_1")
    rec=recorder()
    rec.anzeige.start_display()
    rec.anzeige.untereZeile('Wait')
    # Wartet solange bis key_1 gedrückt wurde
    while (True):
        on = rec.anzeige.key1()
        if on==1:
            break
    print("kettler recording script")
    rec.anzeige.untereZeile('Start')
    rec.start()
    rec.save()


if __name__ == "__main__":
    main()





