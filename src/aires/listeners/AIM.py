"""AOL Instant Messenger."""

from aires.listeners import Listener

# The OSCAR protocol is used by both AIM & ICQ.
from aires.listeners.oscar import OscarListener

from twisted.words.protocols import oscar
from twisted.internet import protocol, reactor

class AIM(Listener):
    def init(self):
        pass

    def is_twisted(self):
        return True

    def signon(self):
        username = self.mirror('username')
        password = self.mirror('password')

        hostport = ('login.oscar.aol.com', 5190)

        class OAuth(oscar.OscarAuthenticator):
            BOSClass = OscarListener

        client = protocol.ClientCreator(reactor, OAuth, username, password, icq=0)
        client.connectTCP(*hostport)

        self.online(True)

    def loop(self):
        pass # reactor.run() # TODO: don't run forever
