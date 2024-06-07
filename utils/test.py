import curses

def custom_print(message, stdscr=None):
    if stdscr:
        stdscr.addstr(message + "\n")
        stdscr.refresh()
    else:
        print(message)

def test_custom_print(stdscr):
    curses.echo()
    stdscr.clear()
    
    custom_print("This is a test message.", stdscr)
    stdscr.addstr("\nPress any key to exit.")
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(test_custom_print)