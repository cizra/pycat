var maxlen = 10;
var socket = null;
var outputf = null;
var inputf = null;
var mudReaderBusy = false;
var mudReader = new FileReader();
var inQ = []; // binary blobs incoming from socket, waiting to be processed
var outS = []; // line-split view of screen, bounded by vertical size
var ansi_up = new AnsiUp;

function capOutput() {
    outS = outS.slice(Math.max(0, outS.length - maxlen));
}

mudReader.addEventListener("loadend", function() {
    var processed = mudReader.result;
    processed = Telnet.parse(processed);
    if (processed) { // just GMCP?
        processed = processed.replace(/\r/g, "");
        processed = ansi_up.ansi_to_html(processed);
        processed = processed.trim();
        var split = processed.split(/\n/);
        split.forEach(function(line){outS.push(line);});
        capOutput();
    }
    if (inQ.length > 0) {
        mudReader.readAsBinaryString(inQ.shift());
    } else {
        mudReaderBusy = false;
        window.setTimeout(scroll, 1); // release the mudReader faster, but still scroll on event
    }
});

function flushQ() {
    if (!mudReaderBusy) {
        mudReaderBusy = true;
        mudReader.readAsBinaryString(inQ.shift());
    }
}

function sendRaw(stuff) {
    var b = new Blob([stuff], {type: 'application/octet-stream'});
    socket.send(b);
}

function send(text) {
    if (text[0] == ';')
        text = text.slice(1);
    else
        text = text.replace(/;/g, "\n");
    sendRaw(text + "\n");
    text.split(/\n/).forEach(function(line) {
        outS.push('⇨' + line);
    });
    capOutput();
    scroll();
    inputf.focus();
}

function scroll() {
    outputf.innerHTML = outS.join('\n');
    // Only scroll if the user isn't reading backlog
    if (inputf === document.activeElement)
        outputf.scrollTop = 1E20;
}

function startSocket() {
    inputf = document.getElementById('inputfield');
    outputf = document.getElementById('output');
    socket = new WebSocket('ws://' + window.location.hostname + ':7901', ['binary']);
    socket.addEventListener('message', function (event) {
        inQ.push(event.data);
        flushQ();
    });
    socket.onerror=function (e) {
        outputf.innerHTML += "\n\n\nWebSocket Error: " + e.reason;
        scroll();
    }
    socket.onclose=function(e){
        outputf.innerHTML += "\n\n\nWebSocket Close: " + e.reason;
        scroll();
    }

    function oninput(event) {
        if (event.keyCode == 13) {
            send(inputf.value);
            inputf.select();
        }
    }
    inputf.onkeypress = function() {return oninput(event);};

    inputf.select();
}

function addGmcpHandlers() {
    /*
    Telnet.handle("room.info", function() {
        console.log("In room " + Telnet.gmcp()['room']['info']['num']);
    });
    */
}

function rnum() {
    return Telnet.gmcp()['room']['info']['num'];
}

function start() {
    startSocket();
    addGmcpHandlers();
    document.getElementById('pInput').onclick = function() { document.getElementById('pInput').select();};
    document.getElementById('pInput').oninput = function() { findRoom('pInput', 'pList');};
    winHeight = parseInt(document.defaultView.getComputedStyle(outputf, null)['height'].replace("px", ""));
    lineHeight = parseInt(document.defaultView.getComputedStyle(outputf, null)['line-height'].replace("px", ""));
    var page = Math.floor(winHeight / lineHeight) + 1;
    maxlen = page * 10;
}
