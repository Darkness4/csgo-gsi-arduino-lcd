# -*- coding: utf-8 -*-
"""
Messenger Thread.

@auteur: Darkness4
"""
from threading import Thread
from time import asctime, time, sleep


def progress(i):
    """Progress bar, for arduino 5px large."""
    switcher = {i <= 0: b"\x07",
                i == 1: b"\x02",
                i == 2: b"\x03",
                i == 3: b"\x04",
                i == 4: b"\x05",
                i >= 5: b"\x06"}
    return switcher[True]


class Messenger(Thread):
    """Give order to the arduino."""

    def __init__(self, ser_arduino):
        """Init save."""
        super(Messenger, self).__init__()
        self.ser_arduino = ser_arduino
        # availablestatus = ["None",
        #                     "Bomb",
        #                     "!Freezetime",
        #                     "Freezetime",
        #                     "Defused",
        #                     "Exploded"]
        self.health = None
        self.armor = None
        self.money = None
        self.kills = None
        self.payload = None
        self.hs = None
        self.status = "None"
        self.__start__ = True
        self.__refresh__ = False

    def bombtimer(self):
        """40s bomb timer on arduino."""
        offset = time()
        actualtime = 40 - time() + offset
        while actualtime > 0 and self.status == "Bomb":
            oldtime = int(actualtime)
            sleep(0.1)
            actualtime = 40 - time() + offset
            if oldtime != int(actualtime):  # Actualization
                self.ser_arduino.write(b'BOMB PLANTED')
                # Wait for second line
                sleep(0.1)
                self.ser_arduino.write(progress(int(actualtime)))  # 5s
                self.ser_arduino.write(progress(int(actualtime - 5)))  # 10s
                self.ser_arduino.write(progress(int(actualtime - 10)))  # 15s
                self.ser_arduino.write(progress(int(actualtime - 15)))  # 20s
                self.ser_arduino.write(progress(int(actualtime - 20)))  # 25s
                self.ser_arduino.write(progress(int(actualtime - 25)))
                self.ser_arduino.write(progress(int(actualtime - 30)))
                self.ser_arduino.write(progress(int(actualtime - 35)))
                self.ser_arduino.write(bytes(str(int(actualtime)).encode()))
        if self.status == "Defused":
            self.ser_arduino.write(b'BOMB DEFUSED')
            # Wait for second line
            sleep(0.1)
            self.ser_arduino.write(b' ')
            sleep(0.1)
        if self.status == "Exploded":
            self.ser_arduino.write(b'BOMB EXPLODED')
            # Wait for second line
            sleep(0.1)
            self.ser_arduino.write(b' ')
            sleep(0.1)

    def playerstats(self):
        """Player's stats writer."""
        self.ser_arduino.write(b'H: ')  # Writing progress bar on Serial
        self.ser_arduino.write(progress(int(self.health / 5)))
        self.ser_arduino.write(progress(int((self.health - 25) / 5)))
        self.ser_arduino.write(progress(int((self.health - 50) / 5)))
        self.ser_arduino.write(progress(int((self.health - 75) / 5)))
        self.ser_arduino.write(b' A: ')
        self.ser_arduino.write(progress(int(self.armor / 5)))
        self.ser_arduino.write(progress(int((self.armor - 25) / 5)))
        self.ser_arduino.write(progress(int((self.armor - 50) / 5)))
        self.ser_arduino.write(progress(int((self.armor - 75) / 5)))
        # Wait for second line
        sleep(0.1)
        # Kill or Money
        if self.status == "!Freezetime":
            # HS and Kill counter
            kills = self.kills - self.hs
            self.ser_arduino.write(b'K: ')
            for _ in range(0, kills):  # counting
                self.ser_arduino.write(b'\x00')  # Byte 0 char : kill no HS
            for _ in range(0, self.hs):  # counting
                self.ser_arduino.write(b'\x01')  # Byte 1 char : HS
        elif self.status == "Freezetime":  # Not kill streak
            self.ser_arduino.write(
                bytes('M: {}'.format(self.money).encode()))
        sleep(0.1)

    def idle(self):
        """Print text while idle."""
        self.ser_arduino.write(b'Waiting for')
        sleep(0.1)
        self.ser_arduino.write(b'matches')

    def changestatus(self, status):
        """Change Messenger behavior."""
        self.status = status
        self.__refresh__ = True

    def setkills(self, kills, hs):
        """Set kills."""
        self.kills = int(kills)
        self.hs = int(hs)

    def run(self):
        """Thread start."""
        while self.__start__:
            if self.__refresh__:
                self.__refresh__ = False
                if self.status in ("Bomb", "Defused", "Exploded"):
                    self.bombtimer()

                elif self.status == "None":
                    self.idle()

                else:
                    self.playerstats()
        print(asctime(), "-", "Messenger is dead.")

    def shutdown(self):
        """Stop the messenger."""
        self.__start__ = False