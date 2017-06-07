# Rationale

Existing MUD clients either
- invent their own scripting language, which usually sucks (Tintin++)
- are written for Windows, and require jumping through crazy hoops to get to work right on Linux/Mac (MUSHclient+Python requires installing Python + Pywin32 in Wine)
- are optimized for Lua, and Python is either absent, or a second-class citizen (MUSHclient can't do cross-module function calls in Python, Mudlet is Lua only)

There are workarounds for everything, but sooner or later you'll wish you could stop working around, and start working on.

... hence:

# pycat

A MUD client inspired by the simplicity of netcat, written in Python, in a modular and hackable way. Its features:
- No redundant functionality (tmux gives scrollback, rlwrap gives line editing capabilities)
- Modular, layered design
  - Telnet connection (supports GMCP)
  - A base client (implements command stacking, #number spam, talks to modules)
  - A bunch of modules doing their own things (for example, the Logger module triggers on all MUD output and stuffs it all into a file)
  - Your 'client' which brings together the modules you want to include (here it's possible to bring in MUD-class-specific stuff)
  - Most of the code is reloadable at runtime
- Triggers, replacements, aliases, yada yada, anything you can implement in Python
- TODO: no timers at moment, but they're easyish to add
- GMCP-based automapper
  - Pathfinding code is written in C++ for fun and speed (it takes 9.5ms to path around a 50k-room randomly connected graph), uses `boost::astar_search` as backend
  - Bookmarked rooms
  - The C++ part is generic enough to be used in non-GMCP-enabled environments, but you'll have to modify the Python parts.
  - TODO: no visualization of any kind, so far

# proxy.py

As a bonus, you get also a TCP keepalive proxy. It holds the MUD connection open in case you want to restart the client fully, or switch computers, or something, then spams you the accumulated MUDside output. Apologies for the crummy code, I wrote it a long time ago.
