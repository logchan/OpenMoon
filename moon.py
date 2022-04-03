import logging
import os
import time
from argparse import ArgumentParser
from pathlib import Path

import serial
import serial.tools.list_ports

from config import ColorConfig, Config, FrameConfig
from specs import get_actual_specs

default_color = [
    FrameConfig(1000, [
        [0, 0.25, 255, 255, 255],
        [0.25, 0.5, 255, 255, 0],
        [0.5, 0.75, 255, 0, 255],
        [0.75, 1, 0, 255, 255],
    ]),
    FrameConfig(1000, [
        [0, 0.25, 255, 255, 0],
        [0.25, 0.5, 255, 0, 255],
        [0.5, 0.75, 0, 255, 255],
        [0.75, 1, 255, 255, 255],
    ])
]


class OpenMoon:
    def __init__(self, config_file, colors_file):
        self.config_file = Path(config_file)
        self.colors_file = Path(colors_file)
        self.cfg: Config = load_object(config_file, Config)
        self.colors: ColorConfig = load_object(colors_file, ColorConfig)
        for lst in [self.colors.inner, self.colors.outer]:
            if len(lst) == 0:
                lst += default_color

        self.durations = [0, 0]
        self.frame_indices = [0, 0]
        self.conn = None

        self.save_config()
        self.save_colors()

    def save_config(self):
        save_object(self.config_file, self.cfg)

    def save_colors(self):
        save_object(self.colors_file, self.colors)

    def loop(self):
        while True:
            if self.conn is None:
                wait = self.connect()
            else:
                wait = self.update()
            time.sleep(wait/1000)

    def connect(self) -> float:
        cfg = self.cfg.serial
        port = cfg.port
        if port is None:
            ports = serial.tools.list_ports.comports()
            if len(ports) > 0:
                port = ports[0].name
            else:
                return cfg.reconn_wait

        try:
            logging.info(f"Connecting to: {port}")
            self.conn = serial.Serial(port, cfg.baudrate, timeout=1)
            if not self.conn.is_open:
                raise ValueError("Connection is not open after creation")
            return cfg.reconn_wait
        except Exception as ex:
            logging.error(f"Faild connecting to {port}: {repr(ex)}")
            self.conn = None

            return cfg.reconn_wait

    def update(self) -> float:
        cfg = self.cfg.serial
        loops = [self.cfg.inner_loop, self.cfg.outer_loop]
        colors = [self.colors.inner, self.colors.outer]
        update_idx = []

        for i in range(len(colors)):
            self.durations[i] -= cfg.update_wait
            if self.durations[i] <= 0:
                update_idx += [i]

        for i in update_idx:
            logging.debug(f"Update group {i}")
            color = colors[i]
            loop = loops[i]

            frame_idx = (self.frame_indices[i] + 1) % len(color)

            frame = color[frame_idx]
            self.frame_indices[i] = frame_idx
            self.durations[i] = frame.duration

            for spec in frame.colors:
                spec = list(spec)
                spec[0] = int(spec[0] * loop.count)
                spec[1] = int(spec[1] * loop.count)

                if len(spec) == 5:
                    actual_specs = [spec]
                else:
                    actual_specs = get_actual_specs(spec)

                for begin, end, r, g, b in actual_specs:
                    logging.debug(f"Set LED {begin} - {end} to ({r}, {g}, {b})")

                    for led in range(begin, end):
                        self.send(f"COL {i} {led} {r} {g} {b}")

            logging.debug("Update LED")
            self.send("SHOW")

        return cfg.update_wait

    def send(self, cmd: str):
        self.conn.write((cmd + "\n").encode("ascii"))
        self.conn.flush()


def save_object(file, obj):
    base_dir = os.path.split(file)[0]
    if base_dir != "":
        os.makedirs(base_dir, exist_ok=True)

    with open(file, "w", encoding="utf-8") as f:
        f.write(obj.to_json(indent=4))


def load_object(file, cls):
    if not os.path.isfile(file):
        return cls()

    with open(file, "r", encoding="utf-8") as f:
        return cls.from_json(f.read())


def main():
    parser = ArgumentParser()
    parser.add_argument("-c", "--colors", default="local/colors.json", help="Path to JSON color settings file")
    parser.add_argument("--config", default="local/config.json", help="Path to JSON configuration file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
        level=logging.DEBUG if args.verbose else logging.INFO)

    moon = OpenMoon(args.config, args.colors)

    try:
        moon.loop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
