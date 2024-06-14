<?php

namespace App\Orchid\Screens;

use App\Models\User;
use App\Models\Video;
use App\Notifications\DroneConfirmationNotification;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Notification;
use Illuminate\Support\Facades\Storage;
use Orchid\Screen\Actions\Button;
use Orchid\Screen\Actions\ModalToggle;
use Orchid\Screen\Fields\Input;
use Orchid\Screen\Fields\TextArea;
use Orchid\Screen\Fields\Upload;
use Orchid\Screen\Screen;
use Orchid\Screen\TD;
use Orchid\Support\Facades\Alert;
use Orchid\Support\Facades\Layout;
use Orchid\Support\Facades\Toast;

class WebCamScreenVideo extends Screen
{
    private ?Video $currentVideo = null;
    private ?string $videoUrl = null;
    /**
     * Fetch data to be displayed on the screen.
     *
     * @return array
     */
    public function query(): iterable
    {
        return [
            'videos' => Video::paginate(10),
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
        return 'Проверка Видео';
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
            Layout::table('videos', [
                TD::make('filename', 'Filename')
                    ->render(function (Video $video) {
                        return $video->filename;
                    }),

                TD::make('action', 'Action')
                    ->align(TD::ALIGN_CENTER)
                    ->render(function (Video $video) {
                        return ModalToggle::make('View')
                            ->modal('asyncVideoModal')
                            ->modalTitle('Video Details')
                            ->asyncParameters(['video' => $video->id]);
                    }),
            ]),
            Layout::modal('asyncVideoModal', [
                Layout::rows([
                    Input::make('video.id')->disabled()->title('id'),
                    Input::make('video.filename')->disabled()->title('Filename'),
                    Input::make('video.metadata')->disabled()->title('Metadata'),
                ]),
                Layout::view('video.video', [
                    'video'=>$this->currentVideo
                ] )
            ])->async('asyncGetVideo'),

            Layout::table('notifiedUsers', [
                TD::make('email', 'Email сотрудника')
            ])->title('Уведомления отправлены:')->canSee($this->query()['notifiedUsers'] !== null)
        ];
    }

    public function upload(Request $request)
    {
        // Получаем файл из запроса
        $video = $request->file('raw_file');

        // Сохранение временного файла
        $path = $video->store('tmp/videos', 'public');

        // Путь к физическому файлу на сервере
        $filePath = Storage::disk('public')->path($path);

        try {
            // Создание HTTP-запроса с использованием multipart формы
            $response = Http::asMultipart()->attach(
                'videos', // Имя поля в форме
                file_get_contents($filePath), // Содержимое файла
                basename($filePath) // Имя файла
            )->timeout(50)->post('http://python-app:5000/video');

            $videoModel = new Video();
            $videoModel->filename = $video->getClientOriginalName();
            $videoModel->metadata = $response->json()['json'];
            $videoModel->path = $response->json()['video_path'];
            $videoModel->save();
        } catch (\Exception $e) {
            // Обработка возможных ошибок
            return response()->json(['error' => $e->getMessage()], 500);
        }
    }

    public function confirmDrone()
    {
        // Получение списка email сотрудников (пример)
        $employees = User::select('email')->get();
        // Очистка сессии для URL видео
//        session()->forget('videoUrl');
        Toast::success('Уведомления отправлены сотрудникам')
            ->delay(2000);

        return redirect()->route('platform.video')->with('message', 'Уведомление о дроне отправлено сотрудникам');
    }

    public function asyncGetVideo(Video $video)
    {
        $this->currentVideo = $video;
        return [
            'video' => $video,
        ];
    }
}
