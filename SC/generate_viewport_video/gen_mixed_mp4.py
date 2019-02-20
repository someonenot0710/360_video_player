import sys
import os

video=sys.argv[1]
#f=open(sys.argv[2],'r') # the target mixed-quality video
seglen=30
outmp4=sys.argv[2]
mixed_outmp4=sys.argv[3]
#seg_dir='/data3/yibin/tmm/videos/'
seg_dir = "/home/jerry/video_10x10/"+video+"_black/"
#black_dir = "/home/jerry/Desktop/black_video/"
segnum=58
s=0
#his=[0 for i in range(200)]
#lines=f.readlines()

all_url=[]
f1 = open("./user30_q_no/diving/quic.txt") ## get quic.txt
f1_file = f1.read().splitlines()
for line in f1_file:
    name = line.split("/")[-1]
    all_url.append(name)

f2 = open("./user30_q/diving/patch_arrive_url.txt") # get patch_arrive_url.txt
f2_file = f2.read().splitlines()
record=[]
for line in f2_file:
    name = line.split("/")[-1]
    all_url.append(name)


for s in range(segnum):
    print("seg: %d"%(s+3))
#    all_cmd = ""
    # init file
#    cmd='cat '+seg_dir+'dash_%s_10x10_qp28_set1_init.mp4 > %s_%d.mp4'%(video,outmp4,s+3)
    cmd = 'cat '+seg_dir+'%s_set1_init.mp4 > %s_%d.mp4'%(video,outmp4,s+3)
#    all_cmd +='cat '+seg_dir+'dash_%s_10x10_qp28_set1_init.mp4'%(video)
    os.system(cmd)
#    cmd='cat '+black_dir+'black_set1_init.mp4 >> %s_%d.mp4'%(outmp4, s+3)
#    os.system(cmd)
	# init files again (track1)
    cmd='cat '+seg_dir+'%s_10x10_qp36_tile_dash_track%d_%d.m4s >> %s_%d.mp4'%(video, 1, s+3, outmp4, s+3)
#    all_cmd += ' '+seg_dir+'%s_10x10_qp28_tile_dash_track%d_%d.m4s'%(video, 1, s+3)
#    all_cmd += ' '+seg_dir+'%s_10x10_qp28_tile_dash_track%d_%d.m4s'%(video, 2, s+3)
    os.system(cmd)
    for t in range(1,101):
        
        this = ""         
        sub = "k"+str(t+1)+"_"+str(s+3)+"."
        # concat selected m4s files (tile)
        for line in all_url:
            if sub in line:
                this = line
                break
        
        if this != "":
            cmd ='cat '+seg_dir+this+' >>  %s_%d.mp4'%(outmp4,s+3)
#            all_cmd += ' '+seg_dir+'%s_10x10_qp28_tile_dash_track%d_%d.m4s'%(video, t+1, s+3)
#            all_cmd += ' '+seg_dir+this       
        
        else:
#            cmd='cat '+black_dir+'%s_dash_track%d_init.mp4 >> %s_%d.mp4'%('black', t+1, outmp4, s+3)
#            if cmd not in record:
#                os.system(cmd)
#                record.append(cmd)
        
#            cmd='cat '+seg_dir+'%s_10x10_qp36_tile_dash_track%d_%d.m4s >> %s_%d.mp4'%(video, t+1, s+3, outmp4, s+3) 
#            print("black")
            cmd='cat '+seg_dir+'%s_dash_track%d_%d.m4s >> %s_%d.mp4'%('black', t+1, s+3, outmp4, s+3) 
#            cmd='cat '+black_dir+'%s_dash_track%d_%d.m4s >> %s_%d.mp4'%('black', t+1, s+3, outmp4, s+3)           
        os.system(cmd)
#    all_cmd += ' >>  %s_%d.mp4'%(outmp4,s+3)
#    os.system(all_cmd)
    cmd='MP4Box -raw 1 %s_%d.mp4'%(outmp4,s+3)
    os.system(cmd)
    # generate mixed-quality tiled mp4
 #   cmd='MP4Box -add %s_%d_track1.hvc:split_tiles -new %s_%d.mp4'%(outmp4, s+3, mixed_outmp4, s+3)
#    os.system(cmd)
    cmd='MP4Box -add %s_%d_track1.hvc:fps=30 -inter 0 -new %s_%d.mp4'%(outmp4, s+3, mixed_outmp4, s+3)
    os.system(cmd)

