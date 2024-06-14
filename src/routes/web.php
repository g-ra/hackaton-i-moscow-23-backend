<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
});

Route::get('/stream-video', [\App\Http\Controllers\VideoStreamController::class, 'streamVideo']);
