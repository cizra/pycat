function start() {
    var inputf = document.getElementById('inputfield');
    var outputf = document.getElementById('output');
    var ansi_up = new AnsiUp;
    socket = new WebSocket('ws://' + window.location.hostname + ':7901', ['binary']);
    socket.addEventListener('message', function (event) {
        var mudReader = new FileReader();
        mudReader.addEventListener("loadend", function() {
            var out = mudReader.result.replace(/\r/g, "");
            outputf.innerHTML += ansi_up.ansi_to_html(out);
            outputf.scrollTop = output.scrollHeight;
        });

        mudReader.readAsText(event.data);
    });
    socket.onerror=function (e) {
        outputf.innerHTML += "\n\n\nWebSocket Error: " + e.reason;
    }
    socket.onclose=function(e){
        outputf.innerHTML += "\n\n\nWebSocket Close: " + e.reason;
    }

    function send(text) {
        var b = new Blob([text, "\n"], {type: 'text/plain'});
        socket.send(b);
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
