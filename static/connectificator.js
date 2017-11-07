var socket = null;
var outputf = null;
var inputf = null;

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
    // Only scroll if the user isn't reading backlog
    if (inputf === document.activeElement)
        outputf.scrollTop = output.scrollHeight;
}

function startSocket() {
    inputf = document.getElementById('inputfield');
    outputf = document.getElementById('output');
    var ansi_up = new AnsiUp;
    socket = new WebSocket('ws://' + window.location.hostname + ':7901', ['binary']);
    socket.addEventListener('message', function (event) {
        var mudReader = new FileReader();
        mudReader.addEventListener("loadend", function() {
            var out = mudReader.result;
            out = Telnet.parse(out);
            out = out.replace(/\r/g, "");
            outputf.innerHTML += ansi_up.ansi_to_html(out);
            scroll();
        });

        mudReader.readAsBinaryString(event.data);
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

function start() {
    startSocket();
    document.getElementById('pInput').oninput = function() { findRoom('pInput', 'pList');};
}
