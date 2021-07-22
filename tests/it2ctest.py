import smbus
import time

bus = smbus.SMBus(1)
address = 0x08

def main():
	i2cData = True
	while 1:
		i2cData = not i2cData
		bus.write_byte(address, i2cData)
				
		print("Answer: ", bus.read_i2c_block_data(address, 0, 6))
		time.sleep(1)

main()
