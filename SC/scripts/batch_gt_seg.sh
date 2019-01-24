videos=(coaster coaster2 diving drive game landscape pacman panel ride sport)
tw=(10 10 5)
th=(10 5 5)
for v in ${videos[@]}; do
    for t in $(seq 0 2); do
        for u in $(seq 1 50); do
            python2.7 gen_gt_seg.py ../gt/${v}_user$(printf %02d $u)_tile.csv ${tw[$t]} ${th[$t]} 1 ../gt_frame/${v}_${tw[$t]}x${th[$t]}_user$(printf %02d $u)_segtile
        done
    done
done
