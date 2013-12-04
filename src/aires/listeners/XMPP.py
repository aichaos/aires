"""Extensible Messaging and Presence Protocol."""

from aires.listeners import Listener
from aires import singleton

from twisted.internet import reactor
from twisted.names.srvconnect import SRVConnector
from twisted.words.xish import domish
from twisted.words.protocols.jabber import xmlstream, client
from twisted.words.protocols.jabber.jid import JID

class XMPP(Listener):
    def init(self):
        self.username, self.server = self.mirror('username').split('@')
        self.password = self.mirror('password')
        listener = self.parent().get_listener(self._id)
        self.resource = listener['resource']
        self.nickname = listener['nickname']

        jid = "%s@%s/%s" % (self.username, self.server, self.resource)
        self.jid = JID(jid)
        self.f = client.XMPPClientFactory(self.jid, self.password)

        self.con = SRVConnector(
            reactor, 'xmpp-client', self.jid.host, self.f, defaultPort=5222)
        #self.con.connect()

    def is_twisted(self):
        return True

    def handlers(self):
        # Register event handlers.
        self.f.addBootstrap(xmlstream.STREAM_CONNECTED_EVENT, self.on_connected)
        self.f.addBootstrap(xmlstream.STREAM_END_EVENT, self.on_disconnected)
        self.f.addBootstrap(xmlstream.STREAM_AUTHD_EVENT, self.on_authenticated)
        self.f.addBootstrap(xmlstream.INIT_FAILED_EVENT, self.on_init_failed)
        pass

    def signon(self):
        # Log in.
        self.con.connect()
        self.online(True)

    def loop(self):
        pass

    def rawDataIn(self, buf):
        #print "RECV: %s" % unicode(buf, 'utf-8').encode('ascii', 'replace')
        pass

    def rawDataOut(self, buf):
        #print "SEND: %s" % unicode(buf, 'utf-8').encode('ascii', 'replace')
        pass

    def send_message(self, to, content):
        message = domish.Element(('jabber:client', 'message'))
        message['to']   = JID(to).full()
        message['type'] = 'chat'
        message.addElement('body', 'jabber:client', content)
        self.xmlstream.send(message)

    def allow_subscribe(self, to):
        """Respond to an add (subscribe) request by allowing it."""
        message = domish.Element({'jabber:client', 'presence'})
        message['to']   = JID(to).full()
        message['type'] = 'subscribed'
        self.xmlstream.send(message)

    def deny_subscribe(self, to):
        """Respond to somebody removing us from their contact list."""
        message = domish.Element({'jabber:client', 'presence'})
        message['to']   = JID(to).full()
        message['type'] = 'unsubscribed'
        self.xmlstream.send(message)

    def on_connected(self, xs):
        #print 'Connected.'
        self.xmlstream = xs

        # Log all traffic.
        xs.rawDataInFn = self.rawDataIn
        xs.rawDataOutFn = self.rawDataOut

    def on_disconnected(self, xs):
        #print 'Disconnected.'
        pass

    def on_authenticated(self, xs):
        #print 'Authenticated.'
        presence = domish.Element(('jabber:client', 'presence'))
        xs.send(presence)

        # Register event handlers.
        xs.addObserver('/message', self.on_message)
        xs.addObserver('/presence', self.on_presence)
        xs.addObserver('/*', self.debug)
#        xs.sendFooter()
#        reactor.callLater(5, xs.sendFooter)

    def on_init_failed(self, failure):
        print 'Initialization failure.'
        print failure

    def on_message(self, el):
        #print "Received message!"

        # The sender.
        source   = str(el['from'])
        username = singleton.format_name('XMPP', source.split("/")[0])

        # Get the chat body.
        body = None
        for e in el.elements():
            if e.name == 'body':
                if el['type'] == 'chat':
                    body = str(e)

        #print "body:", body
        if body is None:
            return

        reply = singleton.get_reply(self._id, username, body)
        self.send_message(source, reply)

    def on_presence(self, el):
        #print "Received presence!"

        # The sender.
        source   = str(el['from'])
        username = singleton.format_name('XMPP', source.split("/")[0])

        # What type of presence message is this?
        if el['type'] == 'subscribe':
            # Somebody added us to their buddy list. Allow this.
            print "Allowing subscription by {}".format(source)
            self.allow_subscribe(source)
        elif el['type'] == 'unsubscribe':
            # They removed us from their list. Revoke the subscription.
            print "{} deleted us, removing subscription.".format(source)
            self.deny_subscribe(source)

    def debug(self, el):
        print el.toXml().encode('utf-8')

    def on_iq(self, con, iq):
        pass
