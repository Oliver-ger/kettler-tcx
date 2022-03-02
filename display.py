#!/usr/bin/env python
import LCD_1in44
import LCD_Config
import RPi.GPIO as GPIO

from PIL import Image,ImageDraw,ImageFont,ImageColor
from time import sleep, time

KEY1_PIN = 21
KEY2_PIN = 20

class display():
    LCD = LCD_1in44.LCD()
        
    def __init__(self):
        # init GPIO
        GPIO.setmode(GPIO.BCM) 
        #GPIO.cleanup()
        GPIO.setup(KEY1_PIN,GPIO.IN,pull_up_down=GPIO.PUD_UP) # Input with pull-up
        GPIO.setup(KEY2_PIN,GPIO.IN,pull_up_down=GPIO.PUD_UP) # Input with pull-up
        # init LCD
        #Lcd_ScanDir = LCD_1in44.U2D_R2L  #( ok für RaspiZero )
        Lcd_ScanDir = LCD_1in44.D2U_L2R  #(oben-unten vertauscht->Raspi3)
        self.LCD.LCD_Init(Lcd_ScanDir)
        self.LCD.LCD_Clear()
        # Display schwärzen
        self.image = Image.new("RGB", (self.LCD.width, self.LCD.height))
        # eigene draw Variable anlegen
        draw = ImageDraw.Draw(self.image)
        # ausführen
        self.LCD.LCD_ShowImage(self.image,0,0)
        
    def start_display(self):
        # eigene draw Variable anlegen
        draw = ImageDraw.Draw(self.image)
        # blauen Rand zeichnen
        draw.line([(0,0),(127,0)], fill = "BLUE",width = 5)
        draw.line([(127,0),(127,127)], fill = "BLUE",width = 5)
        draw.line([(127,127),(0,127)], fill = "BLUE",width = 5)
        draw.line([(0,127),(0,0)], fill = "BLUE",width = 5)
        # ausführen
        self.LCD.LCD_ShowImage(self.image,0,0)
        
    def obereZeile(self, Wert='xxx'):
        # eigene draw Variable anlegen
        draw = ImageDraw.Draw(self.image)
        # Schriftart
        fontsize = 34
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',fontsize)
        # draw Rechteck li oben , re unten
        draw.rectangle([(4,4),(123,43)],fill = "BLUE")
        # draw Text 
        draw.text((5,7),Wert,font=font, fill = "WHITE")
        # ausführen
        self.LCD.LCD_ShowImage(self.image,0,0)
        
        
    def mittlereZeile(self, Wert='xxx'):
        # eigene draw Variable anlegen
        draw = ImageDraw.Draw(self.image)
        # Schriftart
        fontsize = 34
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',fontsize)
        # draw Rechteck li oben , re unten
        draw.rectangle([(4,46),(123,85)],fill = "RED")
        # draw Text 
        draw.text((5,48),Wert+'W',font=font, fill =(162,255,0))
        # ausführen
        self.LCD.LCD_ShowImage(self.image,0,0)
        
        
    def untereZeile(self, Wert='xxx'):
        # eigene draw Variable anlegen
        draw = ImageDraw.Draw(self.image)
        # Schriftart
        fontsize = 31
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',fontsize)
        # draw Rechteck li oben , re unten
        draw.rectangle([(4,86),(123,123)],fill ="BLUE")
        # draw Text 
        draw.text((5,88),Wert,font=font, fill = "WHITE")
        # ausführen
        self.LCD.LCD_ShowImage(self.image,0,0)
        
    
    def counter(self):
        if time() > self.end_time:
            self.end_time = time() + 0.1
            self.zaehler = self.zaehler + 1
        return(self.zaehler)
    
    
    def key1(self):
        if GPIO.input(KEY1_PIN) == 0: # button is pressed
            state = 1
        else: # button is released
            state = 0
        return(state)
    
    
    def key2(self):
        if GPIO.input(KEY2_PIN) == 0: # button is pressed
            state = 1
        else: # button is released
            state = 0
        return(state)
    
    # Sekunden in h:m:s wandeln
    def convertSecInhms(self,seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        out_hms= str("%d:%02d:%02d" % (h, m, s))
        return out_hms
        
    
        
def main():
    print("Display Test")
    Raspi_Display=display()
    Raspi_Display.start_display()
    Raspi_Display.obereZeile('1009')
    Raspi_Display.mittlereZeile('123')
    #Raspi_Display.untereZeile('5678')
    Raspi_Display.zaehler=0
    Raspi_Display.end_time=time()
    mem = 0
    while (True):
        on = Raspi_Display.key1()
        off = Raspi_Display.key2()
        if on==1:
            mem = 1
        elif off==1:
            mem = 0
        if mem==1:
            ctr_sec = Raspi_Display.counter()
            ctr_hms = Raspi_Display.convertSecInhms(ctr_sec)
            Raspi_Display.untereZeile(ctr_hms)
            print("\rZähler: ",ctr_hms,end='')
            
if __name__ == "__main__":
    main()
