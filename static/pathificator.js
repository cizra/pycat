function findRoom(where) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            tgt = document.getElementById('roomlist')
            tgt.innerHTML = "";
            buildHtmlTable(where, tgt, JSON.parse(this.responseText));
        }
    };
    roomname = document.getElementById('input' + where).value;
    xhttp.open("GET", "findRoom/" + roomname, true);
    xhttp.send();
}

function pathfind() {
    to = document.getElementById('inputto');
    if (!to.value || isNaN(to.value)) {
        document.getElementById('inputto').focus();
        return;
    }

    from = document.getElementById('inputfrom');
    if (!from.value || isNaN(from.value)) {
        document.getElementById('inputfrom').focus();
        return;
    }

    var xhttp = new XMLHttpRequest();
    var start_time = new Date().getTime();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById('roomlist').innerHTML = "";
            document.getElementById('path').innerHTML = this.responseText;
            document.getElementById('lag').innerHTML = "Search took " + (new Date().getTime() - start_time) + "ms";
        }
    };
    xhttp.open("GET", "pathFind/" + from.value + "/" + to.value, true);
    xhttp.send();
}

var _tr_ = document.createElement('tr'),
    _td_ = document.createElement('td');

function buildHtmlTable(where, table, dict) {
    for (var id in dict) {
        var tr = _tr_.cloneNode(false);
        tr.onclick = function(id) { return function() {
            document.getElementById('input' + where).value = id;
            pathfind();
        }}(id)
        var tdId = _td_.cloneNode(false);
        tdId.appendChild(document.createTextNode(id));
        var tdName = _td_.cloneNode(false);
        tdName.appendChild(document.createTextNode(dict[id]));
        tr.appendChild(tdId);
        tr.appendChild(tdName);
        table.appendChild(tr);
    }
}
