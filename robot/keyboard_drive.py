import time
import curses

from gpiozero import Button, Motor, Robot

# Motors
robot = Robot(
    left=Motor('GPIO12', 'GPIO18'),
    right=Motor('GPIO19', 'GPIO13')
)

# Emergency stop button
# GPIO26 = physical pin 37
# Other side of button goes to GND
emergency = Button('GPIO26', pull_up=True, bounce_time=0.05)

# Stop the motors immediately when button is pressed
emergency.when_pressed = robot.stop

try:
    stdscr = curses.initscr()
    curses.cbreak()
    stdscr.keypad(1)

    stdscr.addstr(0, 10, "WASD to drive, E to stop, Q to quit")
    stdscr.nodelay(1)

    direction = None

    while direction != ord('q'):
        stdscr.refresh()
        direction = stdscr.getch()

        if direction == ord('e'):
            stdscr.addstr(1, 10, "Stop     ")
            robot.stop()

        if direction == ord('a'):
            stdscr.addstr(1, 10, "Left     ")
            robot.left()

        if direction == ord('s'):
            stdscr.addstr(1, 10, "Backward ")
            robot.backward()

        if direction == ord('d'):
            stdscr.addstr(1, 10, "Right    ")
            robot.right()

        if direction == ord('w'):
            stdscr.addstr(1, 10, "Forward  ")
            robot.forward()

        time.sleep(0.04)

finally:
    robot.stop()
    emergency.close()

    curses.nocbreak()
    stdscr.keypad(0)
    curses.endwin()
    