from jnius import autoclass

"""
All functions are implemented according to android studio
https://developer.android.com/reference/android/media/MediaPlayer
date: 25-01-2023
"""
MediaPlayer = autoclass('android.media.MediaPlayer')


class AudioPlayer:
    def __init__(self, file_path=None):
        self.duration = None
        self.path = file_path
        self.audioplayer = MediaPlayer()
        self.state = 'ready'

    def play(self) -> None:
        self.state = 'playing'
        self.audioplayer.start()

    def pause(self) -> None:
        self.state = 'ready'
        self.audioplayer.stop()

    def seek(self, to: int) -> None:
        self.audioplayer.seekTo(to)

    def jump_in_time(self, t: int = 10, backward: bool = False) -> None:
        """
        :param t: time \'t\' is seconds to jump forward or backward
        :param backward: if skipping is backward or not
        :return: Nothing
        """

        new_time = self.current_pos + t * 1000 * (1 - 2 * int(backward))  # gives -1 if backward else +1 (not tested)
        if new_time > self.duration:
            self.seek(self.duration)
        elif new_time < 0:
            self.seek(0)
        else:
            self.seek(new_time)

    def release(self):
        self.audioplayer.release()

    @property
    def length(self) -> int:
        return self.duration

    @property
    def current_pos(self) -> int:
        return self.audioplayer.getCurrentPosition()

    @property
    def is_playing(self) -> bool:
        """
        :return: boolean value saying audio is playing or not
        """
        return self.audioplayer.isPlaying()

    @property
    def file_path(self) -> str:
        return self.path

    @file_path.setter
    def file_path(self, path):
        assert isinstance(path, str), 'File path is not \'str\''
        if self.path == path:
            if self.current_pos == self.duration:
                self.play()
            return
        elif self.audioplayer is not None:
            self.audioplayer = MediaPlayer()
        self.path = path
        self.audioplayer.setDataSource(path)
        self.audioplayer.prepare()
        self.duration = self.audioplayer.getDuration()
        self.play()
        # self.current_pos = 0


if __name__ == "__main__":
    a = AudioPlayer()
    print(a.file_path)
    a.file_path = '/storage/emulated/0/'
    print(a.file_path)
