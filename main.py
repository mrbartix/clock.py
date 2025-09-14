from datetime import datetime
import os, threading, readchar, yaml
from playsound3 import playsound

options = ["clock", "timer", "alarm", "face"]
currentIndex = 0
running = True

timerReset = False
timerPaused = False
timerPassed = 0

alarmFinished = False
alarmPaused = False
alarmDoIwaitforInput = False
alarmReset = True
alarmInp = "placeholderValue"
h = "placeholderValue"
m = "placeholderValue"
s = "placeholderValue" #junk, junk and junk but hey it works, i am not proud of it

timerTick = 0
alarmTick = 0 #yes i had to make two of them... junky

#get the config
with open("config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)
digits = config['ascii']['digits']
soundLocalization = config['soundPath']
soundRequired = config['soundRequired']
alarmDone = config['alarmDoneTxt']

if os.name == "posix": clearCmd = 'clear' # check the system, cuz windows is stupid and doesn't have the same cmd to clear the terminal
elif os.name == "nt": clearCmd = 'cls'

def wait(s):
    threading.Event().wait(s) # had to add wait

def InputKeys():
    global currentIndex, running, timerReset, timerPaused, alarmDoIwaitforInput, alarmPaused, alarmReset, alarmInp, h, m, s
    while True:
        key = readchar.readkey()
        if key == readchar.key.RIGHT:
            currentIndex = (currentIndex + 1) % len(options)
        if key == readchar.key.LEFT:
            currentIndex = (currentIndex - 1) % len(options)

        ### Timer things
        if currentIndex == 1 and key == "p":
            if timerPaused: #if its paused, then it will unpause
                timerPaused = False
            elif not timerPaused: #if its not paused then it will pause
                timerPaused = True
        elif currentIndex == 2 and key == "p":
            if alarmPaused: #if its paused, then it will unpause
                alarmPaused = False
            elif not alarmPaused: #if its not paused then it will pause
                alarmPaused = True            
        if currentIndex == 1 and key == "r":
            timerReset = True
        elif currentIndex == 2 and key == "r":
            alarmReset = True
            alarmInp = "placeholderValue"
            h = "placeholderValue"
            m = "placeholderValue"
            s = "placeholderValue"

        ### QUIT
        if key == "q":
            running = False
            os.system(clearCmd)
            print("Bye!")
            break
        if currentIndex == 2  and key == readchar.key.ENTER:
            alarmDoIwaitforInput = True
            break #breaks it, main will restart
    wait(0.1)


def main():

    while running: #if running == True then it will run. basically i can control it through InputKeys()
        time = datetime.now()
        os.system(clearCmd)
        print()
        print("    Press [q] to quit")
        #### MENU ####
        drawAscii("menu", options[currentIndex])

        # alarm input things so it wont just wait for u to input ;-;

        # define the thread:
            

        #### below the menu ####
        if options[currentIndex] == "clock": ######## CLOCK ########

            print()
            print()
            timeHr = time.strftime("   %H:%M:%S")
            drawAscii("time", timeHr)

            #secondary date thing

            time = datetime.now() # define the time
            day = int(time.day)
            if day in (1, 21, 31):
                suffix = "st"
            elif day in (2, 22):
                suffix = "nd"
            elif day in (3, 23):
                suffix = "rd"
            else:
                suffix = "th"
            textTime = f"{time.strftime('%A, %B the')} {day}{suffix}, {time.strftime('%Y')}"
            print()
            print(textTime.center(73))
            wait(0.1) # dont need to wait a whole 1 sec, cuz the system will give the next second when it happens so i dont need to care lol
        elif options[currentIndex] == "timer": ######## STOPWATCH ######## well its a stopwatch but who cares XD [its correct in the ui]

            global timerPassed, timerTick, timerPaused, timerReset
            if timerReset:
                timerTick = 0
                timerPassed = 0
                timerReset = False
            
            if timerTick == 10: # adds seconds     ####  IF TESTING MAKE SURE TO CHANGE IT BACK TO 10 ####
                if timerPaused:
                    timerPassed += 0
                elif not timerPaused:
                    timerPassed += 1
                timerTick = 0
                
            timerHrs = timerPassed // 3600 # calculates the numbers which will get print
            timerMins = timerPassed // 60
            timerSec = timerPassed % 60

            ## draw the time - final stage
            print("Warning: If you scroll to another option on the menu, the timer will pause")
            print()
            drawAscii("time", f"   {timerHrs:02d}:{timerMins:02d}:{timerSec:02d}")
            pauseReset("timer")
            wait(0.1)
            if not timerPaused:
                timerTick += 1
        elif options[currentIndex] == "alarm": ######## ALARM ######## again the name changed lol
            global alarmDoIwaitforInput, alarmReset, alarmPaused, alarmInp, alarmFinished, h,m,s
            print()
            if alarmReset:
                alarmFinished = True
                print("Press [ENTER] to input the time which it will count down from")
                print("This will stop you from doing anything, until you input something in")
                print("Input [-] to exit without starting a countdown")
                wait(0.1)
            if alarmDoIwaitforInput:
                print()
                alarmInp = input("Input the time, it should count down from (HH:MM:SS): ")
                try:
                    if alarmInp != "-" and alarmInp != "placeholderValue":
                        h, m, s = map(int, alarmInp.split(":"))
                        if h >= 0 and m in range(0, 59) and s in range(0, 59):
                            alarmDoIwaitforInput = False
                            alarmReset = False
                            threading.Thread(target=InputKeys, daemon=True).start()
                            threading.Thread(target=alarmTicking, daemon=True).start()
                        else:
                            alarmInp = "placeholderValue"
                            print("Error: Input error in alarm, gonna reset so you can re-input")
                            wait(1)
                    elif alarmInp == "placeholderValue":
                        print("Poof! You found an easter egg")
                        print("To punish you, I'm gonna kill this process")
                        print("Do not mess with me again")
                        wait(1)
                        print("or at least try to...")
                        print("well, I couldn't do that :c")
                        print("I'm gonna spare you!")
                        wait(5)
                        wait(0.1)                        
                    else:
                        alarmInp = "placeholderValue"
                        threading.Thread(target=InputKeys, daemon=True).start()
                        alarmDoIwaitforInput = False
                        alarmReset = True
                except:
                    print("Error: Input error in alarm, gonna reset so you can re-input")
                    wait(1)                   
            if alarmInp != "placeholderValue":
                if not alarmFinished:
                    drawAscii("time", f"   {h:02}:{m:02}:{s:02}")
                    pauseReset("alarm")
                    wait(0.1)
                elif alarmFinished:
                    drawAscii("time", "   00:00:00")
                    pauseReset("alarm")
                    print(alarmDone)
                    wait(0.1)
        elif options[currentIndex] == "face": ######## CREDITS ########
            print()
            print("   > Created by @mrbartix; MIT license")
            print("   > Visit the config [clock.conf] if you want to edit anything [WORK IN PROGRESS]")
            print("   > 13.09.2025")
            wait(0.1)

def pauseReset(mode: str): # basically i dont want to repeat the same thing like 3-4 times
    global timerPassed, alarmPaused
    print()
    if mode == "timer":
        if timerPaused:
            pausePrint = "Unpause"
            resetPrint = "Reset"
        else:
            pausePrint  = " Pause"
            resetPrint = " Reset"
        print("                         ",pausePrint,"       ",resetPrint) # this is dumb as hell but works XD
        print("                            [P]            [R] ")
    elif mode == "alarm":
        if alarmPaused:
            pausePrint = "Unpause"
            resetPrint = "Reset"
        else:
            pausePrint  = " Pause"
            resetPrint = " Reset"
        print("                         ",pausePrint,"       ",resetPrint) # this is dumb as hell but works XD
        print("                            [P]            [R] ")

def alarmTicking():
    global h, m, s, alarmFinished, alarmTick
    alarmFinished = False
    while running and not alarmFinished:
        if alarmTick == 10:
            if s > 0:
                s -= 1
            else: #if s = 0 or less
                if m > 0 and s == 0:
                    m -= 1
                    s += 59
                else: #if m = 0 or less
                    if h >  0 and m == 0:
                        h -= 1
                        m += 59
                    else: #if hour is equal to 0 then it will stop
                        alarmFinished = True
                        if soundRequired: 
                            playsound(soundLocalization) 
                        else: 
                            pass
            alarmTick = 0
        wait(0.1)
        if alarmPaused:
            alarmTick += 0
        elif not alarmPaused:
            alarmTick += 1

def drawAscii(mode, str): # moved that over from libDrawDegits since it was split between config.yaml and this script
        if mode == "time":
            for row in range(5): #does the same thing 5 times
                line = "" # creates a var which will store the line to print
                for character in str: # splits the inputed string, e. g. 12:30 to 1,2,:,3,0 
                    line += digits.get(character, ["   "]*5)[row] + "  " # searches for a key in self.digits, \\
                    # for example searches for 0 in self.digits, and then returns 5 lines of characters based on the \\
                    # dictionary, then chooses with [row] which of the outputed line to use based on the row we are on now, \\
                    # so if we are on row 0, and it was searching for 5, it will choose "███"
                print("  " , line) # prints the line which it chose to use based on its searches  in self.digits
        elif mode == "menu": #basically the same but skips splitting the characters so "clock" wont fuck up and split
            for row in range(5):
                line = ""
                line += digits.get(str, [...]*5)[row] + "  "
                print(line)

if __name__ == "__main__":
    threading.Thread(target=InputKeys, daemon=True).start()
    main()