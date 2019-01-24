SC 2019/01/18

directories:
gt/ # ground truth in frame level
gt_seg/ # ground truth in segment level (generated from gt/ using batch_gt_seg.sh and required by cur prediction) 
sensors/ # sensor data in frame level (required by dr prediction)

scripts:
$ bash compile_calprob.sh # compile cal_prob.pyx (required by dr prediction)
$ bash batch_gt_seg.sh # gen ground truth tiles in segment level
$ python2.7 cur_predict_seg.py gt_seg/[gt seg file] [t seg] [output] # output cur's prediction for t segments later
$ python2.7 dr_predict_sec.py sensors/[sensor file] [tile_w] [tile_h] [t sec] [output] # output dr's prediction every t seconds
