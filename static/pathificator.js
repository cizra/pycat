var url = window.location.href.substr(0, window.location.href.length - 1) + ':8000/';
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

function findRoom(inputName, tableName) {
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
    xhttp.open("GET", url + "pathFind/" + rnum() + "/" + targetRoom, true);
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
