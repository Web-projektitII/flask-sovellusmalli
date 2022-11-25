const url = '/save-local'
console.log(`preview_org:${preview_org},img_org:${img_org}`)

const uploadFile = file => {  
console.log('uploadFile:',file.name)    
document.querySelector('#preview').src = URL.createObjectURL(file);
const postData = new FormData();
postData.append('file', file);
fetch(url,{
    method:'POST',
    body:postData})
.then(response => response.json())
.then(success => {
    document.querySelector('#img').value = file.name;
    console.log(success)
    alert(success.msg)
    })
.catch(error => {
    console.log(error)
    alert('Tiedostoa ei tallennettu.')
    })
}


/* Function to get the temporary signed request from the Python app.
If request successful, continue to upload the file using this signed
request. */
/* const getRequest = file => {
fetch(`/sign-local?file-name=${file.name}&file-type=${encodeURIComponent(file.type)}`)
.then(response => response.json())
.then(response => {
    console.log('response:',response)
    uploadFile(file, response.url);
    })
.catch(error => {
    console.log(error)
    alert('Tiedostolle ei löytynyt tallennusosoitetta')
    })
}
*/

/* 
Function called when file input updated. If there is a file selected, then
start upload procedure by asking for a signed request from the app.
*/
const initUpload = () => {
const files = document.querySelector('#file-input').files;
const file = files[0];
if(!file){
    return alert('No file selected.');
    }
uploadFile(file);
document.querySelector('#file-clear').disabled = false;
document.querySelector('#file-reload').disabled = false;
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