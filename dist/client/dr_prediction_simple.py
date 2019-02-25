
# coding: utf-8

# In[214]:


import math
import timeit
# from IPython.display import Image


# In[161]:


# dir_path = "sensors/"
# user_file_name = "coaster_user07_orientation.csv"
# trace = open(dir_path+user_file_name)
# gt_trace = dict()


# In[162]:


# trace_data = trace.read().splitlines()
# for frame in range(1,len(trace_data)):
#     split = trace_data[frame].split(", ")
#     gt_trace[int(split[0])]=dict()
#     gt_trace[int(split[0])]['yaw']=float(split[7]) # theta
#     gt_trace[int(split[0])]['pitch']=float(split[8]) # phi
#     gt_trace[int(split[0])]['roll']=float(split[9])




# In[225]:


view_degree = 110.0


# In[226]:


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


# In[227]:


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
#             canditate.append(view_degree) # degree_max+pitch
#             canditate.append((-1)*view_degree) # -1.0*degree_max+pitch
            break

        canditate.append(count) #add_degree+pitch
        canditate.append(-1.0*count) #-1.0*add_degree+pitch
        count +=1
    return canditate




# In[228]:


##dr prediction

def dr_prediction(pre_time,now_time,v_pre={'yaw': 0, 'pitch': 0},length=0):

    #time1 = 60
    #time2 = 90
    # prediction_time = (time2-time1)/30.0  #0.5 # should be time1 - time2 , need to transform to second /30
    global gt_trace
    time1 = int(pre_time*30)+1 #frame1
    time2 = int(now_time*30)+1 #frame2
    prediction_time = now_time - pre_time
    
    if float(prediction_time) == 0.0:
        prediction_time = 0.001
    
    
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

#     print(next_center)
    return next_center , v_now
#     print("yaw:%f , pitch:%f"% (next_center['yaw'],next_center['pitch']))


# In[229]:


##dr prediction

def dr_prediction_acceleration(pre_time,now_time,v_pre={'yaw': 0, 'pitch': 0},a_pre={'yaw': 0, 'pitch': 0},length=0):

    global gt_trace
    time1 = int(pre_time*30)+1 #frame1
    time2 = int(now_time*30)+1 #frame2
    prediction_time = now_time - pre_time

    # print("predict")
    # print(prediction_time)
    # if float(prediction_time) == 0.0:
    #     prediction_time = 0.001

    if length ==0:
        length = prediction_time


    v_now = dict() # for recording current velocity
    v_now['yaw']=0
    v_now['pitch']=0
    alpha = 0.1

    a_now = dict() # for recording current velocity
    a_now['yaw']=0
    a_now['pitch']=0

    next_center = dict() # for recording position that is predictred

    # V_t = alpha*V_(t-1) + (1-alpha)(P_(t)-P_(t-1))
    v_now['yaw'] = alpha*v_pre['yaw'] + (1-alpha)*(gt_trace[time2]['yaw']-gt_trace[time1]['yaw'])/prediction_time
    v_now['pitch'] = alpha*v_pre['pitch'] + (1-alpha)*(gt_trace[time2]['pitch']-gt_trace[time1]['pitch'])/prediction_time

    a_now['yaw'] = alpha*a_pre['yaw'] + (1-alpha)*(v_now['yaw']-v_pre['yaw'])/prediction_time
    a_now['pitch'] = alpha*a_pre['pitch'] + (1-alpha)*(v_now['pitch']-v_pre['pitch'])/prediction_time


    # P_(n+d) = P_n + d*V_n # d  we want to predict the fixation d time length later
    next_center['yaw'] = gt_trace[time2]['yaw'] + 0.5 * a_now['yaw'] * length*length
    next_center['pitch'] = gt_trace[time2]['pitch'] + 0.5 * a_now['pitch'] * length*length


    # 1. if yaw > 180 --> minus 360 , if yaw<-180 ---> plus 360
    # 2. if pitch > 90 --> new_pitch = 180 - pitch, new_yaw = yaw-180  ,
    #    if pitch < -90 --> new_pitch = -180 - pitch , new_yaw = yaw+180

#     print("yaw:%f , pitch:%f"% (next_center['yaw'],next_center['pitch']))

    next_center['yaw'] = check_yaw(next_center['yaw'])
    next_center['yaw'] , next_center['pitch'] = check_pitch_then_yaw(next_center['yaw'],next_center['pitch'])

    return next_center , v_now , a_now


# In[230]:


def get_width(r,pitch):
    return (r/math.cos(math.radians(pitch)))*(3840.0/360.0)

def get_width_circle(diameter,center_pitch,other_pitch):
    radius = diameter/2.0

    ## approach 1
    # r_tmp = radius * math.cos(math.asin((other_pitch-center_pitch)/radius))
    ## approach 2
    r_tmp = radius * math.sqrt(1-math.pow(1/math.tan(math.radians(radius)),2)*math.pow(math.tan(math.radians(other_pitch-center_pitch)),2))

    #   print("tmp:%f , tmp_s:%f"%(r_tmp,r_tmp_s))

    return get_width(r_tmp,other_pitch)#,get_width(r_tmp_s,other_pitch)

def check_left_right(right,left):
    if right > 3840.0:
#         right  = right - 3840.0
        right  = right - 3840.0*int(right/3840.0)
    if left < 0 :
#         left = left + 3840.0
        left = left + 3840.0*(int((-1)*left/3840.0)+1)
    return right,left


# In[239]:


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

#     width_length = get_width(view_degree,next_center['pitch'])
#     width_length = (view_degree/math.cos(math.radians(next_center['pitch'])))*(3840.0/360.0) # the width length we need to request at center
    tmp_pitch = pitch_canditate(next_center['pitch'],each_tile_degree) # all pitch that we have to consider

#     print(tmp_pitch)

    request_tile = dict()

    for item in tmp_pitch:
        '''
        if item > 90.0:
            now_pitch = next_center['pitch'] + degree_max
            item = degree_max/each_tile_degree
        elif item < -90.0:
            now_pitch = next_center['pitch'] - degree_max
            item = -1*(degree_max/each_tile_degree)
        else:
        '''
        now_pitch = item*each_tile_degree + next_center['pitch']

        # print(now_pitch)

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

        w =  get_width_circle(view_degree,next_center['pitch'],now_pitch) ## circle

#         print("pitch:%f , width:%f , width_s:%f"%(now_pitch,w*2,2*w_s))

        x_right_o = x + w
        x_left_o = x - w
        _,tmp_y=transform_to_equi(next_center['yaw'],now_pitch)
#         tmp_y = y + item*each_tile_height*(-1.0)  ## ?? hight over 1920


#         print('original:  right=%f , left=%f'%(x_right,x_left))
        x_right,x_left=check_left_right(x_right_o,x_left_o)
#         print('changed:  right=%f , left=%f'%(x_right,x_left))

        right_tile = math.floor(x_right/each_tile_width)
        left_tile = math.floor(x_left/each_tile_width)
        y_tile_num = math.floor(tmp_y/each_tile_height)

#         print("left_tile: %d , right_tile:%d"%(left_tile,right_tile))
        if y_tile_num not in request_tile:
            request_tile[y_tile_num]=list()


        if x_right_o - x_left_o >= 3840.0 or  x_left_o - x_right_o >= 3840.0:
            for i in range(0,tile_num_w):
                    if i not in request_tile[y_tile_num]:
                        request_tile[y_tile_num].append(i)
        elif left_tile > right_tile :
            for i in range(left_tile-1,tile_num_w):
                if i not in request_tile[y_tile_num]:
                    request_tile[y_tile_num].append(i)
            for i in range(0,right_tile+1):
                if i not in request_tile[y_tile_num]:
                    request_tile[y_tile_num].append(i)
        elif  right_tile > left_tile:
            for i in range(left_tile,right_tile+1):
                if i not in request_tile[y_tile_num]:
                    request_tile[y_tile_num].append(i)
        else:
            for i in range(0,tile_num_w):
                if i not in request_tile[y_tile_num]:
                    request_tile[y_tile_num].append(i)


    request_tile_in_number = list()
    for item in request_tile:
        for num in request_tile[item]:
            number = item*tile_num_w + num + 1
            if number not in request_tile_in_number:
                request_tile_in_number.append(number)
#     print(request_tile_in_number)
    return request_tile_in_number



# In[246]:


# init_file("coaster","09")

# #### without accerlation
# v_pre = {'yaw': 0, 'pitch': 0}
# start = timeit.default_timer()
# next_center , v_pre = dr_prediction(2,8,v_pre,8)
# a=get_request_tile(10,10,next_center)
# exe_time = timeit.default_timer() - start
# print(exe_time*1000)
# a.sort()
# print(a)


# In[245]:


#### with accerlation
# v_pre = {'yaw': 0, 'pitch': 0}
# a_pre = {'yaw': 0, 'pitch': 0}
# start = timeit.default_timer()
# next_center , v_pre , a_pre = dr_prediction_acceleration(2,8,v_pre,a_pre,8)
# b=get_request_tile(10,10,next_center)
# exe_time = timeit.default_timer() - start
# print(exe_time*1000)
# b.sort()


# In[195]:


# v_pre = {'yaw': 0, 'pitch': 0}
# next_center , v_pre = dr_prediction(3,6,v_pre,1)
# a=get_request_tile(10,10,next_center)
# a.sort()
# print(a)


# In[244]:


# tile_num_h=10
# tile_num_w=10
# for i in range(tile_num_h):
#     for j in range(tile_num_w):
#         if i*tile_num_w+j+1 in a:
#             print("1  ", end = '')
#         else: print("0  ", end = '')
#     print('\n')
