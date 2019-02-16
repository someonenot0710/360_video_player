#python dist/client/dash_client.py -m http://140.114.77.125/coaster_10x10/dash_coaster_10x10_qp28_new.mpd -p 'basic'
rm experiment/*

#python dist/client/dash_client.py -m http://140.114.77.125/mpd_with_size/dash_coaster_10x10_qp28_new.mpd -p 'netflix' -u 30 -s l

#dash_diving_10x10_qp28_new.mpd

#python dist/client/dash_client.py -m http://140.114.77.125/mpd_with_size/dash_diving_10x10_qp28_new.mpd -p 'netflix' -u 20 -s l

finish='false'

while [ $finish == 'false' ]
do
rm experiment/*
finish='true'
gtimeout 70s python dist/client/dash_client.py -m http://140.114.77.125/mpd_with_size/dash_drive_10x10_qp28_new.mpd -p 'netflix' -u 35 -s l || finish='false'
done

echo "finish video"
