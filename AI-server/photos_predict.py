from ultralytics import YOLOv10
import os 

# Load a model
model = YOLOv10("best_yolo_v10_100_final.pt")  # pretrained YOLOv8n model

DIRECTORY = "uploads/"
SAVE_DIR = "export/"

def convert_value(value):
    conversion_dict = {3: 0, 2: 1, 1: 2, 0: 3, 4: 4}
    return conversion_dict.get(value, "Invalid value")

def write_output_file(bboxes, filename,full=True):

    with open(SAVE_DIR+filename, 'w') as f:
        if full:
                
            for bbox in bboxes:
                line = f"{bbox['id_class']};{bbox['x_center']};{bbox['y_center']};{bbox['width']};{bbox['height']}\n"
                f.write(line)
        else:
            f.write("")

def pics_to_text():
    # Run batched inference on a list of images
    pics = os.listdir(DIRECTORY)
    for pic in pics:
        results = model(source=DIRECTORY+pic)  # return a list of Results objects

        # Process results list
        for result in results:

            if result != None:
                boxes = result.boxes.xywhn.cpu().numpy().astype(float)  # Boxes object for bounding box outputs
                classes =  result.boxes.cls.cpu().numpy().astype(int)
                bboxes = []
                for cls, box in zip(classes,boxes):
                    x_center, y_center, width, height = box
                    bboxes.append({'id_class': convert_value(cls), 'x_center': x_center, 'y_center': y_center, 'width': width, 'height': height})
                write_output_file(bboxes, f"{pic[:-3]}txt")  # save bounding boxes to disk

            else:
                write_output_file(None, f"{pic[:-3]}txt",full=False)


    return SAVE_DIR