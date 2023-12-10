import logging

from pynput import mouse

from lib.logger import setup_logger
from week1.emitter import ClickEvent, EventEmitter

_logger = logging.getLogger(__name__)

emitter = EventEmitter()
setup_logger()


@emitter.on("click", lambda x: x["x"] < 500)
async def on_click_left(event: ClickEvent):
    print("CLICK LEFT")


@emitter.on("click", lambda x: x["x"] >= 500)
async def on_click_right(event: ClickEvent):
    print("CLICK RIGHT")


def on_click(x: float, y: float, button: str, pressed: bool):
    if pressed:
        print(f"Mouse clicked at ({x}, {y}) with button {button}")
        emitter.emit("click", x=x, y=y)


def main():
    with mouse.Listener(on_click=on_click) as listener:
        print("Listening to mouse events. Click anywhere to see the event.")
        listener.join()


if __name__ == "__main__":
    main()
