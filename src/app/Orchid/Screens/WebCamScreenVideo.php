<?php

namespace App\Orchid\Screens;

use App\Models\User;
use App\Notifications\DroneConfirmationNotification;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Notification;
use Illuminate\Support\Facades\Storage;
use Orchid\Screen\Actions\Button;
use Orchid\Screen\Fields\Input;
use Orchid\Screen\Fields\Upload;
use Orchid\Screen\Screen;
use Orchid\Screen\TD;
use Orchid\Support\Facades\Layout;

class WebCamScreenVideo extends Screen
{
    private ?string $videoUrl = null;
    /**
     * Fetch data to be displayed on the screen.
     *
     * @return array
     */
    public function query(): iterable
    {
        return [
            'videoUrl' => session('videoUrl', null),
            'notifiedUsers' => session('notifiedUsers', null),
        ];
    }

    /**
     * The name of the screen displayed in the header.
     *
     * @return string|null
     */
    public function name(): ?string
    {
        return 'WebCamScreenVideo';
    }

    /**
     * The screen's action buttons.
     *
     * @return \Orchid\Screen\Action[]
     */
    public function commandBar(): iterable
    {
        return [ Button::make('Upload Video')
            ->icon('upload')
            ->method('upload'),
            Button::make('Подтвердить наличие дрона')
                ->method('confirmDrone')
                ->canSee($this->query()['videoUrl'] !== null)
                ->rawClick()
                ->class('btn btn-danger'),
        ];
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
                Input::make('raw_file')
                    ->type('file')
                    ->acceptedFiles('video/*')
                    ->title('File input example')
                    ->horizontal(),
            ]),
            Layout::view('video.video', [
                'videoUrl' => $this->query()['videoUrl']
            ]),
            Layout::table('notifiedUsers', [
                TD::make('email', 'Email сотрудника')
            ])->title('Уведомления отправлены:')->canSee($this->query()['notifiedUsers'] !== null)
        ];
    }

    public function upload(Request $request)
    {
        $video = $request->file('raw_file');

        // Сохранение временного файла
        $path = $video->store('tmp/videos', 'public');

        // Путь для доступа к файлу
        $url = Storage::disk('public')->url($path);

        // Сохранение URL в сессии для доступа при рендере страницы
        session()->flash('videoUrl', $url);

        return redirect()->route('platform.video');
    }

    public function confirmDrone()
    {
        // Получение списка email сотрудников (пример)
        $employees = User::select('email')->get();
        // Эмуляция отправки уведомлений сотрудникам
        session()->flash('notifiedUsers', $employees);
        // Очистка сессии для URL видео
        session()->forget('videoUrl');

        return redirect()->route('platform.video')->with('message', 'Уведомление о дроне отправлено сотрудникам');
    }
}
