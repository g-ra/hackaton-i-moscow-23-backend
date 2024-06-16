<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('platform.video');
});

Route::get('/stream-video', [\App\Http\Controllers\VideoStreamController::class, 'streamVideo']);
