import smbus
import time
from subprocess import Popen, PIPE

assets_path = "/home/pi/IntriCebela/assets/"

class State:
    IDLE = "0"
    PIKCASTE_IN_SESTAVLJENE_OCI = "C"
    SIMULACIJA_CEBELJEGA_VIDA = "D"
    RILCEK_IN_MEDNA_GOLSA = "E"
    TIPALNICE = "F"
    CVETNI_PRAH = "G"
    VOSKOVNA_ZLEZA = "H"
    ZELO = "I"
    NOTRANJI_ORGANI = "J"
    PROPOLIS = "K"
    VAROJA = "L"

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

            print("Read Input: ", char)
            return buttonInput
        
        except IOError as e:
            print("Error reading from i2c", e)
            return None
        except ValueError as e:
            print("Invalid value:", char, ",", e)
            return None
        except Exception as e:
            print("Other error", e)
            return None

class BackgroundImage:
    def __init__(self):
        Popen(["fbi", "-a", "-noverbose", assets_path + "background.jpg"])

class Camera:
    def __init__(self, time=10):
        Popen(["raspivid", "-ifx", "colourswap", "-t", str(time*1000)])

class Video:
    def __init__(self, video_url):
        Popen(['omxplayer', "-o", "local", video_url])

class StateMachine:

    def __init__(self):
        self.current_timeout = 0
        self.current_state = State.IDLE

        self.i2c = I2C()

    def on_enter_state(self, new_state):
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
	state_machine = StateMachine()

	last_update = time.time()
	while True:
		now = time.time()
		delta_time = now - last_update

		last_update = now
		state_machine.update(delta_time)
		
		time.sleep(0.03)

if __name__ == "__main__":
    main()
