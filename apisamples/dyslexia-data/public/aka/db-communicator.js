//NextCloud WebDAV 

let NextCloud_baseURL = "http://localhost:3000/storage";

function saveFile(filename, blob, cb) {
  const req = new XMLHttpRequest();
  req.open("PUT", NextCloud_baseURL + '/' + filename, true);
  req.onload = (event) => {
    // Uploaded
    console.log("Uploaded: " + filename);
    cb();
  };
  req.send(blob);  
}

function getFile(filename, cb) {
  const req = new XMLHttpRequest();
  req.open("GET", NextCloud_baseURL + '/' + filename, true);
  req.responseType = 'blob';
  req.onload = (event) => {
    // Uploaded
    console.log("Downloaded: " + filename);
    cb(req.response);
  };
  req.send();  
}

function deleteFile(filename, cb) {
  const req = new XMLHttpRequest();
  req.open("DELETE", NextCloud_baseURL + '/' + filename, true);
  req.responseType = 'blob';
  req.onload = (event) => {
    // Uploaded
    console.log("Deleted: " + filename);
    cb();
  };
  req.send();  
}


//CouchDB begin

let couchDB_baseURL = "http://localhost:3000/couchdb/dyslexia";

function saveObject(data_object, onSuccess){
  let xhr = new XMLHttpRequest();

  if(data_object._id)
  {
//we use our server as a proxy to access CouchDB, the server knows and substitutes the credentials
//    xhr.open("PUT", couchDB_baseURL + "/" + data_object._id, true, couchDB_username, couchDB_password);
    xhr.open("PUT", couchDB_baseURL + "/" + data_object._id, true);
  }
  else
//    xhr.open("POST", couchDB_baseURL, true, couchDB_username, couchDB_password);
    xhr.open("POST", couchDB_baseURL, true);

  xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4) {
      let response = JSON.parse(xhr.response);
//TODO: process errors
      onSuccess(response, xhr.status);
    }
  };
  xhr.send(JSON.stringify(data_object));
}

function findObjectsFullQuery(query, onSuccess, onError) {
  let xhr = new XMLHttpRequest();
  
  xhr.open("POST", couchDB_baseURL + "/_find", true);
  xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4) {
      let response = JSON.parse(xhr.response);
      onSuccess(response);
	  //TODO: process errors and call onError if needed
    } 
  };
  xhr.send(JSON.stringify(query));
}

function findObjects(selector, onSuccess, onError) {
  let xhr = new XMLHttpRequest();
  
  xhr.open("POST", couchDB_baseURL + "/_find", true);
  xhr.setRequestHeader('Content-type', 'application/json; charset=utf-8');
  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4) {
      let response = JSON.parse(xhr.response);
      onSuccess(response);
	  //TODO: process errors and call onError if needed
    } 
  };
	var query = {
	    "limit" : 5000
	};
	query.selector = selector;
  xhr.send(JSON.stringify(query));
}

function getListOfPendingHumanTasksBySeriesID(task_series_id, onSuccess, onError){
  let xhr = new XMLHttpRequest();
  let url = couchDB_baseURL + '/_design/dyslexia/_view/human_tasks?key="' + task_series_id + '"';
  console.log("accessing url " + url);

//  xhr.open("GET", url, true, couchDB_username, couchDB_password);
  xhr.open("GET", url, true);
  xhr.setRequestHeader("Content-type", "application/json");
  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4) {
      if(xhr.status == 200){
        onSuccess(JSON.parse(xhr.response));
        console.log("getListOfPendingHumanTasksBySeriesID() -- OK");
      }
      else{
        onError(xhr.response);
        console.log("getListOfPendingHumanTasksBySeriesID() -- FAIL");
      }
    }
  };
  xhr.send();
}

function getObjectByID(object_id, onSuccess, onError){
  let xhr = new XMLHttpRequest();
  let url = couchDB_baseURL + '/' + object_id; // + (rev?("?rev=\"" + rev + "\""):"");

  xhr.open("GET", url, true);
//  xhr.open("GET", url, true, couchDB_username, couchDB_password);
  xhr.setRequestHeader("Content-type", "application/json");
  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4) {
      if(xhr.status == 200){
        onSuccess(JSON.parse(xhr.response));
        console.log("getObjectByID() -- OK");
      }
      else{
        console.log("getObjectByID() -- FAIL, code = " + xhr.status + ", response = " + xhr.response);
        if(onError)
          onError(xhr.response);
      }
    }
  };
  xhr.send();
}

function getObjectByIDSync(object_id){
  let xhr = new XMLHttpRequest();
  let url = couchDB_baseURL + '/' + object_id; // + (rev?("?rev=\"" + rev + "\""):"");

//  xhr.open("GET", url, false, couchDB_username, couchDB_password);
  xhr.open("GET", url, false);
  xhr.setRequestHeader("Content-type", "application/json");
  xhr.send();
  return {"http_status": xhr.status, "response":(xhr.status == 200?JSON.parse(xhr.response):xhr.response)};
}

function deleteObjectByID(id, rev, onSuccess, onError) {
  let xhr = new XMLHttpRequest();
  let url = couchDB_baseURL + '/' + id + "?rev=" + rev;

//  xhr.open("DELETE", url, true, couchDB_username, couchDB_password);
  xhr.open("DELETE", url, true);
  xhr.setRequestHeader("Content-type", "application/json");
  xhr.onreadystatechange = function () {
    if (xhr.readyState === 4) {
      if(xhr.status == 200){
        onSuccess(JSON.parse(xhr.response));
        console.log("deleteObjectByID(" + id + ", " + rev + ") -- OK");
      }
      else{
        onError(xhr.response);
        console.log("deleteObjectByID(" + id + ", " + rev + ") -- FAIL");
      }
    }
  };
  xhr.send();
}


//CouchDB end
