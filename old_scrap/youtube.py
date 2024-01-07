from pytube import Channel, helpers
from os import path
from retrying import retry


@retry(stop_max_attempt_number = 1000, wait_fixed=30)
def download_one_video(video):
    basename = helpers.safe_filename(video.title)
    caption_name = basename + ".srt"
    video_name = basename + ".mp4"
    if not path.exists(caption_name):
        caption = video.captions['en']
        with open(caption_name, 'w', encoding='utf-8') as f:
            f.write(caption.xml_captions)
    if not path.exists(video_name):
        video.streams.get_highest_resolution().download()
        print(video.title, " downloaded done!")
    else:
        print("skip ", video.title)


def download_channel():
    c = Channel('https://www.youtube.com/user/SuperSimpleSongs')
    print(f'Downloading videos by: {c.channel_name}')
    for video in c.videos:
        try:
            print(video.title)
            download_one_video(video)
        except KeyError as e:
            print("KeyError Skip", e)

download_channel()
