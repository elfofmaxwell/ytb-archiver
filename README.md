# ytb-archiver
A small tool to download all videos in a youtube channel. 

## Dependencies
Please ensure that `yt-dlp` is available in your environment. `FFmpeg` is required for high-res videos. Since this script is not formally published, you need to prepare your own google oauth secrets (see here: [Obtaining authorization credentials](https://developers.google.com/youtube/registering_an_application)), and save the secret json file as `secret.json` in working path. Also, you need `google-api-python-client` as well as `google-auth-oauthlib`, both of which could be installed via `pip`. 

## Usage of one-click script: 

For first time use please initialize the config of the script. You could run
```
python one-click.py init
```
to initialize interactively or run
```
python one-click.py init --file
```
to initialize with existing `config.json` file. 

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
<specified_dir>/downloads/<channelID>/by_upload_date/<upload_time>/<title [video id]>.webm
```

In order to prevent "Too much requests" error, the script would in default run under slow mode, sleeping for around 10 min after each download finished. Slow mode time could be modified or directly toggle off in config file or during initialization. If the script quits during downloading, it would restart from unfinished video at next start. After downloads are finished, a completeness check would run and check if all contents are downloaded successfully. Note that only when download task is fully finished (i.e. the newest video is downloaded) the completeness check would run; if you want to run the completeness check in middle way, run completeness_check.py. A file `\<channelID\>_diff.list` would be created to show which videos are not successfully downloaded. You could redownload these videos by run download_with_id.py. A `\<channelID\>_download.log` file would show all error and warning encountered during downloading. 

### Update settings with `config.json`
Use your text editor to open `config.json`. The first entry, inside the square bracket, is for channel ID's; the ID's should be wrapped by double quotes and be separated by comma, if multiple ID's are provided. The second entry, `"download_path"`, is for download path, which should be wrapped by double quotes too. The third entry, `slow_mode_time` is for the sleeping time (second) in slow mode, default value is 600s. Enter 0 if wishing not to use slow mode. 

## Download videos manually `download_with_id.py`
If there are videos that are not successfully finished, you could use this script to redownload them in a simple way. The script would first ask you about download path. You could offer an actual path, or you could offer a channel ID that used to be initialized or downloaded. If a channel ID is offered, the videos would be downloaded to the folder where previous downloads of that channel is saved. If the path is left blank, videos would be downloaded to working path. 

## Running scripts separately
### `get_video_list.py`
Pull video list of a channel. 

Required argument: `<channel ID>`. 

Output: `./video_lists/<channel id>_list.json`, containing information of all uploaded videos in the given channel. 

### `download_w_list.py`
Download videos in a video information list. 

Arguments: `<channel id>`, must be the first argument. 

Possible options: 

`--edit-checkpoint`: manually move pointer of checkpoint to a certain video (interactive)

`--init-checkpoint`: pre-define a download path for a channel, parameter (optional): `<project download path>`

`--log`: save download errors in `<channel_id>_download.log`, parameter (optional): `append` [not clear previous log]

`--slow`: slow mode, in default sleep around 10 min every video finished during automatic mode, parameter (optional): `sleep time (s)`

`-q`: quiet mode, do not ask about path at beginning

`-y`: automatic mode, automatic go over the list without asking continue or not

Output: videos, checkpoint files, error logs

### `completeness_check.py`
Check completeness of downloads. 

Arguments: `<channel ID>`, must be first argument

Possible options: 

`<start index>` (position arg): an integer to indicate start index in the video list to check completeness, default is 0. 

`<end index>` (position arg): an inter to indicate end index in the video list to check completeness, default is the most downloaded video's index. 
