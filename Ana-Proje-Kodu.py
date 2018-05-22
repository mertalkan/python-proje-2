#!/usr/bin/env python

import time
import collections
from threading import Thread
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

import time


timeout = 1.5
last_touch = 0

SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))


class heartbeadPlot:
    def __init__(self, plotLength = 100, dataNumBytes = 2): # gerekli tanimlamalar
        self.plotMaxLength = plotLength
        self.dataNumBytes = dataNumBytes
        self.rawData = bytearray(dataNumBytes)
        self.data = collections.deque([0] * plotLength, maxlen=plotLength)
        self.isRun = True
        self.isReceiving = False
        self.thread = None
        self.plotTimer = 0
        self.previousTimer = 0


    def getData(self, frame, lines, lineValueText, lineLabel, timeText):
        currentTimer = time.clock()
        self.plotTimer = int((currentTimer - self.previousTimer) * 1000)     #ilk okuma hatalidir
        self.previousTimer = currentTimer
        timeText.set_text('Plot Interval = ' + str(self.plotTimer) + 'ms')
        value = float(mcp.read_adc_difference(0))# veri alindi
        last_touch = time.time()
        self.data.append(value)    # son datayi alip arraya ekliyoruz
        lines.set_data(range(self.plotMaxLength), self.data)
        lineValueText.set_text('[' + lineLabel + '] = ' + str(value))

    def backgroundThread(self):    # dataya tekrar bak
        time.sleep(1.0)  
        while (self.isRun):
            self.serialConnection.readinto(self.rawData)
            self.isReceiving = True

    def close(self):
        self.isRun = False
        self.thread.join()
        print('Baglanti kesildi...')



def main():

    maxPlotLength = 150
    dataNumBytes = 2 #4        # bir data doktasinin byte degeri
    s = heartbeadPlot(maxPlotLength, dataNumBytes)   # gerekli degiskenler orneklendi

    # grafikleme baslangici
    pltInterval = 1    # grafik animansyonunun peryodu [ms]
    xmin = 0
    xmax = maxPlotLength 
    ymin = 0
    ymax = 1000
    fig = plt.figure()
    ax = plt.axes(xlim=(xmin, xmax), ylim=(float(ymin - (ymax - ymin) / 10), float(ymax + (ymax - ymin) / 10)))
    ax.set_title('Kalp Atisi Nabzi')
    ax.set_xlabel("zaman")
    ax.set_ylabel("Nabiz Degeri")

    lineLabel = 'Nabiz Sensor Degeri'
    timeText = ax.text(0.50, 0.95, '', transform=ax.transAxes)
    lines = ax.plot([], [], label=lineLabel)[0]
    lineValueText = ax.text(0.50, 0.90, '', transform=ax.transAxes)
    anim = animation.FuncAnimation(fig, s.getData, fargs=(lines, lineValueText, lineLabel, timeText), interval=pltInterval) # animasyon baslasin

    plt.legend(loc="sol ust")
    plt.show()

    s.close()


if __name__ == '__main__':
    main()     # main fonksiyonu cagrilir
