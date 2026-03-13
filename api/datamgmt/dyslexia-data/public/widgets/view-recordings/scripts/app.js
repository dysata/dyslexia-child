
var test_widget = (test_widget === undefined) ? {} : test_widget;
test_widget['view-recordings'] = function(){
	console.log('view-recordings widget is here: test passed');
};

var list_of_files = [];
var current_file_indx = -1;
var current_file = null;

window.onload = function(){
	const next_btn = document.getElementById('next-btn');
  const prev_btn = document.getElementById('prev-btn');
  next_btn.onclick = function(){
    select_next_file();
  };

  prev_btn.onclick = function(){
    select_prev_file();
  };  

  var query = {
    "selector" : {
      "dataobject": {
        "files": {
            "$elemMatch": {
              "mime": {
                  "$regex": "audio*"
              }
            }
        }
      }
    },
    "limit" : 1000
  };
  
  findObjectsFullQuery(query, 
    function (response) {
      console.log(response);
      var count = 0;
      alert("Found recordings: " + response.docs.length);
      list_of_files = response.docs;
      current_file_indx = 0;
      show_audio();      
    },
    function (response) {
      console.log(response);
    }
  );
}

function show_audio() {
  if(current_file_indx == -1) {
    alert("File list is empty");
  }
    
  if(current_file_indx < list_of_files.length) {
    if(list_of_files[current_file_indx]['deleted'])
      build_widget();
    else {
      var filename = list_of_files[current_file_indx].dataobject.files[0].path;
      const soundClips = document.querySelector('.sound-clips');
      
      soundClips.innerHTML = '<h2 class="text-info">Downloading your audio file. Please wait.</h2>';

      getFile(filename, function(file_body){
        current_file = file_body;
        build_widget();
      });  
    }
  } else {
    console.log("current_file_indx > list_of_files.length");
  }
}

function select_next_file() {
    
    if(current_file_indx + 1 == list_of_files.length) {
      var str = "is";
      if(list_of_files[current_file_indx]['deleted'])
      {
        str = "was"
      }
      alert("It " + str + "the last file in the list");
    }
    else {
        current_file_indx ++;
        show_audio();
    }
}

function select_prev_file() {
    
  if(current_file_indx  == 0) {
    var str = "is";
    if(list_of_files[current_file_indx]['deleted']) {
      str = "was"
    }
    alert("It " + str + " the first file in the list");
  }
  else {
      current_file_indx --;
      show_audio();
  }
}


function build_widget() {

  var file_info = JSON.stringify(list_of_files[current_file_indx], undefined, 4);
  var file_info_pre = document.getElementById("file-info");
  file_info_pre.innerHTML = file_info;


  const soundClips = document.querySelector('.sound-clips');
  if(list_of_files[current_file_indx]['deleted'])
  {
    soundClips.innerHTML = '<h2 class="text-danger">You have deleted this file. The file info was also deleted from our database. You can copy it below and save somewhere else if you need it.</h2>';
    return;
  }



  soundClips.innerHTML = "";


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
  var audio_type = list_of_files[current_file_indx].dataobject.files[0].mime;
  audio_type += "; codecs=opus";

  const audioURL = window.URL.createObjectURL(current_file);
  audio.src = audioURL;

  //TODO: move to onload function
  deleteButton.onclick = function() {
    if(confirm("Are you sure you want to delete this file?")) {
      deleteFile(list_of_files[current_file_indx].dataobject.files[0].path, function () {
        deleteObjectByID(list_of_files[current_file_indx]._id, list_of_files[current_file_indx]._rev, 
          function(response) {
            console.log("deleted an object from couchDB: " + response);
            soundClips.innerHTML = "";
            list_of_files[current_file_indx].deleted = true;
            select_next_file();
          }, 
          function(response) {
            console.log("a problem deleting an object from couchDB: " + response);
          }
          );      
      });
    } else {
      console.log("Delete canceled");
    }
  }
  //TODO: remove this, implement a form to edit file info
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
