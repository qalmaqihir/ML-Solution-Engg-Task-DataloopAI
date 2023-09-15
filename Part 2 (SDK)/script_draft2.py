import datetime
import os
import json
import dtlpy as dl


# get the credentials
with open('config.json') as config_file:
    config = json.load(config_file)

email = config["dataloop_email"]
password = config["dataloop_password"]

# Step 1: Login to Dataloop
print("Logging in to Dataloop...")
dl.login(email, password)
print(f"Login successful!\n{'--'*45}")


# Step 2: Create a new dataset (or get an existing one)  
project_name = "demo_SDK_final"
dataset_name = "demo_SDK_dataset_final"

print(f"Creating dataset '{dataset_name}' in project '{project_name}'...")
project = dl.projects.create(project_name=project_name)
print(f"Creating project '{project_name}'successfully!\n{'--'*20} ...")

try:
    dataset = project.datasets.create(dataset_name=dataset_name)
    print(f"Dataset '{dataset_name}' created successfully!\n{'--'*20}")
except dl.exceptions.ExistingDataset:
    dataset = project.datasets.get(dataset_name=dataset_name)
    print(f"Dataset '{dataset_name}' already exists. Getting the existing dataset...")
    
    
# Step 3: Add labels to the dataset recipe
labels_to_add = ["1", "2", "3", "top", "bottom"]
print(f"Adding labels to the dataset recipe: {labels_to_add}")
dataset.add_labels(labels_to_add)
print(f"Labels added successfully!\n{'--'*20}")



# Step 4: Upload images
image_dir = "./" 

print(f"Uploading images from '{image_dir}'...")
for filename in os.listdir(image_dir):
    if filename.endswith(".jpg"):
        local_path = os.path.join(image_dir, filename)
        dataset.items.upload(local_path=local_path)
        print(f"Uploaded {filename}")

print(f"Image upload completed!\n{'--'*20}")


# Step 5: Add UTM metadata to items
current_time = datetime.datetime.utcnow().isoformat()
metadata = {"collected": current_time}
print("Adding UTM metadata to items...")
for item in dataset.items.list().all():
    item.metadata["user"] = metadata
    item.update()
print(f"Metadata added to items!\n{'--'*20}")



# Step 6: Upload annotations from JSON file
annotations_file = "./ML Solution Engineering Home Assignment.json"

print(f"Uploading annotations from '{annotations_file}'...")
with open(annotations_file, "r") as json_file:
    annotations_data = json.load(json_file)

for item_name, annotations in annotations_data.items():
    for annotation in annotations:
        label_name = annotation['label']
        confidence = annotation['confidence']

        if 'box' in annotation:
            annotation_type = 'box'
            annotation_info = annotation['box']
        elif 'point' in annotation:
            annotation_type = 'point'
            annotation_info = annotation['point']
        elif 'polygon' in annotation:
            annotation_type = 'polygon'
            annotation_info = annotation['polygon']
        else:
            print(f"Skipping annotation for item '{item_name}' with unsupported type.")
            continue

        print(f"Successfully got the annotations for {item_name}:\nDetails are as below:\n Label Name: {label_name}\nConfidence: {confidence}\n\
              Annotation Type: {annotation_type}\nAnnotation Info: {annotation_info}\n\n")

        item = dataset.items.get(filepath=item_name)

        if annotation_type == "box":
            annotation_definition = dl.Box(top=annotation_info[0]['y'],
                                            left=annotation_info[0]['x'],
                                            bottom=annotation_info[1]['y'],
                                            right=annotation_info[1]['x'],
                                            label=label_name)
        elif annotation_type == "point":
            annotation_definition = dl.Point(x=annotation_info['x'],
                                              y=annotation_info['y'],
                                              label=label_name)
        elif annotation_type == "polygon":
            points = [(point['x'], point['y']) for point in annotation_info]
            annotation_definition = dl.Polygon(geo=points, label=label_name)

        builder = item.annotations.builder()
        builder.add(annotation_definition=annotation_definition)
        item.annotations.upload(builder)

    print("Annotations added, moving to the next one")

print(f"Annotations uploaded successfully!\n{'--'*20}")



# Step 7: Query and print image items labeled as "top"
print("Querying and printing image items labeled as 'top':")
for item in dataset.items.list(filters=dl.Filters().labels(field="label", values="top")):
    print(f"Item Name: {item.name}, Item ID: {item.id}")



# Step 8: Query and print all point annotations
print("\nQuerying and printing all point annotations:")
for item in dataset.items.list():
    print(f"Item Name: {item.name}, Item ID: {item.id}")
    for annotation in item.annotations.list().all():
        if isinstance(annotation, dl.Point):
            print(
                f"Annotation ID: {annotation.id}, "
                f"Label: {annotation.label}, "
                f"Position: ({annotation.x}, {annotation.y})"
            )



# Step 9: Logout from Dataloop
dl.logout()
print("\nLogged out from Dataloop.")





