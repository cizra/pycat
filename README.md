# Rationale

Existing MUD clients either
- invent their own scripting language, which usually sucks (Tintin++)
- are written for Windows, and require jumping through crazy hoops to get to work right on Linux/Mac (MUSHclient+Python used to require installing Python + Pywin32 in Wine (and these days it's just plain impossible))
- are optimized for Lua, and Python is either absent, or a second-class citizen (MUSHclient can't do cross-module function calls in Python, Mudlet is Lua only)

There are workarounds for everything, but sooner or later you'll wish you could stop working around, and start working on.

... hence:

# pycat

A MUD client inspired by the simplicity of netcat, written in Python, in a modular and hackable way. Its features:
- Works as a proxy: you run pycat, then connect a regular basic MUD client to localhost
- Caching: if your frontend MUD client disconnects from pycat, it'll keep running triggers/timers and accumulating output. Upon reconnecting, it'll dump the whole output into your MUD client.
- No redundant functionality. In particular, no Readline support.
- Modular, layered design
  - Telnet connection (supports GMCP)
  - A base client (implements command stacking, #number spam, talks to modules)
  - A bunch of modules doing their own things (for example, the Logger module triggers on all MUD output and stuffs it all into a file)
  - Your 'client' which brings together the modules you want to include (here it's possible to bring in MUD-class-specific stuff)
  - Most of the code is reloadable at runtime
- Triggers, replacements, aliases, yada yada, anything you can implement in Python
- GMCP-based automapper

# howto

1. Clone the repo
2. Install Python3
3. Edit the `sample.py, specify the host/port to connect to
4. run `python3 ./pycat.py sample 4000`
5. connect a regular MUD client to host `::1` port 4000 (edit the bind address and socket address family if your frontend MUD client doesn't support IPv6) 
6. write your own world module. There's a bunch of sample code in `coffee.py`.  You can pass command-line parameters from pycat to your world module.
