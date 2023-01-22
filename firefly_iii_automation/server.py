from simple_websocket_server import WebSocket, WebSocketServer


class SimpleWebSocketServer(WebSocket):
    def handle(self):
        # echo message back to client
        self.send_message(self.data)

    def connected(self):
        print(self.address, 'connected')

    def handle_close(self):
        print(self.address, 'closed')


if __name__ == "__main__":
    server = WebSocketServer('', 8000, SimpleWebSocketServer)
    server.serve_forever()