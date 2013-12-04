# Aires

Aires is a multiprotocol, multibrained chatbot written in Python with a focus on
instant messaging platforms. It has a dynamic module structure to make it easy
for developers to add new protocols and brain backends to it as needed.

Currently it has built-in support for XMPP and AIM (via the OSCAR protocol; ICQ
should be easy to add too!) and comes with support for a
[RiveScript](https://github.com/kirsle/rivescript-python) brain backend. Other
protocols and backends (perhaps AIML) may be explored in the future.

This project is still in early development.

# Setup

The Python dependencies are listed in `requirements.txt` and can easily be
installed via `pip`:

```bash
pip install -r requirements.txt
```

## Bot Settings

There is a default `Sample.json` bot config file in the `bots/` folder which is
preconfigured to listen to the `CLI` front-end (command line interface). Simply
running `python aires-cli.py` will let you chat with a bot immediately.

The files in the `bots/` folder are JSON-encoded config files that can be edited
in any text editor. They have JavaScript-style comments that describe the
various options. To turn on the bots for a particular protocol front-end, e.g.
XMPP, just set `"active": true` under its settings and fill in its login details
in the `mirrors` section.

# Extending

There are base classes for brains and listeners, which are defined in the
`__init__.py` file in each module, respectively. Brains and listeners should
extend from the base classes; use the existing implementations as reference.

The extensions should be self-contained and run using the bot's main loop.
They shouldn't run a loop themselves (as this would block the other bots),
and they should avoid pausing for long periods of time, as the bot is
currently single-threaded.

# License

RiveScript - Rendering Intelligence Very Easily
Copyright (C) 2013 Noah Petherbridge

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
