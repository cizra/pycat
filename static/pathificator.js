var Pathificator = function() {
    var exports = {}

    var url = function() {
        var parser = document.createElement('a');
        parser.href = window.location.href;
        // replace port with 8000, if it's unset
        var port = ":8000";
        if (parser.port)
            port = ":" + parser.port;
        console.log(parser.protocol + "//" + parser.hostname + port + "/");
        return parser.protocol + "//" + parser.hostname + port + "/";
    }()

    function getRooms(name, callback) {
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                // { roomid: roomname }
                callback(JSON.parse(this.responseText));
            }
        };
        xhttp.open("GET", url + "findRoom/" + name, true);
        xhttp.send();
    }

    exports.findRoom = function(inputName, tableName) {
        var input = document.getElementById(inputName);
        getRooms(input.value, function(rooms) {
            var table = document.getElementById(tableName);
            table.innerHTML = "";
            buildHtmlTable(input, table, rooms);
        });
    }

    function pathfind(targetRoom, input) {
        var xhttp = new XMLHttpRequest();
        var start_time = new Date().getTime();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                document.getElementById('lag').innerHTML = (new Date().getTime() - start_time) + "ms";
                send(this.responseText);
                input.innerHTML = "";
            }
        };
        xhttp.open("GET", url + "pathFind/" + Gmcp.rnum() + "/" + targetRoom, true);
        xhttp.send();
    }

    var _tr_ = document.createElement('tr'),
    _td_ = document.createElement('td');

    function buildHtmlTable(input, table, rooms) {
        for (var id in rooms) {
            var tr = _tr_.cloneNode(false);
            tr.onclick = function(id) { return function() {
                input.value = rooms[id];
                table.innerHTML = "";
                pathfind(id, input);
            }}(id)
            var tdId = _td_.cloneNode(false);
            tdId.appendChild(document.createTextNode(id));
            var tdName = _td_.cloneNode(false);
            tdName.appendChild(document.createTextNode(rooms[id]));
            tr.appendChild(tdId);
            tr.appendChild(tdName);
            table.appendChild(tr);
        }
    }
    return exports;
}
