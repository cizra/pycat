var Ui = function() {
    var exports = {};
    var socket = null;
    exports.init = function(socket) { this.socket = socket }
    var outS = []; // line-split view of screen, bounded by vertical size
    var inputf = document.getElementById('inputfield');
    var outputf = document.getElementById('output');
    var ansi_up = new AnsiUp;
    winHeight = parseInt(document.defaultView.getComputedStyle(outputf, null)['height'].replace("px", ""));
    lineHeight = parseInt(document.defaultView.getComputedStyle(outputf, null)['line-height'].replace("px", ""));
    var page = Math.floor(winHeight / lineHeight) + 1;
    var maxlen = page * 10;

    exports.blit = function() {
        outputf.innerHTML = outS.join('');
        // Only scroll if the user isn't reading backlog
        if (inputf === document.activeElement)
            outputf.scrollTop = 1E20;
    };

    function capOutput() {
        outS = outS.slice(Math.max(0, outS.length - maxlen));
    };

    exports.output = function(mudstr) {
        mudstr = mudstr.replace(/\r/g, "");
        mudstr = ansi_up.ansi_to_html(mudstr);
        var split = mudstr.split(/\n/);
        outS.push(split.shift());
        split.forEach(function(line){
            outS.push('\n' + line);
        });
        capOutput();
    };

    exports.macros = {
         97: function() {send("sw")},
         98: function() {send("s")},
         99: function() {send("se")},
        100: function() {send("w")},
        101: function() {send("l")},
        102: function() {send("e")},
        103: function() {send("nw")},
        104: function() {send("n")},
        105: function() {send("ne")},
        107: function() {send("d")},
        109: function() {send("u")}
    }

    inputf.onkeydown = function(e) {
        if (e.key == "Enter") {
            send(inputf.value);
            inputf.select();
            return false;
        } else if (e.keyCode in exports.macros) {
            exports.macros[e.keyCode]();
            return false;
        }
    }

    inputf.select();
    return exports;
};
