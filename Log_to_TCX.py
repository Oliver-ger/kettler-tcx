#!/usr/bin/env python

from time import time,sleep,strftime
import shutil
from kettler_config import config
from tcx import *



#Read log file and convert to states        
class logreader():

    #save last num_states states to evaluate countdown mode
    last_states=[]

    #last workout time
    last_workouttime = 0
    first_run = True #erster Durchlauf
        

    #State vom kettlerstate_log.txt lesen
    def read_state_from_file(self):
        # Zugriff auf Methode iso8691_to_time aus Klasse tcx
        time_first_run = tcx.iso8601_to_time(self,config['START_TRAINING'])+3600 # Korrektur +1h
        filename = config['LOGFILE']
        f=open(filename,'r')
        for raw_state in f:
            numbers = raw_state.split('\t')
            #print(numbers) # Kontrolle
            workouttime = 60*int(numbers[6].split(':')[0])+int(numbers[6].split(':')[1]) # in seconds
            # Berechnung timediff aus workouttime und last_workouttime
            if self.first_run: #wenn 1. Durchlauf
                runtime = 0
                self.last_workouttime = workouttime
                time_for_state = time_first_run # time_for_state wird auf eigene Startzeit gesetzt
                self.first_run = False
            timediff = self.last_workouttime - workouttime
            self.last_workouttime = workouttime
            # Fortlaufende time_for_state in [s] epic format , startet bei 0 + berechnete timediff aus workouttime
            time_for_state = time_for_state + timediff
            # Fortlaufende Runtime in [s], startet bei 0 + berechnete timediff aus workouttime
            runtime = runtime + timediff 
            #print("Runtime: ",runtime, " TimeDiff: ",timediff," TimeForState: ",time_for_state) # Kontrolle
            state={
                "time"    :   time_for_state, # letzte Zeit + Zeitdifferenz in [s] float epic time format                
                "runtime":    runtime, # wird für TotalTimeSeconds verwendet in [s]
                "timediff"  :   timediff, # Zeitdifferenz zum letzten Eintrag time
                "pulse" :    int(numbers[0]),
                "rpm"    :    int(numbers[1]),
                "speed"    :    int(numbers[2]), # 0.1km/h
                "distance":    int(numbers[3]), # 0.1 km in m
                "power"    :    int(numbers[4]),
                "energy":    int(numbers[5]), # kJ
                "workouttime"    :    workouttime, # in seconds
                "act_power":    int(numbers[7]),
                "my_altitude":    int(config['MY_ALTITUDE'])
            }
            self.append_state_to_list(state) # neuen state in die Liste last_states hinten anhängen         
        pass

    #einen State in die Liste hinten anhängen
    def append_state_to_list(self,state):
        self.last_states.append(state)



class write_state_to_tcx():

    workout=tcx() # Objekt von Klasse tcx anlegen
    reader = logreader() # Objekt von Klasse log_reader anlegen

    #start read from states and write xml
    def gen_tcx_from_log(self):
        self.workout.add_activity()
        self.workout.lap.set("StartTime",config['START_TRAINING']) # Startzeit selber setzen
        self.workout.set_id(config['START_TRAINING']) # Id mit eigener Startzeit setzen
        self.reader.read_state_from_file() # Methode der anderen Klasse aufrufen
        amount = len(self.reader.last_states)
        print("Generating datapoints: ", amount)
        for x in self.reader.last_states:
            tcxpoint=self.kettler_to_tcx(x) # x ist ein einzelner state
            self.workout.add_trackpoint(tcxpoint)
        self.save()
        

    def kettler_to_tcx(self,kettlerstate):
        #convert kettler state to tcx trackpoint
        tcxpoint={
                "Time"        :     kettlerstate['time'],
                "TimeDiff"  :   kettlerstate['timediff'], # wird nicht benutzt
                "HeartRateBpm"    :    kettlerstate['pulse'],
                "Cadence"    :    kettlerstate['rpm'],
                "Speed"        :    kettlerstate['speed']*100/3600,    # 0.1km/h in m/s
                "DistanceMeters":    kettlerstate['distance']*100,        # 0.1 km in m
                "AltitudeMeters":    kettlerstate['my_altitude'],            # my altitude
                "Calories"    :    int(kettlerstate['energy']*0.239006),    # kJ in kcal
                "TotalTimeSeconds":    kettlerstate['runtime'],        # in seconds
                "Watts" :   kettlerstate['power'] # in Watts
                }
        return tcxpoint


    def save(self,filename="Ergo_"+strftime("%Y_%m_%d_%H-%M-%S")+".tcx"): # write filename with date & time
        self.workout.write_xml(filename)


def main():
    print("kettler generating tcx from logfile")
    writer=write_state_to_tcx()
    writer.gen_tcx_from_log()


if __name__ == "__main__":
    main()

