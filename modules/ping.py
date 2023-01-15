import telnetlib
from typing import Any

from modules.basemodule import BaseModule


class Ping(BaseModule):
    """
    Periodically sends an AYT (Are you there) packet, to ensure NAT'd connections aren't closed for being silent too long.

    We use an AYT so that the mud doesn't update the idle time of the player.
    """
    def getTimers(self) -> dict[str, Any]:
        return {
            "ping": self.mktimer(60, self.ping, False),
        }

    def ping(self, mud) -> None:
        if mud.mud.telnet:
            mud.mud.telnet.sock.sendall(telnetlib.AYT)
