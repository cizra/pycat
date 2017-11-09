var socket = null;
var mudReader = new FileReader();
var inQ = []; // binary blobs incoming from socket, waiting to be processed
var ui = null;

mudReader.addEventListener("loadend", function() {
    var mudstr = mudReader.result;
    mudstr = Gmcp.parse(mudstr);
    if (mudstr) // just GMCP?
        ui.output(mudstr);
    if (inQ.length > 0)
        mudReader.readAsBinaryString(inQ.shift());
    else
        window.setTimeout(ui.blit, 1); // release the mudReader faster, but still scroll on event
});

function flushQ() {
    if (mudReader.readyState != 1) {
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
        ui.output('⇨' + line + '\n');
    });
    ui.blit();
}

function startSocket() {
    socket = new WebSocket('ws://' + window.location.hostname + ':7901', ['binary']);
    socket.addEventListener('message', function (event) {
        inQ.push(event.data);
        flushQ();
    });
    socket.onerror=function (e) {
        ui.output("\n\n\nWebSocket Error: " + e.reason);
        ui.blit();
    }
    socket.onclose=function(e){
        ui.output("\n\n\nWebSocket Close: " + e.code + " " + e.reason);
        ui.blit();
    }
}

function addGmcpHandlers() {
    /*
    Gmcp.handle("room.info", function() {
        console.log("In room " + Gmcp.gmcp()['room']['info']['num']);
    });
    */
}

function changelog() {
    var changes = [
        "Basic working client",
        "Keypad navigation! Use your numeric keypad, with NumLock \"on\", to walk the world. Plus and Minus go down and up. 5 issues the \"look\" command."
    ]
    var version = changes.length;
    var oldVersion = window.localStorage.getItem('version') || 0
    console.assert(version >= oldVersion)
    var changelog = "Changelog:\n";
    for (i = oldVersion; i < version; ++i)
        changelog += "\nv" + (i+1) + ":\n" + changes[i] + '\n';
    if (changelog != "Changelog:\n")
        alert(changelog);
    window.localStorage.setItem('version', version)
}

function start() {
    ui = Ui();
    startSocket();
    addGmcpHandlers();
    document.getElementById('pInput').onclick = function() { document.getElementById('pInput').select();};
    document.getElementById('pInput').oninput = function() { findRoom('pInput', 'pList');};
    changelog();
}
