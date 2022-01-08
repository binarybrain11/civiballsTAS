import pyautogui
import pynput
import time

class TASBOT:
    def __init__(self):
        self.x = None
        self.y = None
        self.xmax = None
        self.ymax = None
        self.xscale = None
        self.yscale = None
        self.levelLoad = 0
        self.listenKey = 0
        self.splitKey = 0
        pass

    # x and y are between 0 and 1
    def moveMouse(self, x, y):
        if 0 > x or x > 1 or 0 > y or y > 1:
            print("TASBOT.moveMouse(x,y) expects arguments between 0 and 1")
            return
        if self.x is None or self.xscale is None or self.y is None or self.yscale is None:
            print("")
        pyautogui.moveTo(self.x + self.xscale * x, self.y + self.yscale * y)

    def mouseClick(self, x, y):
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
        log = "0,"
        # Wait for first click before starting timer
        self.waitForClick()
        start = time.time()
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
            while not hasattr(event, 'pressed'):
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
            while not hasattr(event, "pressed"):
                event = mouseListener.get(.001) 
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

    def replayLog(self, log):
        # process the log string into click events
        # Key listener allows for user to escape 
        print("Replay started! Cancel replay with ESC:")
        keyListener = pynput.keyboard.Listener(on_press=self.listenerOnPress)
        keyListener.start()
        log = [[float(num) for num in click.split(",")] for click in log.split("\n")]
        # log = [click.split(",") for click in log.split("\n")]
        start = time.time()
        for click in log:
            sleep = click[0] - (time.time() - start)
            if sleep >= 0:
                if self.listenKey == pynput.keyboard.Key.esc:
                    print("Cancelled wait: ESC")
                    keyListener.stop()
                    # Reset ESC key 
                    if (self.listenKey is not None):
                        keyListener = pynput.keyboard.Listener(on_release=self.listenerEscReset)
                        keyListener.start()
                        keyListener.join()
                    return False
                time.sleep(click[0] - (time.time() - start))
            self.mouseClick(click[1], click[2])



bot = TASBOT()
if bot.findGame():
    # print("Bot will start recording on the first click. Stop recording with the ESC key:")
    
    log = bot.logClicks()
    logFile = open("egypt1.txt", "w")
    logFile.write(log)
    logFile.close()
    quit()
    
    worlds = ["egypt", "china", "greece"]
    log = ""
    for world in worlds:
        for level in range(1,11):
            # print("Ready to log " + world + str(level))
            '''
            log = bot.logClicks()
            logFile = open(world + str(level) + ".txt", "w")
            logFile.write(log)
            logFile.close()
            '''
            logFile = open(world + str(level) + ".txt", "r")
            log += logFile.read()[:-1]
            logFile.close()
    bot.replayLog(log)
    
