class Brain(object):
    """Base class for Aires brains."""

    def __init__(self, parent, params):
        self._parent = parent
        self.init(params)

    def init(self, params):
        """This method is called when the brain is initialized or reloaded.
        The 'params' field are the arguments given by the bot config file.
        For example, if your bot requires a directory to load replies from,
        the params would indicate that directory."""
        pass

    def reply(self, username, message):
        """Get a reply for the user's message. This method must return a
        string response."""
        return "[ERR: Brain didn't override reply() method!]"

    def say(self, *messages):
        """Convenience method: a shortcut to say() from the parent Aires
        object."""
        self._parent.say(*messages)

    def parent(self):
        """Shortcut to the parent Aires object."""
        return self._parent
