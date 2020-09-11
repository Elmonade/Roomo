from gpiozero import LightSensor

ldr = LightSensor(21)
print(ldr.value)
