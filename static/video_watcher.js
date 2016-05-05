// This function creates an <iframe> (and YouTube player)
// after the API code downloads.
var player;
function onYouTubeIframeAPIReady() {
  get_video( function(video){
    LTI_ENV.video = video;
    console.log('got', video);

    $('#video_id').val(video.video_id);
    $('#minimum_percent').val(video.minimum_percent);
    if(LTI_ENV.is_instructor){
      $('#video_description').val(video.description);
    }else{
      $('#video_description').text(video.description);
    }
    player = new YT.Player('player', {
      height: '390',
      width: '640',
      videoId: video.video_id,
      playerVars: {
        rel: 0,
        modestbranding: 1
      },
      events: {
        'onReady': onPlayerReady,
        'onStateChange': onPlayerStateChange
      }
    });
  
  });
}

// The API will call this function when the video player is ready.
var interval;
function onPlayerReady(event) {
  event.target.playVideo();
  checkProgress(function(){
    console.log('setting up interval');
    interval = setInterval(checkProgress, 5000); // check every 10 seconds
  });
}

// The API calls this function when the player's state changes.
// The function indicates that when playing a video (state=1),
// the player should play for six seconds and then stop.
function onPlayerStateChange(event) {
  //console.log(YT.PlayerState);
  if (event.data == YT.PlayerState.ENDED ) {
    console.log('currentTime', player.getCurrentTime());
    console.log('duration', player.getDuration());
    checkProgress();
  }
}

function checkProgress(cb){
  if(typeof(cb) != 'function'){ cb = function(){} };
  if(LTI_ENV.is_instructor){
    if(interval) { window.clearInterval(interval); }
    cb();
    return
  }
  if(player.getDuration() > 0  ){
    // The player has watched at least 90% of the video
    // Send signal that video is finished playing
    // TODO make this take account of the minimum_percent

    var min_duration = LTI_ENV.video.minimum_percent / 100 * player.getDuration();
    var score = player.getCurrentTime() / min_duration; 
    get_current_score(function(current_score){
      var per_progress = Math.floor(current_score * 100);
      $('#you_have_watched').text(per_progress);
      $('#prog_bar').css('width',per_progress+'%').attr('aria-valuenow', per_progress).text(per_progress+'%');
      console.log('updating score to ' + score);
      if(score>=1){
        window.clearInterval(interval);
      }
      if( current_score == false || score > current_score ){
        $.post('/lti/yt_watch_for_points/finished',{score:score}).done( function(res, status){
          scores_db.child(score_id()).set({score:score});
          cb();
        });
      }else{
        cb();
      }
    });
  }else{
    cb();
  }
}

var firebase = new Firebase('https://burning-fire-7264.firebaseio.com/');
var scores_db = firebase.child('scores:'+LTI_ENV.context_id);
function get_current_score(callback){
  var score = scores_db.child(score_id());
  score.once('value', function(snapshot){
    var ret_value = false;
    if(snapshot.exists()){
      ret_value = snapshot.val().score;
    }
    callback(ret_value);
  });
}

function score_id(){
  return LTI_ENV.resource_link_id + '::' + LTI_ENV.custom_canvas_user_id;
}

function get_video(cb){
  var video_ref = scores_db.child('videos').child(LTI_ENV.resource_link_id);
  video_ref.on('value', function(snapshot){
    if (snapshot.exists()){
      cb( snapshot.val())
    }
  });
}

function set_video_id(video_id, description, minimum_percent, cb){
  scores_db.child('videos').child(LTI_ENV.resource_link_id).set({
    video_id:video_id, 
    description:description, 
    minimum_percent:minimum_percent
  },
  cb());
}
