from lxml import etree
from time import time,strftime,gmtime,strptime,mktime

class tcx:
	#Namespaces:
	XML_NS="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
	XSI_NS="http://www.w3.org/2001/XMLSchema-instance"
	XSD_NS="http://www.w3.org/2001/XMLSchema"
	NS2_NS="http://www.garmin.com/xmlschemas/ActivityExtension/v2"
	#Schemalocation:
	XML_SCHEMA="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"


	def __init__(self):
		NS_MAP={None: self.XML_NS, "xsi": self.XSI_NS, "xsd": self.XSD_NS , "ns2": self.NS2_NS}
		self.tcx = etree.Element("TrainingCenterDatabase" , nsmap=NS_MAP)
		self.tcx.set("{%s}schemaLocation" % self.XSI_NS, self.XML_SCHEMA)

		self.starttime=time()
		self.activities = etree.SubElement(self.tcx, "Activities")
		self.trackpoints=[]

	def time_to_iso8601(self,time):
		return strftime("%Y-%m-%dT%H:%M:%SZ",gmtime(time))

	def iso8601_to_time(self,iso):
		time=strptime(iso, "%Y-%m-%dT%H:%M:%SZ")
		return mktime(time)

	def add_activity(self):
		self.activity=etree.SubElement(self.activities, "Activity", Sport="Other")
		self.id=etree.SubElement(self.activity, "Id")

		self.lap=etree.SubElement(self.activity, "Lap", StartTime="2015")

		self.totaltime=etree.SubElement(self.lap, "TotalTimeSeconds")
		etree.SubElement(self.lap, "DistanceMeters").text="100"
		etree.SubElement(self.lap, "MaximumSpeed").text="1.0"
		etree.SubElement(self.lap, "Calories").text="100"
		etree.SubElement(self.lap, "Intensity").text="Active"
		etree.SubElement(self.lap, "TriggerMethod").text="Manual"
		self.track=etree.SubElement(self.lap, "Track")

	def set_id(self,id=None):
		if not id:
			id=self.time_to_iso8601(self.starttime)
		self.id.text=id

	def set_starttime(self,time=None):
		if not time:
			self.lap.set("StartTime",self.time_to_iso8601(self.starttime))

	def set_totaltime(self,time=None):
		if not time:
			if self.trackpoints:
				starttime=self.iso8601_to_time(self.id.text)

				for element in self.trackpoints[-1].iter("Time"):
					endtime=self.iso8601_to_time(element.text)
				totaltime=endtime-starttime
			else:
				totaltime=0
			self.totaltime.text=str(totaltime)

	def add_trackpoint(self,point):

		self.trackpoints.append(etree.SubElement(self.track, "Trackpoint"))
		if "workouttime" in point:
			#calculate time from starttime
			timestring=self.time_to_iso8601(self.starttime+point["workouttime"])

		elif "Time" in point:
			timestring=point["Time"]
		etree.SubElement(self.trackpoints[-1], "Time").text=timestring

#<xsd:element name="Time" type="xsd:dateTime"/>

#<xsd:element name="Position" type="Position_t" minOccurs="0"/>
		if "Position" in point:
			etree.SubElement(self.trackpoints[-1], "Postion").text=str(point["Position"])

#<xsd:element name="AltitudeMeters" type="xsd:double" minOccurs="0"/>
		if "AltitudeMeters" in point:
			etree.SubElement(self.trackpoints[-1], "AltitudeMeters").text=str(point["AltitudeMeters"])

#<xsd:element name="DistanceMeters" type="xsd:double" minOccurs="0"/>
		if "DistanceMeters" in point:
			etree.SubElement(self.trackpoints[-1], "DistanceMeters").text=str(point["DistanceMeters"])

#<xsd:element name="HeartRateBpm" type="HeartRateInBeatsPerMinute_t" minOccurs="0"/>
		if "HeartRateBpm" in point:
			etree.SubElement(self.trackpoints[-1], "HeartRateBpm").text=str(point["HeartRateBpm"])

#<xsd:element name="Cadence" type="CadenceValue_t" minOccurs="0"/>
		if "Cadence" in point:
			etree.SubElement(self.trackpoints[-1], "Cadence").text=str(point["Cadence"])

#<xsd:element name="SensorState" type="SensorState_t" minOccurs="0"/>
		if "SensorState" in point:
			etree.SubElement(self.trackpoints[-1], "SensorState").text=str(point["SensorState"])
#<xsd:element name="Extensions" type="Extensions_t" minOccurs="0">



	def write_xml(self,filename):
		tree = etree.ElementTree(self.tcx)
		tree.write(filename,pretty_print=True, xml_declaration=True,encoding='utf-8')