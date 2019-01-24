import sys
import math

f=open(sys.argv[1],'r') # ground truth
tilew=20
tileh=10
tile_num=tilew*tileh
otilew=int(sys.argv[2]) # output tile in width
otileh=int(sys.argv[3]) # output tile in height
total_frames=1800
seglen=int(sys.argv[4]) # fps
fo=open(sys.argv[5],'w')
segnum=int(float(total_frames)/float(seglen))
out_tilenum=otilew*otileh
lines=f.readlines()[1:]
tiles=[[0.0 for i in range(tile_num)] for j in range(total_frames)]
fidx=0
for line in lines:
    arr=line.strip().split(',')
    for i in range(len(arr)-1):
        tiles[fidx][int(arr[i+1])-1]=1
    fidx=fidx+1

tile_seg=[[0.0 for i in range(tile_num)] for j in range(segnum)]
for i in range(segnum):
    for j in range(tile_num):
        for k in range(seglen):
            tile_seg[i][j]=tile_seg[i][j]+tiles[i*seglen+k][j]
out_tile=[[0.0 for i in range(out_tilenum)] for j in range(segnum)]
fw=int(float(tilew)/float(otilew))
fh=int(float(tileh)/float(otileh))
for i in range(segnum):
    for j in range(tileh):
        for k in range(tilew):
            if tile_seg[i][j*tilew+k]>0.0:
                ow=int(math.floor(float(k)/float(fw)))
                oh=int(math.floor(float(j)/float(fh)))
                out_tile[i][oh*otilew+ow]=1
#                print j*tilew+k,oh*otilew+ow
for i in range(segnum):
    fo.write('seg%03d, '%(i+1))
    for j in range(otileh):
        for k in range(otilew):
            fo.write(str(out_tile[i][j*otilew+k])+" ")
    fo.write('\n')
fo.close()




