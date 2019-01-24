import sys
import math

f=open(sys.argv[1],'r') # ground truth in segment level
#tilew=int(sys.argv[2]) # tile in width
#tileh=int(sys.argv[3]) # tile in height
#segnum=int(sys.argv[4]) # fps
t=int(sys.argv[2]) # predict the viewed tiles after t seconds
fo=open(sys.argv[3],'w')

tiles=[]
for line in f:
    tile=[]
    arr=line.strip().split(',')
    arr2=arr[1].split()
    for i in range(len(arr2)):
        tile.append(float(arr2[i]))
    tiles.append(tile)

segnum=len(tiles)
tilenum=len(tiles[0])
print segnum, tilenum
for i in range(t):
    fo.write('gt_seg_%03d, '%(i+1))
    for j in range(tilenum):
        fo.write(str(tiles[i][j])+" ")
    fo.write("\n")
for i in range(segnum-t):
    fo.write('pred_seg %03d_%03d, '%(i+1,i+t+1))
    for j in range(tilenum):
        fo.write(str(tiles[i][j])+" ")
    fo.write('\n')
    


