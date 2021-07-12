__all__ = ["ChemyxFusion"]

import asyncio
from typing import Dict, Any, List

from yaqd_core import IsDaemon, HasPosition, HasLimits, UsesSerial, UsesUart, aserial

class ChemyxFusion(IsDaemon):
    _kind = "chemyx-fusion"

    def __init__(self, name, config, config_filepath):
        super().__init__(name, config, config_filepath)
        self._ser = aserial.ASerial(
            self._config["serial_port"], baudrate=self._config["baud_rate"]
        )
        self._rate = None
        self._purging = False
        self._loop.create_task(self._get_rate())  # cache the rate later

    def close(self):
        self._ser.close()

    def direct_serial_write(self, message: bytes):
        self._ser.write(message)

    def get_rate(self) -> float:
        return self._rate

    def prime(self):
        # withdraw fully
        self.logger.info("Priming.")
        self._busy = True
        raise NotImplementedError

    def purge(self):
        # purge fully
        # this also implies that the new position is zero
        self.logger.info("Purging.")
        self._busy = True
        raise NotImplementedError

    def _set_position(self, position: float) -> None:
        amount_from_here = position - self._state["position"]
        self._ser.write(f"set volume {amount_from_here}".encode())
        self._ser.write("start".encode())

    def set_rate(self, rate):
        self._ser.write(f"set rate {rate}".encode())

    async def update_state(self):
        while True:
            out = self._ser.write_then_read("view parameter")
            print(out)
