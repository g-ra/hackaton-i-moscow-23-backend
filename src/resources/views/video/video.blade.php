
@if(!empty($video))
    <video controls height="500" width="100%" loop>
        <source src="{{ $video->path }}" type="video/mp4">
        Your browser does not support the video tag.
    </video>
@endif
