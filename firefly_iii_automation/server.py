import json
import tempfile
from pathlib import Path

from simple_websocket_server import WebSocket, WebSocketServer

from firefly_iii_automation.transactions_parsers import parse_bt_transaction_report


class SimpleWebSocketServer(WebSocket):
    def handle(self):
        data = json.loads(self.data)
        with tempfile.TemporaryDirectory() as tempdir:
            tempdir = Path(tempdir)
            temp_file = tempdir / 'file.csv'
            with temp_file.open('w') as f:
                f.write(data['content'])

        result = [
            # item.to_dict()
            # for item in parse_bt_transaction_report(temp_file)
        ]

        self.send_message(json.dumps({"result": result}))

    def connected(self):
        print(self.address, 'connected')

    def handle_close(self):
        print(self.address, 'closed')


server = WebSocketServer('', 8000, SimpleWebSocketServer)

if __name__ == "__main__":
    server = WebSocketServer('', 8000, SimpleWebSocketServer)
    server.serve_forever()
