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
            greet: "Hello! I'm Albot Einstein, your personal Einstein bot. " +
                "Ask me anything about myself. But before we proceed, what should I call you? " +
                "Also, how familiar are you with my scientific work on a scale of 1-5? (5 being very)",
            error: "I'm sorry, I did not get that. Could you please try again?"
        }
    };
    initEvents();
    addToChat(config.msgs.greet, true)
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
            '       <img src="/static/img/ico.png">' +
            '   </div>' +
            '   <div class="received_msg">' +
            '       <div class="received_withd_msg">' +
            '           <p>' + msg + '</p>' +
            '           <span class="time_date">' + moment().format('hh:mm a | MMM D, YYYY') + '</span>' +
            '       </div>' +
            '   </div>' +
            '</div>'
        ));

    } else {

        msgHistoryWindow.append($(
            '<div class="outgoing_msg">' +
            '   <div class="sent_msg">' +
            '       <p>' + msg + '</p>' +
            '       <span class="time_date">' + moment().format('hh:mm a | MMM D, YYYY') + '</span>' +
            '   </div>' +
            '</div>'
        ));
    }

    var chatWindowJS = document.getElementsByClassName(config.elems.msgHistoryClass)[0];
    chatWindowJS.scrollTo(0, chatWindowJS.scrollHeight);
}

function initEvents() {

    var chatWindow = $('.' + config.elems.chatWindowClass);
    chatWindow.keypress(function (event) {
        if (event.which === 13) {
            var msg = chatWindow.val();
            chatWindow.val('');
            addToChat(msg);
            chat(msg);

        }
    });

    var sendButton = $('.' + config.elems.sendButtonClass);
    sendButton.click(function () {
        var msg = chatWindow.val();
        chatWindow.val('');
        addToChat(msg);
        chat(msg);
    });
}

