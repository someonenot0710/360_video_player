#!/usr/local/bin/python
"""
Author:            Parikshit Juluri
Contact:           pjuluri@umkc.edu
Testing:
    import dash_client
    mpd_file = <MPD_FILE>
    dash_client.playback_duration(mpd_file, 'http://198.248.242.16:8005/')

    From commandline:
    python dash_client.py -m "http://198.248.242.16:8006/media/mpd/x4ukwHdACDw.mpd" -p "all"
    python dash_client.py -m "http://127.0.0.1:8000/media/mpd/x4ukwHdACDw.mpd" -p "basic"

"""
from __future__ import division
import read_mpd
#import urlparse
from urllib.parse import urlparse
from urllib.parse import urljoin
import urllib
import urllib.error
import urllib.request
import random
import os
import sys
import errno
import timeit
import http.client
from string import ascii_letters, digits
from argparse import ArgumentParser
from multiprocessing import Process, Queue
from collections import defaultdict
from adaptation import basic_dash, basic_dash2, weighted_dash, netflix_dash
from adaptation.adaptation import WeightedMean
import config_dash
import dash_buffer
from configure_log_file import configure_log_file, write_json
import time
import re
import threading
'''
try:
    WindowsError
except NameError:
    from shutil import WindowsError
'''

# Constants
DEFAULT_PLAYBACK = 'BASIC'
DOWNLOAD_CHUNK = 1024

# Globals for arg parser with the default values
# Not sure if this is the correct way ....
MPD = None
LIST = False 
PLAYBACK = DEFAULT_PLAYBACK
DOWNLOAD = False
SEGMENT_LIMIT = None


dir_path='coaster_10x10/'


class DashPlayback:
    """
    Audio[bandwidth] : {duration, url_list}
    Video[bandwidth] : {duration, url_list}
    """
    def __init__(self):

        self.min_buffer_time = None
        self.playback_duration = None
        self.audio = dict()
        self.video = dict()


def get_mpd(url):
    """ Module to download the MPD from the URL and save it to file"""
    print (url)
    try:
        connection = urllib.request.urlopen(url, timeout=10)
    except (urllib.error.HTTPError, error):
        config_dash.LOG.error("Unable to download MPD file HTTP Error: %s" % error.code)
        return None
    except urllib.error.URLError:
        error_message = "URLError. Unable to reach Server.Check if Server active"
        config_dash.LOG.error(error_message)
        print (error_message)
        return None
    except (IOError, http.client.HTTPException):
        message = "Unable to , file_identifierdownload MPD file HTTP Error."
        config_dash.LOG.error(message)
        return None
    
    mpd_data = connection.read()
    connection.close()
    mpd_file = url.split('/')[-1]
    mpd_file_handle = open(mpd_file, 'w')
    mpd_file_handle.write(mpd_data.decode('utf-8'))
    mpd_file_handle.close()
    config_dash.LOG.info("Downloaded the MPD file {}".format(mpd_file))
    return mpd_file


def get_bandwidth(data, duration):
    """ Module to determine the bandwidth for a segment
    download"""
    return data * 8/duration


def get_domain_name(url):
    """ Module to obtain the domain name from the URL
        From : http://stackoverflow.com/questions/9626535/get-domain-name-from-url
    """
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
     #Jerry
    return domain


def id_generator(id_size=6):
    """ Module to create a random string with uppercase 
        and digits.
    """
    return 'TEMP_' + ''.join(random.choice(ascii_letters+digits) for _ in range(id_size))


def download_segment(segment_url, dash_folder, segment_size):
    """ Module to download the segment """
    try:
        
        quic_file = open("./quic_file.txt","a")
        for url in segment_url:
            # url_new=str(url).replace("140.114.77.125","www.example.org")
            quic_file.write(str(url)+"\n") # url_new
        quic_file.close()
        
        '''
        ## for request quic server
        quic_file = open("/home/jerry/Desktop/for_quic/quic.txt","a")
        for num in range(0,len(segment_url)):
            url = str(segment_url[num])
            # url_new=str(url).replace("140.114.77.125/coaster_10x10","www.example.org")
            # url_new=url_new.replace("http","https")
            quic_file.write(url+"\n") # url_new
        quic_file.close()        
        ##
        '''
        s_size = sum(segment_size)
        return s_size,segment_url[0]

        # connection = urllib.request.urlopen(segment_url) #Jerry
        
    except urllib.error.HTTPError as error: #Jerry
        config_dash.LOG.error("Unable to download DASH Segment {} HTTP Error:{} ".format(segment_url, str(error.code)))
        return None
    
    parsed_uri = urlparse(segment_url)
    segment_path = '{uri.path}'.format(uri=parsed_uri)
    while segment_path.startswith('/'):
        segment_path = segment_path[1:]        
    segment_filename = os.path.join(dash_folder, os.path.basename(segment_path))
    make_sure_path_exists(os.path.dirname(segment_filename))
    segment_file_handle = open(segment_filename, 'wb')
    segment_size = 0
    while True:
        segment_data = connection.read(DOWNLOAD_CHUNK)
        segment_size += len(segment_data)
        segment_file_handle.write(segment_data)
        if len(segment_data) < DOWNLOAD_CHUNK:
            break
    connection.close()
    segment_file_handle.close()
    #print "segment size = {}".format(segment_size)
    #print "segment filename = {}".format(segment_filename)
    return segment_size, segment_filename


def get_media_all(domain, media_info, file_identifier, done_queue):
    """ Download the media from the list of URL's in media
    """
    bandwidth, media_dict = media_info
    media = media_dict[bandwidth]
    media_start_time = timeit.default_timer()
    for segment in [media.initialization] + media.url_list:
        start_time = timeit.default_timer()
        segment_url = urljoin(domain, segment)
        _, segment_file = download_segment(segment_url, file_identifier)
        elapsed = timeit.default_timer() - start_time
        if segment_file:
            done_queue.put((bandwidth, segment_url, elapsed))
    media_download_time = timeit.default_timer() - media_start_time
    done_queue.put((bandwidth, 'STOP', media_download_time))
    return None


def make_sure_path_exists(path):
    """ Module to make sure the path exists if not create it
    """
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def print_representations(dp_object):
    """ Module to print the representations"""
    print( "The DASH media has the following video representations/bitrates")
    for bandwidth in dp_object.video:
        print (bandwidth)

def download_patch_segment(segment_url):
    """ Module to download the segment """
    try:
        
        quic_file = open("./quic_patch_file.txt","w")
        for url in segment_url:
            # url_new=str(url).replace("140.114.77.125","www.example.org")
            quic_file.write(str(url)+"\n")
        quic_file.close()
        
        '''
        ## for request quic server
        quic_file = open("/home/jerry/Desktop/for_quic/quic_patch.txt","a")
        for num in range(0,len(segment_url)):
            url = str(segment_url[num])
            # url_new=str(url).replace("140.114.77.125/coaster_10x10","www.example.org")
            # url_new=url_new.replace("http","https")
            quic_file.write(url+"\n")
        quic_file.close()        
        ##
        '''
        # s_size = sum(segment_size)
        # return s_size,segment_url[0]

        # connection = urllib.request.urlopen(segment_url) #Jerry
        
    except urllib.error.HTTPError as error: #Jerry
        config_dash.LOG.error("Unable to download DASH Segment {} HTTP Error:{} ".format(segment_url, str(error.code)))
        return None
        
    

def get_patch_tile(player,media_list,patch_dict):
    
    '''
    patch_file_name = "compare_tile/coaster_10x10_user07_segtile_1_02"
    patch_tiles = open(patch_file_name)
    patch_original = patch_tiles.read().splitlines()
    patch_split = [line.split(",") for line in patch_original]
    patch_key = [float(i.split(",")[0].split("_")[0]) for i in patch_original]
    patch_segment = [int(i.split(",")[0].split("_")[1]) for i in patch_original]
    #print(patch_key)
    #print(patch_segment)
    patch_dict = dict()

    for i in range(0,len(patch_key)):
        patch_dict[patch_key[i]]=list()
        patch_dict[patch_key[i]].append(patch_segment[i])
        for j in range(1,len(patch_split[i])):
            patch_dict[patch_key[i]].append(patch_split[i][j])
    '''
    
    global bitrate_for_patch
    period = 0.2
    next_period = 0.2
    while True:
        play_time = float(player.playback_timer.time_float())
        if play_time>= 59.8:
            break
        # print(player.playback_timer.time_float())
        # play_time = round(float(player.playback_timer.time_float()),6)
        if play_time >= next_period :
            p_time = float(round(play_time,1))
            patch_url=media_list[patch_dict[p_time][0]][bitrate_for_patch] ## float(round(play_time,1)
            if len(patch_dict[p_time]) != 1:
                patch_tile_url = []
                # f.write(str(p_time)+"  ,bitrate: "+str(bitrate_for_patch))
                # f.write("\n")
                for k in range(1,len(patch_dict[p_time])):
                    patch_tile_url.append(patch_url[int(patch_dict[p_time][k])-1])
                    # f.write(str(patch_url[int(patch_dict[p_time][k])-1]))
                    # f.write("\n")
                # patch_tile_url = ["http://140.114.77.125/coaster_10x10/"+str(f) for f in patch_tile_url]
                download_patch_segment(patch_tile_url)
            # f.write(str(round(play_time,1))+"  ,bitrate: "+str(bitrate_for_patch))
            
            next_period += period
    # f.close()
    
    
        
        
def start_playback_smart(dp_object, domain, playback_type=None, download=False, video_segment_duration=None):
    """ Module that downloads the MPD-FIle and download
        all the representations of the Module to download
        the MPEG-DASH media.
        Example: start_playback_smart(dp_object, domain, "SMART", DOWNLOAD, video_segment_duration)

        :param dp_object:       The DASH-playback object
        :param domain:          The domain name of the server (The segment URLS are domain + relative_address)
        :param playback_type:   The type of playback
                                1. 'BASIC' - The basic adapataion scheme
                                2. 'SARA' - Segment Aware Rate Adaptation
                                3. 'NETFLIX' - Buffer based adaptation used by Netflix
        :param download: Set to True if the segments are to be stored locally (Boolean). Default False
        :param video_segment_duration: Playback duratoin of each segment
        :return:
    """
    # Initialize the DASH buffer
    dash_player = dash_buffer.DashPlayer(dp_object.playback_duration, video_segment_duration)
    dash_player.start()
    # A folder to save the segments in
    file_identifier = id_generator()
    config_dash.LOG.info("The segments are stored in %s" % file_identifier)
    dp_list = defaultdict(defaultdict)
    # Creating a Dictionary of all that has the URLs for each segment and different bitrates
    dp_size = defaultdict(defaultdict) # Jerry for segment size
    
    

    
    
    for bitrate in dp_object.video:
        # Getting the URL list for each bitrate
        dp_object.video[bitrate] = read_mpd.get_url_list(dp_object.video[bitrate], video_segment_duration,
                                                         dp_object.playback_duration, bitrate)
                                                         
        
        # if "$Bandwidth$" in dp_object.video[bitrate].initialization:
        #     dp_object.video[bitrate].initialization = dp_object.video[bitrate].initialization.replace(
        #         "$Bandwidth$", str(bitrate))
        # media_urls = [dp_object.video[bitrate].initialization] + dp_object.video[bitrate].url_list
        media_urls = dp_object.video[bitrate].url_list
        media_size = dp_object.video[bitrate].url_size

        
        #print "media urls"
        #print media_urls
        # for segment_count, segment_url in enumerate(media_urls, dp_object.video[bitrate].start):
        
        for segment_count in range(1,int(dp_object.playback_duration/video_segment_duration)+1):
            segment_url=[]
            segment_size=[]
            for track in range(0,len(media_urls)): # track numbers
                add_domain = "https://www.example.org/"+str(media_urls[track][segment_count-1])
                segment_url.append(add_domain) #media_urls[track][segment_count-1]
                segment_size.append(media_size[track][segment_count-1])
            dp_list[segment_count][bitrate] = segment_url # segment_url = track_1_x~track_200_x  a segment_url represent a segment with # of track
            dp_size[segment_count][bitrate] = segment_size

            
            
    bitrates = dp_object.video.keys() # ['high', 'medium', 'low']
    bitrates = list(bitrates) #Jerry
    bitrates.reverse() #['low','medium','high']

     
    average_dwn_time = 0
    segment_files = []
    # For basic adaptation
    previous_segment_times = []
    recent_download_sizes = []
    weighted_mean_object = None
    current_bitrate = bitrates[0]
    previous_bitrate = None
    total_downloaded = 0
    # Delay in terms of the number of segments
    delay = 0
    segment_duration = 0
    segment_size = segment_download_time = None
    # Netflix Variables
    average_segment_sizes = netflix_rate_map = None
    netflix_state = "INITIAL"
    # Start playback of all the segments
    global bitrate_for_patch
    bitrate_for_patch = current_bitrate
    
    
    patch_file_name = "compare_tile/coaster_10x10_user07_segtile_1_02"
    patch_tiles = open(patch_file_name)
    patch_original = patch_tiles.read().splitlines()
    patch_split = [line.split(",") for line in patch_original]
    patch_key = [float(i.split(",")[0].split("_")[0]) for i in patch_original]
    patch_segment = [int(i.split(",")[0].split("_")[1]) for i in patch_original]
    #print(patch_key)
    #print(patch_segment)
    patch_dict = dict()

    for i in range(0,len(patch_key)):
        patch_dict[patch_key[i]]=list()
        patch_dict[patch_key[i]].append(patch_segment[i])
        for j in range(1,len(patch_split[i])):
            patch_dict[patch_key[i]].append(patch_split[i][j])
    
    
    ## patch //Jerry 
    patch_thread = threading.Thread(target = get_patch_tile,args = (dash_player,dp_list,patch_dict,))
    patch_thread.start()    
    
    
    ## Read tiles that need to request //Jerry
    current_file_name = "compare_tile/coaster_10x10_user07_segtile_1"
    cur = open(current_file_name)
    cur_original = cur.read().splitlines()
    cur_predict = [re.split(', | |\n',line)[:-1] for line in cur_original]
    patch = dict()
    for line in cur_predict:
        segment_number = int(re.split('_| ',line[0])[-1]) # 1 ~ 60
        patch[segment_number]=list()
        for i in range(1,len(line)):
            if float(line[i])==1:
                patch[segment_number].append(i)
    ###
    
    
    for segment_number, segment in enumerate(dp_list, dp_object.video[current_bitrate].start):
        bitrate_for_patch = current_bitrate ## for patch
        
        config_dash.LOG.info(" {}: Processing the segment {}".format(playback_type.upper(), segment_number))
        write_json()
        if not previous_bitrate:
            previous_bitrate = current_bitrate
        if SEGMENT_LIMIT:
            if not dash_player.segment_limit:
                dash_player.segment_limit = int(SEGMENT_LIMIT)
            if segment_number > int(SEGMENT_LIMIT):
                config_dash.LOG.info("Segment limit reached")
                break
        print ("segment_number ={}".format(segment_number))
        # print ("dp_object.video[bitrate].start={}".format(dp_object.video[bitrate].start))
        if segment_number == dp_object.video[bitrate].start:
            current_bitrate = bitrates[0]
        else:
            if playback_type.upper() == "BASIC":
                current_bitrate, average_dwn_time = basic_dash2.basic_dash2(segment_number, bitrates, average_dwn_time,
                                                                            recent_download_sizes,
                                                                            previous_segment_times, current_bitrate)

                if dash_player.buffer.qsize() > config_dash.BASIC_THRESHOLD:
                    delay = dash_player.buffer.qsize() - config_dash.BASIC_THRESHOLD
                config_dash.LOG.info("Basic-DASH: Selected {} for the segment {}".format(current_bitrate,
                                                                                         segment_number + 1))
            elif playback_type.upper() == "SMART":
                if not weighted_mean_object:
                    weighted_mean_object = WeightedMean(config_dash.SARA_SAMPLE_COUNT)
                    config_dash.LOG.debug("Initializing the weighted Mean object")
                # Checking the segment number is in acceptable range
                if segment_number < len(dp_list) - 1 + dp_object.video[bitrate].start:
                    try:
                        current_bitrate, delay = weighted_dash.weighted_dash(bitrates, dash_player,
                                                                             weighted_mean_object.weighted_mean_rate,
                                                                             current_bitrate,
                                                                             get_segment_sizes(dp_object,
                                                                                               segment_number+1))
                    except (IndexError, e):
                        config_dash.LOG.error(e)

            elif playback_type.upper() == "NETFLIX":
                config_dash.LOG.info("Playback is NETFLIX")
                # Calculate the average segment sizes for each bitrate
                if not average_segment_sizes:
                    average_segment_sizes = get_average_segment_sizes(dp_object) # change get_average_segment_sizes
                if segment_number <= len(dp_list) - 1 + dp_object.video[bitrate].start: # Original < Jerry
                    try:
                        if segment_size and segment_download_time:
                            segment_download_rate = segment_size / segment_download_time
                        else:
                            segment_download_rate = 0
                        current_bitrate, netflix_rate_map, netflix_state = netflix_dash.netflix_dash(
                            bitrates, dash_player, segment_download_rate, current_bitrate, average_segment_sizes,
                            netflix_rate_map, netflix_state)
                        config_dash.LOG.info("NETFLIX: Next bitrate = {}".format(current_bitrate))
                    except IndexError as e:
                        config_dash.LOG.error(e)
                        return None
                else:
                    config_dash.LOG.critical("Completed segment playback for Netflix")
                    break

                # If the buffer is full wait till it gets empty
                if dash_player.buffer.qsize() >= config_dash.NETFLIX_BUFFER_SIZE:
                    delay = (dash_player.buffer.qsize() - config_dash.NETFLIX_BUFFER_SIZE + 1) * segment_duration
                    config_dash.LOG.info("NETFLIX: delay = {} seconds".format(delay))
            else:
                config_dash.LOG.error("Unknown playback type:{}. Continuing with basic playback".format(playback_type))
                current_bitrate, average_dwn_time = basic_dash.basic_dash(segment_number, bitrates, average_dwn_time,
                                                                          segment_download_time, current_bitrate)
        segment_path = dp_list[segment][current_bitrate]
        segment_size = dp_size[segment][current_bitrate]
        
        
        
        
        # segment_url = []
        # for seg_path in segment_path:
        #     req_url = domain+dir_path+seg_path
        #     segment_url.append(req_url)
        
        ## only get current predict
        regular_url = []
        regular_size = []
        for number in patch[segment]:
            regular_url.append(segment_path[int(number)-1]) #segment_url
            regular_size.append(segment_size[int(number)-1])
            
            
        # print(regular_url)
        # return None
        # segment_url = urljoin(domain, segment_path)
        
        # print(segment_url)
         
        #print "segment url"
        #print segment_url
        # config_dash.LOG.info("{}: Segment URL = {}".format(playback_type.upper(), segment_url)) //Jerry
        if delay:
            delay_start = time.time()
            config_dash.LOG.info("SLEEPING for {}seconds ".format(delay*segment_duration))
            while time.time() - delay_start < (delay * segment_duration):
                time.sleep(1)
            delay = 0
            config_dash.LOG.debug("SLEPT for {}seconds ".format(time.time() - delay_start))
            
            
        start_time = None
        try:
            while(1):
                if dash_player.do_request==True or segment<=config_dash.INITIAL_BUFFERING_COUNT:
                    dash_player.do_request = False
                    break
            start_time = timeit.default_timer()
            segment_size, segment_filename = download_segment(regular_url, file_identifier, regular_size)
             
            
            # config_dash.LOG.info("{}: Downloaded segment {}".format(playback_type.upper(), segment_url))
            
            # return None # Jerry
        
        except IOError as e: #Jerry
            config_dash.LOG.error("Unable to save segment %s" % e)
            return None
        
        '''
        ## for Server   
        tt = [name.split('/')[-1] for name in regular_url]    
        d_file_name=[]
        while not set(tt).issubset(set(d_file_name)) :
            d_file_name=[]
            d_regular = open("/home/jerry/Desktop/for_quic/log.txt")
            for i, line in enumerate(d_regular):
                d_file_name.append(line.rstrip('\n'))  
            d_regular.close()
        ###        
        '''
            
        segment_download_time = timeit.default_timer() - start_time
        previous_segment_times.append(segment_download_time)
        recent_download_sizes.append(segment_size)
        # Updating the JSON information
        # segment_name = os.path.split(segment_url)[1] # Original
        segment_name = segment_filename
        if "segment_info" not in config_dash.JSON_HANDLE:
            config_dash.JSON_HANDLE["segment_info"] = list()
        config_dash.JSON_HANDLE["segment_info"].append((segment_name, current_bitrate, segment_size,
                                                        segment_download_time))
        total_downloaded += segment_size
        config_dash.LOG.info("{} : The total downloaded = {}, segment_size = {}, segment_number = {}".format(
            playback_type.upper(),
            total_downloaded, segment_size, segment_number))
        if playback_type.upper() == "SMART" and weighted_mean_object:
            weighted_mean_object.update_weighted_mean(segment_size, segment_download_time)

        
        segment_info = {'playback_length': video_segment_duration,
                        'size': segment_size,
                        'bitrate': current_bitrate,
                        'data': segment_filename,
                        'URI': segment_url[0],
                        'segment_number': segment_number}
                        
        # print('-------------------------------')
        # print(segment_info)
        
        segment_duration = segment_info['playback_length']
        dash_player.write(segment_info)
        # print('------------------------+++++++:  '+str(dash_player.buffer.qsize()))
        
        segment_files.append(segment_filename)
        
        # config_dash.LOG.info("Downloaded %s. Size = %s in %s seconds" % (
        #     segment_url, segment_size, str(segment_download_time)))
        
        if previous_bitrate:
            if int(previous_bitrate) < int(current_bitrate):
                config_dash.JSON_HANDLE['playback_info']['up_shifts'] += 1
            elif int(previous_bitrate) > int(current_bitrate):
                config_dash.JSON_HANDLE['playback_info']['down_shifts'] += 1
            previous_bitrate = current_bitrate

    # waiting for the player to finish playing
    while dash_player.playback_state not in dash_buffer.EXIT_STATES:
        time.sleep(1)
        if dash_player.playback_timer.time()>= dp_object.playback_duration:
            #playback_state.playback_state="END"
            break

    write_json()
    patch_thread.join() #Jerry
    
    if not download:
        clean_files(file_identifier)


def get_segment_sizes(dp_object, segment_number):
    """ Module to get the segment sizes for the segment_number
    :param dp_object:
    :param segment_number:
    :return:
    """
    segment_sizes = dict([(bitrate, dp_object.video[bitrate].segment_sizes[segment_number]) for bitrate in dp_object.video])
    config_dash.LOG.debug("The segment sizes of {} are {}".format(segment_number, segment_sizes))
    return segment_sizes


def get_average_segment_sizes(dp_object):
    """
    Module to get the avearge segment sizes for each bitrate
    :param dp_object:
    :return: A dictionary of aveage segment sizes for each bitrate
    """
    average_segment_sizes = dict()
    for bitrate in dp_object.video:
        # segment_sizes = dp_object.video[bitrate].segment_sizes
        # segment_sizes = [float(i) for i in segment_sizes]
        segment_sizes = dp_object.video[bitrate].url_size
        segment_sizes = [float(sum(i)) for i in segment_sizes]
        try:
            average_segment_sizes[bitrate] = sum(segment_sizes)/len(segment_sizes)
        except ZeroDivisionError:
            average_segment_sizes[bitrate] = 0
    config_dash.LOG.info("The avearge segment size for is {}".format(average_segment_sizes.items()))
    return average_segment_sizes


def clean_files(folder_path):
    """
    :param folder_path: Local Folder to be deleted
    """
    if os.path.exists(folder_path):
        try:
            for video_file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, video_file)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            os.rmdir(folder_path)
        except e: #(WindowsError, OSError, e):
            config_dash.LOG.info("Unable to delete the folder {}. {}".format(folder_path, e))
        config_dash.LOG.info("Deleted the folder '{}' and its contents".format(folder_path))


def start_playback_all(dp_object, domain):
    """ Module that downloads the MPD-FIle and download all the representations of 
        the Module to download the MPEG-DASH media.
    """
    # audio_done_queue = Queue()
    video_done_queue = Queue()
    processes = []
    file_identifier = id_generator(6)
    config_dash.LOG.info("File Segments are in %s" % file_identifier)
    # for bitrate in dp_object.audio:
    #     # Get the list of URL's (relative location) for the audio
    #     dp_object.audio[bitrate] = read_mpd.get_url_list(bitrate, dp_object.audio[bitrate],
    #                                                      dp_object.playback_duration)
    #     # Create a new process to download the audio stream.
    #     # The domain + URL from the above list gives the
    #     # complete path
    #     # The fil-identifier is a random string used to
    #     # create  a temporary folder for current session
    #     # Audio-done queue is used to exchange information
    #     # between the process and the calling function.
    #     # 'STOP' is added to the queue to indicate the end
    #     # of the download of the sesson
    #     process = Process(target=get_media_all, args=(domain, (bitrate, dp_object.audio),
    #                                                   file_identifier, audio_done_queue))
    #     process.start()
    #     processes.append(process)

    for bitrate in dp_object.video:
        dp_object.video[bitrate] = read_mpd.get_url_list(bitrate, dp_object.video[bitrate],
                                                         dp_object.playback_duration,
                                                         dp_object.video[bitrate].segment_duration)
        # Same as download audio
        process = Process(target=get_media_all, args=(domain, (bitrate, dp_object.video),
                                                      file_identifier, video_done_queue))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()
    count = 0
    for queue_values in iter(video_done_queue.get, None):
        bitrate, status, elapsed = queue_values
        if status == 'STOP':
            config_dash.LOG.critical("Completed download of %s in %f " % (bitrate, elapsed))
            count += 1
            if count == len(dp_object.video):
                # If the download of all the videos is done the stop the
                config_dash.LOG.critical("Finished download of all video segments")
                break


def create_arguments(parser):
    """ Adding arguments to the parser """
    parser.add_argument('-m', '--MPD',                   
                        help="Url to the MPD File")
    parser.add_argument('-l', '--LIST', action='store_true',
                        help="List all the representations")
    parser.add_argument('-p', '--PLAYBACK',
                        default=DEFAULT_PLAYBACK,
                        help="Playback type (basic, sara, netflix, or all)")
    parser.add_argument('-n', '--SEGMENT_LIMIT',
                        default=SEGMENT_LIMIT,
                        help="The Segment number limit")
    parser.add_argument('-d', '--DOWNLOAD', action='store_true',
                        default=False,
                        help="Keep the video files after playback")


def main():
    """ Main Program wrapper """
    # configure the log file
    # Create arguments
    parser = ArgumentParser(description='Process Client parameters')
    create_arguments(parser)
    args = parser.parse_args()
    globals().update(vars(args))
    configure_log_file(playback_type=PLAYBACK.lower())
    config_dash.JSON_HANDLE['playback_type'] = PLAYBACK.lower()
    if not MPD:
        print ("ERROR: Please provide the URL to the MPD file. Try Again..")
        return None
    config_dash.LOG.info('Downloading MPD file %s' % MPD)
    # Retrieve the MPD files for the video
    mpd_file = get_mpd(MPD) # return MPD file name
    domain = get_domain_name(MPD)
    dp_object = DashPlayback()
    # Reading the MPD file created
    

    
    print('file: '+mpd_file)
    
    # read_mpd.read_mpd(mpd_file, dp_object) # just test
    # return None
    
    dp_object, video_segment_duration = read_mpd.read_mpd(mpd_file, dp_object,3) # 3 high  2 medium   1 low
    dp2 = DashPlayback()
    dp3 = DashPlayback()
    dp2, video_segment_duration = read_mpd.read_mpd('dash_coaster_10x10_qp32_new.mpd', dp2,'2')
    dp3, video_segment_duration = read_mpd.read_mpd('dash_coaster_10x10_qp36_new.mpd', dp3,'1')
    
    dp_object.video['2'] = dp2.video['2']
    dp_object.video['1']=dp3.video['1']
    
    config_dash.LOG.info("The DASH media has %d video representations" % len(dp_object.video))
    
    global now_play_time  # Jerry
    
    if LIST:
        # Print the representations and EXIT
        print_representations(dp_object)
        return None
    if "all" in PLAYBACK.lower():
        if mpd_file:
            config_dash.LOG.critical("Start ALL Parallel PLayback")
            start_playback_all(dp_object, domain)
    elif "basic" in PLAYBACK.lower():
        config_dash.LOG.critical("Started Basic-DASH Playback")
        start_playback_smart(dp_object, domain, "BASIC", DOWNLOAD, video_segment_duration)
    elif "sara" in PLAYBACK.lower():
        config_dash.LOG.critical("Started SARA-DASH Playback")
        start_playback_smart(dp_object, domain, "SMART", DOWNLOAD, video_segment_duration)
    elif "netflix" in PLAYBACK.lower():
        config_dash.LOG.critical("Started Netflix-DASH Playback")
        start_playback_smart(dp_object, domain, "NETFLIX", DOWNLOAD, video_segment_duration)
    else:
        config_dash.LOG.error("Unknown Playback parameter {}".format(PLAYBACK))
        return None
    # 
if __name__ == "__main__":
    sys.exit(main())
