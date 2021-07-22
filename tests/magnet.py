import smbus
import time

bus = smbus.SMBus(1)
address = 0x36

def main():
	i2cData = True
	while 1:
		i2cData = not i2cData
		bus.write_byte(address, i2cData)
				
		data = bus.read_i2c_block_data(address, 0, 28)

		print(data[0x0c], data[0x0d])
		raw_angle = (data[0x0c] << 8) + data[0x0d]
		print(raw_angle)
		angle = raw_angle * 0.0878

		
		print("Raw data", data)
		print("Angle", angle)
		print("Status", (data[0x0b] & 0x20) > 0, "Low", (data[0x0b] & 0x10) > 0, "High", (data[0x0b] & 0x08) > 0)
		time.sleep(1)

main()
