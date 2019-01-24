import numpy as np
from scipy.signal import butter, lfilter, freqz
#import matplotlib.pyplot as plt
import sys
from cal_prob import gen_prob
# 1: video, 2: fov_degree, 3: tile_num, 4: us, 5: ut
#gentile(int(sys.argv[5]), int(sys.argv[6]), sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]))


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y


# Filter requirements.
#order = 6
order = 6
fs = 30.0       # sample rate, Hz
cutoff = 3.667  # desired cutoff frequency of the filter, Hz
#cutoff = 9

# Data
f=open(sys.argv[1],"r") # sensor file
tilew=int(sys.argv[2]) # 20
tileh=int(sys.argv[3]) # 10
seglen=30 # 30
total_frames=1800
segnum=int(float(total_frames)/float(seglen)) # 60
window=float(sys.argv[4]) # previous time window for moving averagei # 30
interval=float(sys.argv[4]) # prediction interval
#t=float(sys.argv[6]) # predict t seconds later
frame_interval=int(float(seglen)*interval) # interval in frame level
frame_w=int(float(seglen)*window) # window in frame level
out=open(sys.argv[5],"w")
#t=int(sys.argv[5]) # interval 2 4 8
lines=f.readlines()[1:]
roll=[]
yaw=[]
pitch=[]
#prev=int(sys.argv[2])
#alpha=float(sys.argv[2])
alpha=0.10

# Get the filter coefficients so we can check its frequency response.
b, a = butter_lowpass(cutoff, fs, order)

for line in lines:
    arr=line.strip().split(',')
    yaw.append(float(arr[7]))
    pitch.append(float(arr[8]))
    roll.append(float(arr[9]))

# Demonstrate the use of the filter.
# First make some data to be filtered.
T = 60.0         # seconds
n = int(T * fs) # total number of samples
n2= int(T / interval)
#n = total_frames
t = np.linspace(0, total_frames, n, endpoint=False)
t2= np.linspace(0, total_frames, n2, endpoint=False)
# "Noisy" data.  We want to recover the 1.2 Hz signal from this.
#data = np.sin(1.2*2*np.pi*t) + 1.5*np.cos(9*2*np.pi*t) + 0.5*np.sin(12.0*2*np.pi*t)
datay=np.array(yaw)
datap=np.array(pitch)
# Filter the data, and plot both the original and filtered signals.
y = butter_lowpass_filter(datay, cutoff, fs, order).tolist()
p = butter_lowpass_filter(datap, cutoff, fs, order).tolist()
# perform DR prediction
vy=[]
vp=[]
for i in range(total_frames):
	if i<frame_w:
		vy.append(0)
		vp.append(0)
	else:
		vy.append((y[i]-y[i-frame_w])/window)
		vp.append((p[i]-p[i-frame_w])/window)
#print vy
vvy=[]
vvp=[]
#print len(vy),len(vy[0])
for i in range(2*frame_w):
    vvy.append(vy[i])
    vvp.append(vp[i])
for i in range(2*frame_w,total_frames):
    vvy.append(alpha*vvy[i-frame_w]+(1-alpha)*(vy[i]))
    vvp.append(alpha*vvp[i-frame_w]+(1-alpha)*(vp[i]))
ty=[]
tp=[]
for i in range(0,2*frame_w,frame_interval):
    ty.append(yaw[i])
    tp.append(pitch[i])

for i in range(2*frame_w,total_frames,frame_interval):
    ty.append(y[i-frame_w]+interval*vvy[i-frame_w])
    tp.append(p[i-frame_w]+interval*vvp[i-frame_w])

final_probs=[]
for i in range(len(ty)):
        out.write('sec_%.2f, '%(i*interval))
        probs=gen_prob(ty[i],tp[i],100,100,tilew,tileh)
        final_probs.append(probs)
        for k in range(tilew*tileh):
            out.write(str(probs[k])+' ')
        out.write('\n')
out.close()
'''
plt.subplot(2, 1, 2)
plt.plot(t2, ty, 'b-', label='data')
#plt.plot(t,yaw,'b-',label='data')
plt.plot(t, y, 'g-', linewidth=2, label='filtered data')
plt.xlabel('Time [sec]')
plt.grid()
plt.legend()

plt.subplots_adjust(hspace=0.35)
plt.show()
'''
#print ty
#print tp

