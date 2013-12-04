"""Command line chat interface."""

from aires.listeners import Listener

import thread
from time import sleep

message = "" # TODO: global, not thread safe, oh well
def read_thread():
    global message
    while True:
        message = raw_input("You> ")
        sleep(0.5)

class CLI(Listener):
    def init(self):
        # Listen for messages in a new thread so it doesn't block the other bots.
        thread.start_new_thread(read_thread, ())

    def loop(self):
        global message
        if len(message) > 0:
            reply = self.parent().get_reply(self._id, 'local', message)
            message = ""
            print "%s> %s" % (self.mirror('username'), reply)
