// get DOM elements                
var dataChannelLog = document.getElementById('data-channel'),
    iceConnectionLog = document.getElementById('ice-connection-state'),
    iceGatheringLog = document.getElementById('ice-gathering-state'),
    signalingLog = document.getElementById('signaling-state');

var onResponseCallback = null;

// peer connection
var pc = null;

// data channel
var dc = null, dcInterval = null;

var activePC = false;
var activeDC = false;
var cb = null;

// счетчик для шагов заданий
var task = 1

// счетчик для переключения между блоками вопросов (их пока всего 2), по умолчанию загружается первый блок, но можно перключаться на второй и обратно
var blockquestion = 1

function toggleLockedState(state = null, isBroken = true) {
  pageLocked  = state;

  // a basic example would look like this:
  //$('body').toggle('isLocked', state);
  if(state)
    $('body').css('pointer-events', 'none');
  else
    $('body').css('pointer-events', 'auto');
  $('#connection-modal').modal(state ? 'show' : 'hide' );
  if(state)
    if(isBroken)
        document.getElementById('connection-modal-text').innerHTML = "Проблемы в сети связи. Пытаемся восстановить соединение. Если ничего не изменится в ближайшее время, попробуйте перезагурзить страницу.";
    else
        document.getElementById('connection-modal-text').innerHTML = "Устанавливаем соединение с сервером. Подождите пожалуйста.";
}

function createPeerConnection(cb) {
    var config = {
        sdpSemantics: 'unified-plan',
    };
    if(!document.getElementById('local-peers-checkbox').checked) {
        console.log('Using STUN server')
        config['iceServers'] = [{ urls: "stun:stun.l.google.com:19302" }];
    } else {
        console.log('Not using STUN server')
    }


    try {
        pc = new RTCPeerConnection(config);
        dc = pc.createDataChannel("BackChannel");
    } catch(e) {
        if(!activePC)
            alert("Невозможно установить соединение с сервером. Проверьте сетевые подключения и перезагрузите страницу.");
        return null;
    }

/*    
    // register some listeners to help debugging
    pc.addEventListener('icegatheringstatechange', function() {
        iceGatheringLog.textContent += ' -> ' + pc.iceGatheringState;
    }, false);
    iceGatheringLog.textContent = pc.iceGatheringState;

    pc.addEventListener('iceconnectionstatechange', function() {
        iceConnectionLog.textContent += ' -> ' + pc.iceConnectionState;
    }, false);
    iceConnectionLog.textContent = pc.iceConnectionState;

    pc.addEventListener('signalingstatechange', function() {
        signalingLog.textContent += ' -> ' + pc.signalingState;
    }, false);
    signalingLog.textContent = pc.signalingState;
*/
    // connect audio
    pc.addEventListener('track', function(evt) {
        document.getElementById('audio').srcObject = evt.streams[0];
    });
    pc.addEventListener("connectionstatechange", function(evt){
        document.getElementById("pc-notification-div").innerHTML = pc?pc.connectionState:"pc == null";
        document.getElementById("dc-notification-div").innerHTML = dc?dc.readyState:"dc == null";
        console.log("111");
        if(pc.connectionState == "connected" && !activePC) {
            activePC = true;
            toggleLockedState(false);
        } else if (pc.connectionState == "connected" && activePC) {
            console.log("333");
            if(pageLocked) {
                console.log("444");
                toggleLockedState(false);
                connectionState = "just_restored";
            }
        } else if (activePC) {
            console.log("555");
            if(!pageLocked) {
                console.log("666");
                toggleLockedState(true);
            }
            if(pc.connectionState == "failed") {
                if(dc)
                    dc.close();
                    dc = null;
                if(pc){
                    pc.close();
                    pc = null;
                }
                try_restore();
            }
        }
    });

    dc.onopen = () => {
        console.log("1111");
        document.getElementById("pc-notification-div").innerHTML = pc?pc.connectionState:"pc == null";
        document.getElementById("dc-notification-div").innerHTML = dc?dc.readyState:"dc == null";

        if(!activeDC) {
            console.log("2222");
            activeDC = true;
            console.log("3333");
            document.getElementById("dc-notification-div").innerHTML = dc.readyState;
            console.log("4444");
            cb();
            console.log("5555");
        } else {
            if(pageLocked) {
                console.log("6666");
                toggleLockedState(false);
                console.log("7777");
            }
        }
    }

    dc.onclose = () => {
        console.log("datachannel close");
        document.getElementById("pc-notification-div").innerHTML = pc?pc.connectionState:"pc == null";
        document.getElementById("dc-notification-div").innerHTML = dc?dc.readyState:"dc == null";
        if(activeDC) {
            if(!pageLocked)
                toggleLockedState(true);
        }
    };

    dc.onmessage = (message) => {
        console.log("DC message: " + message);
        result = JSON.parse(message.data);
        if(result.hasOwnProperty('result_string'))
            document.getElementById('feedback-div-text').innerHTML = result.result_string;
        if(onResponseCallback) {
            if(pageLocked)
                pageLocked = false;
            onResponseCallback();
        }
    }


    return pc;
}

async function try_restore(){
    if(!pc) {
        console.log("trying to restore connection");
        await start();
        setTimeout(try_restore, 5000);
    }
}

function negotiate() {
    console.log('preparing offer');
    return pc.createOffer().then(function(offer) {
        console.log("setting local description")
        return pc.setLocalDescription(offer);
    }).then(function() {
        // wait for ICE gathering to complete
        return new Promise(function(resolve) {
            if (pc.iceGatheringState === 'complete') {
                console.log('Ice Gathering State: complete immediately');
                resolve();
            } else {
                function checkState() {
                    console.log('in icegatheringstatechange handler')
                    if (pc.iceGatheringState === 'complete') {
                        console.log('Ice Gathering State: complete after waiting');
                        pc.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                }
                pc.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }).then(function() {
        var offer = pc.localDescription;
        var codec;
        //https://stackoverflow.com/questions/46063374/is-it-really-possible-for-webrtc-to-stream-high-quality-audio-without-noise
        offer.sdp = offer.sdp.replace('useinbandfec=1', 'useinbandfec=1; stereo=1; maxaveragebitrate=510000');
        console.log('sending offer');
        return fetch('offer', {
            body: JSON.stringify({
                sdp: offer.sdp,
                type: offer.type
            }),
            headers: {
                'Content-Type': 'application/json'
            },
            method: 'POST'
        });
    }).then(function(response) {
        return response.json();
    }).then(function(answer) {
        console.log('offer accepted');
        var result = pc.setRemoteDescription(answer);
        console.log('showing content');
        return result;
    }).catch(function(e) {
        alert(e);
    });
}

function start(cb) {

    console.log("start");
    pc = createPeerConnection(cb);
    if(!pc)
        return null;

    var time_start = null;

    function current_stamp() {
        if (time_start === null) {
            time_start = new Date().getTime();
            return 0;
        } else {
            return new Date().getTime() - time_start;
        }
    }

    var constraints = {
        //https://stackoverflow.com/questions/46063374/is-it-really-possible-for-webrtc-to-stream-high-quality-audio-without-noise
        audio: {
            autoGainControl: false,
            channelCount: 2,
            echoCancellation: false,
            latency: 0,
            noiseSuppression: false,
            sampleRate: 48000,
            sampleSize: 16,
            volume: 1.0            
        } //true
    };

    if (constraints.audio) {
        navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
            stream.getTracks().forEach(function(track) {
                pc.addTrack(track, stream);
            });
            return negotiate();
        }, function(err) {
            alert('Could not acquire media: ' + err);
            return false;
        });
    } else {
        return negotiate();
    }
}

function start_recording(meta, cb) {
    if (dc.readyState == "open") {
        var message = {
            action : "start_recording",
            meta: meta
        };
        dc.send(JSON.stringify(message));
        cb();
    } else
        alert("dc.readyState = " + dc.readyState + ',\npc.connectionState = ' + pc.connectionState);
}

function stop_recording(postmeta, cb) {
    console.log("stop_recording");
    if (dc.readyState == "open") {
        if(cb) {
            onResponseCallback = cb;
            pageLocked = true;
        }
        var message = {
            action: "stop_recording",
            postmeta: postmeta
        };
        dc.send(JSON.stringify(message));
    }
}

function stop() {
    if (dc) {
        dc.close();
    }
    // close transceivers
    if (pc.getTransceivers) {
        pc.getTransceivers().forEach(function(transceiver) {
            if (transceiver.stop) {
                transceiver.stop();
            }
        });
    }
    // close local audio
    pc.getSenders().forEach(function(sender) {
        sender.track.stop();
    });
/*
    // close peer connection
    setTimeout(function() {
        pc.close();
    }, 500);
*/
    pc.close();
}

function gonext() {
    //alert('Task='+task+'__block='+blockquestion);
    document.getElementById(('block'+blockquestion+'step'+task)).style.display = 'none';
    document.getElementById('goprev').style.display = 'inline-block';
    task = task+1
    
    if (task < 3){
        document.getElementById(('block'+blockquestion+'step'+task)).style.display = 'inline-block';
    } else if (task == 3){
        document.getElementById(('block'+blockquestion+'step'+task)).style.display = 'inline-block';
        document.getElementById('gonext').style.display = 'none';
    }
    document.getElementById('currentstep').value = task 
    //alert('Task='+task);
}

function goprev() {
    document.getElementById(('block'+blockquestion+'step'+task)).style.display = 'none';
    task = task-1
    if (task > 1 && task <= 3){
        document.getElementById(('block'+blockquestion+'step'+task)).style.display = 'inline-block';
        if (task != 3) {
            document.getElementById('gonext').style.display = 'inline-block';     
        }
        
    } else if (task == 1){
        document.getElementById(('block'+blockquestion+'step'+task)).style.display = 'inline-block';
        document.getElementById('goprev').style.display = 'none';
        document.getElementById('gonext').style.display = 'inline-block';
    }
    document.getElementById('currentstep').value = task 
    //alert("Task="+task);
}

function startblock2(){
    document.getElementById(('block'+blockquestion)).style.display = 'none';
    blockquestion = 2
    document.getElementById(('block'+blockquestion)).style.display = 'inline-block'; 
    document.getElementById('gonext').style.display = 'none';
    document.getElementById('goprev').style.display = 'none';
    task = 1  
}

function startblock1(){
    document.getElementById(('block'+blockquestion)).style.display = 'none';
    blockquestion = 1
    document.getElementById(('block'+blockquestion)).style.display = 'inline-block';   
    document.getElementById('gonext').style.display = 'none';
    document.getElementById('goprev').style.display = 'none';
    task = 1
}

function getNewPhrase() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("phrase").innerHTML = this.responseText;
        }
    };
xhttp.open("GET", "http://localhost:8080/handle_new_phrase", true);
xhttp.send();
}

//setInterval(getNewPhrase, 1000);
