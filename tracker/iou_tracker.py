# ---------------------------------------------------------
# IOU Tracker
# Copyright (c) 2017 TU Berlin, Communication Systems Group
# Licensed under The MIT License [see LICENSE for details]
# Written by Erik Bochinski
# ---------------------------------------------------------

import time
import os
import cv2
import numpy as np
from tracker.util import load_mot, iou

PATH_RESULT = '/app/CenterNet/Detection/npy_tracking_results'
PATH_SVID = '/app/CenterNet/Detection/mp4_tracking_results'
if not os.path.isdir(PATH_RESULT):
    os.mkdir(PATH_RESULT)
if not os.path.isdir(PATH_SVID):
    os.mkdir(PATH_SVID)

def track_iou_edited(vid_name, detections, sigma_l, sigma_h, sigma_iou, t_min, path_video, viz):
    """
    Simple IOU based tracker.
    See "High-Speed Tracking-by-Detection Without Using Image Information by E. Bochinski, V. Eiselein, T. Sikora" for
    more information.

    Args:
         detections (list): list of detections per frame, usually generated by util.load_mot
         sigma_l (float): low detection threshold.
         sigma_h (float): high detection threshold.
         sigma_iou (float): IOU threshold.
         t_min (float): minimum track length in frames.

    Returns:
        list: list of tracks.
    """
    visualize = viz
    video_path = os.path.join(path_video, vid_name+".mp4")
    idx = 0
    print(video_path)
    input = cv2.VideoCapture(video_path)
    width = int(input.get(3)) # get width
    height = int(input.get(4)) #get height
    info_tracking = []
    if(visualize == True):
        output = cv2.VideoWriter(PATH_SVID + '/' + vid_name+".mp4", cv2.VideoWriter_fourcc('M','J','P','G'), 5.0, (width, height))
    tracks_active = []
    all_tracks = []
    tracks_finished = []
    duration = time.time()
    skip_frame = 1


    while (input.isOpened()):
        ret, frame = input.read()
        if not ret:
            break
        if idx%skip_frame==0:
            frame_num = idx
            detections_frame = detections[frame_num]

            dets = [det for det in detections_frame if det['score'] >= sigma_l]

            updated_tracks = []
            for track_id, track in enumerate(tracks_active):
                if track == "Done":
                    continue
                if len(dets) > 0:
                    # get det with highest iou
                    best_match = max(dets, key=lambda x: iou(track['bboxes'][-1], x['bbox']))
                    if iou(track['bboxes'][-1], best_match['bbox']) >= sigma_iou and best_match['class']==track['class']:
                        track['bboxes'].append(best_match['bbox'])
                        # track['max_score'] = max(track['max_score'], best_match['score'])
                        track['conf_score'].append(best_match['score'])
                        updated_tracks.append(track)
                        #
                        # remove from best matching detection from detections
                        del dets[dets.index(best_match)]
                # if track was not updated
                if len(updated_tracks) == 0 or track is not updated_tracks[-1]:
                    # finish track when the conditions are met
                    tracks_active[track_id] = "Done"

            # create new tracks
            new_tracks = [{'bboxes': [det['bbox']], 'max_score': det['score'], 'start_frame': frame_num, 'class':det['class'], 'conf_score':[det['score']]} for det in dets]
            tracks_active = tracks_active + new_tracks

            info_fr = []
            class_text = ['None', 'car', 'truck']

            for track_id, track in enumerate(tracks_active):
                if track == "Done":
                    continue

                box = track['bboxes'][-1]
                obj_id = track_id
                class_id = track['class']
                score = track['conf_score'][-1]
                # recording
                info_tracking.append([class_id, idx, score, obj_id, box[0], box[1], box[2], box[3]])
                if visualize == True:
                    cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 3 )
                    cv2.putText(frame, class_text[class_id]+str(obj_id).zfill(5), (box[0], box[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2,cv2.LINE_AA) 
            if visualize == True:
                output.write(frame)
        idx += 1
    input.release()
    if visualize == True:
        output.release()
    
    np.save(PATH_RESULT + '/info_' + vid_name+".mp4", info_tracking)
    duration = time.time() - duration
    print("Finish writing %s takes %s"%(vid_name, str(duration)))

