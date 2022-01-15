#!/usr/bin/env python

import serial
from time import time,sleep
import shutil
from kettler_config import config

class kettler():

    commands={
        #ALIAS:('COMMANDCODE',"description",'example response')
        'RESET':('RS',"reset device",'ACK'),
        'ID': ('ID',"Get device ID",'SDFB3026'),
        'FIRMWARE':('VE',"Get device firmware",'130'),
        'MODEL':('KI','get model name','SDFB    X3'),
        'STATUS':('ST',"Get status (relevant for recording)",'000     000     000     000     025     0000    00:00   000'),
        'RPM':('VS','get current rpm','070'),
        'PROGRAMS':('RP',"Get programs",'32    025    025    050    050    075    075    100    100    125    125    150    150    175    175    200    200    225    225    250    250    275    275    300    300    325    325    350    350    375    375    400    400    27    025    025    050    050    075    075    100    100    100    100    100    100    100    100    100    100    100    100    100    100    100    075    075    050    050    025    025    30    050    050    075    075    100    100    125    125    125    125    125    125    125    100    100    100    100    125    125    125    125    125    125    125    100    100    075    075    050    050    36    050    050    075    075    100    100    125    125    150    150    150    150    150    100    100    100    150    150    150    150    150    100    100    100    100    150    150    150    150    150    125    125    100    100    075    075    38    050    050    075    075    100    100    125    125    150    200    100    100    200    100    100    200    100    100    200    100    100    200    100    100    200    100    100    200    100    100    200    175    150    125    100    100    075    075    36    075    075    100    100    125    125    175    100    200    175    225    125    150    175    200    225    300    150    150    175    200    225    200    175    150    125    175    125    175    125    175    150    125    125    100    100    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00    00'),
        'COMMANDMODE':('CM',"Enter command mode",'ACK or RUN when already active'),
        'COMMANDMODE2':('CD','Enter command mode','ACK or RUN when already active'),
        'SET_POWER':('PW',"set power of x watts",'000     000     000     000     025     0000    00:00   000'),
        'SET_TIME':('PT', "set time of mmss",'000     000     000     000     025     0000    00:00   000'),
        'SET_DISTANCE':('PD',"set x/10 km distance",'000     000     000     000     025     0000    00:00   000'),
        'SET_ENERGY':('PE','set energy of x kJ','000     000     000     000     025     0000    00:00   000'),
        'RESET2':('CP','reset?CP? works after COMMANDMODE','ACK'),
        'UNKNOWN0':('CA','unknown','326'),
        'UNKNOWN1':('ES','unknown',''),
        'UNKNOWN2':('GB','unknown','00000   00000   00000'),
        'UNKNOWN3':('RD','unknown','2    326    1    0    0    0    0    0    1    0    0    1    -1    -1    -1    -1    -1    -1    0    0    025    400    075    030    020    030    040    050    060    070    080    100    120    140    000    040    080    120    180    220    320    400    460    511    003    004    006    010    017    022    033    041    046    048    005    006    011    017    030    040    063    080    089    097    007    009    015    025    044    059    097    124    142    155    009    012    020    034    060    080    133    173    199    219    011    015    025    043    076    102    170    223    260    287    013    019    031    053    094    124    209    275    322    359    016    023    037    063    110    148    250    328    385    430    022    030    050    083    146    194    329    435    514    577    028    038    063    104    181    241    410    545    647    729    035    046    077    127    220    293    496    658    781    882    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1    -1'),
        'UNKNOWN4':('SB','unknown','ACK')
    }

    #save last num_states states to evaluate countdown mode
    last_states=[]
    num_states=4
    #max age of state before force new read_state()
    max_state_age=10

    #is ergometer active
    active=False

    #is ergometer in time countdown mode and from which value?
    countdown=False
    countdown_from=0

    #variables for except / try
    last_pulse = 0
    last_rpm = 0
    last_speed = 0
    last_distance = 0
    last_power = 0
    last_energy = 0
    last_workouttime = 0
    last_actpower = 0
    last_runtime = 0.0

    #starttime of workout:
    starttime=time()

    #last state_time for timediff
    last_state_time = 0

    def __init__(self,port='/dev/ttyUSB0'):
        self.ser = serial.Serial()
        self.ser.baudrate = 9600  # 9600 is maximum !
        self.ser.port = port
        self.ser.timeout = 20
        self.ser.open()

    def reset(self):
        print("Reset: " + self.send_command('RESET'))
        print(self.ser.readline())

    def send_command(self,command_string=None,command_code=None):
        if not command_code:
            command_code=self.commands[command_string][0]
        self.ser.write(bytearray(command_code+'\r\n','utf-8'))
        response=self.ser.readline()
        #TODO: error-code
        return response.decode('utf-8')

    def read_programs(self):
        response=self.send_command('PROGRAMS')
        response=response.split('\t')
        self.programs=[]
        #not very elegant but works for now
        i=0
        while i<len(response) and int(response[i])>0:
            m=int(response[i])
            self.programs.append((m,[]))
            for x in range(m):
                i+=1
                self.programs[-1][1].append(int(response[i]))
            i+=1
        return list(map(lambda x: x[0],self.programs))

    def read_state(self):
        state=self.send_command('STATUS')
        #print(state,"\n")  # nur für Fehlersuche
        self.write_read_state_to_file(state) # die Rohwerte von read_state abspeichern
        numbers=state.split('\t')
        # empfangene Daten von Schnittstelle umwandeln von String --> Integer
        # alles mit try / except, da empfangene Daten korrupt sein könnten
        runtime = time()-self.starttime #TODO: implement runtime() function to calculate runtime from response?
        try:
            pulse = int(numbers[0])
        except:
            pulse = self.last_pulse
        try:
            rpm = int(numbers[1])
        except:
            rpm = self.last_rpm
        try:
            speed = int(numbers[2]) # 0.1km/h
        except:
            speed = self.last_speed
        try:
            distance = int(numbers[3]) # 0.1 km in m
        except:
            distance = self.last_distance
        try:
            power = int(numbers[4]) #setvalue power in Watt
        except:
            power = self.last_power
        try:
            energy = int(numbers[5])
        except:
            energy = self.last_energy
        try:
            if self.last_workouttime == 0 and len(self.last_states) > 2:
                workouttime = 0 # workout bleibt beendet !
            else:
                workouttime = 60*int(numbers[6].split(':')[0])+int(numbers[6].split(':')[1]) # in seconds
        except:
            workouttime = 0 # workout wird beendet !
            if ";" in numbers[6]:
                print("Ende Workout except wegen ;")
            else:
                print("Ende Workout except")
        try:
            act_power = int(numbers[7])
        except:
            act_power = self.last_act_power
        #timediff
        state_time = time()
        if self.last_state_time == 0:
            timediff = 1 # im 1. Durchlauf ist meist 1 sec. vergangen
        else:
            timediff = state_time - self.last_state_time
        # save last values
        self.last_pulse = pulse
        self.last_rpm = rpm
        self.last_speed = speed
        self.last_distance = distance
        self.last_power = power
        self.last_energy = energy
        self.last_workouttime = workouttime
        self.last_act_power = act_power
        self.last_runtime = runtime
        self.last_state_time = state_time
        state={
            "time"    :    state_time, # Zeit in [s] float epic time format
            "runtime":    runtime, # wird für TotalTimeSeconds verwendet in [s]
            "timediff"  : timediff, # wird für Berechnung distance verwendet [s]
            "pulse" :    pulse,
            "rpm"    :    rpm,
            "speed"    :    speed, # 0.1km/h
            "distance":    distance, # 0.1 km in m
            "power"    :    power,
            "energy":    energy, # kJ
            "workouttime"    :    workouttime, # in seconds
            "act_power":    act_power,
            "my_altitude":    int(config['MY_ALTITUDE'])
            }
        #print("\nWorkout: ",workouttime,"timediff: ",timediff,"Runtime: ",runtime)#nur für Fehlersuche
        self.set_last_state(state)
        return state

    #Den read_state in einen File schreiben    
    def write_read_state_to_file(self, state):
        filename = config['LOGFILE']
        with open(filename,'a')as f: # append data
            f.write(state)


    #Letzten State abspeichern 
    def set_last_state(self,state):  
        self.last_states.insert(0,state) #Vorne in Liste einfügen
        if len(self.last_states) > self.num_states: #Wenn mehr als 4 states in Liste
            self.last_states.pop() #Dann den letzten aus Liste löschen

    # Den letzten State aus der Liste holen
    def get_state(self):
        # Wenn Zeitunterschied letzter State und aktuelle Zeit > 10s, dann read_state() auslösen
        if len(self.last_states)>0 and time()-self.last_states[0]['time'] < self.max_state_age:
            return self.last_states[0]
        else:
            return self.read_state()

    def is_active(self):
        #TODO: distancemode?
        self.read_state()
        #last state was active, check if activity has stopped:
        if self.active:
            # Zeitdifferenz zwischen letzten State[0] und vorletztem State[1]
            workouttimediff=self.last_states[0]['workouttime']-self.last_states[1]['workouttime']
            if workouttimediff==0:
                self.active=False
            else:
                self.active=True
        #last state was inactive, check if activity hast started:
        else:
            #enough states to compare?
            if len(self.last_states) > 1:
                timediff=self.last_states[0]['time']-self.last_states[1]['time']
                workouttimediff=self.last_states[0]['workouttime']-self.last_states[1]['workouttime']
                #if workouttime has changed but not more than the time between measurements, an activity has been started
                if 0 < abs(workouttimediff) <= timediff+1:
                    self.active=True
                    self.starttime=time()-abs(workouttimediff)
                    if workouttimediff < 0:
                        self.countdown=True
                        self.countdown_from=self.last_states[1]['workouttime']
                    else:
                        self.countdown=False
                        self.countdown_from=0
                else:
                    self.active=False
            #not enough states to compare, wait 1 second and check again:
            else:
                sleep(1)
                self.active=self.is_active()
        return self.active


    def testmode(self,intervall=5,timeout=60):
        starttime=time()
        while True:
            print("----- "+str(time()-starttime)+ " -----")
            for command in sorted(self.commands):
                if 'RESET' in command:
                    continue
                if 'COMMANDMODE' in command:
                    continue
                if 'SET_' in command:
                    continue
                if command=='PROGRAMS':
                    continue
                print(command + " (" + self.commands[command][0]+ "): " + self.send_command(command))
            if time()-starttime>timeout:
                break
            sleep(intervall)

    #Testmode um STATUS zu lesen
    def testmode_read_status(self,intervall=5, timeout=15):
        starttime=time()
        while True:
            print("STATUS " + self.send_command('STATUS'))
            if time()-starttime>timeout:
                break
            sleep(intervall)



def main():
    print("kettler test script")
    ergo=kettler()

#    print(ergo.read_programs())
#    print(ergo.send_command('UNKNOWN0'))
#    print(ergo.send_command('RESET2'))
#    print(ergo.send_command('STATUS'))
#    ergo.testmode(timeout=60)
#    ergo.testmode_read_status(timeout=15)

if __name__ == "__main__":
    main()
