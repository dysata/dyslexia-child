var test_widget = (test_widget === undefined) ? {} : test_widget;
test_widget['label-audio-task'] = function(){
	console.log('label-audio-task widget is here: test passed');
};

var container_div = null;
var active_task = false;
var blob = null;
var task_id = null;
var task_series_id = null;
var task = null;

var initialized = false;

var build_widget = (build_widget === undefined) ? {} : build_widget;
build_widget['label-audio-task'] = function(container_div_id, cb){
	container_div = container_div_id;
	console.log('building label-audio-task widget');
	$.get('../label-audio-task/widget_body.html')
		.done(function(html) {
			console.log("Widget body loaded");
			container_div_id.innerHTML = html;
			label_audio_widget_init(cb);
		})
		.fail(function(error){
			console.log(error);
		});
};

function update_widget(task_name, cb) { 
	label_audio_widget_init(function(){
		var title_field = document.getElementById('label_audio_task_name');
		console.log("Title field");
		console.log(title_field);
		console.log(task_name);
		title_field.innerHTML = task_name;
		cb();
	});
}

var new_task = (new_task === undefined) ? {} : new_task;
new_task['label-audio-task'] = function(task_, cb) {
	console.log('label-audio-task widget: new task');
	if(!active_task) {
		task = task_;
		active_task = true;
		update_widget(task.human_task.name, function(){
			task_id = task._id;
			task_series_id = task.human_task.task_series_id;
			console.log("111 Task = ");
			console.log(task);
//			var text_to_read_div = document.getElementById('text_to_read');
//			text_to_read_div.innerHTML = task.human_task.text;
			if(cb)
				cb();
		});
	} else {
		alert("Previous task results have not been submitted");
	}
}

var get_result = (get_result === undefined) ? {} : get_result;
get_result['label-audio-task'] = function(cb) {
	console.log('label-audio-task widget: get result');
	if(active_task) {
		active_task = false;
		console.log(localStorage.regions);
		if(!localStorage.regions) 
			localStorage.regions = "[]";
		getObjectByID(task.human_task.audio.id,
			function(dataobject) {
				if(!dataobject.dataobject.hasOwnProperty('meta'))
					dataobject.dataobject['meta'] = {};
				dataobject.dataobject.meta['annotation'] = {};
				dataobject.dataobject.meta['annotation']['value'] = JSON.parse(localStorage.regions);
				localStorage.regions = null;
				dataobject.dataobject.meta['annotation']['by'] = {
					task_id : task._id,
					task_rev : task._rev,
					task_series_id : task.human_task.task_series_id
				};
				dataobject.dataobject.meta['annotation']['timestamp'] = Date.now();
				console.log(dataobject);
				saveObject(dataobject, 
					function(response) {
					var result = {
						description : "annotated audio",
						reference : {
							"storage" : "couchDB",
							"id" : response.id,
							"rev" : response.rev
						}
					};
					cb(result);
				},
					function(error) {
						//TODO: process errors
					}
				);
			},
			function(error) {
				//TODO: process errors
			}
		);
		
	} else {
		alert("no active task");
		return null;
	}
}

function label_audio_widget_init(cb) {
	var file = location.pathname.split( "/" ).pop();
	var styles = ["app.css", "ribbon.css", "style.css"];
	styles.forEach(function(css_file) {
		var link = document.createElement( "link" );
		link.href = "../label-audio-task/styles/" + css_file;
		link.type = "text/css";
		link.rel = "stylesheet";
		link.media = "screen,print";
		document.getElementsByTagName( "head" )[0].appendChild( link );
	});

	if(!initialized) {

//TODO: rewrite
	var base_path = "https://unpkg.com/";
	var path = "https://unpkg.com/wavesurfer.js/dist/plugin/";
	var local_path = "../label-audio-task/scripts/";
	path = base_path = local_path;
	$.getScript(base_path + "wavesurfer.js")
		.done(function(script, textStatus) {
			$.getScript(path + "wavesurfer.timeline.js")
				.done(function(script, textStatus) {
					$.getScript(path + "wavesurfer.regions.js")
						.done(function(script, textStatus) {
//							$.getScript(path + "wavesurfer.minimap.js")
//								.done(function(script, textStatus) {
									$.getScript(local_path + "audio.js")
										.done(function(script, textStatus) {
											console.log("First build. Task = ");
											console.log(task);
											initialized = true;
											build_widget_();
											load_audio(task, cb);
										})
										.fail(function(jqxhr, settings, exception) {
											console.log("Error in getting scripts: ");
										}); 
//								})
//								.fail(function(jqxhr, settings, exception) {
//									console.log("Error in getting scripts: ");
//								}); 
						})
						.fail(function(jqxhr, settings, exception) {
							console.log("Error in getting scripts: ");
						}); 
					})
				.fail(function(jqxhr, settings, exception) {
					console.log("Error in getting scripts: ");
				}); 
		})
		.fail(function(jqxhr, settings, exception) {
			console.log("Error in getting scripts: ");
		}); 
	} else {
		console.log("Initialized, task = ");
		console.log(task);
		load_audio(task, cb)
	}

}
