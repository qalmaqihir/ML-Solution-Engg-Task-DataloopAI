import json

# get the credentials

with open('config.json') as config_file:
    config = json.load(config_file)

email = config["dataloop_email"]
password = config["dataloop_password"]

    
import dtlpy as dl
import json
from datetime import datetime

# Set your Dataloop credentials

# dl.setenv(email='your_email@example.com', password='your_password')
dl.setenv(email=email, password=password)


# Step 1: Create a new dataset (or get an existing one)
project_name = "demo_SDK0"
dataset_name = "demo_SDK_dataset0"

# project = dl.projects.get(project_name=project_name)
project = dl.projects.create(project_name=project_name)
dataset = project.datasets.create(dataset_name=dataset_name)

# Step 2: Add labels to the dataset recipe
labels = ["1", "2", "3", "top", "bottom"]
for label in labels:
    dataset.add_label(label_name=label)

# Step 3: Upload images
images_directory = "./" 
dataset.items.upload(local_path=images_directory)

# Step 4: Add UTM metadata to item user metadata
current_time_utc = datetime.utcnow().isoformat()
for item in dataset.items.list():
    item.metadata['user'] = {'collected': current_time_utc}
    item.update()

# Step 5: Upload annotations from a JSON file
annotations_file = "./ML_Solution_Engineering_Home_Assignment.json"

with open(annotations_file, 'r') as f:
    annotations_data = json.load(f)

for annotation in annotations_data:
    label_name = annotation['label']
    annotation_type = annotation['type']
    points = annotation['points']
    confidence = annotation['confidence']
    
    # Find the label ID by name
    label_id = None
    for label in dataset.labels:
        if label.name == label_name:
            label_id = label.id
            break

    if label_id:
        annotation_info = {
            "labelId": label_id,
            "annotationType": annotation_type,
            "points": points,
            "model_info3": confidence
        }
        item_id = annotation['item_id']  # You should specify the item_id from your JSON data
        item = dataset.items.get(item_id=item_id)
        item.annotations.upload(annotations=annotation_info)

# Step 6: Create a query to select "top" labeled images
query = dl.Filters()
query.add_join(field='annotations.label', values='top')

# Print item name and item id for each selected item
for item in dataset.items.list(filters=query):
    print(f"Item Name: {item.name}, Item ID: {item.id}")

# Step 7: Retrieve all point annotations
query = dl.Filters()
query.add_join(field='annotations.annotationType', values='point')

# Print item name and item id for each item, and annotation details
for item in dataset.items.list(filters=query):
    print(f"Item Name: {item.name}, Item ID: {item.id}")
    
    for annotation in item.annotations.list(filters=query):
        annotation_id = annotation.id
        annotation_label = dataset.labels.get(label_id=annotation.label_id).name
        annotation_position = annotation.definition['points']
        print(f"Annotation ID: {annotation_id}, Annotation Label: {annotation_label}, Annotation Position: {annotation_position}")
