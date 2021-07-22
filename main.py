import smbus
import time
from subprocess import Popen, PIPE
from RPi import GPIO

assets_path = "/home/pi/IntriCebela/assets/"

class State:
    IDLE = "0"
    PIKCASTE_IN_SESTAVLJENE_OCI = "E"
    SIMULACIJA_CEBELJEGA_VIDA = "F"
    RILCEK_IN_MEDNA_GOLSA = "C"
    TIPALNICE = "D"
    CVETNI_PRAH = "H"
    VOSKOVNA_ZLEZA = "J"
    ZELO = "L"
    NOTRANJI_ORGANI = "G"
    PROPOLIS = "I"
    VAROJA = "K"

    MAIN_ROTATION = {
        IDLE: 0,
        PIKCASTE_IN_SESTAVLJENE_OCI: 0,
        SIMULACIJA_CEBELJEGA_VIDA: 0,
        RILCEK_IN_MEDNA_GOLSA: 0,
        TIPALNICE: 0,
        CVETNI_PRAH: 0,
        VOSKOVNA_ZLEZA: 0,
        ZELO: 0,
        NOTRANJI_ORGANI: 0,
        PROPOLIS: 0,
        VAROJA: 0
    }

    TIME = {
        IDLE: 0,
        PIKCASTE_IN_SESTAVLJENE_OCI: 56,
        SIMULACIJA_CEBELJEGA_VIDA: 30,
        RILCEK_IN_MEDNA_GOLSA: 47,
        TIPALNICE: 34,
        CVETNI_PRAH: 46,
        VOSKOVNA_ZLEZA: 40,
        ZELO: 37,
        NOTRANJI_ORGANI: 67,
        PROPOLIS: 56,
        VAROJA: 25
    }

    VIDEO = {
        PIKCASTE_IN_SESTAVLJENE_OCI: "PIKCASTE_IN_SESTAVLJENE_OCI.mp4",
        SIMULACIJA_CEBELJEGA_VIDA: None,
        RILCEK_IN_MEDNA_GOLSA: "RILCEK_IN_MEDNA_GOLSA.mp4",
        TIPALNICE: "TIPALNICE.mp4",
        CVETNI_PRAH: "CVETNI_PRAH.mp4",
        VOSKOVNA_ZLEZA: "VOSKOVNA_ZLEZA.mp4",
        ZELO: "ZELO.mp4",
        NOTRANJI_ORGANI: "NOTRANJI_ORGANI.mp4",
        PROPOLIS: "PROPOLIS.mp4",
        VAROJA: "VAROJA.mp4"
    }

    BUTTONS = {
        PIKCASTE_IN_SESTAVLJENE_OCI: "C",
        SIMULACIJA_CEBELJEGA_VIDA: "D",
        RILCEK_IN_MEDNA_GOLSA: "E",
        TIPALNICE: "F",
        CVETNI_PRAH: "G",
        VOSKOVNA_ZLEZA: "H",
        ZELO: "I",
        NOTRANJI_ORGANI: "J",
        PROPOLIS: "K",
        VAROJA: "L",
    }

    @staticmethod
    def get_rotation(state):
        return State.MAIN_ROTATION.get(state, None)

    @staticmethod
    def get_time(state):
        return State.TIME.get(state, None)
    
    @staticmethod
    def get_video_url(state):
        video_name = State.VIDEO.get(state, None) 
        return assets_path + video_name if video_name is not None else None

    @staticmethod
    def get_state_from_button(button):
        for key, value in State.BUTTONS.items():
            if value == button:
                return key
        return None

class I2C:

    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.arduino_address = 8
        self.magnet_address = 0x36

    def get_pressed_button(self):
        try:
            self.bus.write_byte(self.arduino_address, 1)
            data = self.bus.read_i2c_block_data(self.arduino_address, 0, 1)

            char = data[0]
            if char == ord('0'):
                buttonInput = None
            elif ord('A') <= char <= ord('L'):
                buttonInput = chr(char)
            else:
                raise ValueError("Invalid value")
	    '''
            print("Read Input: ", char)
            '''
	    return buttonInput

        except IOError as e:
            print("Error reading from i2c arduino", e)
            return None
        except ValueError as e:
            print("Invalid value from arduino:", char, ",", e)
            return None
        except Exception as e:
            print("Other error from arduino", e)
            return None

    def get_magnet_position(self):
        try:
	    data = self.bus.read_i2c_block_data(self.magnet_address, 0, 28)

            raw_angle = (data[0x0c] << 8) + data[0x0d]
	    angle = raw_angle * 0.0878
	    status = (data[0x0b] & 0x20) > 0
	    too_low = (data[0x0b] & 0x10) > 0
	    too_high = (data[0x0b] & 0x08) > 0

	    print("Main Motor Angle", angle, "status", status, " too low", too_low, "High", too_high)

            if not status:
	        if too_low:
	            raise ValueError("Magnet signal too low")
                elif too_high:
                    raise ValueError("Magnet signal too high")
                else:
                    raise ValueError("No status")
	    return raw_angle
        except IOError as e:
	    '''
            print("Error reading from i2c magnet", e)
            '''
	    return None
        except ValueError as e:
            print("Invalid value from manget:", e)
            return None
        except Exception as e:
            print("Other error from magnet", e)
            return None

class BackgroundImage:
    def __init__(self):
        Popen(["fbi", "-a", "-noverbose", assets_path + "background.jpg"])

class Camera:
    def __init__(self, time=10):
        Popen(["raspivid", "-t", str(time*1000)])

class Video:
    def __init__(self, video_url):
        Popen(['omxplayer', "-o", "local", video_url])

class LinearMotor:
    def __init__(self, forward_pin, backward_pin, sensor_front_pin, sensor_back_pin):
	self.forward_pin = forward_pin
	self.backward_pin = backward_pin
	self.sensor_front_pin = sensor_front_pin
	self.sensor_back_pin = sensor_back_pin
        
	GPIO.setup(forward_pin, GPIO.OUT)
        GPIO.setup(backward_pin, GPIO.OUT)

	GPIO.setup(sensor_front_pin, GPIO.IN)
	GPIO.setup(sensor_back_pin, GPIO.IN)

	self.moving_forward = False
	self.moving_backward = False

	self.stop()

    def is_moving(self):
	return self.moving_forward or self.moving_backward

    def is_front_sensor_blocked(self):
	return GPIO.input(self.sensor_front_pin) == GPIO.LOW

    def is_back_sensor_blocked(self):
	return GPIO.input(self.sensor_back_pin) == GPIO.LOW

    def move_to_front(self):
	print("Moving to front")
	if self.is_front_sensor_blocked():
	    self.stop()
	    return

	self.moving_forward = True
	self.moving_backward = False
	GPIO.output(self.forward_pin, GPIO.HIGH)
	GPIO.output(self.backward_pin, GPIO.LOW)
	self.movement_timeout = 15

    def move_to_back(self):
	print("Moving to back")
	if self.is_back_sensor_blocked():
	    self.stop()
	    return

	self.moving_forward = False
	self.moving_backward = True
	GPIO.output(self.forward_pin, GPIO.LOW)
	GPIO.output(self.backward_pin, GPIO.HIGH)
	self.movement_timeout = 15

    def stop(self):
	print("Stopping movement of Linear motor")
	GPIO.output(self.forward_pin, GPIO.LOW)
	GPIO.output(self.backward_pin, GPIO.LOW)
	
	self.moving_forward = False
	self.moving_backward = False
	self.movement_timeout = 0

    def update(self, delta_time):
	if self.is_moving():
	    self.movement_timeout -= delta_time
	    if self.movement_timeout <= 0:
		print("Motor timeout!")
		self.stop()

	    if self.moving_forward and self.is_front_sensor_blocked():
		self.stop()
	    if self.moving_backward and self.is_back_sensor_blocked():
		self.stop()

class StateMachine:

    def __init__(self, motor_zelo, motor_celjust, motor_jezicek, motor_tipalke, motor_voskovna):
	self.motor_zelo = motor_zelo
	self.motor_celjust = motor_celjust
	self.motor_jezicek = motor_jezicek
	self.motor_tipalke = motor_tipalke
	self.motor_voskovna = motor_voskovna

        self.current_timeout = 0
        self.current_state = State.IDLE

        self.i2c = I2C()
	'''
	BackgroundImage()
	'''

    def on_enter_state(self, new_state):
	self.on_state_exit()

	self.current_state = new_state

        # Probably move motors first, then play video
        self.current_timeout = State.get_time(new_state)

        print("Entering new state ", new_state)

        # Play video or camera
        if self.current_state == State.SIMULACIJA_CEBELJEGA_VIDA:
            Camera(self.current_timeout)
        else:
            video_url = State.get_video_url(self.current_state)
            if video_url is not None:
                Video(video_url)

	    if self.current_state == State.RILCEK_IN_MEDNA_GOLSA:
		self.motor_celjust.move_to_front()
	    elif self.current_state == State.TIPALNICE:
		self.motor_tipalnice.move_to_front()
	    elif self.current_state == State.PIKCASTE_IN_SESTAVLJENE_OCI:
		pass
	    elif self.current_state == State.SIMULACIJA_CEBELJEGA_VIDA:
		pass
	    elif self.current_state == State.NOTRANJI_ORGANI:
		pass
	    elif self.current_state == State.CVETNI_PRAH:
		GPIO.output(27, GPIO.HIGH)
	    elif self.current_state == State.PROPOLIS:
		GPIO.output(17, GPIO.HIGH)
	    elif self.current_state == State.VOSKOVNA_ZLEZA:
		self.motor_voskovna.move_to_front()
	    elif self.current_state == State.VAROJA:
		pass
	    elif self.current_state == State.ZELO:
		self.motor_zelo.move_to_front()

    def on_state_exit(self):
	if self.current_state == State.RILCEK_IN_MEDNA_GOLSA:
	    self.motor_celjust.move_to_back()
	elif self.current_state == State.TIPALNICE:
	    self.motor_tipalnice.move_to_back()
	elif self.current_state == State.PIKCASTE_IN_SESTAVLJENE_OCI:
	    pass
	elif self.current_state == State.SIMULACIJA_CEBELJEGA_VIDA:
	    pass
	elif self.current_state == State.NOTRANJI_ORGANI:
	    pass
	elif self.current_state == State.CVETNI_PRAH:
            GPIO.output(27, GPIO.LOW)
	elif self.current_state == State.PROPOLIS:
            GPIO.output(17, GPIO.LOW)
	elif self.current_state == State.VOSKOVNA_ZLEZA:
	    self.motor_voskovna.move_to_back()
	elif self.current_state == State.VAROJA:
	    pass
	elif self.current_state == State.ZELO:
	    self.motor_zelo.move_to_back()


    def on_state_timeout(self):
        self.on_enter_state(State.IDLE)

    def try_to_enter_new_state(self):
        button = self.i2c.get_pressed_button()
        if button is not None:
            state = State.get_state_from_button(button)
            if state is not None:
                self.on_enter_state(button)

    def update(self, delta_time):

        if self.current_timeout > 0:
            self.current_timeout -= delta_time
            if self.current_timeout <= 0:
                self.on_state_timeout()

        else:
            if self.current_state == State.IDLE:
                self.try_to_enter_new_state()


def main():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(17, GPIO.OUT)
	GPIO.setup(27, GPIO.OUT)

	motor_zelo = LinearMotor(18, 23, 22, 10)
	motor_celjust = LinearMotor(24, 25, 9, 11)
	motor_jezicek = LinearMotor(8, 7, 0, 5)
	motor_tipalke = LinearMotor(1, 12, 6, 13)
	motor_voskovna = LinearMotor(16, 20, 19, 26)

	motors = [motor_zelo, motor_celjust, motor_jezicek, motor_tipalke, motor_voskovna]

	'''
	for i in range(1, 1000):
		time.sleep(0.08)

		linear_motor.update(0.08)
		print("Moving:", linear_motor.is_moving())
		print("Sensor front", linear_motor.is_front_sensor_blocked())
		print("Sensor back", linear_motor.is_back_sensor_blocked())

		if not linear_motor.is_moving():
			time.sleep(5)
			linear_motor.move_to_front()
			if not linear_motor.is_moving():
				linear_motor.move_to_back()

	'''

	state_machine = StateMachine(motor_zelo, motor_celjust, motor_jezicek, motor_tipalke, motor_voskovna)

	last_update = time.time()
	while True:
		now = time.time()
		delta_time = now - last_update

		last_update = now
		state_machine.update(delta_time)

		time.sleep(0.03)
		
		for motor in motors:
			motor.update(delta_time)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
	import traceback
	traceback.print_exc(e)
    
    finally:
	GPIO.cleanup()
