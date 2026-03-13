var currenTask = 0;
var currentLevel = 0;
var keysGame = [];
var results = [];
var resultStr = '';

var StrSp = '';

// массив слов
var words = wordList;

var pics = imageList;

var ready = true;
var init = false;

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

function startGame() {
    document.addEventListener('keyup', event => {
        if(!pageLocked) {
            if (event.code === 'ArrowLeft') {
              btnclkNotLive()
            } else if (event.code === 'ArrowRight') {
                btnclkLive()
            } else {
                alert("Нажмите стрелку влево если объект неживой, стрелку вправо -- если живой")
            }
        } else {
            console.log("Page Locked, no user interaction is allowed");
            event.stopPropagation();
        }
      })

    document.getElementById("start").style.display = 'none';
    document.getElementById("game_settings").style.display = 'none';
    document.getElementById("main").style.display = 'block';

    ready = true;
    init = false;
    start(process);
}

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}


 function logopedClicked(){
    var arRadio=document.getElementsByName("logopedChecked");
    var resReturn = 0;
    for (var i = 0; i < arRadio.length; i++) {
        if (arRadio[i].type == "radio" && arRadio[i].checked) {
            resReturn = arRadio[i].value;
        }
    }
    if(resReturn == 0){
        return ' - ';
    } else {
        return answersLogoped[resReturn-1];
    }
 }

function checkSpeech(StrSp){
    let randomInt1 = getRandomInt(0, 1);
    let randomInt2 = getRandomInt(0, 1);
    resultStr += "<b>"+StrSp +"</b>"+ ": " + answers[randomInt1][randomInt2] + ", проверил логопед: " + logopedClicked()+"<br />";
    return resultStr;
}

function wordProcess(){
    if (wordsRemain.length !== 0){
        intIndex = getRandomInt(0, (wordsRemain.length-1));
            while(words.indexOf(shownString) == intIndex)
                intIndex = getRandomInt(0, (wordsRemain.length-1));
        //alert('word = '  + intIndex , ' mass=', alert (wordsRemain.toString())+' ____' + wordsRemain[intIndex]+' shownString='+shownString);
        wordsDone.push(wordsRemain[intIndex]);
        document.getElementById("content").innerHTML = '';
        document.getElementById('image-container').innerHTML = '';
        ind = wordsRemain.indexOf(wordsRemain[intIndex]);
        shownString = wordsRemain[intIndex];

        var dt = new Date();
        utc = dt.toISOString().replaceAll(':', '-').replaceAll('.', '-');
        var meta = {
            wordIndex: ind,
            word: shownString,
            isImage: false,
            game: 'game2d',
            connectionState : connectionState,
            datetime: utc
        };
        if(connectionState == "just_restored")
            connectionState = "normal";
        start_recording(meta, function(){
            document.getElementById("content").innerHTML = /*"Произнеси"+/*uiTexts[currentLevel] + "<br />" +*/ wordsRemain[intIndex];
            //alert(" до удаления элемента = "+ wordsRemain.toString());
            //alert("ind="+ ind+ "  ")
            if (ind !== -1) {
                //!!!!!!!!!!!!!!!!!!!!!1
                wordsRemain.splice(ind, 1);
            // alert(" after deleting element = "+ wordsRemain.toString());
            } else {
                shownString = '';
            }
            try {
                sendLabel(64, com_writer);
            } catch (e) {
                console.log(e);
            }
        });
    }else if(shownString.length !== 0) {
//            document.getElementById("results").innerHTML = checkSpeech(shownString);
        shownString = '';
    } else {
        alert("Задания закончились!" );
    }
}

function btnclkLive(){
    try {
        sendLabel(60, com_writer);
    } catch (e) {
        console.log(e);
    }
    isLive = true;
    btnclk();
}

function btnclkNotLive(){
    try {
        sendLabel(59, com_writer);
    } catch (e) {
        console.log(e);
    }
    isLive = false;
    btnclk();
}

function btnclk(){
    setTimeout(process, 500);
}

function process(){
    while(!ready);
    if(init) {
        if(shownString != '')
            stop_recording({'isLive' : isLive});
    } else {
        init = true;
        wordsRemain = words.slice();
        picsRemain = pics.slice();
    }

    if (activeElement == 'word'){
        wordProcess();
        activeElement = 'pic';
    }else if (activeElement == 'pic') {// показываем картинку
        if (picsRemain.length !== 0){
            document.getElementById('content').innerHTML = '';
            document.getElementById('image-container').innerHTML = '';
            intIndex = getRandomInt(0, (picsRemain.length-1));
            while(shownString == picsRemain[intIndex])
                intIndex = getRandomInt(0, (picsRemain.length-1));

            var ind = words.indexOf(picsRemain[intIndex]);
            console.log(picsRemain[intIndex]);
            console.log(ind);
            console.log(words[ind]);
            console.log(words.length);
            shownString = picsRemain[intIndex];

            //alert ('picsRemain= '+picsRemain.length + '  index=' + ind + '  __' + picsRemain[intIndex]);

            picsDone.push(shownString);
            picsRemain.splice(intIndex, 1);
            //alert (' string== '+picsRemain.toString() );
            if (ind !== -1 ) {
                ready = false;
                var dt = new Date();
                utc = dt.toISOString().replaceAll(':', '-').replaceAll('.', '-');

                var meta = {
                    wordIndex: ind,
                    word: shownString,
                    isImage: true,
                    game: 'game2d',
                    connectionState: connectionState,
                    datetime: utc
                };
                if(connectionState == "just_restored")
                    connectionState = "normal";
                start_recording(meta, function(){
                    ready = true;
                    const img = document.createElement('img');
                    img.src = 'static/game2d/images/'+ (ind) + '.jpg';
                    img.style.height = '100%';
                    img.style.width = 'auto';
                    img.style.objectFit = 'contain';
                    document.getElementById('image-container').append(img);
                    isImage = true;
                    try {
                        sendLabel(64, com_writer);
                    } catch (e) {
                        console.log(e);
                    }
                });

            }
        }else {
            wordProcess();
        }
        activeElement = 'word';
            //document.getElementById("content").innerHTML = '<img scr="./../images/' + intIndex + '.jpg"' + '/>'
    }
    if(shownString.length == 0)
    {
        alert("Задания закончились!" );
        stop();
        window.location.replace("../");
    }
}
