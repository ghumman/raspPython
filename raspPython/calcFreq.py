import RPi.GPIO as GPIO #GPIO pins for raspberry pi 
import time 		# for using functions like time	
from time import sleep	# for giving some delay
from sys import argv	# for taking argument at command line
import datetime		# for displaying current time 

# make the argument equal to filename
script, filename = argv 

# write starting application time in the text file
target = open(filename, 'a') # open and append the file
target.write("Starting time of application: ")
t = datetime.datetime.now()
target.write(t.strftime('%1:%M:%S%p %Z on %b %d, %Y\n'))	# convert current to format ' 10:49AM on Dec 29, 2016'
target.close()


# Define constants
constInputSignal = 25
constOutputLatch = 24
constMinFreq = 4

# don't show me warnings like GPIO pin is already being used by other processes, just overwrite it. 
GPIO.setwarnings(False)

# We'll be using GPIO BCM notation for pinouts of raspberry pi
GPIO.setmode(GPIO.BCM)

# Set Pin 25 to take input from signal whose frequency we need to measure
# Set 24 to output
GPIO.setup(constInputSignal, GPIO.IN)
GPIO.setup(constOutputLatch, GPIO.OUT)

# Initialization of variables. We need to have finalTime so that we can use this value for initial frequency calculation
finalTime = time.time() 
frequency = 0
GPIO.output(constOutputLatch, 0)
lowFreq = 0

# callback funciton: occur whenever we get a rising edge interrupt
# frequency = 1 / duration
# duratation = time of current rising edge - time of previous rising edge
def my_callback(channel):
	if GPIO.input(constInputSignal):
		global finalTime
		global frequency
		start = time.time()
		duration = start - finalTime 
		frequency = 1 / duration
		print frequency
		finalTime = time.time() 

# call funciton-> my_callback whenever we get rising edge at pin 25	
GPIO.add_event_detect(constInputSignal, GPIO.RISING, callback=my_callback, bouncetime=80)

# if frequency is less than 4 increment lowFreq
# if lowFreq is increment to 4 set the pin 24 
try: 
	while True:
		currentTime = time.time()
		elapsedTime = currentTime - finalTime
		if elapsedTime > 5:
			frequency = 0	
		if frequency < constMinFreq: 
			lowFreq+=1
			if lowFreq > 4:
				GPIO.output(constOutputLatch, 1)
				target = open(filename, 'a') # open and append the file
				tn = datetime.datetime.now()
				target.write(tn.strftime('%1:%M:%S%p %Z on %b %d, %Y: '))	# convert current to format ' 10:49AM on Dec 29, 2016'
				target.write("Frequency has gone below 4\n")
				print "Frequency has gone below 4"
				target.close()
		
		# if frequency is greater than 4, lowFreq needs to get corrected again
		# following will stabilize the logic. And will make logic more deterministic
		else :
			if lowFreq > 0:
				lowFreq-=1
		
		# add one second delay
		sleep(1)


# release every gpio pin 
finally:
	GPIO.cleanup()


