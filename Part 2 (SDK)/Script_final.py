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
project_name = "demo_SDK_Final"
dataset_name = "demo_SDK_dataset_Final"

print(f"Creating dataset '{dataset_name}' in project '{project_name}'...")
project = dl.projects.create(project_name=project_name)
print(f"Creating project '{project_name}'successfully!\n{'--'*20} ...")

try:
    dataset = project.datasets.create(dataset_name=dataset_name)
    print(f"Dataset '{dataset_name}' created successfully!\n{'--'*20}")
except dl.exceptions.ExistingDataset:
    dataset = project.datasets.get(dataset_name=dataset_name)
    print(f"Dataset '{dataset_name}' already exists. Getting the existing dataset...")


project = dl.projects.get(project_name=project_name)
dataset = project.datasets.get(dataset_name=dataset_name)

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
        
        
        item = dataset.items.get(filepath='/'+item_name) # https://console.dataloop.ai/projects/d66a0a1e-9d95-4746-87da-0a0a05958b72/datasets/6503e721485fae2c61d4ef57/items/6503e729e3cf617e9ae79bc2
        
        # try:
        #     item = dataset.items.get(filepath=dataset_name+'/'+item_name) # https://console.dataloop.ai/projects/d66a0a1e-9d95-4746-87da-0a0a05958b72/datasets/6503e721485fae2c61d4ef57/items/6503e729e3cf617e9ae79bc2
        # except:
        #     print(f"Item {item_name} Not Found...")

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
            points = [(point[0]['x'], point[1]['y']) for point in annotation_info]
            annotation_definition = dl.Polygon(geo=points, label=label_name)

        builder = item.annotations.builder()
        builder.add(annotation_definition=annotation_definition)
        item.annotations.upload(builder)

        print("Annotations added, moving to the next one\n")
    print("Checking the plot\n")
    import matplotlib.pyplot as plt
    plt.figure()
    plt.imshow(builder.show())
    for annotation in builder:
        plt.figure()
        plt.imshow(annotation.show())
        plt.title(annotation.label)

print(f"All Annotations uploaded successfully!\n{'--'*20}")



# # Step 7: Query and print image items labeled as "top"

print("Querying and printing image items labeled as 'top':\n")
filter_query = dl.Filters().add(field="label", values="top")
for item in dataset.items.list(filters=filter_query).all():
    annotations = item.annotations.list()
#     item.print(columns=['filename'])
    print(f"\n\nTop Annotation - ID:\n {annotation.id}, \nLabel: {annotation.label}, \nPosition: ({annotation.x}, {annotation.y})")



# # Step 8: Query and print all point annotations
print("\nQuerying and printing all point annotations:")

# Iterate through all items in the dataset
for item in dataset.items.list().all():
#     print(f"Item Name: {item.name}, Item ID: {item.id}")
    
    annotations = item.annotations.list()
    for annotation in annotations:
        if annotation.type == dl.AnnotationType.POINT:
            # Handle point annotations
            print(f"\n\nPoint Annotation - ID:\n {annotation.id}, \nLabel: {annotation.label}, \nPosition: ({annotation.x}, {annotation.y})")


# Step 9: Logout from Dataloop
dl.logout()
print("\nLogged out from Dataloop.")