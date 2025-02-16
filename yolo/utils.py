# Wrapper functions for yolov5
from .yolov5.utils.general import scale_boxes

def processPrediction(pred, img1_shape, img0_shape, names):
    '''
    :param pred: predictions from yolo model
    :param img1: image (pytorch)
    :param img0: image (orig numpy)
    :param names: labels
    :param colors: colors of label box
    :return: centers of boxes for each label category
    '''
    # Process detections
    pos = {}
    sizes = {}

    for cls in range(len(names)):
        pos[cls] = []
        sizes[cls] = []
    for i, det in enumerate(pred):  # detections per image
        if len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_boxes(img1_shape[2:], det[:, :4], img0_shape).round()
                
            for *xyxy, conf, cls in reversed(det):
                sizes[int(cls)].append((float(xyxy[2]-xyxy[0])/img0_shape[1],
                                            float(xyxy[3]-xyxy[1])/img0_shape[0]))
                pos[int(cls)].append( (float(xyxy[0])/img0_shape[1],
                                        float(xyxy[1])/img0_shape[0]) )
    return pos, sizes

