document.addEventListener('DOMContentLoaded', function() {
    const HubName = 'testHub';
    const AuthorizedUser = JSON.parse(document.getElementById("Auth_username").textContent);
    let crosses = document.querySelector('#friendlist').children;

    const HubSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/hub/'
            + HubName
            + '/'
        );

    HubSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const message = data['message'];
        if (message == 'init_connected_users_list') {
            init_online_users(data['connected_users']);
        } else if (message == 'new_connectoin') {
            client_connected(data['sender']);
        } else if (message == 'disconnection') {
            client_disconnected(data['sender']);
        } else if (message == 'new_message') {
            appeared_new_message(data['sender']);
        } else if (message == 'finded') {
            finded_users(data['users']);
        }
    };

    function init_online_users(connected_users) {
        for (let i = 0; i < connected_users.length; i++) {
            user = document.querySelector('#' + connected_users[i]);
            if (user) {
                user.children[1].children[1].children[0].textContent = 'Online';
            }
        }
    };

    function client_connected(client) {
        if (client != AuthorizedUser) {
            user = document.querySelector('#' + client);
            if (user) {
                user.children[1].children[1].children[0].textContent = 'Online';
            }
        }
    };

    function client_disconnected(client) {
        user = document.querySelector('#' + client);
        if (user) {
            user.children[1].children[1].children[0].textContent = 'Offline';
        }
    };

    function appeared_new_message(sender) {
        user = document.querySelector('#' + sender);
        if (user) {
            value = user.children[0].textContent;
            if (value == '') {
                user.children[0].textContent = '1';
            } else {
                value = Number(value) + 1;
                user.children[0].textContent = `${value}`;
            }
        }
    };

    let friendlist = document.querySelector('#friendlist').innerHTML;
    $('#search-input').on("input", function() {
        var query = this.value;
        if (query != '') {
            get_users(query);
        } else {
            document.querySelector('#friendlist').innerHTML = friendlist;
            HubSocket.send(JSON.stringify({
                'command': 'refresh_conn_users'
            }));
        }
    });

    function get_users(query) {
        HubSocket.send(JSON.stringify({
                'command': 'find_persons',
                'query': query
            }));
    };

    function finded_users(data) {

        document.querySelector('#friendlist').innerHTML = '';

        if (data != 'no_users') {
            users = JSON.parse(data);

            for (let i = 0; i < users.length; i++) {
                paint_users(users[i]);
            }
        } else {
            document.querySelector('#friendlist').innerHTML += 'Ooops... We hasn`t users with this name!';
        }

    };

    $(document).ready(function () {
        for (let i=0; i< crosses.length; i++) {
            crosses[i].addEventListener('mouseenter', (e) => {
                if (e.target.children[1]) {
                    e.target.children[1].style.visibility = 'visible';
                }
            })
            crosses[i].addEventListener('mouseleave', (e) => {
                if (e.target.children[1]) {
                    e.target.children[1].style.visibility = 'hidden';
                }
            })
        }
    });

    function paint_users(user) {
        let link = document.createElement('a');
        link.href = document.getElementById("add_friend").getAttribute("data-url") + "?friend_id=" + user['id'].toString() + "&prev=" + document.URL;
        link.className = 'list-group-item list-group-item-action border-0';
        link.id = user['username'];
        let div1 = document.createElement('div');
        div1.className = 'badge bg-success float-right';
        link.appendChild(div1);
        let div2 = document.createElement('div');
        div2.className = 'd-flex align-items-start';
        let ImgTag = document.createElement('img');
        ImgTag.src = user['Photo'];
        ImgTag.className = 'rounded-circle mr-1';
        ImgTag.alt = user['username'];
        ImgTag.width = 40;
        ImgTag.height = 40;
        div2.appendChild(ImgTag);
        let div22 = document.createElement('div');
        div22.className = 'flex-grow-1 ml-3';
        div22.innerHTML = user['username'];
        let div222 = document.createElement('div');
        div222.className = 'small';
        let span = document.createElement('span');
        span.className = 'fas fa-circle chat-online';
        div222.appendChild(span);
        div222.innerHTML += user['Status'];
        div22.appendChild(div222);
        div2.appendChild(div22);
        link.appendChild(div2);
        document.querySelector('#friendlist').appendChild(link);
    };

    HubSocket.onclose = function(e) {
        console.error('Hub socket closed unexpectedly');
    };
}, false);