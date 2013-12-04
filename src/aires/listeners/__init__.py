class Listener(object):
    """Base class for Aires listeners."""

    def __init__(self, parent, id, bot, mirror):
        self._parent = parent
        self._id     = id
        self._bot    = bot
        self._mirror = mirror
        self._online = False
        self.init()

    def init(self):
        """This method is called when the listener is first initialized.
        This method should be used to initialize the object for the
        listener and nothing more."""
        pass

    def is_twisted(self):
        """All listeners that rely on Twisted should return a True value
        for this function."""
        return False

    def handlers(self):
        """This method should be used to (re)define handler bindings."""
        pass

    def mirror(self, key):
        """Query the mirror object for the given key (for example, username
        and password). Returns None if the key wasn't found."""
        if key in self._mirror:
            return self._mirror[key]
        return None

    def online(self, value=None):
        """Indicate whether your bot is currently online or not.
        In your signon() method, you should call online(True) to update
        its status!"""
        if isinstance(value, bool):
            self._online = value
        return self._online

    def signon(self):
        """This method is called to sign on to the network."""
        self.online(True)

    def signoff(self):
        self.online(False)

    def loop(self):
        pass

    def say(self, *messages):
        self._parent.say(*messages)

    def parent(self):
        return self._parent
