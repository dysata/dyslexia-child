var list_of_tasks = {};
var current_task_indx = null;
var current_task = null;
var current_task_rev = null;
var task_type = null;
var task_series = null;


function update_task_list(cb) {
	    getListOfPendingHumanTasksBySeriesID(task_series, function(response){
			list_of_tasks = response.rows;
			console.log('My Tasks:');
			console.log(response);
			if(response.rows.length > 0) {
				cb();
			}
			else {
				alert("No tasks Available for this Task Series ID");
			}
	    },
	    function(response) {
			alert("Cannot get the list of tasks from our DB. Please authorize");
			window.location = "http://localhost:3000/login";
	    });

}

function start_series(series){ 
	task_series = series;
	update_task_list(function(){
				
				var task_num = 0;
				var task = null;
				var flag = true;
				do
				{
					task = list_of_tasks[task_num].value;
					task_num ++;
					flag = task.human_task.hasOwnProperty("done") && task.human_task.done;
				}
				while( flag && task_num < list_of_tasks.length);

				if(flag) {
					alert("Все задания в этой серии выполнены (всего " + list_of_tasks.length + " заданий в серии)");
					return;
				}
				
				task_type = task.human_task.type;
				
				var widget_script_path = '../' + task_type + '/scripts/app.js';
				$.getScript(widget_script_path)
					.done(function(script, textStatus) {
						console.log("my-tasks: getScript done");
						console.log(textStatus);
						test_widget[task_type]();
						$("#task_series_settings").collapse("hide");
						build_widget[task_type](document.getElementById('widget_container'), function() {
							current_task_indx = task_num-1;
							current_task = task;
							current_task_rev = task._rev;
							new_task[task_type](task); 
						});
					})
					.fail(function(jqxhr, settings, exception) {
						console.log("Error in getting scripts: " + widget_script_path);
					});
});
}

function save_task(cb) {
	saveObject(current_task, function(response, rstatus) {
		console.log("saveObject cb response: ");
		console.log(response);
		if(rstatus == 409) {
			update_task_list(function(){
				current_task._rev = list_of_tasks[current_task_indx].value._rev;
				save_task(cb);
			});
		} else {
			cb();
		}
	});
}

window.onload = function() {
	const start_work_btn = document.getElementById('start_work');
	start_work_btn.onclick = function() {
    	console.log("Start Work btn handler");
	    const human_id = document.getElementById('human_id');
		console.log("Starting with value = " + human_id.value);
		start_series(human_id.value);

	};
	const submit_btn = document.getElementById('submit_task_result');
	submit_btn.onclick = function() {
		get_result[task_type](function(result){
			console.log(result);
			current_task.human_task.done_times = current_task.human_task.done_times + 1;
			current_task.human_task.done = true;
			//TODO: use real user_id here
			current_task.human_task.processed_by_user_id = 1;
			if(current_task.human_task.hasOwnProperty('results')) {
				current_task.human_task.results.push(result);
			} else {
				current_task.human_task.results = [result];
			}
			save_task(function() {
				if(!current_task.human_task.hasOwnProperty('multiple_results_allowed') || !current_task.human_task.multiple_results_allowed || (current_task.human_task.hasOwnProperty('done_times_max') && current_task.human_task.done_times >= current_task.human_task.done_times_max)) {


					if(current_task_indx + 1 < list_of_tasks.length)
					{
						task_num = current_task_indx + 1;
						var task = null;
						var flag = true;
						do
						{
							task = list_of_tasks[task_num].value;
							task_num ++;
							flag = task.human_task.hasOwnProperty("done") && task.human_task.done;
						}
						while( flag && task_num < list_of_tasks.length);

						if(flag) {
							alert("All is done, thanks");
							$('submit_task_result').prop('disabled', true);
							$('cancel_task').prop('disabled', true);
							return;
						}	
						current_task_indx = task_num-1;
						task = list_of_tasks[current_task_indx].value;
						current_task = task;
						current_task_rev = task._rev;
						new_task[task_type](task);
					}
					else
					{
						alert("All is done, thanks");
						$('submit_task_result').prop('disabled', true);
						$('cancel_task').prop('disabled', true);
					}
				} else {
					new_task[task_type](current_task);
				}
			});
		});
	};
	const queryString = window.location.search;
	console.log(queryString);
	const urlParams = new URLSearchParams(queryString);
	if(urlParams.has('series')) {
		const series = urlParams.get('series');
		start_series(series);
	} 
}

