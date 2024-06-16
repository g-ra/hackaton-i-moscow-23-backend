<head>


    <!-- If you'd like to support IE8 (for Video.js versions prior to v7) -->
    <!-- <script src="https://vjs.zencdn.net/ie8/1.1.2/videojs-ie8.min.js"></script> -->
</head>
@if(!empty($video))

    <video
        controls
        width="99%"
        height="400px"
    >
        <source src="http://localhost:8181/stream-video?videoName={{ $video->path }}" />
        <p class="vjs-no-js">
            To view this video please enable JavaScript, and consider upgrading to a
            web browser that
            <a href="https://videojs.com/html5-video-support/" target="_blank"
            >supports HTML5 video</a
            >
        </p>
    </video>
    <div id="video-controls">
        @php
            $times = array_column(json_decode($video->metadata, true), 'time');
            $uniqueTimes = array_unique($times);
            sort($uniqueTimes);
        @endphp
        @foreach($uniqueTimes as $time)
            <button onclick="seekTo({{ $time }})">{{ gmdate("H:i:s", $time) }}</button>
        @endforeach
    </div>
    <script>
        function seekTo(time) {
            var video = document.getElementById('myVideo');
            video.currentTime = time;
            video.play();
        }
    </script>
@endif

