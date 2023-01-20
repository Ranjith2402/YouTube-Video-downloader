import os
import re
import urllib.error
import http.client
from typing import Union

from pytube import YouTube, exceptions


def re_sort(itt) -> list:
    """given an iterable of video/audio quality (str) returns int sort while its rest is kept with it(applicable only
    when format like below int-str
    """
    try:
        adder = re.search(r'\D{1,4}', itt[0]).group()  # getting 'p' or 'kbps'  ex: 144p or 128kbps
    except IndexError:
        return []
    return [i + adder for i in map(str, sorted(map(int, [re.search(r'\d*', i).group() for i in itt.copy()])))]


def new_name(name: str, audio=False):
    folder = 'Music' if audio else 'Movies'
    print(folder)
    try:
        tmp = name.split('.')
        format_ = tmp[-1] if audio else 'mp3'
        print('format -->', format_)
        name = '.'.join(tmp[:-1])
    except Union[KeyError, IndexError]:
        format_ = 'mp4' if audio else 'mp3'
    lst = os.listdir(folder)
    for i in lst:
        print(i)
    i = 0
    name_ = name + '.' + format_
    if name_ in lst:
        print('File exists')
        i = 1
        name = f"{name}(1).{format_}"
        while name in lst:
            name = name.replace(f"({i})", f"({i + 1})")
            i += 1
        name_ = name
    return name_, i


class Downloader:
    def __init__(self, link, on_complete, unavailable, progress=None, bypass_age_gate=False):
        self.video_qualities = ['2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']
        self.video_only_qualities = self.video_qualities.copy()
        self.audio_qualities = []
        self.size = 0
        self.youtube_object = None
        self.stream_object = None
        self.link = link
        self.res = "360p"
        self.fps = 30
        self.file_extension = "mp4"
        self.bit_rate = '128kbps'
        self.audio_only = False
        self.video_only = False
        self.downloaded_p = 0.0
        self.on_complete = on_complete
        self.error = unavailable
        self.progress = progress
        self.youtube_object = YouTube(self.link,
                                      on_progress_callback=self.on_progress,
                                      on_complete_callback=self.on_complete)
        if bypass_age_gate:
            self.bypass_age_gate()
        self.is_error = False
        self.includes_audio = False
        self.audio_size = 0

    def bypass_age_gate(self):
        try:
            self.youtube_object.bypass_age_gate()
        except exceptions.AgeRestrictedError:
            self.error('tier 3 age restriction')

    def reset(self):
        self.video_qualities = ['2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']
        self.size = 0
        self.stream_object = None

    def check_available_quality(self):
        tmp_list_video = []
        tmp_list_audio = []
        tmp_list_vo = []
        tmp = False
        try:
            for item in self.youtube_object.streams:
                q = item.resolution
                if q is not None and item.is_progressive:  # if resolution exist
                    tmp_list_video.append(q)  # add it to progressive list
                elif q is not None:
                    tmp_list_vo.append(q)  # add it to video only list
                    if q == self.res:
                        tmp = True
                else:
                    tmp_list_audio.append(item.abr)  # if it has no resolution it must be audio quality
        except urllib.error.URLError:
            self.is_error = True
            self.error('no connection-1a0')
            return
        except KeyError:
            self.is_error = True
            self.error('can\'t by pass age gate (video unavailable) :(')
        except http.client.RemoteDisconnected:
            self.is_error = True
            self.error('poor connection')
            return
        except ConnectionAbortedError:
            self.is_error = True
            self.error('no connection-1a0')
            return

        self.video_qualities = re_sort(list(set(tmp_list_video))[::-1]).copy()  # to get avail quality in descending
        # order
        self.video_only_qualities = re_sort(list(set(tmp_list_vo))[::-1]).copy()
        self.audio_qualities = re_sort(list(set(tmp_list_audio))[::-1]).copy()
        if not any([tmp_list_video, tmp_list_vo, tmp_list_audio]):
            self.is_error = True
            self.error('something went wrong3')
            return
        if tmp or self.res not in tmp_list_video:
            try:
                self.res = self.video_qualities[0]
            except IndexError:
                self.res = None
        self.audio_only = True
        self.create_object()  # this may not take too much time, since steams already loaded
        self.audio_size = self.size
        self.audio_only = False
        if not self.video_qualities:
            self.error('no connection')
            self.is_error = True
            self.reset()

    def on_progress(self, _, __, remaining):
        self.downloaded_p = 1 - round(remaining / self.size, 2)
        if self.progress is not None:
            self.progress(self.downloaded_p)

    @property
    def get_size(self):
        if self.stream_object is None:
            self.create_object()
        if not self.includes_audio and not self.audio_only:
            return self.size + self.audio_size
        return self.size

    def create_object(self, test=False, recur=False):
        try:
            if self.audio_only:
                self.stream_object = self.youtube_object.streams.filter(only_audio=True, abr=self.bit_rate).first()
            elif self.video_only:
                self.stream_object = self.youtube_object.streams.filter(only_video=True, resolution=self.res).first()
            else:
                self.stream_object = self.youtube_object.streams.filter(res=self.res).first()
        except urllib.error.URLError:
            self.error('no connection')
            return
        except KeyError:
            self.error('something went wrong3')
            return

        if test:
            return bool(self.stream_object)

        try:
            # print(self.res, self.bit_rate, self.video_only, self.audio_only)
            self.size = self.stream_object.filesize
            self.includes_audio = self.stream_object.includes_audio_track
            print(self.stream_object.default_filename)
            print(self.stream_object.get_file_path())
        except KeyError:
            self.error("something went wrong2")
        except AttributeError:
            self.error('not available')
            if not recur:
                self.res = self.video_qualities[0]
                self.bit_rate = self.audio_qualities[-1]
                self.create_object(recur=True)
        except urllib.error.URLError:
            self.error('no connection')
        except http.client.IncompleteRead:
            self.error("no connection")  # this error never happened, it for safety precaution

    def set_filter(self, res='360p', audio_only=False, video_only=False):
        self.audio_only = audio_only
        self.video_only = video_only
        if audio_only:
            self.bit_rate = res
        else:
            self.res = res
        self.create_object()

    def download(self, ignore=False, rename=False):
        try:
            out_folder = 'Music' if self.audio_only else 'Movies'
            # if not (self.includes_audio or self.audio_only):  # De Morgan's law don't confuse (condition is true
            # when both were false) video_stream = self.stream_object self.audio_only = True self.create_object()
            # audio_stream = self.stream_object self.audio_only = False _ffmpeg_downloader(audio_stream=audio_stream,
            # video_stream=video_stream, target='') else:
            old_name = self.stream_object.default_filename
            name, flag = new_name(old_name, self.audio_only)
            if not ignore and flag:
                self.error('file exists')
                return
            if not rename:
                name = old_name
            print(name, "is new name")
            self.stream_object.download(output_path=out_folder, filename=name)  # indent this if the above code is
            # uncommented (commented part only un-commented is rewritten)
        except urllib.error.URLError:
            self.error('no connection')
        except http.client.RemoteDisconnected:
            self.error("no connection")
        except http.client.IncompleteRead:
            self.error('poor connection')
        except ConnectionAbortedError:
            self.error("poor connection")
        if self.stream_object is None:
            self.error("something went wrong")
