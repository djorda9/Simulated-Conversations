from django import template
from simcon import settings

register = template.Library()
 
@register.simple_tag
def getRecorderHead():
    '''
    Supplies the required header elements for:
    jquery, recorder, and ajax sends
    '''
    return '''
<script type="text/javascript" src="''' + settings.STATIC_URL + '''jquery-2.1.0.min.js"> </script>
<script type="text/javascript" src="''' + settings.STATIC_URL + '''recorder.js"> </script>
<link rel="stylesheet" type="text/css" href="''' + settings.STATIC_URL + '''dist/css/bootstrap.css" />
<script>
$(document).ready(function(){      
    <!-- the snippet below ensures the AJAX POST has a CSRF token for django -->
      $(document).ajaxSend(function(event, xhr, settings) {
	  function getCookie(name) {
	      var cookieValue = null;
	      if (document.cookie && document.cookie != '') {
		  var cookies = document.cookie.split(';');
		  for (var i = 0; i < cookies.length; i++) {
		      var cookie = jQuery.trim(cookies[i]);
		      // Does this cookie string begin with the name we want?
		      if (cookie.substring(0, name.length + 1) == (name + '=')) {
			  cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
			  break;
		      }
		  }
	      }
	      return cookieValue;
	  }
	  function sameOrigin(url) {
	      // url could be relative or scheme relative or absolute
	      var host = document.location.host; // host + port
	      var protocol = document.location.protocol;
	      var sr_origin = '//' + host;
	      var origin = protocol + sr_origin;
	      // Allow absolute or scheme relative URLs to same origin
	      return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
		  (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
		  // or any other URL that isn't scheme relative or absolute i.e relative.
		  !(/^(\/\/|http:|https:).*/.test(url));
	  }
	  function safeMethod(method) {
	      return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
	  }

	  if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
	      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
	  }
      });
      });
      <!-- end snippet -->    
</script>'''


@register.simple_tag
def load_getUserMedia(callBackFunction):
    ''' 
    Used to load an instance of a recorder
    callBackFunction:  the function to be called with the created blob of the recording
    '''
    return '''
  <button class="btn btn-default btn-lg" onclick="startRecording(this);"><span class="glyphicon glyphicon-record"/>Record</button>
  <button class="btn btn-default btn-lg" onclick="stopRecording(this);" disabled><span class="glyphicon glyphicon-stop"\>Stop</button>
  
  <script>
  function __log(e, data) {
    console.log(e + " " + (data || ''));
  }

  var audio_context; // moved these out to global scope due to persistence issues
  var recorder;
  var input;
  var zeroGain;

  function startUserMedia(stream) {
    window.keepStreamAlive = stream;
    input = audio_context.createMediaStreamSource(stream);
    __log('Media stream created.');
    
    zeroGain = audio_context.createGain();
    zeroGain.gain.value = 0;
    input.connect(zeroGain);
    zeroGain.connect(audio_context.destination);
    __log('Input connected to muted gain node connected to audio context destination.');
    
    var cfg = {}
    cfg.workerPath = "''' + settings.STATIC_URL + '''recorderWorker.js";
    recorder = new Recorder(input, cfg);
    __log('Recorder initialised.');
  }

  function startRecording(button) {
    recorder && recorder.record();
    button.disabled = true;
    button.nextElementSibling.disabled = false;
    __log('Recording...');
  }

  function stopRecording(button) {
    recorder && recorder.stop();
    button.disabled = true;
    button.previousElementSibling.disabled = false;
    __log('Stopped recording.');
    
    // create WAV download link using audio data blob
    createDownloadLink();
    
    recorder.clear();
  }

  function createDownloadLink() {
    recorder && recorder.exportWAV(function(blob) {
      var url = URL.createObjectURL(blob);
      window.savedUrl = url; // kick this into global context so we can reference on the other end
      
      ''' +  callBackFunction  + '''(blob);
    });
  }

  $(document).ready(function(){ 
    try {
      // webkit shim
      window.AudioContext = window.AudioContext || window.webkitAudioContext;
      navigator.getUserMedia = navigator.getUserMedia || navigator.mozGetUserMedia || navigator.webkitGetUserMedia;
      window.URL = window.URL || window.webkitURL;
      
      audio_context = new AudioContext;
      __log('Audio context set up.');
      __log('navigator.getUserMedia ' + (navigator.getUserMedia ? 'available.' : 'not present!'));
    } catch (e) {
      alert('No web audio support in this browser!');
    }
    
    navigator.getUserMedia({audio: true}, startUserMedia, function(e) {
      __log('No live audio input: ' + e);
    });
  });
  </script>
'''

@register.simple_tag
def defaultHandler(func):
    '''
    This is the default handler for recorder saves
    func designates the function to call upon successful save
    '''
    return '''
    <script type="text/javascript">
    function '''+func+'''(blob){
        alert("recording made");
        window.savedAudio = blob;
        saveRecording(blob);
    }
    function saveRecording(blob){
           var fd = new FormData();  // needed to wrap the blob
           fd.append('data', blob);
           var data = { recording:blob };
           var args = { type:"POST", url:"/audio/save", data:fd, processData: false, contentType: false, cache:false, complete:function(){
                           alert("saved audio");
                       } };
           $.ajax(args);
    }
    </script>'''
    