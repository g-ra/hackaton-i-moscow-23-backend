import cv2
from ultralytics import YOLOv10
import time
import numpy as np
from collections import deque
import json
import os
import warnings
import logging
logger = logging.getLogger(__name__)
# Ignore numpy's VisibleDeprecationWarning only
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)
# Example usage:
model = YOLOv10('best_yolo10b_200it.pt')

model.fuse()

def preprocess(frame):

    logger.info(f"preprocess")

    # Grayscale
    try:
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    except Exception:
        logger.info('вот тут')
        return frame
    
    mn = np.quantile(gray_frame,0.5)
    # Make objects mask
    _, gray = cv2.threshold(gray_frame, mn-15, 255, cv2.THRESH_BINARY_INV)

    if mn >= 165:    

        return gray
    # Make sky mask
    _,sky =  cv2.threshold(gray_frame, mn-5, 255, cv2.THRESH_BINARY_INV )

    # Morph sky mask (denoize)
    kernel = np.ones((10,10),np.uint8)  #kernel for morphology to smooth sky mask
    sky = cv2.morphologyEx(sky, cv2.MORPH_CLOSE, kernel)
    sky = cv2.morphologyEx(sky, cv2.MORPH_OPEN, kernel)
    gray = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
    # Dilate the image to add a border
    kernel_s = np.ones((10,10), np.uint8)  # kernel for dilate path to smooth sky mask
    kernel_o = np.ones((3,3), np.uint8)
    sky = cv2.dilate(sky, kernel_s, iterations=1)
    gray =cv2.dilate(gray, kernel_o, iterations=1)


    # Substract sky mask from objects
    output = cv2.subtract(gray,sky)
    return output

def process_frame(frame,frame_width,frame_height):
    output = preprocess(frame)
    contours, _ = cv2.findContours(output, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    x_cent = []
    y_cent = []
    
    for contour in contours:
        if cv2.contourArea(contour) > 3 and cv2.contourArea(contour) < 50:
            x, y, w, h = cv2.boundingRect(contour)
            x1,y1,x2,y2 = x,y,(x+w),(y+h)
            
            x_center = int((x1 + x2) / 2)
            y_center = int((y1 + y2) / 2)
            
            x_cent.append(x_center)
            y_cent.append(y_center)

    if len(x_cent)>0:
        xmin, ymin, xmax, ymax =np.clip(min(x_cent)-250,1,frame_width),np.clip(min(y_cent)-250,1,frame_height),np.clip(max(x_cent)+250,1,frame_width),np.clip(max(y_cent)+250,1,frame_height)
        
        # Calculate the aspect ratio of the bounding box
        bbox_width = xmax - xmin
        bbox_height = ymax - ymin
        bbox_aspect_ratio = bbox_width / bbox_height

        x_center = int((xmin + xmax) / 2)
        y_center = int((ymin + ymax) / 2)

        # If the bounding box aspect ratio is less than the desired aspect ratio, increase the width
        if bbox_aspect_ratio < 640/480:
            bbox_width = int(bbox_height * (640/480))
            xmin = max(0, int(x_center - bbox_width / 2))
            xmax = min(frame_width, int(x_center + bbox_width / 2))
        # If the bounding box aspect ratio is greater than the desired aspect ratio, increase the height
        elif bbox_aspect_ratio > 640/480:
            bbox_height = int(bbox_width / (640/480))
            ymin = max(0, int(y_center - bbox_height / 2))
            ymax = min(frame_height, int(y_center + bbox_height / 2))

        # Ensure the bounding box is at least 640x480
        if bbox_width < 640 or bbox_height < 480:
            xmin = max(0, int(x_center - 640 / 2))
            xmax = min(frame_width, int(x_center + 640 / 2))
            ymin = max(0, int(y_center - 480 / 2))
            ymax = min(frame_height, int(y_center + 480 / 2))
    

        return [xmin, ymin, xmax, ymax]

        
    return  [0,0,0,0]

def euclidean_distance(p, q):
    return np.sqrt(sum([(a - b) ** 2 for a, b in zip(p, q)]))

def compare_boxes(list1, list2,add_list):
    one_list_flag = 0

    if len(list1)>0:
        for i in range(len(list1)):
            item = list(list1[i])
            item[0] = [np.sum(x) for x in zip(item[0], add_list)]
            list1[i] = tuple(np.array(item))
    else: one_list_flag = 1

    if len(list2)>0:
        for i in range(len(list1)):
            item = list(list1[i])
            list1[i] = tuple(np.array(item))
    else: one_list_flag = 2
    
    if one_list_flag !=0:
        if one_list_flag == 1:
            return list2
        else: return list1

    if one_list_flag == 0 :
        list1.extend(list2)
        list1.sort(key=lambda coord: [coord[0][0],coord[0][1],coord[0][2],coord[0][3]])

        n = range(len(list1)-1)
        to_pop = []
        for i in n:
            
            if list1[i][3] != list1[i+1][3]:
                
                if euclidean_distance(list1[i][0],list1[i+1][0])<100: #check if boxes are near

                    if list1[i][2] > list1[i+1][2]:
                           to_pop.append(i+1)
                    else:  to_pop.append(i)
            else:

                    continue
        
        return [point for index,point in enumerate(list1) if index not in to_pop]


def process_video_with_compete(model = model, input_video_path = None, mem_frames=8, show_video=False, save_video=True, output_video_path="output_video.mp4"):
    #
    logger = logging.getLogger(__name__)
    logger.info(f"Starting video processing for: {input_video_path}")

    scary_classes=[3,4]
    # Open the input video file
    cap = cv2.VideoCapture(input_video_path)

    if not cap.isOpened():
        logger.info("Error: Could not open video file.")

    # Get input video frame rate and dimensions
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    #print([frame_height,frame_width])
    if save_video:
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))
    # start_time = time.time()
    frame_count = 0

    zoom_memory = deque([[0,0,0,0]],maxlen=mem_frames)
    danger_json = []
    while True:

        ret, frame = cap.read()
        f_b= process_frame(frame,frame_width=frame_width,frame_height=frame_height)
        if np.mean(f_b)!=0:
            zoom_memory.append(f_b)

        mem_bb = np.median(np.array(list(zoom_memory)),axis=0).astype(int)
    
        # if len(zoom_memory)>1:
        #     cv2.rectangle(frame, (mem_bb[0], mem_bb[1]), (mem_bb[2], mem_bb[3]), (255, 0, 255), 2)
        
       
        if not ret:
            break
        try:
            results = model.predict(frame, conf=0.25,iou=0.8, imgsz=640, verbose=False)#, tracker= "botsort.yaml") #tracker="bytetrack.yaml")
            
            if len(zoom_memory)>1:
                results_zoom = model.predict(frame[mem_bb[1]:mem_bb[3], mem_bb[0]:mem_bb[2]],conf=0.25,iou=0.8, imgsz=640, verbose=False)
            else: results_zoom = None
        except Exception as e:
            logger.debug(str(e)[:200])
    

        

        if results[0].boxes != None: 

            boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
            confid = results[0].boxes.conf.cpu().numpy().astype(float)
            classes = results[0].boxes.cls.cpu().numpy().astype(int)
            
            

            if results_zoom != None:
                if results_zoom[0].boxes != None: # this will ensure that id is not None -> exist tracks

                    boxes_z = results_zoom[0].boxes.xyxy.cpu().numpy().astype(int)
                    confid_z = results_zoom[0].boxes.conf.cpu().numpy().astype(float)
                    classes_z = results_zoom[0].boxes.cls.cpu().numpy().astype(int)
                    flag_z = [1 for i in boxes_z]
                    flag = [0 for i in boxes]
                    
                    results_ziped = [*zip(boxes, classes,confid,flag)]
                    results_zoom_ziped = [*zip(boxes_z, classes_z,confid_z,flag_z)]

                    winner = compare_boxes(results_zoom_ziped,results_ziped,[mem_bb[0],mem_bb[1],mem_bb[0],mem_bb[1]])
                    
                    for box, cls, conf,flag in winner:
                        if cls in scary_classes:
                            logger.debug(cls)
                            logger.debug(int(frame_count/fps))
                            danger_json.append(
                                {
                                    "cls":int(cls),
                                    "time":int(frame_count/fps)
                                }
                            )

                        color = (255,255,255)
                        cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3],), color, 2)
                        cv2.putText(
                            frame,
                            f"{model.model.names[cls]}|cf {round(conf,2)}",
                            (box[0], box[1]),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 255),
                            1
                        )
            else:        
                    
                for box, cls, conf   in zip(boxes, classes,confid):

                    
                    color = (255,0,0)
                    cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3],), color, 2)
                    cv2.putText(
                        frame,
                        f"{model.model.names[cls]}|cf {round(conf,2)}",
                        (box[0], box[1]),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 255),
                        1
                    )


        frame_count += 1

        if save_video:
            
            out.write(frame)

        if show_video:
            frame = cv2.resize(frame, (0, 0), fx=0.75, fy=0.75)

            cv2.imshow("frame", frame)

        if not ret:
            break

    # Release the input video capture and output video writer
    cap.release()
    if save_video:
        out.release()

    # Close all OpenCV windows
    cv2.destroyAllWindows()

    return output_video_path, json.dumps(danger_json)#json_path



