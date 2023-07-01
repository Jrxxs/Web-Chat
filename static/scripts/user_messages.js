document.addEventListener('DOMContentLoaded', function() {
    const companion = JSON.parse(document.getElementById("Companion_username").textContent);
	const client = JSON.parse(document.getElementById("Client_username").textContent);
	const HubName = 'testHub';
	let roomName = '';
	let Unreaded_Messages = [];
	let crosses = document.querySelector('#friendlist').children;


	if (client < companion) {
		roomName = client + '_and_' + companion;
	} else {
		roomName = companion + '_and_' + client;
	};

    const chatSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/chat/'
            + roomName
            + '/'
        );

    const HubSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/hub/'
            + HubName
            + '/'
        );

	$(document).ready(function() {
		let div = document.getElementById('chat-log');
		let divs = div.children;
		for (var i = 0; i < divs.length; i++) {
			let status = divs[i].querySelector('#Status-False');
			if (status != null) {
				let className = divs[i].className;
				if (className == 'chat-message-left pb-4' && status.id == 'Status-False') {
					Unreaded_Messages.push(divs[i].id);
				}
			}
		}
		if (Unreaded_Messages.length > 0) {
			document.getElementById(Unreaded_Messages[0]).scrollIntoView({block: "end", behavior: "auto"});
		}
		else {
			if (div.lastChild.previousSibling) {
				div.lastChild.previousSibling.scrollIntoView({block: "end", behavior: "auto"});
			}
		}
	});

    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
		console.log(data);
        const message = data['message'];
        const sender = data['sender'];
        const date = data['date'];
		const message_id = data['Message_Id'];
        if (sender == companion && sender != client) {
			let msgListTag = document.createElement('div');
			msgListTag.className = 'chat-message-left pb-4';
			msgListTag.setAttribute("id", message_id);
			let divStat = document.createElement('div');
			divStat.setAttribute("id", "Status-False");
			msgListTag.appendChild(divStat);
			let div1 = document.createElement('div');
			let ImgTag = document.createElement('img');
			ImgTag.className = 'rounded-circle mr-1';
			ImgTag.src = JSON.parse(document.getElementById("Companion_photo_url").textContent);
			ImgTag.alt = companion;
			ImgTag.width = 40;
			ImgTag.height = 40;
			let div11 = document.createElement('div');
			div11.className = 'text-muted small text-nowrap mt-2';
			div11.innerHTML += date;
			div1.appendChild(ImgTag);
			div1.appendChild(div11);
			let div2 = document.createElement('div');
			div2.className = 'flex-shrink-1 bg-light rounded py-2 px-3 ml-3';
			let div22 = document.createElement('div');
			div22.className = 'font-weight-bold mb-1';
			div22.innerHTML += companion;
			div2.appendChild(div22);
			div2.innerHTML += message;

			msgListTag.appendChild(div1);
			msgListTag.appendChild(div2);
			document.querySelector('#chat-log').appendChild(msgListTag);
        } else {
        	let msgListTag = document.createElement('div');
			msgListTag.className = 'chat-message-right pb-4';
			msgListTag.setAttribute("id", message_id);
			let divStat = document.createElement('div');
			divStat.setAttribute("id", "Status-False");
			msgListTag.appendChild(divStat);
			let div1 = document.createElement('div');
			let ImgTag = document.createElement('img');
			ImgTag.src = JSON.parse(document.getElementById("Client_photo_url").textContent);
			ImgTag.className = 'rounded-circle mr-1';
			ImgTag.alt = client;
			ImgTag.width = 40;
			ImgTag.height = 40;
			let div11 = document.createElement('div');
			div11.className = 'text-muted small text-nowrap mt-2';
			div11.innerHTML += date;
			div1.appendChild(ImgTag);
			div1.appendChild(div11);
			let div2 = document.createElement('div');
			div2.className = 'flex-shrink-1 bg-light rounded py-2 px-3 mr-3';
			let div22 = document.createElement('div');
			div22.className = 'font-weight-bold mb-1';
			div22.innerHTML += 'You';
			div2.appendChild(div22);
			div2.innerHTML += message;

			msgListTag.appendChild(div1);
			msgListTag.appendChild(div2);
			document.querySelector('#chat-log').appendChild(msgListTag);

			document.getElementById(message_id).scrollIntoView({block: "end", behavior: "smooth"});
        }
		Unreaded_Messages.push(message_id);
    };

    HubSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        let message = data['message'];
		if (message == 'init_connected_users_list') {
			init_online_users(data['connected_users']);
		} else if (message == 'new_connectoin') {
			client_connected(data['sender']);
		} else if (message == 'disconnection') {
			client_disconnected(data['sender']);
		} else if (message == 'new_message') {
			appeared_new_message(data['sender']);
		} else if (message == 'reading_successful') {
			set_readed_status(data['id'], data['sender']);
		} else if (message == 'finded') {
			finded_users(data['users']);
		}
    };

	$(document.getElementById('chat-log')).scroll( function() {
		if (this.scrollTop == 0) {
			get_latest_messages(this.firstChild.nextSibling.id);
		}
		for (var i = 0; i < Unreaded_Messages.length; i++) {
			elem = "#"+`${Unreaded_Messages[i]}`;
			if (document.getElementById(Unreaded_Messages[i]).className == 'chat-message-left pb-4' && is_visible(this, elem)){
				message_reading(Unreaded_Messages[i]);
			}
		}
	})

	function is_visible(window, elem) {
		let Offset = document.getElementById('input-group').clientHeight;
		let wt = $(window).scrollTop();
		let wh = $(window).height() - Offset;
		let et = $(elem).offset().top;
		let eh = $(elem).outerHeight();
		let dh = $(document).height();   
		return (wt + wh >= et || wh + wt == dh || eh + et < wh);
	}

	function message_reading(id) {
		HubSocket.send(JSON.stringify({
				'command': 'read_message',
				'sender': companion,
				'receiver': client,
				'id': id
			}));
	}

	function get_latest_messages(id) {
		$.ajax({
			url: window.location.pathname,
			type: 'get',
			dataType: 'json',
			data: {'type': 'update', 'value': id},
			success: function(response) {
				for (let i=0; i<response.length; i++) {
					append_new_messages(response[i], id);
				}
			}
		});
	}

	function append_new_messages(object, scroll_id){
        const sender = object['sender'];
        const date = object['Date_Time'];
		const message_id = object['id'];
        const message = object['From_User']['username'];
		if (sender == companion && sender != client) {
			let msgListTag = document.createElement('div');
			msgListTag.className = 'chat-message-left pb-4';
			msgListTag.setAttribute("id", message_id);
			let divStat = document.createElement('div');
			divStat.setAttribute("id", "Status-True");
			msgListTag.appendChild(divStat);
			let div1 = document.createElement('div');
			let ImgTag = document.createElement('img');
			ImgTag.className = 'rounded-circle mr-1';
			ImgTag.src = JSON.parse(document.getElementById("Companion_photo_url").textContent);
			ImgTag.alt = companion;
			ImgTag.width = 40;
			ImgTag.height = 40;
			let div11 = document.createElement('div');
			div11.className = 'text-muted small text-nowrap mt-2';
			div11.innerHTML += date;
			div1.appendChild(ImgTag);
			div1.appendChild(div11);
			let div2 = document.createElement('div');
			div2.className = 'flex-shrink-1 bg-light rounded py-2 px-3 ml-3';
			let div22 = document.createElement('div');
			div22.className = 'font-weight-bold mb-1';
			div22.innerHTML += companion;
			div2.appendChild(div22);
			div2.innerHTML += message;

			msgListTag.appendChild(div1);
			msgListTag.appendChild(div2);
			document.querySelector('#chat-log').prepend(msgListTag);
        } else {
        	let msgListTag = document.createElement('div');
			msgListTag.className = 'chat-message-right pb-4';
			msgListTag.setAttribute("id", message_id);
			let divStat = document.createElement('div');
			divStat.setAttribute("id", "Status-True");
			msgListTag.appendChild(divStat);
			let div1 = document.createElement('div');
			let ImgTag = document.createElement('img');
			ImgTag.src = JSON.parse(document.getElementById("Client_photo_url").textContent);
			ImgTag.className = 'rounded-circle mr-1';
			ImgTag.alt = client;
			ImgTag.width = 40;
			ImgTag.height = 40;
			let div11 = document.createElement('div');
			div11.className = 'text-muted small text-nowrap mt-2';
			div11.innerHTML += date;
			div1.appendChild(ImgTag);
			div1.appendChild(div11);
			let div2 = document.createElement('div');
			div2.className = 'flex-shrink-1 bg-light rounded py-2 px-3 mr-3';
			let div22 = document.createElement('div');
			div22.className = 'font-weight-bold mb-1';
			div22.innerHTML += 'You';
			div2.appendChild(div22);
			div2.innerHTML += message;

			msgListTag.appendChild(div1);
			msgListTag.appendChild(div2);
			document.querySelector('#chat-log').prepend(msgListTag);

			document.getElementById(scroll_id).scrollIntoView({block: "start", behavior: "auto"});
        }
	}

	function set_readed_status(id, sender) {
		elem = document.getElementById(id).querySelector('#Status-False');

		user = document.querySelector('#' + sender);
		if (user && elem != null && elem.id == 'Status-False' && Unreaded_Messages.includes(id)) {
			value = user.children[0].textContent;
			if (value != '' && value != '1') {
				value = Number(value) - 1;
			} else {
				value = '';
			}
			user.children[0].textContent = `${value}`;
			let index = Unreaded_Messages.indexOf(id);
			if (index !== -1) {
				Unreaded_Messages.splice(index, 1);
			}
			elem.id = 'Status-True';
		}
	}

	function init_online_users(connected_users) {
		for (let i = 0; i < connected_users.length; i++) {
			user = document.querySelector('#' + connected_users[i]);
			if (user) {
				user.children[1].children[1].children[0].textContent = 'Online';
			}
		}
	};

	function client_connected(conn_client) {
		if (conn_client != client) {
			user = document.querySelector('#' + conn_client);
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
		if (user && sender != client) {
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

    chatSocket.onclose = function(e) {
    	console.error('Chat socket closed unexpectedly');
    };

    HubSocket.onclose = function(e) {
    	console.error('Hub socket closed unexpectedly');
    };

    document.querySelector('#message-input').focus();
    document.querySelector('#message-input').onkeyup = function(e) {
    	if (e.keyCode === 13) {
            document.querySelector('#send-button').click();
        }
    };

    document.querySelector('#send-button').onclick = function(e) {
    	const messageInputDom = document.querySelector('#message-input');
        const message = messageInputDom.value;
        const date = new Date(Date.now()+(1000*60*(-(new Date()).getTimezoneOffset()))).toISOString().replace('T',' ').replace('Z','');
        if (message != '') {
			chatSocket.send(JSON.stringify({
				'message': message,
				'sender': client,
				'receiver': companion,
				'date': date
			}));

			HubSocket.send(JSON.stringify({
				'command': 'send_new_message',
				'sender': client,
				'receiver': companion,
			}));

			messageInputDom.value = '';
        }
	};
}, false); 