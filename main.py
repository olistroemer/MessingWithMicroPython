from machine import *
import time
import network
import espnow

ledState = Pin(13, Pin.OUT)
ledStateTimeout = 0

ledPool = [
    Pin(25, Pin.OUT),
    Pin(12, Pin.OUT),
    Pin(14, Pin.OUT)
    ]

ledDict = {}

i2c = I2C(0, scl=Pin(26), sda=Pin(27))
mpuAddr = 104
# Wake up MPU6050
i2c.writeto_mem(mpuAddr, 0x6B, b'\x00')

sta = network.WLAN(network.STA_IF)
sta.active(True)

broadcastAddr = b'\xff\xff\xff\xff\xff\xff'
e = espnow.ESPNow()
e.active(True)
e.add_peer(broadcastAddr)

windowSize = 5000
window = []
mAvg = 0.0

while True:
    if e.any():
        host, msg = e.recv()
        ledHost = ledDict.get(str(host))
        print(host, msg, ledHost)

        if ledHost is None:
            if len(ledPool) >= 1:
                ledHost = ledPool.pop(0)
                ledDict[str(host)] = ledHost
                print(f"Registered new host {host} as {ledHost}")
            else:
                print(f"No free LED left for new host {host}")

        if ledHost is not None:
            if msg == b'on':
                ledHost.on()
            elif msg == b'off':
                ledHost.off()
            else:
                print(f"Unknown command '{msg}'")

    current = int.from_bytes(i2c.readfrom_mem(mpuAddr, 0x3B, 2), "big")
    window.append(current)

    if (len(window) > windowSize):
        mAvg = mAvg + (current - window.pop(0)) / windowSize
    else:
        mAvg = mAvg * (len(window)-1)/len(window) + current * 1/len(window)

    if current > mAvg * 2:
        if not ledState.value():
            ledStateTimeout = time.ticks_add(time.ticks_ms(), 500)
            e.send(broadcastAddr, b'on', False)
            print(f"send 1 c {current} mAvg {mAvg} lST {ledStateTimeout} t.t_ms {time.ticks_ms()}")
            ledState.on()

    if ledState.value() and time.ticks_diff(ledStateTimeout, time.ticks_ms()) < 0:
        e.send(broadcastAddr, b'off', False)
        print(f"send 0 c {current} mAvg {mAvg} lST {ledStateTimeout} t.t_ms {time.ticks_ms()}")
        ledState.off()
