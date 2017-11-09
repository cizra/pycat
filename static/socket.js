Socket = function(ui, gmcp) {
    var exports = {}
    var mudReader = new FileReader();
    var inQ = []; // binary blobs incoming from websock, waiting to be processed

    // eats strings or Uint8Arrays (GMCP)
    function send(stuff) {
        if (stuff.length > 0) {
            console.debug("sock> ", stuff)
            var b = new Blob([stuff], {type: 'application/octet-stream'});
            websock.send(b);
        }
    }

    mudReader.addEventListener("loadend", function() {
        console.debug("sock< ", mudReader.result)
        var parseResult = gmcp.parse(mudReader.result);
        var mudstr = parseResult[0];
        send(new Uint8Array(parseResult[1])); // outgoing GMCP commands
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

    var websock = new WebSocket('ws://' + window.location.hostname + ':7901', 'binary');
    websock.addEventListener('message', function (event) {
        inQ.push(event.data);
        flushQ();
    });
    websock.onerror=function (e) {
        ui.output("\n\n\nWebSocket Error: " + e.reason);
        ui.blit();
    }
    websock.onclose=function(e){
        ui.output("\n\n\nWebSocket Close: " + e.code + " " + e.reason);
        ui.blit();
    }

    exports.send = send;
    exports.gmcpSend = function(cmd) { send(gmcp.gmcpify(cmd)) };

    return exports;
};
