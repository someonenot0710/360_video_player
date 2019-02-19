#videos=(coaster2 game sport)
#users=(14 20 38)
#videos=(coaster2 game sport sport game)
#users=(14 20 38 19 29)
#for u in $(seq 0 0); do
#    rm mixed_videos/mixed_20x10_${videos[$u]}_user$(printf %02d ${users[$u]})_0.053_pred.mp4 
cmd=""
for j in $(seq 3 60); do
    cmd="$cmd -cat mixed_videos/f_$(printf %d $j).mp4"
#        cmd="$cmd -unalign-cat mixed_videos/mixed_${videos[$u]}_user$(printf %02d ${users[$u]})_0.053_pred_$(printf %d $j).mp4"
done
echo $cmd
MP4Box $cmd -inter 0 mixed_videos/mixed.mp4
#done
