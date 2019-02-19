# this script used to generate black video 
# remember to execute the script under empty folder
# need to have ffmpeg kvazaar MP4Box
ffmpeg -t 60 -f lavfi -i color=c=black:s=3840x1920 -c:v libx264 -tune stillimage -pix_fmt yuv420p -r 30 black.mp4
ffmpeg -i black.mp4 -f rawvideo -pix_fmt yuv420p black.yuv
mv black.mp4 black_origin.mp4
kvazaar -i black.yuv --input-res=3840x1920 --input-fps 30.0 --qp 28 -p 30 --gop 0 --mv-constraint frametile --tiles 10x10 --slices tiles -o black.hvc
MP4Box -add black.hvc:split_tiles -new black.mp4
MP4Box -dash 1000 -profile live -out black.mpd black.mp4
