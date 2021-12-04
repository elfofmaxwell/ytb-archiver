# ytb-archiver
A small tool to download all videos in a youtube channel. 

## Dependencies
Please ensure that yt-dlp is available in your environment. FFmpeg is required for high-res videos. Since the script is not formally published, you need to prepare your own google oauth secrets (see here: https://developers.google.com/youtube/registering_an_application), and save the secret json file as "secret.json" in working path, and you need "google-api-python-client" as well as "google-auth-oauthlib", both of which could be installed via pip. 

## Usage of one-click script: 

First please initialize the config of the script. You could run
```
python one-click.py init
```
to initialize interactively or run
```
python one-click.py init --file
```
to initialize with existing config.json file. 

After initializing, use 
```
python one-click.py start
```
to start a download task, or use
```
python one-click.py <channelId>
```
to download contents of a specified channel. Note that this channel would not be added to config file and would not be automatically download next time. 

The structure in your specified project download file is 
```
<specified_dir>/downloads/<channelID>/sort_by_date/<upload_time>/<videos>
```

After downloads are finished, a completeness check would run and check if all contents are downloaded successfully. Note that only when download task is fully finished (i.e. the newest video is downloaded) the completeness check would run; if you want to run the completeness check in middle way, run completeness_check.py. A file "\<channelID\>_diff.list" would be created to show which videos are not successfully downloaded. You could redownload these videos by run download_with_id.py. A "\<channelID\>_download.log" file would show all error and warning encountered during downloading. 

## Run scripts separately
### get_video_list
Pull video list of a channel. 

Argument: channel ID. 

### download_w_list
Download videos in a video information list. 

Arguments: first argument must be channel ID

Possible options: 

    --edit-checkpoint: manually move pointer of checkpoint to a certain video

    --init-checkpoint: pre-define a download path for a channel, parameter (optional): project download path

    --log: save download errors in <channel_id>_download.log, parameter (optional): "append" [not clear previous log]

    --slow: slow mode, in default sleep around 10 min every video finished during automatic mode, parameter (optional): sleep time

    -q: quiet mode, do not ask about path at beginning

    -y: automatic mode, automatic go over the list without asking continue or not

### download_with_id
Interactively download videos with video ID's. 

### completeness_check
Check completeness of downloads. 

Arguments: Channel ID

Possible options: 

    <start index>: an integer to indicate start index in the video list to check completeness, default is 0. 

    <end index>: an inter to indicate end index in the video list to check completeness, default is the most downloaded video's index. 
