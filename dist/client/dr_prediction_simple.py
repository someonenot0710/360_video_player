
# coding: utf-8

# In[144]:


import math
# from IPython.display import Image


# In[145]:


# dir_path = "sensors/"
# user_file_name = "coaster_user07_orientation.csv" 
# trace = open(dir_path+user_file_name)
# gt_trace = dict()


# In[146]:


# trace_data = trace.read().splitlines()
# for frame in range(1,len(trace_data)):
#     split = trace_data[frame].split(", ")
#     gt_trace[int(split[0])]=dict()
#     gt_trace[int(split[0])]['yaw']=float(split[7]) # theta
#     gt_trace[int(split[0])]['pitch']=float(split[8]) # phi
#     gt_trace[int(split[0])]['roll']=float(split[9])



# In[147]:


view_degree = 135.0


# In[148]:


def init_file(video,user):
    dir_path = "SC/sensors/"
    user_file_name = video+"_user"+str(user)+"_orientation.csv"
#     user_file_name = "coaster_user07_orientation.csv" 
    trace = open(dir_path+user_file_name)
    global gt_trace
    gt_trace = dict()
    trace_data = trace.read().splitlines()
    for frame in range(1,len(trace_data)):
        split = trace_data[frame].split(", ")
        gt_trace[int(split[0])]=dict()
        gt_trace[int(split[0])]['yaw']=float(split[7]) # theta
        gt_trace[int(split[0])]['pitch']=float(split[8]) # phi
        gt_trace[int(split[0])]['roll']=float(split[9])


# In[149]:


## dr prediction formula
# Image("dr_formula.png")


# In[150]:


# x = (yaw + 180)/360 × width 
# y = (90 − pitch)/180 × height
def transform_to_equi(yaw,pitch):
    x = (yaw + 180)/360 * 3840
    y = (90 - pitch)/180 * 1920
    return x,y

def check_yaw (yaw):
    if yaw > 180.0:
        return yaw - 360.0
    elif yaw < -180.0:
        return yaw + 360.0
    else:
        return yaw

def check_pitch_then_yaw (yaw,pitch):
    if pitch > 90.0:
        pitch = 180.0-pitch
        yaw = check_yaw(yaw - 180)
    elif pitch < - 90.0:
        pitch = -180.0-pitch
        yaw = check_yaw(yaw + 180)
    
    return yaw,pitch

def pitch_canditate (pitch , each_tile_degree):
    degree_max = view_degree / 2.0
    count = 1.0
    canditate = []
    canditate.append(0) #pitch
    while True:
        add_degree = count * each_tile_degree
        if add_degree > degree_max:
            canditate.append(view_degree) # degree_max+pitch
            canditate.append((-1)*view_degree) # -1.0*degree_max+pitch
            break
            
        canditate.append(count) #add_degree+pitch
        canditate.append(-1.0*count) #-1.0*add_degree+pitch
        count +=1
    return canditate
    
    


# In[151]:


##dr prediction

def dr_prediction(pre_time,now_time,v_pre={'yaw': 0, 'pitch': 0},length=0):

    #time1 = 60
    #time2 = 90
    # prediction_time = (time2-time1)/30.0  #0.5 # should be time1 - time2 , need to transform to second /30
    global gt_trace
    time1 = int(pre_time*30)+1 #frame1
    time2 = int(now_time*30)+1 #frame2
    prediction_time = now_time - pre_time
    if length ==0:
        length = prediction_time
#     print(length)
    
    # v_pre = dict() # for recording previous velocity
    # v_pre['yaw']=0
    # v_pre['pitch']=0

    v_now = dict() # for recording current velocity
    v_now['yaw']=0
    v_now['pitch']=0
    alpha = 0.1

    next_center = dict() # for recording position that is predictred

    # V_t = alpha*V_(t-1) + (1-alpha)(P_(t)-P_(t-1))
    v_now['yaw'] = alpha*v_pre['yaw'] + (1-alpha)*(gt_trace[time2]['yaw']-gt_trace[time1]['yaw'])/prediction_time
    v_now['pitch'] = alpha*v_pre['pitch'] + (1-alpha)*(gt_trace[time2]['pitch']-gt_trace[time1]['pitch'])/prediction_time
    # P_(n+d) = P_n + d*V_n # d  we want to predict the fixation d time length later
    next_center['yaw'] = gt_trace[time2]['yaw'] + length*v_now['yaw']
    next_center['pitch'] = gt_trace[time2]['pitch'] + length*v_now['pitch']
    
    # 1. if yaw > 180 --> minus 360 , if yaw<-180 ---> plus 360
    # 2. if pitch > 90 --> new_pitch = 180 - pitch, new_yaw = yaw-180  , 
    #    if pitch < -90 --> new_pitch = -180 - pitch , new_yaw = yaw+180 

#     print("yaw:%f , pitch:%f"% (next_center['yaw'],next_center['pitch']))

    next_center['yaw'] = check_yaw(next_center['yaw'])
    next_center['yaw'] , next_center['pitch'] = check_pitch_then_yaw(next_center['yaw'],next_center['pitch'])

    # print(next_center)
    return next_center , v_now
#     print("yaw:%f , pitch:%f"% (next_center['yaw'],next_center['pitch']))


# In[152]:


def get_width(pitch):
    return (view_degree/math.cos(math.radians(pitch)))*(3840.0/360.0)

def get_width_circle(width,center_pitch,other_pitch):
    return width*math.cos(math.radians(other_pitch)-math.radians(center_pitch))

def check_left_right(right,left):
    if right > 3840.0:
        right  = right - 3840.0 
    if left < 0 :
        left = left + 3840.0
    return right,left


# In[153]:


# match yaw pitch to equirectangular
def get_request_tile(tile_num_w,tile_num_h,next_center): 

    # tile_num_w = 5
    # tile_num_h = 5
    degree_max = view_degree / 2.0
    width = 3840.0
    height = 1920.0
    each_tile_height = height/tile_num_h
    each_tile_width = width/tile_num_w
    each_tile_degree = 180.0/float(tile_num_h)

    x,y = transform_to_equi(next_center['yaw'],next_center['pitch']) # match yaw pitch to equirectangular x y

    width_length = (view_degree/math.cos(math.radians(next_center['pitch'])))*(3840.0/360.0) # the width length we need to request at center

    tmp_pitch = pitch_canditate(next_center['pitch'],each_tile_degree) # all pitch that we have to consider

    request_tile = dict()
    for item in tmp_pitch:
        if item > 90.0:
            now_pitch = next_center['pitch'] + degree_max
            item = degree_max/each_tile_degree
        elif item < -90.0:
            now_pitch = next_center['pitch'] - degree_max
            item = -1*(degree_max/each_tile_degree)
        else:
            now_pitch = item*each_tile_degree + next_center['pitch']

        if now_pitch > 90.0:
            request_tile[0]=list()
            for i in range(0,tile_num_w):
                request_tile[0].append(i)
            continue
        elif now_pitch < -90.0:
            request_tile[tile_num_h-1]=list()
            for i in range(0,tile_num_w):
                request_tile[tile_num_h-1].append(i)
            continue        

#         w = get_width(now_pitch) ## square

        w =  get_width_circle(width_length,next_center['pitch'],now_pitch) ## circle
#         print(w)        
        x_right_o = x + w/2.0
        x_left_o = x - w/2.0
#         print("pitch:%f"%(now_pitch))
#         print("w:%f"%w)
        tmp_y = y + item*each_tile_height*(-1.0)  ## ?? hight over 1920

#         print('original:  right=%f , left=%f'%(x_right,x_left))
        x_right,x_left=check_left_right(x_right_o,x_left_o)
#         print('changed:  right=%f , left=%f'%(x_right,x_left))
        right_tile = math.floor(x_right/each_tile_width)
        left_tile = math.floor(x_left/each_tile_width)
        y_tile_num = math.floor(tmp_y/each_tile_height)
#         print("left_tile: %d , right_tile:%d"%(left_tile,right_tile))
        request_tile[y_tile_num]=list()
#         print(x_right-x_left)
        if x_right_o - x_left_o >= 3840.0 or  x_left_o - x_right_o >= 3840.0:
#             print('in')
            for i in range(0,tile_num_w):
                    if i not in request_tile[y_tile_num]:
                        request_tile[y_tile_num].append(i)
        elif left_tile > right_tile :
            for i in range(left_tile-1,tile_num_w):
                if i not in request_tile[y_tile_num]:
                    request_tile[y_tile_num].append(i)
            for i in range(0,right_tile):
                if i not in request_tile[y_tile_num]:
                    request_tile[y_tile_num].append(i)
        elif  right_tile > left_tile:
            for i in range(left_tile,right_tile):
                if i not in request_tile[y_tile_num]:
                    request_tile[y_tile_num].append(i)
        else:
            for i in range(0,tile_num_w):
                if i not in request_tile[y_tile_num]:
                    request_tile[y_tile_num].append(i)        

#     print(request_tile)

    request_tile_in_number = list()
    for item in request_tile:
        for num in request_tile[item]:
            number = item*tile_num_w + num + 1
            if number not in request_tile_in_number:
                request_tile_in_number.append(number)
#     print(request_tile_in_number)
    return request_tile_in_number
    


# In[154]:


# init_file("coaster","09")

# v_pre = {'yaw': 0, 'pitch': 0}
# # v_pre={'yaw': -0.5679027777780008, 'pitch': 10.458011111110004}
# next_center , v_pre = dr_prediction(3,6,v_pre,10)
# a=get_request_tile(10,10,next_center)
# a.sort()
# print(len(a))


# In[155]:


# v_pre = {'yaw': 0, 'pitch': 0}
# next_center , v_pre = dr_prediction(3,6,v_pre,1)
# a=get_request_tile(10,10,next_center)
# a.sort()
# print(a)


# In[123]:


# for i in range(tile_num_h):
#     for j in range(tile_num_w):
#         if i*tile_num_w+j+1 in request_tile_in_number:
#             print("1  ", end = '')
#         else: print("0  ", end = '')
#     print('\n')

