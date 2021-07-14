let fileSystem = require('fs');
var socketIO = require('socket.io')

let Server = class {
	constructor() {
		console.log("Starting Server");
		this.gpioReader = new GPIOReader();
		this.httpServer = new HTTPServer();
		this.socketListener = new SocketListener(this.httpServer, this.gpioReader);

		let delta_time = 0.1;
		setInterval(() => {
			this.update(delta_time);
		}, delta_time * 1000);
	}

	update(delta_time) {
		this.gpioReader.update(delta_time);
	}

	deinit() {
		this.gpioReader.deinit();
		this.socketListener.deinit();
	}
};

let HTTPServer = class {
	constructor() {
		this.http = require('http').createServer(this.http_request_handler);
		this.http.listen(80);
	}

	http_request_handler(request, response) {
		fileSystem.readFile(__dirname + request.url, function (err, data) {
			if (err) {
				response.writeHead(404, { 'Content-Type': 'text/html' });
				return response.end("404 Not Found");
			}
			response.writeHead(200, { 'Content-Type': 'text/html' });
			response.write(data);
			return response.end();
		});
	}


};

let GPIOReader = class {
	constructor() {
		if (process.platform === "win32") {
			return;
		}
		// var Gpio = require('onoff').Gpio;
		// this.input1 = new Gpio(5, 'in');
		// this.input_aligned = false;
	}

	update(delta_time) {
		if (process.platform === "win32") {
			return;
		}

	}

	deinit() {
		if (process.platform === "win32") {
			return;
		}
	}
};

let SocketListener = class {
	constructor(httpServer, gpioReader) {
		this.httpServer = httpServer;
		this.gpioReader = gpioReader;
		this.initListeners();
	}

	initListeners() {
		console.log("Initializing socket");
		let socketServer = socketIO(this.httpServer.http);

		var self = this;
		socketServer.sockets.on('connection', function (socket) {
			console.log("Client Connected");

			// socket.on('get_state', function (data) {
			// 	self.onGetState(socket);
			// });
		});
	}

	onGetState(socket) {
		// console.log("[CLIENT] get_state");
		// let state = this.gpioReader.get_sensor_state();
		// if (state != null) {
		// 	console.log("[SERVER] sensor_state is " + state + ". Sending state.");
		// 	socket.emit('set_state', { state: state });
		// } else {
		// 	console.log("[SERVER] sensor_state is null. Not replying.");
	}

	deinit() {
	}
}


intriEksponat = new Server();
process.on('SIGINT', function () {
	intriEksponat.deinit();
	process.exit();
});

