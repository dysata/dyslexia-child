
window.onload = function(){
	const submit_btn = document.getElementById('create_tasks');
	submit_btn.onclick = function() {
    	 console.log("Submit btn handler");
	const submit_btn=document.getElementById('create_tasks');
	var task = {};
	var task_name_prefix = document.getElementById('task_series_id').value;
	task.type = "voice-record-task";
	task.done_times = 0;
	task.text = document.getElementById('text_to_read').value;
	task.task_series_id = document.getElementById('task_series_id').value;
	task.multiple_results_allowed = document.getElementById('checkbox_multiple').checked;


//	task.tags = 
	var taskNumber = document.getElementById('tasknumber').value;
	console.log("Task:\n" + task);
	console.log("Task Number = " + taskNumber);
	for(var i = 0; i<taskNumber; i++)
	{
		task.name = task_name_prefix + '-' + i;
		var human_task = {};
		human_task.human_task = task;
		saveObject(human_task, function(response){
			console.log(response);
			if('ok' in response && response.ok)
				alert("Created");
			else
				alert("Some problem, see logs. Auth problem maybe?");
		});
	}
}
}

