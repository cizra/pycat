var Gmcp = function() {
    var exports = {}
    var gmcp = {};
    var handlers = {};
    exports.gmcp = function() { return gmcp; };
    var gmcpIn_fragment = "";
    var plaintext_fragment = "";
    var state = 0;

    const GMCP = 0xc9;
    const SE   = 0xf0;
    const SB   = 0xfa;
    const WILL = 0xfb;
    const WONT = 0xfc;
    const DO   = 0xfd;
    const DONT = 0xfe;
    const IAC  = 0xff;

    // state machine:
    /* 0: plaintext,
       1: got IAC while in plaintext,
       2: got WILL,
       3: got IAC SB,
       4: got IAC SB GMCP,
       5: got IAC SB unknown subchannel,
       6: got IAC while in subchannel,
       */

    var state_handlers = [
        function(c) { // 0
            if (c == IAC)
                state = 1;
            else
                plaintext_fragment += String.fromCharCode(c);
        },
        function(c) { // 1
            if (c == WILL)
                state = 2;
            else if (c == SB)
                state = 3;
            else {
                // echo on/off?
                console.log("IAC junk ", c);
                plaintext_fragment += String.fromCharCode(c);
                state = 0;
            }
        },
        function(c) { // 2
            var out = [];
            if (c == GMCP) {
                console.log("Server requested GMCP, enabling");
                out.push(IAC, DO, GMCP);
                var version = window.localStorage.getItem('version') || "0";
                gmcpify('Core.Hello { "client": "Cizrian Connectificator", "version": "' + version  + '" }').forEach(a => out.push(a));
                gmcpify('Core.Supports.Set ["char 1", "char.base 1", "char.maxstats 1", "char.status 1", "char.statusvars 1", "char.vitals 1", "char.worth 1", "comm 1", "comm.tick 1", "group 1", "room 1", "room.info 1"]').forEach(a => out.push(a));
            } else {
                console.log("IAC WILL junk ", c);
                out.push(IAC, DONT, c);
            }
            state = 0;
            return out;
        },
        function(c) { // 3
            if (c == GMCP) {
                state = 4;
            } else {
                console.log("IAC SB unknown subchannel ", c);
                state = 5;
            }
        },
        function(c) { // 4
            if (c == IAC)
                state = 6;
            else
                gmcpIn_fragment += String.fromCharCode(c);
        },
        function(c) { // 5
            if (c == IAC)
                state = 6;
        },
        function(c) { // 6
            if (c != SE)
                console.log("IAC SB data IAC junk", c);
            state = 0;
            handleGmcp(gmcpIn_fragment);
            gmcpIn_fragment = "";
        }
    ];

    function gmcpify(str) {
        var byteArray = [IAC, SB, GMCP]
        for (i in str)
            byteArray.push(str[i].charCodeAt());
        return byteArray.concat([IAC, SE]);
    }

    function handleGmcp(str) {
        var space = str.indexOf(' ');
        var cmd = str.slice(0, space);
        var data = str.slice(space+1);
        var keys = cmd.split('.');
        var nesting = keys.splice(0, keys.length - 1);
        var lastkey = keys[keys.length - 1];
        var current = gmcp;
        for (i in nesting) {
            var nest = nesting[i];
            if (! (nest in current))
                current[nest] = {}
            current = current[nest];
        }
        var obj = null;
        try {
            obj = JSON.parse(data);
        } catch(e) {
            if (e instanceof SyntaxError)
                obj = {"string": data};
            else
                throw e;
        }
        current[lastkey] = obj;
        runOnGmcps(cmd, obj);
    }

    function runOnGmcps(cmd, obj) {
        if (cmd in handlers)
            handlers[cmd]();
    }

    exports.parse = function(input) {
        var cmds = [];
        for (i in input) {
            var reaction = state_handlers[state](input[i].charCodeAt());
            if (reaction) {
                reaction.forEach(a => cmds.push(a))
            }
        }
        var plaintext = plaintext_fragment;
        plaintext_fragment = "";
        return [plaintext, cmds]
    }

    exports.handle = function(cmd, callable) {
        handlers[cmd] = callable;
    }

    exports.rnum = function() {
        if ('room' in gmcp
            && 'info' in gmcp['room']
            && 'num' in gmcp['room']['info'])
            return gmcp['room']['info']['num'];
        return 0;
    }

    exports.gmcpify = gmcpify;

    return exports;
};
