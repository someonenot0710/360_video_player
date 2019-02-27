#python dist/client/dash_client.py -m http://140.114.77.125/coaster_10x10/dash_coaster_10x10_qp28_new.mpd -p 'basic'
#rm -r experiment/*

#python dist/client/dash_client.py -m http://140.114.77.125/mpd_with_size/dash_coaster_10x10_qp28_new.mpd -p 'netflix' -u 30 -s l

#dash_diving_10x10_qp28_new.mpd


## original
#python3 dist/client/dash_client.py -m http://140.114.77.125/mpd_with_size/dash_diving_10x10_qp28_new.mpd -p 'netflix' -u $1 -s s -pro q -urgent y -comp n


# video , user
python3 dist/client/dash_client.py -m http://140.114.77.125/mpd_server/dash_$1_10x10_qp28_new.mpd -p 'netflix' -u $2 -s s -pro q -urgent y -comp n










#python3 dist/client/dash_client.py -m http://140.114.77.125/mpd_with_size/dash_diving_10x10_qp28_new.mpd -p 'netflix' -u 30 -s s -pro h2 -urgent n -comp y


#finish='false'
#while [ $finish == 'false' ]
#do
#rm experiment/*
#finish='true'
#gtimeout 70s python dist/client/dash_client.py -m http://140.114.77.125/mpd_with_size/dash_drive_10x10_qp28_new.mpd -p 'netflix' -u 35 -s l || finish='false'
#done

#echo "finish video"

