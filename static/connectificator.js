var maxlen = 10000;
var socket = null;
var outputf = null;
var inputf = null;
var mudReaderBusy = false;
var mudReader = new FileReader();
var inQ = [];
var outS = [];
var ansi_up = new AnsiUp;

mudReader.addEventListener("loadend", function() {
    // var out = mudReader.result;
    // out = Telnet.parse(out);
    // out = out.replace(/\r/g, "");
    // out = ansi_up.ansi_to_html(out);
    outS.push(ansi_up.ansi_to_html(Telnet.parse(
                mudReader.result.replace(/\r/g, ''))));
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
    split = text.split(/\n/);
    for (i in split)
        outputf.innerHTML += "➡" + split[i] + "\n";
    inputf.focus();
}

function scroll() {
    var out = outS.join('');
    if (out.length >= maxlen) {
        outputf.innerHTML = out.substr(out.length - maxlen);
    } else if (outputf.innerHTML.length + out.length >= maxlen) {
        var sum = outputf.innerHTML + out;
        outputf.innerHTML = sum.substr(out.length - maxlen);
    } else {
        outputf.innerHTML += out;
    }
    outS = [];
    // Only scroll if the user isn't reading backlog
    if (inputf === document.activeElement)
        outputf.scrollTop = 1E10;
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
}
