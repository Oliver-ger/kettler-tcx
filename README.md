# kettler-tcx
Generate tcx files from Kettler ergometer

#Hardware
Raspberry Pi Zero W
1.44" LCD Display HAT for Raspberry Pi from WAVESHARE with 3 keys

#Installation
Nothing fancy. Download in some folder...

#Usage
Connect Kettler Ergometer with usb or serial port. Set serial port in source code, if necessary. Defaults to '/dev/ttyUSB0'.
I'm using a Kettler X7 Ergometer which runs with the software.

Start record.py. or record_without_display.py 
If using the Waveshare display then press key No.1.
The script resets the ergometer and waits for activity (timer on ergometer starts running).
The script records until activity stops (timer on ergometer does not 
change for 5 seconds). Afterwards the workout is saved to a file named Ergo_YEAR_MONTH_DAY_TIME.TCX

During the training another log file is written. Ever 5sec. the actual trainig data are appended to the log file.
With this logfile and the program LOG_TO_TCX.py a TCX-file can be generated afterwards, too.
This is useful, if an unexpected error occurs during training and the record.py didn't generated a tcx-file.

After training the tcx-file can be uploaded to Garmin Connect for example.


![Ergo0](https://user-images.githubusercontent.com/61313720/156410494-83b71616-7332-4ade-a6c5-c4bce731c720.JPG)
![ergo1](https://user-images.githubusercontent.com/61313720/156410526-e60a27dc-fd55-4892-bce5-4864a6819181.jpg)
