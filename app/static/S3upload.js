function uploadFile(file, s3Data, url){
console.log('uploadFile:',file.name)    
document.querySelector('#preview').src = URL.createObjectURL(file);
const postData = new FormData();
for(key in s3Data.fields){
  postData.append(key, s3Data.fields[key]);
  }
postData.append('file', file);
fetch(s3Data.url,{
    headers: new Headers({'x-amz-acl': 'public-read'}),
    method:'POST',
    body:postData})
.then(response => response.text())
.then(success => {
  console.log(success)  
  if (success.msg){
      document.querySelector('#img').value = file.name;
      alert(success.msg)
  }
  else if (virhe) {
      alert(success.virhe)
  }    
  })
.catch(error => {
  console.log(error)
  alert('Tiedostoa ei tallennettu.');
  })
}

/* Function to get the temporary signed request from the Python app.
If request successful, continue to upload the file using this signed
request. */
function getSignedRequest(file){
const url = `/sign-s3?file-name=${file.name}&file-type=${encodeURIComponent(file.type)}`
fetch(url)
.then(response => response.json())
.then(response => {
  console.log(response)
  uploadFile(file, response.data, response.url);
  document.querySelector('#file-clear').disabled = false;
  document.querySelector('#file-reload').disabled = false;      
  })
.catch(error => {
  console.log(error)
  alert('Could not upload file.');
  })
}

/* 
Function called when file input updated. If there is a file selected, then
start upload procedure by asking for a signed request from the app.
*/
function initUpload(){
const files = document.querySelector('#file-input').files;
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