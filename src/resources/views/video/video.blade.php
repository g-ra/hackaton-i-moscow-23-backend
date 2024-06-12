@if(!empty($videoUrl))
    <video controls height="500" width="500" loop>
        <source src="{{ $videoUrl }}" type="video/mp4">
        Your browser does not support the video tag.
    </video>
@endif
