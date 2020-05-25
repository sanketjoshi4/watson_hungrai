$(document).ready(function () {
    window.config = {
        elems: {
            botName: 'HungrAI',
            chatWindowClass: 'write_msg',
            msgHistoryClass: 'msg_history',
            sendButtonClass: "msg_send_btn"
        },
        urls: {
            chat: '/chat'
        },
        msgs: {
            error: "I'm sorry, I did not get that. Could you please try again?"
        }
    };
    initEvents();
});

function chat(msg) {
    $.post({
        url: config.urls.chat,
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({msg: msg}),
        success: function (response) {
            addToChat(response.output.generic[0].text, true);
            console.log(response.output.generic[0].text);
        },
        error: function (e) {
            addToChat(config.msgs.error, true);
            console.log(e.responseJSON);
        }
    });
}

function addToChat(msg, incoming) {

    var msgHistoryWindow = $('.' + config.elems.msgHistoryClass);

    if (incoming) {

        msgHistoryWindow.append($(
            '<div class="incoming_msg">' +
            '   <div class="incoming_msg_img">' +
            '       <img src="https://ptetutorials.com/images/user-profile.png" alt="sunil">' +
            '   </div>' +
            '   <div class="received_msg">' +
            '       <div class="received_withd_msg">' +
            '           <p>' + msg + '</p>' +
            '           <span class="time_date"> 11:01 AM    |    June 9</span>' +
            '       </div>' +
            '   </div>' +
            '</div>'
        ));

    } else {

        msgHistoryWindow.append($(
            '<div class="outgoing_msg">' +
            '   <div class="sent_msg">' +
            '       <p>' + msg + '</p>' +
            '       <span class="time_date"> 11:01 AM    |    June 9</span>' +
            '   </div>' +
            '</div>'
        ));

    }
}

function initEvents() {

    var chatWindow = $('.' + config.elems.chatWindowClass);
    chatWindow.keypress(function (event) {
        if (event.which === 13) {
            var msg = chatWindow.val();
            chatWindow.val('');
            addToChat(msg);
            chat(msg)
        }
    });

    var sendButton = $('.' + config.elems.sendButtonClass);
    sendButton.click(function () {
        var msg = chatWindow.val();
        chatWindow.val('');
        addToChat(msg);
        chat(msg)
    });
}

