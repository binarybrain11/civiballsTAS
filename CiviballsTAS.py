import pyautogui
import pynput
import time
import os
import numpy as np

class TASBOT:
    def __init__(self, x = None, y = None, xmax = None, ymax = None):
        self.x = x
        self.y = y
        self.xmax = xmax
        self.ymax = ymax
        if not (x is None or y is None or xmax is None or ymax is None):
            self.xscale = self.xmax - self.x
            self.yscale = self.ymax - self.y
        else:
            self.xscale = None
            self.yscale = None
        self.rate = .0001
        self.levelLoad = 0.01
        self.splitKey = 0
        self.focusClick = {"x":0.05, "y":0.5}
        # Keyboard listener logs the last key pressed here
        self.listenKey = 0
        # Clicks this close together aren't moved since 
        # moving the mouse takes about this much time
        self.doubleClickThreshold = 0.105
        pass

    def gameFound(self):
        if self.x is None or self.y is None or self.xmax is None or \
           self.ymax is None or self.xscale is None or self.yscale is None:
            return False
        return True

    # x and y are between 0 and 1
    def moveMouse(self, x, y):
        if 0 > x or x > 1 or 0 > y or y > 1:
            print("TASBOT.moveMouse(x,y) expects arguments between 0 and 1, not ", (x, y))
            return
        if self.x is None or self.xscale is None or self.y is None or self.yscale is None:
            print("")
        pyautogui.moveTo(self.x + self.xscale * x, self.y + self.yscale * y)

    def mouseClick(self, x = None, y = None):
        if x != None and y != None:
            self.moveMouse(x, y)
        pyautogui.click()

    def getMouse(self):
        return pyautogui.position()

    def findGame(self):
        borderColor = (0, 0, 0)

        while choice[0] != "h" and choice[0] != "f":
            choice = input("Use html color or flash color for border detection? (h/f)")
            if choice = "h":
                borderColor = (192, 200, 211)          # Color for html version
            elif choice = "f":
                borderColor = (0, 0, 0)
            else:
                print(choice, " is not a valid option!")

        print("Click somewhere on the Civiballs game window:")

        if self.waitForClick():
            print("Click detected! Searching for game border...")
        else:
            return False

        # Find game border
        # If game window is wider than tall, border appears on the sides,
        # however if the window is taller than wide, the border appears
        # on the top and bottom 
        mousex,mousey = pyautogui.position()
        try:
            # Locate left and right borders
            x = mousex
            y = mousey
            while not pyautogui.pixelMatchesColor(x,y, borderColor):
                x -= 1
            print("Left found!")
            while pyautogui.pixelMatchesColor(x,y,borderColor):
                y -= 1
            print("Top found!")
            self.x = x
            self.y = y

            x = mousex
            y = mousey
            while not pyautogui.pixelMatchesColor(x,y, borderColor):
                x += 1
            print("Right found!")
            while pyautogui.pixelMatchesColor(x,y,borderColor):
                y += 1
            print("Bottom found!")
            self.xmax = x
            self.ymax = y
            
        except:
            try:
                # Locate top and bottom borders
                x = mousex
                y = mousey
                while not pyautogui.pixelMatchesColor(x,y,borderColor):
                    y -= 1
                print("Top found!")
                while pyautogui.pixelMatchesColor(x,y, borderColor):
                    x -= 1
                print("Left found!")
                self.x = x
                self.y = y

                x = mousex
                y = mousey
                while not pyautogui.pixelMatchesColor(x,y, borderColor):
                    y += 1
                print("Bottom found!")
                while pyautogui.pixelMatchesColor(x,y,borderColor):
                    x += 1
                print("Right found!")
                self.xmax = x
                self.ymax = y
            except:
                print("Couldn't find game")
                return False

        self.xscale = self.xmax - self.x
        self.yscale = self.ymax - self.y
        print("Min: (%i, %i)\nMax: (%i, %i)" % (self.x, self.y, self.xmax, self.ymax))
        return True

    def printClick(self):
        self.waitForClick()
        x,y = pyautogui.position()
        print("(x = ", x, ", y = ", y, ")")
        print("Color = ", pyautogui.pixel(x, y))
        if self.x is None or self.xscale is None or self.y is None or self.yscale is None:
            print("Game window not located yet")
        else:
            print("(x = ", (x - self.x) / self.xscale, ", y = ", (y - self.y) / self.yscale, ')')

    # Stores user inputs as a csv string with format
    # time, x, y
    # where time was since first click
    def logClicks(self):
        # Check that game window is found
        if not self.gameFound():
            self.findGame()
        log = []
        # Wait for first click before starting timer
        self.waitForClick()
        start = time.time()
        x,y = pyautogui.position()
        scaledx = (x - self.x)/self.xscale
        scaledy = (y - self.y)/self.yscale
        log.append([0, scaledx, scaledy])
        print((x,y), end=" -> ")
        print((scaledx, scaledy))
        while self.waitForClick():
            curtime = time.time() - start
            x,y = pyautogui.position()
            scaledx = (x - self.x)/self.xscale
            scaledy = (y - self.y)/self.yscale
            log.append([curtime, scaledx, scaledy])
            print((x,y), end=" -> ")
            print((scaledx, scaledy))
        logstr = ""
        for click in log:
            logstr += str(click[0]) + "," + str(click[1]) + "," + str(click[2]) + "\n"

        # return everything but the last newline
        return logstr[:-1] 
            

    def setSplitKey(self):
        self.waitForKeyPress()
        self.splitKey = self.listenKey

    def listenerOnClick(self, x, y, button, pressed):
        if pressed:
            return False

    def waitForClick(self):
        with pynput.mouse.Events() as mouseListener:
            # Key listener allows for user to escape 
            keyListener = pynput.keyboard.Listener(on_press=self.listenerOnPress)
            keyListener.start()
            event = mouseListener.get(self.rate) 
            # while event hasn't registered a click
            while not (hasattr(event, 'pressed') and event.pressed):
                if self.listenKey == pynput.keyboard.Key.esc:
                    print("Cancelled wait: ESC")
                    keyListener.stop()
                    # Reset ESC key 
                    if (self.listenKey is not None):
                        keyListener = pynput.keyboard.Listener(on_release=self.listenerKeyReset)
                        keyListener.start()
                        keyListener.join()
                    return False
                event = mouseListener.get(self.rate)
            self.clockErr = time.time()
            return True
        

    def listenerOnPress(self, key):
        self.listenKey = key
        return False

    def listenerKeyReset(self, key):
        self.listenKey = None
        return False

    def waitForKeyPress(self):
        with pynput.keyboard.Listener(on_press=self.listenerOnPress) as listener:
            listener.join()

    def replayClickLog(self, log, focus=False, space=False):
        # Check that game window is found
        if not self.gameFound():
            self.findGame()
        # process the log string into click events
        # Key listener allows for user to escape 
        print("Replay started! Cancel replay with ESC:")
        keyListener = pynput.keyboard.Listener(on_press=self.listenerOnPress)
        log = [[float(num) for num in click.split(",")] for click in log.split("\n")]
        # Click on the game window to put it in focus
        if focus:
            self.mouseClick(self.focusClick["x"], self.focusClick["y"])
        # Reset the stage
        if space:
            pyautogui.press(" ")
        # Don't start key listener until after space has been pressed
        keyListener.start()
        # click[0] time after first click
        # click [1] x of click
        # click [2] y of click
        # Start time after first click
        click = log[0]
        clicknum = 0
        lastClickTime = click[0]
        self.moveMouse(click[1], click[2])
        # time.sleep(self.levelLoad)
        self.mouseClick()
        start = time.time()
        # print(clicknum, ": ", click) 
        # clicknum += 1
        for click in log[1:]:
            if click[0] < lastClickTime + self.doubleClickThreshold:
                if click[0] > (time.time() - start):
                    time.sleep(click[0] > (time.time() - start))
                self.mouseClick()
                # print("Double Click!", end=" ")
                # print(clicknum, ": ", click) 
                # clicknum += 1
                lastClickTime = click[0]
                continue
            self.moveMouse(click[1], click[2])
            lastClickTime = click[0]
            if self.listenKey == pynput.keyboard.Key.esc:
                print("Cancelled wait: ESC")
                keyListener.stop()
                # Reset ESC key 
                if (self.listenKey is not None):
                    '''
                    keyListener = pynput.keyboard.Listener(on_release=self.listenerKeyReset)
                    keyListener.start()
                    keyListener.join()
                    '''
                    self.listenKey = None
                return False
            # print(clicknum, ": ", click) 
            if click[0] > (time.time() - start):
                
                time.sleep(click[0] - (time.time() - start))
                self.mouseClick()
            else:
                self.mouseClick()
                # print("Mouse moved too slow!", end=" ")
            # clicknum += 1

        return True

    def editClickLog(self, path):
        print("Editor launched for %s. Type 'help' for a list of commands" % (path))
        # Keep track of the min and max delay to do a binary search for best delay
        clickRange = {"min": None, "max": None, "fast grow": 1}
        clickDict = {}
        logFile = open(path, "r")
        log = logFile.read()
        logFile.close()
        change = False
        command = "help"
        while True:
            # command processing
            command = input(path + "> ").split(" ")
            if command[0] == "help":
                print('''
quit                        Quits the editor
fast    <click number>      Attempts to do an incremental binary search for best time 
                            on <click number>. Clicks are 0 indexed and can be 
                            negative indexed (last click is index -1). Fast 
                            indicates the click was too fast, so the delay will be 
                            increased.
slow    <click number>      Attempts to do an incremental binary search for best time 
                            on <click number>. Clicks are 0 indexed and can be 
                            negative indexed (last click is index -1). Slow 
                            indicates the click was too slow, so the delay will be 
                            decreased.
add     <click number> <n>  Add n to the time, default to 0.01
sub     <click number> <n>  Subtract n to the time, default to 0.01
swap    <click 1> <click 2> Swaps the order of the two clicks specified. 
record                      Overwrites the current file with a new recording. After 
                            confirmation prompt, recording starts on the next click.
play                        Replays the recording
load    <file path>         Saves the current file and opens the file specified. If
                            that file can't be opened, then the current file remains
                            open. 
new     <file path>         Creates a new file and loads that file. 
save    <file path>         Saves the current recording to the specified file. If no 
                            file is provided, the currently open file is used

                ''')
            # fast indicates the click was too soon. Click number is first argument
            # and is 0 indexed for simple code, in other words the first click has 
            # click number 0. Negative numbers read from the last click, so the last
            # click could be referenced with click number -1
            elif command[0] == "fast":
                logLines = log.split("\n")
                if len(command) < 2:
                    print("Improper use of fast:\n: fast <click number>")
                elif int(command[1]) >= len(logLines) or int(command[1]) < -1 * len(logLines):
                    print("Click number exceeds number of clicks")
                else:
                    click = None
                    click = logLines[int(command[1])].split(",")
                    clickTime = float(click[0])
                    newClickTime = None
                    # If the current click has no entry in the dictionary, add a blank one
                    if int(command[1]) not in clickDict:
                        clickDict[int(command[1])] = clickRange.copy()
                    range = clickDict[int(command[1])]
                    # Since the click was too fast, the click has at least this delay
                    range["min"] = clickTime
                    if range["max"] is None:
                        newClickTime = range["min"] + 1
                    else:
                        newClickTime = (range["max"] + range["min"])/2
                    click[0] = str(newClickTime)
                    # combine elements in array click to a single string
                    newLogLine = ",".join(click)
                    logLines[int(command[1])] = newLogLine
                    log = "\n".join(logLines)
                    change = True
                    self.replayClickLog(log, space=True, focus=True)

            elif command[0] == "slow":
                logLines = log.split("\n")
                if len(command) < 2:
                    print("Improper use of slow:\n: slow <click number>")
                elif int(command[1]) > len(logLines) or int(command[1]) < -1 * len(logLines):
                    print("Click number exceeds number of clicks")
                else:
                    click = None
                    click = logLines[int(command[1])].split(",")
                    clickTime = float(click[0])
                    newClickTime = None
                    # If the current click has no entry in the dictionary, add a blank one
                    if int(command[1]) not in clickDict:
                        clickDict[int(command[1])] = clickRange.copy()
                    range = clickDict[int(command[1])]
                    # Since the click was too slow, the click has at most this delay
                    range["max"] = clickTime
                    if range["min"] is None:
                        newClickTime = range["max"] - 1
                        if newClickTime < 0:
                            newClickTime = range["max"] / 2
                            range["min"] = 0
                    else:
                        newClickTime = (range["max"] + range["min"])/2
                    click[0] = str(newClickTime)
                    # combine elements in array click to a single string
                    newLogLine = ",".join(click)
                    logLines[int(command[1])] = newLogLine
                    log = "\n".join(logLines)
                    change = True
                    self.replayClickLog(log, space=True, focus=True)

            elif command[0] == "add":
                logLines = log.split("\n")
                if len(command) < 2:
                    print("Improper use of add:\n: slow <click number> <n (optional)>")
                elif int(command[1]) > len(logLines) or int(command[1]) < -1 * len(logLines):
                    print("Click number exceeds number of clicks")
                else:
                    n = 0.01
                    if len(command) >= 3:
                        n = float(command[2])
                    click = None
                    click = logLines[int(command[1])].split(",")
                    clickTime = float(click[0])
                    click[0] = str(clickTime + n)
                    # combine elements in array click to a single string
                    newLogLine = ",".join(click)
                    logLines[int(command[1])] = newLogLine
                    log = "\n".join(logLines)
                    change = True
                    self.replayClickLog(log, space=True, focus=True)
                
            elif command[0] == "sub":
                logLines = log.split("\n")
                if len(command) < 2:
                    print("Improper use of add:\n: slow <click number> <n (optional)>")
                elif int(command[1]) > len(logLines) or int(command[1]) < -1 * len(logLines):
                    print("Click number exceeds number of clicks")
                else:
                    n = 0.01
                    if len(command) >= 3:
                        n = float(command[2])
                    click = None
                    click = logLines[int(command[1])].split(",")
                    clickTime = float(click[0])
                    click[0] = str(clickTime - n)
                    # combine elements in array click to a single string
                    newLogLine = ",".join(click)
                    logLines[int(command[1])] = newLogLine
                    log = "\n".join(logLines)
                    change = True
                    self.replayClickLog(log, space=True, focus=True)

            elif command[0] == "swap":
                logLines = log.split("\n")
                if len(command) < 3:
                    print("Improper use of swap:\n: swap <click number> <click number>")
                elif int(command[1]) > len(logLines) or int(command[1]) < -1 * len(logLines) or int(command[2]) > len(logLines) or int(command[2]) < -1 * len(logLines):
                    print("Click number exceeds number of clicks")
                else:
                    click1 = [float(num) for num in logLines[int(command[1])].split(",")]
                    click2 = [float(num) for num in logLines[int(command[2])].split(",")]
                    # We want the times to stay the same
                    temp = [click1[0], click2[1], click2[2]]
                    click2[1], click2[2] = click1[1], click1[2]
                    click1[1], click1[2] = temp[1], temp[2]
                    logLines[int(command[1])] = ",".join([str(num) for num in click1])
                    logLines[int(command[2])] = ",".join([str(num) for num in click2])
                    log = "\n".join(logLines)
                    clickDict[int(command[1])] = clickRange.copy()
                    clickDict[int(command[2])] = clickRange.copy()
                    change = True
                    self.replayClickLog(log, space=True, focus=True)

            elif command[0] == "moveclick":
                logLines = log.split("\n")
                if len(command) < 2:
                    print("Improper use of moveclick:\n: moveclick <click number>")
                elif int(command[1]) > len(logLines) or int(command[1]) < -1 * len(logLines):
                    print("Click number exceeds number of clicks")
                else:
                    click = None
                    click = logLines[int(command[1])].split(",")
                    print("Click where click number ", int(command[1]), "should go: ")
                    self.waitForClick()
                    x, y = pyautogui.position()
                    scaledx = (x - self.x)/self.xscale
                    scaledy = (y - self.y)/self.yscale
                    click[1], click[2] = str(scaledx), str(scaledy)
                    # combine elements in array click to a single string
                    newLogLine = ",".join(click)
                    logLines[int(command[1])] = newLogLine
                    log = "\n".join(logLines)
                    change = True

            elif command[0] == "record":
                print("Stop the recording by holding ESC.")
                print("Recording will start on your first click: ")
                log = self.logClicks()
                change = True

            elif command[0] == "play":
                self.replayClickLog(log, space=True, focus=True)

            elif command[0] == "load":
                if len(command) < 2:
                    print("Improper use of load:\n: load <file path>")
                elif change:
                    ok = input("There are unsaved changes. Are you sure you want to lose changes and quit? (y/n) ")
                    if ok[0] != 'y':
                        continue
                if os.access(command[1], os.R_OK) and os.access(command[1], os.W_OK):
                    path = command[1]
                    clickDict = {}
                    logFile = open(path, "r")
                    log = logFile.read()[:-1]
                    logFile.close()
                    change = False
                else:
                    print("Can't read or can't write to ", path)

            elif command[0] == "new":
                if len(command) < 2:
                    print("Improper use of new:\n: new <file path>")
                elif change:
                    ok = input("There are unsaved changes. Are you sure you want to lose changes and create a new file? (y/n) ")
                    if ok[0] != 'y':
                        continue
                path = command[1]
                logfile = open(path, "w")
                logfile.close()
                clickDict = {}
                log = None

            elif command[0] == "quit":
                if change:
                    ok = input("There are unsaved changes. Are you sure you want to lose changes and quit? (y/n) ")
                    if ok[0] != 'y':
                        continue
                return
                
            elif command[0] == "save":
                logFile = open(path, "w")
                logFile.write(log)
                logFile.close()
                change = False
                clickDict = {}

            elif command[0] == "":
                # do nothing
                True
            else: 
                print("Command not recognized. ")

            
    def cli(self):
        print("Type 'help' for a list of commands")
        command = "help"
        while True:
            # command processing
            command = input(": ").split(" ")
            if command[0] == "help":
                print('''
quit                        Quits the cli
record                      Same as new
load    <file path>         Loads the file into the recording editor
new     <file path>         Creates a new file, records the user's clicks, then saves 
                            the recording to that file. 
findborders                 Tells the bot to find the game window (recommended)
setborders                  Manually set the game borders in case findgame fails 
                            (or takes too long, though we recommend using findgame for 
                            better replay consistency)
checkborders                Moves cursor to top-left of game window and bottom right of 
                            game window to make sure the detection is correct
playlogs                    Play logs in order as they are given
                ''')

            elif command[0] == "load":
                if len(command) < 2:
                    print("Improper use of load:\n: load <file path>")
                else:
                    if os.access(command[1], os.R_OK) and os.access(command[1], os.W_OK):
                        self.editClickLog(command[1])


            elif command[0] == "new" or command[0] == "record":
                if len(command) < 2:
                    path = input("Name of log file to create: ")
                else:
                    path = command[1]
                logfile = open(path, "w")
                logfile.close()
                self.editClickLog(path)

            elif command[0] == "findborders":
                self.findGame()

            elif command[0] == "checkborders":
                print("Moving cursor to top-left ", (self.x,self.y), ".")
                self.moveMouse(0,0)
                print("Cursor moved! Press any key to check bottom right: ")
                self.waitForKeyPress()
                print("Moving cursor to bottom-right ", (self.xmax, self.ymax), ".")
                self.moveMouse(1,1)
                print("Cursor moved!")

            elif command[0] == "setborders":
                print("Click in the top-left of your game window: ")
                self.waitForClick()
                self.x, self.y = pyautogui.position()
                print((self.x, self.y))
                print("Click in the bottom-right of your game window: ")
                self.waitForClick()
                self.xmax, self.ymax = pyautogui.position()
                print((self.xmax, self.ymax))
                self.xscale = self.xmax - self.x
                self.yscale = self.ymax - self.y

            elif command[0] == "playlogs":
                for filepath in command[1:]:
                    print("Running ", filepath)
                    with open(filepath, 'r') as file:
                        if not self.replayClickLog(file.read()):
                            break

            elif command[0] == "quit":
                return

            elif command[0] == "":
                # do nothing
                True
            else: 
                print("Command not recognized. ")

if __name__ == "__main__": 
    bot = TASBOT()
    bot.cli()
        
        
