# -*- coding: utf8 -*-

'''
A tool to get video list from a channel. 
Argument: channel ID
'''

import os
import sys
import json

import googleapiclient.discovery
import googleapiclient.errors
import google_auth_oauthlib

scopes = ['https://www.googleapis.com/auth/youtube.force-ssl']


def get_video_info(single_video: dict)->dict: 
    '''
    single video: an item in 'items' props of getListItems() result. 
    Take an item dict and extract video ID, title, and upload time. 
    '''
    video_info = {
        "videoId": single_video["snippet"]["resourceId"]["videoId"], 
        "title": single_video["snippet"]["title"], 
        "date": single_video["snippet"]["publishedAt"][:10]
    }
    return video_info


def main(): 
    channel_id = sys.argv[1]

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"
    

    # set api credentials
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "secrets.json"
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    # if no refresh token, request brand new token set
    if not os.path.isfile('refresh_token.json'): 
        credentials = flow.run_console()
        with open('refresh_token.json', 'w') as f: 
            json.dump(credentials.refresh_token, f)
    # if there is refresh token, use it to get new access token
    else: 
        with open(client_secrets_file) as f: 
            client_info = json.load(f)
        client_id = client_info["installed"]["client_id"]
        with open('refresh_token.json') as f: 
            refresh_token = json.load(f)
        flow.oauth2session.refresh_token(flow.client_config['token_uri'], refresh_token=refresh_token, client_id=client_id, client_secret=flow.client_config['client_secret'])
        credentials = google_auth_oauthlib.helpers.credentials_from_session(flow.oauth2session, flow.client_config)
        with open('refresh_token.json', 'w') as f: 
            json.dump(credentials.refresh_token, f)
    # create api client
    youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
    
    
    video_info_list = []
    video_info_list_old = []
    meet_old_video = False
    # load existed video list 
    if not os.path.isdir("video_lists"): 
        os.mkdir("video_lists")
    if os.path.isfile(os.path.join("video_lists", "%s_list.json" % channel_id)): 
        with open(os.path.join("video_lists", "%s_list.json" % channel_id)) as f: 
            video_info_list_old = json.load(f)

    try: 
        # get channel detail => upload video playlist
        request = youtube.channels().list(
            id = channel_id, 
            part = "contentDetails", 
            maxResults = 1
        )
        response = request.execute()
        uploads_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # get detail of videos inside upload playlist
        request = youtube.playlistItems().list(
            part="snippet", 
            playlistId=uploads_id, 
            maxResults=50, 
        )
        # keep ask for next page if there is more results 
        while request: 
            response = request.execute()
            for single_video in response["items"]: 
                if single_video['snippet']['resourceId']['kind'] == 'youtube#video': 
                    single_video_info = get_video_info(single_video)
                    # if returned video info match existing video info, stop
                    if single_video_info['videoId'] in [i['videoId'] for i in video_info_list_old]: 
                        meet_old_video = True
                        break
                    video_info_list.append(get_video_info(single_video))
            if meet_old_video: 
                break
            request = youtube.playlistItems().list_next(request, response)
    except: 
        raise
    # concatenate the old and new lists 
    video_info_list = video_info_list+video_info_list_old

    # save list as json file 
    with open(os.path.join("video_lists", "%s_list.json" % channel_id), 'w') as f: 
        json.dump(video_info_list, f)
    

if __name__ == "__main__": 
    main()