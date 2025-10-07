var wavesurfer;

var audio_blob;

var base_url = "http://localhost:3000";

var selected_color = 'rgba(220, 0, 0, 0.1)';
var basic_color = 'rgba(0, 200, 100, 0.1)';

var edited_region = null;

function build_widget_()  {
    console.log("Init wavesurfer");
    wavesurfer = WaveSurfer.create({
        container: '#waveform',
        height: 100,
        pixelRatio: 1,
        scrollParent: true,
        normalize: true,
        minimap: true,
        backend: 'MediaElement',
        plugins: [
            WaveSurfer.regions.create(),
/*            WaveSurfer.minimap.create({
                height: 30,
                waveColor: '#ddd',
                progressColor: '#999',
                cursorColor: '#999'
            }),
*/			
            WaveSurfer.timeline.create({
                container: '#wave-timeline'
            })
        ]
    });
	console.log("WS created");

	    /* Regions */

    wavesurfer.on('ready', function() {
        wavesurfer.enableDragSelection({
            color: selected_color
        });
	wavesurfer.on('error', function(e) {
		console.log('wavesurfer: error: ' + e);
	});

var GLOBAL_ACTIONS = { // eslint-disable-line
    play: function() {
        wavesurfer.play(); //Pause();
    },

    back: function() {
        wavesurfer.skipBackward();
    },

    forth: function() {
        wavesurfer.skipForward();
    },

    'toggle-mute': function() {
        wavesurfer.toggleMute();
    }
};

    document.addEventListener('keydown', function(e) {
        let map = {
            32: 'play', // space
            37: 'back', // left
            39: 'forth' // right
        };
        let action = map[e.keyCode];
        if (action in GLOBAL_ACTIONS) {
            if (document == e.target || document.body == e.target || e.target.attributes["data-action"]) {
                e.preventDefault();
            }
            GLOBAL_ACTIONS[action](e);
        }
    });

    [].forEach.call(document.querySelectorAll('[data-action]'), function(el) {
        el.addEventListener('click', function(e) {
            let action = e.currentTarget.dataset.action;
            if (action in GLOBAL_ACTIONS) {
                e.preventDefault();
                GLOBAL_ACTIONS[action](e);
            }
        });
    });




        if (localStorage.regions) {
            loadRegions(JSON.parse(localStorage.regions));
        }
		
		else {
            // loadRegions(
            //     extractRegions(
            //         wavesurfer.backend.getPeaks(512),
            //         wavesurfer.getDuration()
            //     )
            // );
/*            fetch('annotations.json')
                .then(r => r.json())
                .then(data => {
                    loadRegions(data);
                    saveRegions();
                });
*/
        }
		
    });

	wavesurfer.on('region-click', function(region, e) {
        e.stopPropagation();
        // Play on click, loop on shift click
        //e.shiftKey ? region.playLoop() : 
		//
		region.play();
    });

    wavesurfer.on('region-click', editAnnotation);
	wavesurfer.on('region-click', setColors);
	wavesurfer.on('region-update-end', editAnnotation);
	wavesurfer.on('region-update-end', setColors);
    wavesurfer.on('region-updated', saveRegions);
    wavesurfer.on('region-removed', saveRegions);
    wavesurfer.on('region-in', showNote);

    wavesurfer.on('region-play', function(region) {
        region.once('out', function() {
//            wavesurfer.play(region.start);
//            wavesurfer.pause();
        });
    });

    /* Toggle play/pause buttons. */
    let playButton = document.querySelector('#play');
    let pauseButton = document.querySelector('#pause');
    wavesurfer.on('play', function() {
        playButton.style.display = 'none';
        pauseButton.style.display = '';
    });
    wavesurfer.on('pause', function() {
        playButton.style.display = '';
        pauseButton.style.display = 'none';
    });


    document.querySelector(
        '[data-action="delete-region"]'
    ).addEventListener('click', function() {
        let form = document.forms.edit;
        let regionId = form.dataset.region;
        if (regionId) {
            wavesurfer.regions.list[regionId].remove();
            form.reset();
        }
    });
	
	let form = document.forms.edit;
    form.oninput = function(e) {
		if(isNaN(form.elements.start.value) || isNaN(form.elements.end.value) || form.elements.start.value.slice(-1) == '.' || form.elements.end.value.slice(-1) == '.')
			return;
        e.preventDefault();
		console.log("on input");
		if(edited_region)
	        edited_region.update({
    	        start: form.elements.start.value,
        	    end: form.elements.end.value,
	            data: {
    	            note: form.elements.note.value,
			rquality: form.elements.rquality.value//document.querySelector('input[name="rquality"]:checked').value
    	        }
       		 });
    };

console.log("Init wavesurfer Done");
}

var audio;

function load_audio(task, cb) {
	if(task) {
		console.log("Init");
		console.log(task);
		console.log("Getting task data from CouchDB");
		getObjectByID(task.human_task.audio.id, 
			function(response) {
				console.log("Got data from CDB");
				console.log(response.dataobject);
				wavesurfer.regions.clear();
				if(response.dataobject.hasOwnProperty("meta"))
					if(response.dataobject.meta.hasOwnProperty("annotation")) {
						localStorage.regions = JSON.stringify(response.dataobject.meta.annotation.value);
//						loadRegions(JSON.parse(localStorage.regions));
					}
				var filename = response.dataobject.files[0].path
				var url = base_url + "/storage/" + filename;
	        let form = document.forms.edit;
				form.reset();
				getFile(filename, function (blob) {
					audio_blob = blob;
					
					wavesurfer.load(URL.createObjectURL(audio_blob));
					cb();				
				});
//				wavesurfer.load(url);
//				console.log("?Loaded?");
				cb();
/*				
				const req = new XMLHttpRequest();
				//sync req
				req.open("GET", "https://hpccloud.ssd.sscc.ru/storage/" + filename, true);
				req.responseType = 'blob';
				//>->---const blob = new Blob(["abc123"], { type: "text/plain" });
				req.onload = () => {
					console.log(req);
					let audio = new Audio();
					audio.src = URL.createObjectURL(req.response);
					wavesurfer.load(audio);
					console.log("Loaded");
					cb();
				};
				req.send(null);
*/
			},
			function(response) {
				//TODO: process errors
			});
	} else {
		console.log("No task");

		cb();
	}

}

function setColors(e_region) {
        Object.keys(wavesurfer.regions.list).map(function(id) {
            let region = wavesurfer.regions.list[id];
			if(id != e_region.id)
				region.update({"color" : basic_color});
			else
				region.update({"color" : selected_color});
        });
}

/**
 * Save annotations to localStorage.
 */
function saveRegions(region) {
    console.log("saveRegions");
	localStorage.regions = JSON.stringify(
        Object.keys(wavesurfer.regions.list).map(function(id) {
            let region = wavesurfer.regions.list[id];
            return {
                start: region.start,
                end: region.end,
                attributes: region.attributes,
                data: region.data
            };
        })
    );
}

/**
 * Load regions from localStorage.
 */
function loadRegions(regions) {
    regions.forEach(function(region) {
        region.color = randomColor(0.1);
        wavesurfer.addRegion(region);
    });
}

/**
 * Extract regions separated by silence.
 */
function extractRegions(peaks, duration) {
    // Silence params
    const minValue = 0.0015;
    const minSeconds = 0.25;

    let length = peaks.length;
    let coef = duration / length;
    let minLen = minSeconds / coef;

    // Gather silence indeces
    let silences = [];
    Array.prototype.forEach.call(peaks, function(val, index) {
        if (Math.abs(val) <= minValue) {
            silences.push(index);
        }
    });

    // Cluster silence values
    let clusters = [];
    silences.forEach(function(val, index) {
        if (clusters.length && val == silences[index - 1] + 1) {
            clusters[clusters.length - 1].push(val);
        } else {
            clusters.push([val]);
        }
    });

    // Filter silence clusters by minimum length
    let fClusters = clusters.filter(function(cluster) {
        return cluster.length >= minLen;
    });

    // Create regions on the edges of silences
    let regions = fClusters.map(function(cluster, index) {
        let next = fClusters[index + 1];
        return {
            start: cluster[cluster.length - 1],
            end: next ? next[0] : length - 1
        };
    });

    // Add an initial region if the audio doesn't start with silence
    let firstCluster = fClusters[0];
    if (firstCluster && firstCluster[0] != 0) {
        regions.unshift({
            start: 0,
            end: firstCluster[firstCluster.length - 1]
        });
    }

    // Filter regions by minimum length
    let fRegions = regions.filter(function(reg) {
        return reg.end - reg.start >= minLen;
    });

    // Return time-based regions
    return fRegions.map(function(reg) {
        return {
            start: Math.round(reg.start * coef * 10) / 10,
            end: Math.round(reg.end * coef * 10) / 10
        };
    });
}

/**
 * Random RGBA color.
 */
function randomColor(alpha) {
    return (
        'rgba(' +
        [
//            ~~(Math.random() * 255),
			0,
//            ~~(Math.random() * 255),
			200,
//            ~~(Math.random() * 255),
			100,
            alpha || 1
        ] +
        ')'
    );
}

Number.prototype.round = function(n) {
  const d = Math.pow(10, n);
  return Math.round((this + Number.EPSILON) * d) / d;
}

/**
 * Edit annotation for a region.
 */


function initEditAnnotation(region) {
	edited_region = region;
	let form = document.forms.edit;
    form.style.opacity = 1;

    form.oninput = function(e) {
		console.log("On input");
		if(isNaN(form.elements.start.value) || isNaN(form.elements.end.value) || form.elements.start.value.slice(-1) == '.' || form.elements.end.value.slice(-1) == '.')
			return;
        e.preventDefault();
		console.log("on input");
        edited_region.update({
            start: form.elements.start.value,
            end: form.elements.end.value,
            data: {
                note: form.elements.note.value,
		rquality: document.querySelector('input[name="rquality"]:checked').value
            }
        });
    };

    region.start = region.start.round(3);//region.start * Math.round(region.start * 1000) / 1000;
    region.end = region.end.round(3);//region.end * Math.round(region.end * 1000) / 1000;

    (form.elements.start.value = region.start),
    (form.elements.end.value = region.end);

    form.elements.note.value = region.data.note || '';
	form.elements.rquality.value = region.data.rquality || 0;
    form.onsubmit = function(e) {
        e.preventDefault();
		console.log("on submit");
        region.update({
            start: form.elements.start.value,
            end: form.elements.end.value,
            data: {
                note: form.elements.note.value,
				rquality: document.querySelector('input[name="rquality"]:checked').value //form.elements.rquality.value
            }
        });
        form.style.opacity = 0;
    };
    form.onreset = function() {
        form.style.opacity = 0;
        form.dataset.region = null;
    };
    form.dataset.region = region.id;
}


function editAnnotation(region) {
	edited_region = region;

    let form = document.forms.edit;
    form.style.opacity = 1;

    region.start = region.start.round(3);//region.start * Math.round(region.start * 1000) / 1000;
    region.end = region.end.round(3);//region.end * Math.round(region.end * 1000) / 1000;

    (form.elements.start.value = region.start),
    (form.elements.end.value = region.end);

    form.elements.note.value = region.data.note || '';
	if(!region.data.hasOwnProperty('rquality')){
		region.data.note = '';
		region.data.rquality = 'bad';
	}
	
	form.elements.rquality.value = region.data.rquality || "bad";
	//default:
	//document.querySelector("input[value='bad']").checked = true;
    form.onreset = function() {
        form.style.opacity = 0;
        form.dataset.region = null;
    };
    form.dataset.region = region.id;
	saveRegions(region);
}

/**
 * Display annotation.
 */
function showNote(region) {
    if (!showNote.el) {
        showNote.el = document.querySelector('#subtitle');
    }
    showNote.el.textContent = region.data.note || '–';
}

