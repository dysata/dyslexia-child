
window.onload = function(){
	const submit_btn = document.getElementById('create_tasks');
	submit_btn.onclick = function() {
		console.log("Submit btn handler");
		const submit_btn=document.getElementById('create_tasks');
		var task = {};

		var task_name_prefix = document.getElementById('task_series_id').value;
		if(!task_name_prefix || task_name_prefix == "") {
			alert("Please set Task Series ID for a new task series to continue");
			return;
		}
		task.type = "label-audio-task";
		task.done_times = 0;
		var produced_by = document.getElementById('produced_by').value;
		task.task_series_id = document.getElementById('task_series_id').value;
		
		var radio = document.querySelector('input[name="btnradio"]:checked');
		if(!radio) {
			alert("Please click 'Tags' or 'Task Series ID' above before pressing 'Create Tasks'");
			return;
		}
		radio = radio.value;
		var selector = {};
		if(radio == "series") {
			if(!produced_by || produced_by == "") {
				alert("Please set Task Series ID to find audio files");
				return;
			}
			selector = {
				"human_task" : {
					"task_series_id" : produced_by
				}
			};
			findObjects(selector, 
				function (response) {
					console.log(response);
					var taskNumber = 0;
					var total_count = 0;
					response.docs.forEach(function(t, t_idx, t_array) {
						//	task.tags = 
						console.log("Task Number = " + taskNumber);
						count = 0;
//						for(const r of t.human_task.results) {
						t.human_task.results.forEach(function(r, r_idx, r_array) {
							task.name = task_name_prefix + '-' + taskNumber + '-' + count;
							
							console.log("Checkinig the referenced result object exists: " + r.reference.id);
							getObjectByID(r.reference.id, 
								function(response) {
									console.log("Response: " + response);
									console.log("Object found, creating labeling task for the object");
									task.audio = r.reference;
									var human_task = {};
									human_task.human_task = task;
									saveObject(human_task, function(response){
										console.log(response);
									});
									count ++;
									total_count ++;
									if(t_idx === t_array.length - 1 && r_idx === r_array.length - 1)
				  						alert("Done: created " + total_count + " tasks");

								},
								function(response) {
									console.log("Response: " + response);
									console.log("Could not get the object from CouchDB");
									console.log("Skipping this result");
								}
							);
						});
						taskNumber ++;
					});
				}, 
				function (response) {
					console.log(response);
				}
			);
	} else { //radio == "tags"
			if(!produced_by || produced_by == "") {
				alert("Please set tags to find audio files");
				return;
			}
			selector = {
				"dataobject" : {
					"tags" : { "$all" : [] }
				}
			};
			var tags = produced_by.split(',');
			for (const tag of tags) {
				selector["dataobject"]["tags"]["$all"].push(tag);
			}
			findObjects(selector, 
				function (response) {
					console.log(response);
					var count = 0;
					
					for(const audio in response.docs) {
						console.log(response.docs[audio]);
						task.name = task_name_prefix + '-' + count;
						count += 1;
						task.audio = {};
						task.audio['storage']  = 'couchDB';
						task.audio['id'] = response.docs[audio]._id;
						task.audio['rev'] = response.docs[audio]._rev;
						var human_task = {};
						human_task.human_task = task;
						saveObject(human_task, function(response){
							console.log(response);
						});
					}
					alert("Done: created " + count + " tasks");
				},
				function (response) {
					console.log(response);
				}
			);
		}
	}
}

