"""Common OSCAR listener class for both AIM and ICQ."""

from aires import singleton
import re
from twisted.internet import default
from twisted.words.protocols import oscar
from twisted.internet import protocol, pollreactor

class OscarListener(oscar.BOSConnection):
    capabilities = [] # [ oscar.CAP_CHAT ]

    def initDone(self):
        self.requestSelfInfo().addCallback(self.gotSelfInfo)
        self.requestSSI().addCallback(self.gotBuddyList)

    def gotSelfInfo(self, user):
        #print user.__dict__
        self.agent = singleton.format_name('AIM', user.name)
        self.name = user.name

    def gotBuddyList(self, l):
        #print l
        self.activateSSI()
        self.setProfile("""Aires-python.""")
        self.setIdleTime(0)
        self.clientReady()

    def updateBuddy(self, user):
        #print user
        pass

    def offlineBuddy(self, user):
        #print "offline", user.name
        pass

    def _sendMessage(self, user, reply):
        self.sendMessage(user, reply, wantAck = 1).addCallback(self.messageAck)

    def receiveMessage(self, user, multiparts, flags):
        #print user.name, multiparts, flags

        username = singleton.format_name('AIM', user.name)
        message  = multiparts[0][0]

        # Sanitize the user's message.
        message = re.sub(r'<(.|\n)+?>', '', message)
        message = re.sub(r'\t+', '', message)
        message = message.strip()

        #print "%s> %s" % (user.name, message)
        reply = singleton.get_reply(self.agent, username, message)

        # Format it with the bot's font settings.
        settings = singleton.get_listener(self.agent)
        formatted = settings['font'][0] + reply + settings['font'][1]

        # Queue the reply.
        output = [(formatted.encode('utf8'),)]
#        self.sendMessage(user.name, output, wantAck = 1).addCallback(self.messageAck)
        singleton.add_queue(
            agent   = self.agent,
            func    = self._sendMessage,
            args    = (user.name, output),
            recover = 3
        )

    def messageAck(self, (username, message)):
        #print "message sent to %s acked" % username
        pass

    def gotAway(self, away, user):
        pass

    def receiveWarning(self, newLevel, user):
        pass

    def warnedUser(self, oldLevel, newLevel, username):
        pass

    def createdRoom(self, (exchange, fullName, instance)):
        pass

    def receiveChatInvite(self, user, message, exchange, fullName, instance, shortName, inviteTime):
        pass

    def chatJoined(self, chat):
        pass

    def chatReceiveMessage(self, chat, user, message):
        pass

    def chatMemberJoined(self, chat, member):
        pass

    def chatMemberLeft(self, chat, member):
        pass
