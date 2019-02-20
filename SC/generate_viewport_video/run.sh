ffmpeg -i black_origin.mp4 -f rawvideo -pix_fmt yuv420p black.yuv
ffmpeg -i diving_equir.mp4 -f rawvideo -pix_fmt yuv420p diving.yuv
kvazaar -i diving.yuv --input-res=3840x1920 --input-fps 30.0 --bitrate 15200000 -p 30 --gop 0 --mv-constraint frametile --tiles 10x10 --slices tiles -o diving_10x10_qp28_tile.hvc
kvazaar -i diving.yuv --input-res=3840x1920 --input-fps 30.0 --bitrate 10133333 -p 30 --gop 0 --mv-constraint frametile --tiles 10x10 --slices tiles -o diving_10x10_qp32_tile.hvc
kvazaar -i diving.yuv --input-res=3840x1920 --input-fps 30.0 --bitrate 5066666 -p 30 --gop 0 --mv-constraint frametile --tiles 10x10 --slices tiles -o diving_10x10_qp36_tile.hvc
kvazaar -i black.yuv --input-res=3840x1920 --input-fps 30.0 --bitrate 5066666 -p 30 --gop 0 --mv-constraint frametile --tiles 10x10 --slices tiles -o black.hvc
MP4Box -add black.hvc:split_tiles -new black.mp4
MP4Box -add diving_10x10_qp28_tile.hvc:split_tiles -new diving_10x10_qp28_tile.mp4
MP4Box -add diving_10x10_qp32_tile.hvc:split_tiles -new diving_10x10_qp32_tile.mp4
MP4Box -add diving_10x10_qp36_tile.hvc:split_tiles -new diving_10x10_qp36_tile.mp4
MP4Box -dash 1000 -profile live -out diving.mpd diving_10x10_qp36_tile.mp4 diving_10x10_qp32_tile.mp4 diving_10x10_qp28_tile.mp4 black.mp4

