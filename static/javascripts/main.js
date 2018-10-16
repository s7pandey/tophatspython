 var errorCallback = function (e) {
     console.log('Rejected!', e);
 };

 navigator.getUserMedia = navigator.getUserMedia ||
     navigator.webkitGetUserMedia ||
     navigator.mozGetUserMedia ||
     navigator.msGetUserMedia;

 var video = document.querySelector('video');

 if (navigator.getUserMedia) {
     navigator.getUserMedia({
         audio: true,
         video: true
     }, function (stream) {
         video.src = window.URL.createObjectURL(stream);
     }, errorCallback);
 } else {
     console.log("Please retry with HTTPS");
     //   video.src = 'somevideo.webm'; // fallback.
 }