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
            ->method('upload')];
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
        foreach ($photos as $photo) {
            $data[] = [
                'name'     => 'photos[]',
                'contents' => fopen($photo->getPathname(), 'r'),
                'filename' => $photo->getClientOriginalName()
            ];
        }

        dd($data);
        // URL to your Python server handling the processing
        $url = 'http://your-python-server.com/process';

        // Send a multipart/form-data POST request
        $response = Http::attach('photos', $photos)->post($url);

        // Assuming the response body is a direct binary data of ZIP file
        $zipContents = $response->body();

        return response()->streamDownload(function () use ($zipContents) {
            echo $zipContents;
        }, 'processed_photos.zip', ['Content-Type' => 'application/zip']);
    }
}
