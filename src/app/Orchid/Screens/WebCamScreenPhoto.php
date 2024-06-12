<?php

namespace App\Orchid\Screens;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;
use Orchid\Screen\Actions\Button;
use Orchid\Screen\Fields\Cropper;
use Orchid\Screen\Fields\Input;
use Orchid\Screen\Fields\Picture;
use Orchid\Screen\Fields\Upload;
use Orchid\Screen\Screen;
use Orchid\Support\Facades\Layout;

class WebCamScreenPhoto extends Screen
{
    /**
     * Fetch data to be displayed on the screen.
     *
     * @return array
     */
    public function query(): iterable
    {
        return [];
    }

    /**
     * The name of the screen displayed in the header.
     *
     * @return string|null
     */
    public function name(): ?string
    {
        return 'WebCamScreenPhoto';
    }

    /**
     * The screen's action buttons.
     *
     * @return \Orchid\Screen\Action[]
     */
    public function commandBar(): iterable
    {
        return [ Button::make('Upload Photos')
            ->icon('upload')
            ->method('upload')->rawClick()];
    }

    /**
     * The screen's layout elements.
     *
     * @return \Orchid\Screen\Layout[]|string[]
     */
    public function layout(): iterable
    {
        return [
            Layout::rows([
                Input::make('photos')
                    ->type('file')
                    ->acceptedFiles('image/*')
                    ->multiple()
                    ->title('File input example')
                    ->horizontal(),
            ])
        ];
    }

    public function upload(Request $request)
    {
        $photos = $request->file('photos');
        $data = [];

        // URL to your Python server handling the processing
        $url = 'http://python-app:5000/image';

        // Send a multipart/form-data POST request
        $response = Http::asMultipart();

        // Добавление каждого фото в форму запроса
        foreach ($photos as $photo) {
            $response->attach(
                'images', // Имя поля в запросе, должно совпадать с ожидаемым Flask-приложением
                file_get_contents($photo->getPathname()), // Содержимое файла
                $photo->getClientOriginalName() // Исходное имя файла
            );
        }

        $response = $response->post($url);

        // Assuming the response body is a direct binary data of ZIP file
        $zipContents = $response->body();
        return response()->streamDownload(function () use ($zipContents) {
            echo $zipContents;
        }, 'processed_photos.zip', ['Content-Type' => 'application/zip']);
    }
}
