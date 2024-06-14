<?php

namespace App\Http\Controllers;

use GuzzleHttp\Client;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\Http;
use Symfony\Component\HttpFoundation\StreamedResponse;

class VideoStreamController extends Controller
{

    public function streamVideo(Request $request)
    {
        $videoName = $request->query('videoName');
        if (empty($videoName)) {
            abort(400, "Video name is required");
        }

        $url = 'http://python-app:5000/' . ltrim($videoName, '/');

        $client = new Client([
            'timeout' => 99999999999999999999,
            'read_timeout' => 999999999999,
            'connect_timeout' => 99999999999
        ]);
        $response = $client->get($url); // Скачиваем файл


        $path = storage_path('public/' . basename($videoName));
        if (!file_exists(storage_path('public/'))) {
            mkdir(storage_path('public/'), 0777, true); // Создаем директорию, если она не существует
        }
        file_put_contents($path, $response->getBody()->getContents());

        return $this->streamVideoFromLocal($request, $path);
    }

    protected function streamVideoFromLocal(Request $request, $path)
    {
        $size = filesize($path);
        $length = $size;
        $start = 0;
        $end = $size - 1;

        $headers = [
            'Content-Type' => 'video/mp4',
            'Accept-Ranges' => 'bytes'
        ];

        if ($request->headers->has('Range')) {
            $ranges = sscanf($request->header('Range'), 'bytes=%d-%d');
            $start = $ranges[0];
            $end = $ranges[1] ?? $size - 1;

            $headers['Content-Range'] = sprintf('bytes %d-%d/%d', $start, $end, $size);
            $length = $end - $start + 1;

            return response()->stream(function () use ($path, $start, $length) {
                $handle = fopen($path, 'rb');
                fseek($handle, $start);
                echo fread($handle, $length);
                fclose($handle);
            }, 206, $headers); // 206 Partial Content
        }

        return response()->file($path, $headers);
    }
}
