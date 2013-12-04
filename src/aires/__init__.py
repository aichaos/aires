#!/usr/bin/env python

from termcolor import colored
from importlib import import_module
from collections import deque
import time
import re

from twisted.internet import pollreactor
pollreactor.install()
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

import config

singleton = None # TODO: I don't like this, want it to be threadsafe

class Aires():
    _debug = True # TODO
    _color = { # Color preferences
        'notice': ['green',  ['bold']],
        'error':  ['red',    ['bold']],
        'user':   ['cyan',   ['bold']],
        'bot':    ['yellow', ['bold']],
        'text':   ['white',  []],
    }
    _twisted = False # Whether we are using Twisted at all
    _loops   = []    # Event loops from the calling program
    _bots    = {}    # Bot configurations
    _brains  = {}    # Bot brain objects
    _mirrors = {}    # Bot listener connections
    _agents  = {}    # Map mirror (agent-names) to their bots.
    _queues  = {}    # Message queues for the agents

    def __init__(self):
        global singleton
        singleton = self
        pass

    def register_loop(self, func, freq):
        """Register a function in your main program that should be called
        iteratively while the Twisted reactor is running. This is useful
        for e.g. graphical front-ends that need to refresh constantly."""
        self._loops.append([ func, freq ])

    def say(self, *messages):
        """Write a message to the terminal.

        @param messages: A list of messages to send."""

        printed = []
        for mess in messages:
            if type(mess) == list:
                color, mess = mess
                ansi = self._color[color]
                printed.append(colored(mess, ansi[0], attrs=ansi[1]))
            else:
                ansi = self._color['text']
                printed.append(colored(mess, ansi[0], attrs=ansi[1]))

        print "".join(printed)

    def init(self):
        self.say(
            ['notice', '-== '],
            ['error', 'Welcome to Aires!'],
            ['notice', ' ==-'],
        )

        # TODO: load core config files

        # Load bot config files.
        self.say(
            ['error', '== '],
            ['notice', 'Reading chatterbot settings'],
            ['error', ' =='],
        )
        for cfg in config.list('bots'):
            self.say(
                ['error', ':: '],
                "Read: %s" % cfg,
            )
            bot = re.sub(r'\.json$', '', cfg)
            self._bots[bot] = config.read('bots/' + cfg)

        # Initialize the brains.
        self.say(
            ['error', '== '],
            ['notice', 'Initializing chatterbot brains'],
            ['error', ' =='],
        )
        for bot in sorted(self._bots):
            brain = self._bots[bot]['brain']['name']
            args  = self._bots[bot]['brain']['args']
            self.say(
                ['error', ':: '],
                'Loading brain "%s" for bot "%s"' % (brain, bot)
            )

            # Dynamically import and load the brain.
            cls = self._dyn_import('aires.brains.'+brain, brain)
            self._brains[bot] = cls(self, args)

        # Initialize the listeners.
        self.say(
            ['error', '== '],
            ['notice', 'Initializing chatterbot listeners (mirrors)'],
            ['error', ' =='],
        )
        for bot in sorted(self._bots):
            for listener, largs in self._bots[bot]['listeners'].iteritems():
                # Skip inactive listeners.
                if largs['active'] != True:
                    continue

                # Import the listener module.
                cls = self._dyn_import('aires.listeners.'+listener, listener)

                # Initialize all the mirrors.
                for mirror in largs['mirrors']:
                    username = mirror['username']
                    uid      = self.format_name(listener, username)
                    self.say("\tCreating mirror: " + uid)

                    # Map the agent name to the bot.
                    self._agents[uid] = bot

                    # Initialize the listener for this mirror.
                    self._mirrors[uid] = cls(self, uid, bot, mirror)
                    self._mirrors[uid].handlers()

                    # Does this mirror use Twisted?
                    if self._mirrors[uid].is_twisted():
                        self._twisted = True

    def run(self):
        """Start the bot running. This signs on all the listeners and fires off
        the Twisted reactor event loop. If your program needs to do things on
        each loop, use the register_loop() method to add your own LoopingCall
        callbacks."""
        # Make sure the bots are online.
        for uid, mirror in self._mirrors.iteritems():
            if not mirror.online():
                # Sign it on.
                mirror.signon()

        # Are we using Twisted?
        if self._twisted:
            # Set up the loop callback in the reactor.
            LoopingCall(self.reactor_loop).start(0.1)

            # Register any custom loops.
            for loop in self._loops:
                func, interval = loop
                LoopingCall(func).start(interval)

            reactor.run()
        else:
            # No, so use a simpler event loop.
            while True:
                self.reactor_loop()
                for loop in self._loops:
                    loop[0]()
                time.sleep(0.1)

    def reactor_loop(self):
        """Our custom main loop for the Twisted reactor."""
        # Run the listeners' loops.
        for uid, mirror in self._mirrors.iteritems():
            if mirror.online():
                mirror.loop()

        # Run through the event queues.
        self.run_queues()

    def format_name(self, listener, name):
        listener = listener.upper()
        name     = name.lower()
        return '-'.join((listener, name))

    def get_listener(self, agent):
        """Given an agent ID, get the corresponding listener data."""
        # Resolve the bot's identity.
        bot = self._agents[agent]
        listener = self._listener_from_uid(agent)
        return self._bots[bot]['listeners'][listener]

    def get_reply(self, agent, username, message):
        """Get a reply."""
        # Resolve the bot's identity.
        bot = self._agents[agent]

        # TODO: blocked users?

        # TODO: check admins

        # Get a reply.
        reply = self._brains[bot].reply(username, message)

        # TODO: log it
        print "[{}] {}".format(username, message)
        print "[{}] {}\n".format(agent, reply)
        return reply

    def add_queue(self, agent, func, args, recover=0):
        """Add a task to an agent's queue."""
        # Does this agent have a queue yet?
        if not agent in self._queues:
            self._queues[agent] = {
                'continue': 0, # The time until the next item can be performed
                'queue': deque(),
            }

        # If there's no recovery time, do this event now.
        if recover == 0:
            self.exec_queue(dict(agent=agent, func=func, args=args, recover=recover))
            return

        # Add to the queue.
        self._queues[agent]['queue'].append(dict(
            agent=agent,
            func=func,
            args=args,
            recover=recover,
        ))

    def run_queues(self):
        """Loop through all queues and run the events. This is called
        automatically as part of the reactor_loop."""
        for agent, q in self._queues.iteritems():
            # Are we waiting?
            if q['continue'] > time.time():
                continue

            # Run the next event
            if len(q['queue']) > 0:
                evt = q['queue'].popleft()
                self.exec_queue(evt)

                # Recovery time?
                if 'recover' in evt and evt['recover'] > 0:
                    q['continue'] = time.time() + evt['recover']

    def exec_queue(self, evt):
        """Execute a queued event."""
        agent = evt['agent']
        func  = evt['func']
        func(*evt['args'])

    def _listener_from_uid(self, uid):
        """Disassemble a UID (LISTENER-name format) and return the listener."""
        parts = uid.split('-')
        return parts[0]

    def _dyn_import(self, mod_name, classname):
        """Dynamically import a module and return the class from within."""
        module = import_module(mod_name)
        return getattr(module, classname)
