$(document).ready(function () {

    window.config = {

        elems: {
            botName: 'HungrAI',
            chatWindowClass: 'write_msg',
            msgHistoryClass: 'msg_history',
            sendButtonClass: "msg_send_btn",
            refreshBarClass: "refresh_bar"
        },
        urls: {
            chat: '/chat',
            refresh: '/refresh'
        },
        msgs: {
            greet: 'Hello there! Are you hungry? I\'ve got you covered! I\'m Hunger A.I., your personal food assistant! Can I have your name please?',
            error: "I'm sorry, I did not get that. Could you please try again?"
        },
        status: {
            end: false,
            recording: false
        },
        text_to_speech_delay: 0
    };

    initEvents();
    $.post({
        url: config.urls.refresh,
        cache: false,
        success: function (resp) {
            console.log('refreshed!')
        },
        error: function (e) {
            console.log('not refreshed! : ' + e.responseText)
        }
    });
    addToChat(config.msgs.greet, true)
});

function chat(msg) {
    $.post({
        url: config.urls.chat,
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({msg: msg}),
        cache: false,
        success: function (resp) {

            if (resp.type === 'generic') {

                addToChat(resp.value, true);
                console.log(resp.value);

                setTimeout(function () {
                    new Audio('/static/resources/text_to_speech_' + (parseInt(resp.dialog_counter) + 1) + '.wav').play();
                }, config.text_to_speech_delay);

            } else if (resp.type === 'end') {

                addToChat(resp.value, true);
                setTimeout(function () {
                    new Audio('/static/resources/text_to_speech_' + (parseInt(resp.dialog_counter) + 1) + '.wav').play();
                }, config.text_to_speech_delay);

                config.status.end = true;
                $('.type_msg').hide();
                $('.' + config.elems.refreshBarClass).show();
                $('#refresh_btn').click(function () {
                    window.location.href = '/';
                });
                console.log(resp.value);

            } else {
                addToChat(config.msgs.error, true);
            }
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
            '       <img src="/static/img/icon_transparent_circle.png">' +
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

    $('.' + config.elems.msgHistoryClass).click();
    setTimeout(function () {
        new Audio('/static/resources/recorded/999.wav').play();
    }, 2000);

    var chatWindow = $('.' + config.elems.chatWindowClass);
    chatWindow.keypress(function (event) {
        if (event.which === 13) {
            var msg = chatWindow.val();
            chatWindow.val('');
            addToChat(msg);
            chat(msg);
        }
    });
}

navigator.mediaDevices.getUserMedia({audio: true})
    .then(stream => {
        handlerFunction(stream)
    });


function handlerFunction(stream) {
    rec = new MediaRecorder(stream);
    rec.ondataavailable = e => {
        audioChunks.push(e.data);
        if (rec.state == "inactive") {
            let blob = new Blob(audioChunks, {type: 'audio/wav'});
            recordedAudio.src = URL.createObjectURL(blob);
            recordedAudio.controls = true;
            recordedAudio.autoplay = false;
            sendData(blob)
        }
    }
}

async function sendData(data) {

    const formData = new FormData();
    formData.append('audio-file', data);

    $.post({
        url: '/audioUpload',
        data: formData,
        cache: false,
        processData: false,
        contentType: false,
        success: function (resp) {
            addToChat(resp.msg);
            chat(resp.msg);
            console.log(resp.msg);
        },
        error: function (e) {
            console.log('not sent! : ' + e.responseText)
        }
    });
}

record.onclick = e => {
    if (config.status.recording == false) {
        config.status.recording = true;
        record.style.backgroundColor = "#8f4039";
        audioChunks = [];
        rec.start();
    } else {
        config.status.recording = false;
        record.style.backgroundColor = "#05728f";
        rec.stop();
    }
};

