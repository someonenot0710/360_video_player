rm -r mixed_videos
mkdir mixed_videos
python gen_mixed_mp4.py diving mixed_videos/t mixed_videos/f
bash concat2_m.sh
