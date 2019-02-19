#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* curl stuff */
#include <curl/curl.h>
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <fstream>
using namespace std;

#define TIMETYPE curl_off_t
//#define PROTO CURL_HTTP_VERSION_2_0
#define PROTO CURL_HTTP_VERSION_1_1

vector<CURL *> row;
vector<string> url_set;

/*
size_t write_data(void *buffer, size_t size, size_t nmemb, void *userp)
{
   return size * nmemb;
}

*/
static size_t write_data(void *ptr, size_t size, size_t nmemb, void *stream)
{
//  size_t written = fwrite(ptr, size, nmemb, (FILE *)stream);
//  return written;
//   cout<<"??"<<endl;
   return size * nmemb;
}


struct myprogress {
  TIMETYPE lastruntime;
  CURL *curl;
//  string url;
};




int progress_func(void* ptr, double TotalToDownload, double NowDownloaded, double TotalToUpload, double NowUploaded)
{




    CURL *curl = (CURL*) ptr;
    char *url = NULL;
    curl_easy_getinfo(curl, CURLINFO_EFFECTIVE_URL, &url);

//    if(url)
//    printf("%s\n", url);

//    printf("now: %f , total: %f\n", NowDownloaded,TotalToDownload);
    return 0;

    // It's here you will write the code for the progress message or bar
}


int main(){
  //check nghttp2 supprt
  const curl_version_info_data *data = curl_version_info(CURLVERSION_NOW);
  if(data->features & CURL_VERSION_HTTP2){
    printf("This libcurl DOES have HTTP2 support!\n");
  } else {
    printf("This libcurl does NOT have HTTP/2 support!\n");
  }

  // Create multi handle with multiplex over a single connection
  CURLM *multi_handle = curl_multi_init();
  curl_multi_setopt(multi_handle, CURLMOPT_MAX_HOST_CONNECTIONS, (long) 1L);
  curl_multi_setopt(multi_handle, CURLMOPT_PIPELINING, CURLPIPE_MULTIPLEX);

  //perform requests
  // https://nosl15.cs.nthu.edu.tw/files/api/download/coaster_10x10_qp28_tile_dash_track56_2.m4s
  int still_running = 0;
  CURLMsg *msg; /* for picking up messages with the transfer status */
  int msgs_left; /* how many messages are left */
  // curl_multi_perform(multi_handle, &still_running);
  int current_number=1;
  int last_number=1;
  string file_name;
  int count=0;
//  while(still_running){
    string check_dir = ("/home/jerry/Desktop/for_quic/quic.txt");
    while(1){
    curl_multi_perform(multi_handle, &still_running);

    std::ifstream inFile(check_dir);
    current_number=std::count(std::istreambuf_iterator<char>(inFile),
             std::istreambuf_iterator<char>(), '\n');
    inFile.close();

    if (current_number != last_number && current_number!=0){
      std::ifstream inFile(check_dir);
      for (int lineno = 0; lineno < current_number; lineno++){
        getline (inFile,file_name);
        if ((lineno >= last_number)||(lineno>= last_number-1 && last_number==1 )){
            CURL *tmp;
            tmp = curl_easy_init();
            curl_easy_setopt(tmp, CURLOPT_VERBOSE, 0L);
            curl_easy_setopt(tmp, CURLOPT_URL,file_name.c_str());
            curl_easy_setopt(tmp, CURLOPT_HTTP_VERSION, PROTO);//CURL_HTTP_VERSION_2_0);
            curl_easy_setopt(tmp, CURLOPT_WRITEFUNCTION, write_data);
            row.push_back(tmp);
            url_set.push_back(file_name);
            curl_multi_add_handle(multi_handle, tmp);
          }
      }
    last_number = current_number;
    }

    // cancel request
    // if (count==100000){
    // printf("count:%d\n",count);
    // curl_multi_remove_handle(multi_handle,row[1]);
    // }

    while((msg = curl_multi_info_read(multi_handle, &msgs_left))) {
    if(msg->msg == CURLMSG_DONE) {
      int idx, found = 0;
      /* Find out which handle this message is about */
      for(idx = 0; idx<row.size(); idx++) {
        found = (msg->easy_handle == row[idx]);
        if(found)
          break;
      }
     string str2 ("/");
     string str3 (".m4s");
     string str4 ("_"); 
     size_t found1 = url_set[idx].find_last_of(str2);
     size_t found3 = url_set[idx].find_last_of(str4);
     size_t found2 = url_set[idx].find(str3);
     std::string f = url_set[idx].substr(found3+1,found2-found3-1);
     string name = url_set[idx].substr(found1+1,found2-found1+4);
//     cout<<name<<endl;
     string dir = ("/home/jerry/Desktop/for_quic/");
     fstream log2;
     log2.open(dir+f,fstream::app);
     if (log2.is_open()){
     log2 <<name<<"\n";
     log2.close();
     }
//     cout<<f<<endl;
     
//     cout<<url_set[idx]<<endl;//" is done "<<msg->data.result<<endl;
    }
  }
}

  //cleanups
  for(int i = 0; i < row.size(); i++)
    curl_easy_cleanup(row[i]);
    curl_multi_cleanup(multi_handle);
    exit(0);
}
