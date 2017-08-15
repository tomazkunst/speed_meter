# -*- coding: utf-8 -*-
try:
    import pygame_sdl2
    pygame_sdl2.import_as_pygame()
except ImportError:
    pass


import pygame
from pygame.locals import *
import os
from time import sleep, time
import requests
import json
import math
import random
import sys
import serial
import re

import multiprocessing as mp

WHEEL_R = 1.35


def degreesToRadians(deg):
    return deg/180.0 * math.pi


def drawCircleArc(screen, color, center, radius, startDeg, endDeg, thickness):
    (x, y) = center
    rect = (x-radius, y-radius, radius*2, radius*2)
    startRad = degreesToRadians(startDeg)
    endRad = degreesToRadians(endDeg)

    pygame.draw.arc(screen, color, rect, startRad, endRad, thickness)


class ReadSerial(object):
    e_rpm = None
    p_rpm = None
    w_rpm = None

    def __init__(self, e_rpm, p_rpm, w_rpm, updated):
        super(ReadSerial, self).__init__()
        self.e_rpm = e_rpm
        self.p_rpm = p_rpm
        self.w_rpm = w_rpm
        self.updated = updated
        self.last_time = time()
        self.ser = serial.Serial('/dev/ttyUSB0', 9600)
        self.read()

    def read(self):
        buffer_data = []
        prev = 0
        while True:
            line = self.ser.readline()
            line = re.sub('\r\n', '', line)
            print line
            sensor, time = line.split(":")
            print "time: " + time
            if sensor == "1":
                self.e_rpm.value = int(60/float(time)*1000)
                self.updated[0] += 1
            elif sensor == "2":
                self.p_rpm.value = int(60/float(time)*1000)
                self.updated[1] += 1
            elif sensor == "3":
                self.w_rpm.value = int(1000/float(time) * 2 * math.pi * WHEEL_R)
                self.updated[2] += 1
            print "speed", self.w_rpm.value


class Speedo(object):
    def __init__(self):
        super(Speedo, self).__init__()
        self.WHITE = (255, 255, 255)
        pygame.init()

        self.scale=2
        self.screen = pygame.display.set_mode((320 * self.scale, 200 * self.scale))
        self.screen.fill((0, 0, 0))
        pygame.display.update()

        self.font_big = pygame.font.Font(None, 164)
        self.font_small = pygame.font.Font(None, 82)
        self.value = ""
        self.v = (160, 160)

        # screen = self.toggle_fullscreen()
        self.text_surface = self.font_big.render('%s' % self.value,
                                                 True,
                                                 self.WHITE)
        self.rect = self.text_surface.get_rect(center=self.v)
        self.screen.blit(self.text_surface, self.rect)

        self.surface1 = pygame.Surface((320 * self.scale, 200 * self.scale))
        self.surface1.set_colorkey((0, 0, 0))
        self.surface1.set_alpha(230)
        self.screen.blit(self.surface1, (320 * self.scale, 200 * self.scale))

        pygame.mouse.set_visible(True)
        pygame.display.update()

        self.rpm = mp.Value('d', 0)
        self.prpm = mp.Value('d', 0)
        self.hitrost = mp.Value('d', 0)

        self.updated = mp.Array('i', range(3))

        self.proces = mp.Process(target=ReadSerial, args=(self.rpm, self.prpm, self.hitrost, self.updated, ))
        self.proces.start()

        self.update()

    def toggle_fullscreen(self):
        self.screen = pygame.display.get_surface()
        tmp = self.screen.convert()
        caption = pygame.display.get_caption()
        # cursor = pygame.mouse.get_cursor()  # Duoas 16-04-2007

        w, h = self.screen.get_width(), self.screen.get_height()
        flags = self.screen.get_flags()
        bits = self.screen.get_bitsize()

        pygame.display.quit()
        pygame.display.init()

        self.screen = pygame.display.set_mode((w,h),flags^FULLSCREEN,bits)
        self.screen.blit(tmp, (0, 0))
        pygame.display.set_caption(*caption)

        pygame.key.set_mods(0) #HACK: work-a-round for a SDL bug??

    def update(self):
        self.surface1.fill((0, 0, 0))

        #RPM (sensor 1)
        # if is not updated in last second set to 0
        rpm_m = self.rpm.value if self.updated[0] else 0
        self.updated[0] = 0
        self.text_surface = self.font_big.render(str(int(rpm_m)), True, self.WHITE)
        rect = self.text_surface.get_rect(center=(100 * self.scale, 170 * self.scale))
        self.screen.fill((0, 0, 0))

        #KMH (sensor 3)
        rpm_w = self.hitrost.value# if self.updated[2] else 0
        self.text_surface1 = self.font_small.render('km/h '+str(int(rpm_w)), True, self.WHITE)
        rect1 = self.text_surface1.get_rect(center=(255 * self.scale, 30 * self.scale))
        self.screen.fill((0, 0, 0))

        #RPM_P (sensor 2)
        rpm_p = self.prpm.value if self.updated[1] else 0
        self.updated[1] = 0
        display_num = str(int(rpm_p)).zfill(4)
        self.text_surface2 = self.font_small.render('rpm ' + display_num,
                                                    True,
                                                    self.WHITE)
        rect2 = self.text_surface2.get_rect(center=(250 * self.scale, 100 * self.scale))
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.text_surface, rect)
        self.screen.blit(self.text_surface1, rect1)
        self.screen.blit(self.text_surface2, rect2)

        drawCircleArc(self.screen, (0 , 255, 0), (100 * self.scale, 200 * self.scale), 100 * self.scale, 45, 180, 20)
        drawCircleArc(self.screen, (255, 140, 0), (100 * self.scale, 200 * self.scale), 100 * self.scale, 45, 115, 20)
        drawCircleArc(self.screen, (255, 0, 0), (100 * self.scale, 200 * self.scale), 100 * self.scale, 45, 70, 20)

        ivan = (rpm_m + 1) / 18.5
        ivan = abs(ivan - 135)
        ivan = ivan + 45
        # 2500 - 0
        # 45 - 180
        # show rpm's
        drawCircleArc(self.surface1, [30, 30, 30, 200], (100  * self.scale, 200  * self.scale), 99 * self.scale, 45, ivan, 18)
        self.screen.blit(self.surface1, (0, 0, 320  * self.scale, 200  * self.scale))

        pygame.display.update()
        return True


# call main
if __name__ == '__main__':
    speedo = Speedo()
    while True:
        sleep(1)
        speedo.update()
