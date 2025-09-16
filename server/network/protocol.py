import json

class ProtocolError(Exception):
    pass

class Protocol:
    @staticmethod
    def encode(message: dict) -> bytes:
        """
        Encode a dictionary into JSON bytes for sending over the socket.
        """
        if not isinstance(message, dict):
            raise ProtocolError("Message must be a dictionary")
        return (json.dumps(message) + "\n").encode("utf-8")  # add newline as delimiter

    @staticmethod
    def decode(data: bytes) -> dict:
        """
        Decode JSON bytes back into a dictionary.
        """
        try:
            return json.loads(data.decode("utf-8"))
        except Exception as e:
            raise ProtocolError(f"Failed to decode message: {e}")
