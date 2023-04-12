function uploadFile(file, s3Data, url){
console.log('uploadFile:',file.filename)    
document.querySelector('#preview').src = URL.createObjectURL(file);
const xhr = new XMLHttpRequest();
xhr.open('POST', s3Data.url);
xhr.setRequestHeader('x-amz-acl', 'public-read');
const postData = new FormData();
for(key in s3Data.fields){
    postData.append(key, s3Data.fields[key]);
    }
postData.append('file', file);
console.log("file:",file)
xhr.onreadystatechange = () => {
    if(xhr.readyState === 4){
        if(xhr.status === 200 || xhr.status === 204){
            document.getElementById('preview').src = url;
            document.getElementById('img').value = file.name;
          }
          else{
            alert('Could not upload file.');
          }
        }
    };
xhr.send(postData);
}

/* Function to get the temporary signed request from the Python app.
If request successful, continue to upload the file using this signed
request. */
function getSignedRequest(file){
const xhr = new XMLHttpRequest();
xhr.open('GET', `/sign-s3?file-name=${file.name}&file-type=${encodeURIComponent(file.type)}`);
xhr.onreadystatechange = () => {
    if(xhr.readyState === 4){
        if(xhr.status === 200){
            const response = JSON.parse(xhr.responseText);
            console.log(`response:${file.name},${response.url}`)
            uploadFile(file, response.data, response.url);
            document.querySelector('#file-clear').disabled = false;
            document.querySelector('#file-reload').disabled = false;
          }
        else{
            alert('Could not get signed URL.');
          }
        }
    };
xhr.send();
}

/* 
Function called when file input updated. If there is a file selected, then
start upload procedure by asking for a signed request from the app.
*/
function initUpload(){
const files = document.getElementById('file-input').files;
const file = files[0];
if(!file){
    return alert('No file selected.');
    }
getSignedRequest(file);
}

const clearFile = () => {
  document.querySelector('#preview').src = "/static/default_profile.png";
  document.querySelector('#img').value = "";
  document.querySelector('#file-clear').disabled = true
  document.querySelector('#file-reload').disabled = false
  document.querySelector('#apulomake').reset()
  }
  
  const reloadFile = () => {
    document.querySelector('#preview').src = preview_org;
    document.querySelector('#img').value = img_org;
    document.querySelector('#file-reload').disabled = true
    document.querySelector('#apulomake').reset()
    }

/* Bind listeners when the page loads.*/
(() => {
  const file_clear = document.querySelector('#file-clear') 
  const file_reload = document.querySelector('#file-reload') 
  if (!document.querySelector("#img").value) {
      file_clear.disabled = true
      }
  document.querySelector('#file-input').onchange = initUpload;
  file_clear.onclick = clearFile;
  file_reload.onclick = reloadFile;
})();