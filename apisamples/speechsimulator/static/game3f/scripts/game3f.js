var currenTask = 0;
var currentLevel = 0;
var keysGame = [];
var results = [];
var resultStr = '';

var StrSp = '';

var tasks = taskList;

var wordsDone = [];
var wordsRemain = [];

var picsDone = [];
var picsRemain = [];

var isLive = false;

var intIndex = 0;
var intPicIndex = 0;
var currW = 0;
var shownString = '';
var activeElement = 'pic';
var ind = 0;
var isImage = false;

var pageLocked = true;

var connectionState = "normal"; // "normal" | "just_restored"

var pronunciationQuality = null;

var repeat = false;

var taskID = 0;

var step = 0;

var remaining = [];
var doAgain = [];

var readyToSwitch = false;

var ready = true;
var init = false;

function run(){
    if(repeat) {
        var dt = new Date();
        utc = dt.toISOString().replaceAll(':', '-').replaceAll('.', '-');
        var meta = {
            taskID: taskID,
            step: step,
            game: 'game3f',
            isImage: false,
            word: shownString,
            datetime: utc,
            connectionState: connectionState
        }
        if(connectionState == "just_restored")
            connectionState = "normal";
        start_recording(meta, function(){
            document.getElementById("content").style.color = 'red';
            try {
                sendLabel(64, com_writer);
            } catch (e) {
                console.log(e);
            }
        });
    }
    else {
        if(step < tasks[taskID].length) {
            if(remaining.length) {
                var index = getRandomInt(0, remaining.length-1);
                shownString = remaining[index];
                remaining.splice(index, 1);
                wordsDone.push(shownString);
                var dt = new Date();
                utc = dt.toISOString().replaceAll(':', '-').replaceAll('.', '-');
                var meta = {
                    taskID: taskID,
                    step: step,
                    game: 'game3f',
                    isImage: false,
                    word: shownString,
                    datetime: utc,
                    connectionState: connectionState
                }
                if(connectionState == "just_restored")
                    connectionState = "normal";
                start_recording(meta, function(){
                    document.getElementById("content").style.color = 'black';
                    document.getElementById("content").innerHTML = /*uiTexts[currentLevel] + "<br />" + */shownString;
                    try {
                        sendLabel(64, com_writer);
                    } catch (e) {
                        console.log(e);
                    }
                }) ;
            } else {
                if(doAgain.length == 0) {
                    step += 1;
                    if(step < tasks[taskID].length)
                        remaining = tasks[taskID][step].slice();
                } else {
                    remaining = doAgain.slice();
                    doAgain = [];
                }
                run();
            }
        } else {
            alert("Задания закончились!" );
            window.location.replace("../");
        }
    }
}
function startGame() {
    taskID = document.getElementById("taskID").value;
    document.getElementById("image-container").style.backgroundImage = "url('static/game3f/images/art/landscape.svg')";
    document.getElementById("image-container").style.backgroundSize = "100% auto";
    document.getElementById("image-container").style.backgroundRepeat = "no-repeat";


    document.addEventListener('keyup', event => {
        if(!pageLocked) {
            if (event.code === 'ArrowLeft') {
              btnclkBad()
            } else if (event.code === 'ArrowRight') {
                btnclkGood()
            } else {
                alert("Нажмите стрелку влево если произношение надо исправить, стрелку вправо, если произношение хорошее")
            }
        } else {
            console.log("Page Locked, no user interaction is allowed");
            event.stopPropagation();
        }
    })

    document.getElementById("start").style.display = 'none';
    document.getElementById("game_settings").style.display = 'none';
    document.getElementById("main").style.display = 'block';

    step = 0;
    remaining = tasks[taskID][step].slice();

    ready = true;
    init = false;
    toggleLockedState(true, false);

    start(run);
}

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function btnclkBad(){
    try {
        sendLabel(58, com_writer);
    } catch (e) {
        console.log(e);
    }

    pronunciationQuality = 'bad';
    if(!repeat)
        repeat = true;
    else {
        doAgain.push(shownString);
        repeat = false;
    }
    btnclk();
}

function btnclkGood(){
    try {
        sendLabel(57, com_writer);
    } catch (e) {
        console.log(e);
    }

    pronunciationQuality = 'good';
    if(repeat) {
        idx = doAgain.indexOf(shownString);
        if(idx != -1)
            doAgain.splice(idx, 1);
        repeat = false;
    }
    btnclk();
}

function btnclk(){
    //small delay
    setTimeout(process, 200);
}

function process(){
    if(shownString.length !== 0){
        stop_recording({
            'pronunciationQuality': pronunciationQuality
        }, run);
    }
    else {
        alert("Задания закончились!" );
        window.location.replace("../");
    }
}


