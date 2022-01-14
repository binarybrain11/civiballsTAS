import pyautogui
import pynput
import time
import os

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
        self.levelLoad = 0.01
        self.splitKey = 0
        self.focusClick = {"x":0.05, "y":0.5}
        # Keyboard listener logs the last key pressed here
        self.listenKey = 0
        pass

    # x and y are between 0 and 1
    def moveMouse(self, x, y):
        if 0 > x or x > 1 or 0 > y or y > 1:
            print("TASBOT.moveMouse(x,y) expects arguments between 0 and 1")
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
        borderColor = (192, 200, 211)

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
        print("(x = ", (x - self.x) / self.xscale, ", y = ", (y - self.y) / self.yscale, ')')

    # Stores user inputs as a csv string with format
    # time, x, y
    # where time was since first click
    def logClicks(self):
        log = ""
        # Wait for first click before starting timer
        self.waitForClick()
        start = time.time()
        log += str(time.time() - start) + ","
        x,y = pyautogui.position()
        log += str((x - self.x)/self.xscale) + ","
        log += str((y - self.y)/self.yscale) + "\n"
        while self.waitForClick():
            log += str(time.time() - start) + ","
            x,y = pyautogui.position()
            log += str((x - self.x)/self.xscale) + ","
            log += str((y - self.y)/self.yscale) + "\n"
        return log
            

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
            event = mouseListener.get(.001) 
            # while event hasn't registered a click
            while not (hasattr(event, 'pressed') and event.pressed):
                if self.listenKey == pynput.keyboard.Key.esc:
                    print("Cancelled wait: ESC")
                    keyListener.stop()
                    # Reset ESC key 
                    if (self.listenKey is not None):
                        keyListener = pynput.keyboard.Listener(on_release=self.listenerEscReset)
                        keyListener.start()
                        keyListener.join()
                    return False
                event = mouseListener.get(.001)
            self.clockErr = time.time()
            return True
        

    def listenerOnPress(self, key):
        self.listenKey = key
        return False

    def listenerEscReset(self, key):
        self.listenKey = None
        return False

    def waitForKeyPress(self):
        with pynput.keyboard.Listener(on_press=self.listenerOnPress) as listener:
            listener.join()

    def replayClickLog(self, log):
        # process the log string into click events
        # Key listener allows for user to escape 
        print("Replay started! Cancel replay with ESC:")
        keyListener = pynput.keyboard.Listener(on_press=self.listenerOnPress)
        keyListener.start()
        log = [[float(num) for num in click.split(",")] for click in log.split("\n")]
        self.mouseClick(self.focusClick["x"], self.focusClick["y"])
        start = time.time()
        # click[0] time after first click
        # click [1] x of click
        # click [2] y of click
        for click in log:
            # if first click in log file, start time after click
            self.moveMouse(click[1], click[2])
            if (click[0] < .0001):
                time.sleep(self.levelLoad)
                self.mouseClick()
                start = time.time()
                continue

            if self.listenKey == pynput.keyboard.Key.esc:
                    print("Cancelled wait: ESC")
                    keyListener.stop()
                    # Reset ESC key 
                    if (self.listenKey is not None):
                        keyListener = pynput.keyboard.Listener(on_release=self.listenerEscReset)
                        keyListener.start()
                        keyListener.join()
                    return False

            if click[0] > (time.time() - start):
                
                time.sleep(click[0] - (time.time() - start))
            else:
                print("Too slow!")
                
            self.mouseClick()
        return True

    def editClickLog(self, path):
        print("Editor launched for %s. Type 'help' for a list of commands" % (path))
        # Keep track of the min and max delay to do a binary search for best delay
        clickRange = {"min": None, "max": None}
        clickDict = {}
        noReplay = ["help", "record"]
        command = ""
        while True:
            if command not in noReplay:
                logFile = open(path, "r")
                log = logFile.read()[:-1]
                logFile.close()
                self.replayClickLog(log)
            newLog = None
            # command processing
            command = input(": ").split(" ")
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
                ''')
            # fast indicates the click was too soon. Click number is first argument
            # and is 0 indexed for simple code, in other words the first click has 
            # click number 0. Negative numbers read from the last click, so the last
            # click could be referenced with click number -1
            elif command[0] == "fast":
                logLines = log.split("\n")
                if len(command) < 2:
                    print("Improper use of fast:\n: fast <click number>")
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
                    # Since the click was too fast, the click has at least this delay
                    range["min"] = clickTime
                    if range["max"] is None:
                        newClickTime = range["min"] + 0.5
                    else:
                        newClickTime = (range["max"] + range["min"])/2
                    click[0] = str(newClickTime)
                    # combine elements in array click to a single string
                    newLogLine = ",".join(click)
                    logLines[int(command[1])] = newLogLine
                    newLog = "\n".join(logLines)

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
                        newClickTime = range["max"] - 0.5
                    else:
                        newClickTime = (range["max"] + range["min"])/2
                    click[0] = str(newClickTime)
                    # combine elements in array click to a single string
                    newLogLine = ",".join(click)
                    logLines[int(command[1])] = newLogLine
                    newLog = "\n".join(logLines)

            elif command[0] == "swap":
                logLines = log.split("\n")
                if len(command) < 3:
                    print("Improper use of swap:\n: swap <click number> <click number>")
                elif int(command[1]) > len(logLines) or int(command[1]) < -1 * len(logLines) or int(command[2]) > len(logLines) or int(command[2]) < -1 * len(logLines):
                    print("Click number exceeds number of clicks")
                else:
                    temp = logLines[int(command[1])]
                    logLines[int(command[1])] = logLines[int(command[2])]
                    logLines[int(command[2])] = temp
                    newLog = "\n".join(logLines)

            elif command[0] == "record":
                confirm = input("Recording will overwrite the current file. Are you sure? (y/n)")
                if confirm[0] == "y":
                    print("Recording will start on your first click: ")
                    newLog = self.logClicks()

            elif command[0] == "load":
                if len(command) < 2:
                    print("Improper use of load:\n: load <file path>")
                else:
                    if os.access(command[1], os.R_OK) and os.access(command[1], os.W_OK):
                        path = command[1]
                        clickDict = {}

            elif command[0] == "new":
                if len(command) < 2:
                    print("Improper use of new:\n: new <file path>")
                else:
                    if os.access(command[1], os.W_OK):
                        path = command[1]
                        clickDict = {}
                        newLog = self.logClicks()

            elif command[0] == "quit":
                return

            if newLog is not None:    
                logFile = open(path, "w")
                logFile.write(newLog)
                logFile.close()
            

#fullscreen = (312, 66, 1607, 1040)
#left = (0, 198, 959, 916)

bot = TASBOT()

if bot.xscale is not None or bot.findGame():
    # print("Bot will start recording on the first click. Stop recording with the ESC key:")
    time.sleep(1)
    
    print("Ready to log.")
    log = bot.logClicks()
    logFile = open("egypt10.txt", "w")
    logFile.write(log)
    logFile.close()
    
    '''
    logFile = open("egypt9.txt", "r")
    log = logFile.read()[:-1]
    logFile.close()
    bot.replayClickLog(log)
    '''
    bot.editClickLog("egypt10.txt")
    
    quit()
    
    
    #worlds = ["egypt", "china", "greece"]
    worlds = ["egypt"]
    log = ""
    for world in worlds:
        for level in range(1,11):
            '''
            print("Ready to log " + world + str(level))
            log = bot.logClicks()
            logFile = open(world + str(level) + ".txt", "w")
            logFile.write(log)
            logFile.close()
            '''
            logFile = open(world + str(level) + ".txt", "r")
            log += logFile.read()[:-1] + "\n"
            logFile.close()
    # remove trailing null
    log = log[:-1]
    bot.replayClickLog(log)
    
    
