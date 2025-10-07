var test_widget = (test_widget === undefined) ? {} : test_widget;
test_widget['voice-record-task'] = function(){
	console.log('voice-record-task widget is here: test passed');
};

var container_div = null;

var build_widget = (build_widget === undefined) ? {} : build_widget;
build_widget['voice-record-task'] = function(container_div_id, cb){
	container_div = container_div_id;
	console.log('building voice-record-task widget');
	$.get('../voice-record-task/widget_body.html')
		.done(function(html) {
			console.log("Widget body loaded");
			container_div_id.innerHTML = html;
			voice_record_widget_init();
			cb();
		})
		.fail(function(error){
			console.log(error);
		});
};

function update_widget(task_name, cb, count = -1) { 
	console.log("update_widget");
	console.log("count = " + count);
	build_widget['voice-record-task'](container_div, function(){
		console.log("cb after bw in uw, updating the title");
		var title_field = document.getElementById('voice_record_task_name');
		title_field.innerHTML = task_name + ((count != -1) ? ("-" + count) : "");
		console.log("innerHTML = " + title_field.innerHTML);
		cb();
	});
}

var active_task = false;
var blob = null;
var task_id = null;
var task_series_id = null;
var actual_task = null;

var new_task = (new_task === undefined) ? {} : new_task;
new_task['voice-record-task'] = function(task, cb) {
	console.log('voice-record-task widget: new task');
	console.log('task:');
	console.log(task);

	if(!active_task) {
		update_widget(task.human_task.name, function(){
				console.log("cb after uw in nt")
				active_task = true;
				task_id = task._id;
				task_series_id = task.human_task.task_series_id;
				actual_task = task;
				var text_to_read_div = document.getElementById('text_to_read');
				text_to_read_div.innerHTML = task.human_task.text;
				if(cb)
					cb();
			},
			(task.human_task.multiple_results_allowed) ? task.human_task.done_times : -1
		);
	} else {
		alert("Previous task results have not been submitted");
	}
}

function makeid(length) {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;
    let counter = 0;
    while (counter < length) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
      counter += 1;
    }
    return result;
}

var get_result = (get_result === undefined) ? {} : get_result;
get_result['voice-record-task'] = function(cb) {
	console.log('voice-record-task widget: get result');
	if(active_task) {
		active_task = false;
		var filename = "audio-" + task_id + "-" + actual_task.human_task.done_times + "-" + makeid(10) + ".ogg";
    saveFile(filename, blob, function(){
      console.log("uploaded");
    });

		// const req = new XMLHttpRequest();
    // req.open("PUT", "https://hpccloud.ssd.sscc.ru/storage/" + filename, true);
		// req.onload = (event) => {
		// 	// Uploaded
		// 	console.log("Uploaded");
		// };
		// req.send(blob);

    var s = document.getElementById("sex_select");
		var sex = s.options[s.selectedIndex].text;

		var meta = {
			dataobject : {
				files: [
					{
						path : filename,
						mime : "audio/ogg"
					}
				],
				produced_by : {
					task : task_id,
					task_series_id : task_series_id
				},
				creator: {
					age : document.getElementById("age_input").value,
					sex : sex
				}
			}
		};

		console.log("Meta:");
		console.log(meta);
		saveObject(meta, function(response) {
			var result = {
				reference : {
					"storage" : "couchDB",
					"id" : response.id,
					"rev" : response.rev
				}
			};
			cb(result);
		});
	} else {
		alert("no active task");
		return null;
	}
}


function voice_record_widget_init() {

// set up basic variables for app

const record = document.querySelector('.record');
const stop = document.querySelector('.stop');
const soundClips = document.querySelector('.sound-clips');
const canvas = document.querySelector('.visualizer');
const mainSection = document.querySelector('.main-controls');

// disable stop button while not recording

stop.disabled = true;

// visualiser setup - create web audio api context and canvas

let audioCtx;
const canvasCtx = canvas.getContext("2d");

//main block for doing the audio recording

if (navigator.mediaDevices.getUserMedia) {
  console.log('getUserMedia supported.');

  const constraints = { audio: true };
  let chunks = [];

  let onSuccess = function(stream) {
    const mediaRecorder = new MediaRecorder(stream,{ mimeType: "audio/ogg; codecs=opus" } );

    visualize(stream);

    record.onclick = function() {
      mediaRecorder.start();
      console.log(mediaRecorder.state);
      console.log("recorder started");
      record.style.background = "red";

      stop.disabled = false;
      record.disabled = true;
    }

    stop.onclick = function() {
      mediaRecorder.stop();
      console.log(mediaRecorder.state);
      console.log("recorder stopped");
      record.style.background = "";
      record.style.color = "";
      // mediaRecorder.requestData();

      stop.disabled = true;
//      record.disabled = false;
    }

    mediaRecorder.onstop = function(e) {
      console.log("data available after MediaRecorder.stop() called.");

      const clipName = "audio";//prompt('Enter a name for your sound clip?','My unnamed clip');

      const clipContainer = document.createElement('article');
      const clipLabel = document.createElement('p');
      const audio = document.createElement('audio');
      const deleteButton = document.createElement('button');

      clipContainer.classList.add('clip');
      audio.setAttribute('controls', '');
      deleteButton.textContent = 'Delete';
      deleteButton.className = 'delete';

      if(clipName === null) {
        clipLabel.textContent = 'My unnamed clip';
      } else {
        clipLabel.textContent = clipName;
      }

      clipContainer.appendChild(audio);
      clipContainer.appendChild(clipLabel);
      clipContainer.appendChild(deleteButton);
      soundClips.appendChild(clipContainer);

      audio.controls = true;
      blob = new Blob(chunks, { 'type' : 'audio/ogg; codecs=opus' });
      chunks = [];
      const audioURL = window.URL.createObjectURL(blob);
      audio.src = audioURL;
      console.log("recorder stopped");

      deleteButton.onclick = function(e) {
        e.target.closest(".clip").remove();
		if(task_active)
			record.disabled = false;
      }

      clipLabel.onclick = function() {
        const existingName = clipLabel.textContent;
        const newClipName = prompt('Enter a new name for your sound clip?');
        if(newClipName === null) {
          clipLabel.textContent = existingName;
        } else {
          clipLabel.textContent = newClipName;
        }
      }
    }

    mediaRecorder.ondataavailable = function(e) {
      chunks.push(e.data);
    }
  }

  let onError = function(err) {
    console.log('The following error occured: ' + err);
  }

  navigator.mediaDevices.getUserMedia(constraints).then(onSuccess, onError);

} else {
   console.log('getUserMedia not supported on your browser!');
}

function visualize(stream) {
  if(!audioCtx) {
    audioCtx = new AudioContext();
  }

  const source = audioCtx.createMediaStreamSource(stream);

  const analyser = audioCtx.createAnalyser();
  analyser.fftSize = 2048;
  const bufferLength = analyser.frequencyBinCount;
  const dataArray = new Uint8Array(bufferLength);

  source.connect(analyser);
  //analyser.connect(audioCtx.destination);

  draw()

  function draw() {
    const WIDTH = canvas.width
    const HEIGHT = canvas.height;

    requestAnimationFrame(draw);

    analyser.getByteTimeDomainData(dataArray);

    canvasCtx.fillStyle = 'rgb(200, 200, 200)';
    canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);

    canvasCtx.lineWidth = 2;
    canvasCtx.strokeStyle = 'rgb(0, 0, 0)';

    canvasCtx.beginPath();

    let sliceWidth = WIDTH * 1.0 / bufferLength;
    let x = 0;


    for(let i = 0; i < bufferLength; i++) {

      let v = dataArray[i] / 128.0;
      let y = v * HEIGHT/2;

      if(i === 0) {
        canvasCtx.moveTo(x, y);
      } else {
        canvasCtx.lineTo(x, y);
      }

      x += sliceWidth;
    }

    canvasCtx.lineTo(canvas.width, canvas.height/2);
    canvasCtx.stroke();

  }
}

window.onresize = function() {
  canvas.width = mainSection.offsetWidth;
}

window.onresize();

}
