import json
from io import StringIO

from simple_websocket_server import WebSocket, WebSocketServer

from firefly_iii_automation.transactions_parsers import parse_bt_transaction_report
from firefly_iii_automation.utils.json import dumps


class SimpleWebSocketServer(WebSocket):
    def handle(self):
        data = json.loads(self.data)
        file_obj = StringIO(data['content'])

        results = [
            item.to_dict()
            for item in parse_bt_transaction_report(file_obj)
        ]

        self.send_message(dumps({"results": results}))

    def connected(self):
        print(self.address, 'connected')

    def handle_close(self):
        print(self.address, 'closed')


server = WebSocketServer('', 8000, SimpleWebSocketServer)

if __name__ == "__main__":
    server = WebSocketServer('', 8000, SimpleWebSocketServer)
    server.serve_forever()
