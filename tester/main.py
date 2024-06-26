from machine import *
import time
import network
import espnow

ledState = Pin(14, Pin.OUT)
ledStateTimeout = 0

sta = network.WLAN(network.STA_IF)
sta.active(True)

broadcastAddr = b'\xff\xff\xff\xff\xff\xff'
e = espnow.ESPNow()
e.active(True)
e.add_peer(broadcastAddr)

while True:
    if time.ticks_diff(ledStateTimeout, time.ticks_ms()) < 0:
        if ledState.value():
            e.send(broadcastAddr, b'off', False)
            ledState.off()
            ledStateTimeout = time.ticks_add(time.ticks_ms(), 4000)
        else:
            e.send(broadcastAddr, b'on', False)
            ledState.on()
            ledStateTimeout = time.ticks_add(time.ticks_ms(), 2000)
