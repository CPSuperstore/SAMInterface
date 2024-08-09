# SAM Interface
A simple interface for Facebook Research's [Segment Anything Model](https://github.com/facebookresearch/segment-anything).

## Installation
First, clone the repository somewhere on your machine.
```shell
git clone https://github.com/CPSuperstore/SAMInterface.git
cd SAMInterface
```

Once that is complete, install the dependencies.
```shell
pip install -r requirements.txt
pip install opencv-python pycocotools matplotlib onnxruntime onnx
pip install git+https://github.com/facebookresearch/segment-anything.git
```

Now, run `main.py`. This will create a new file in the working directory called `preferences.json`.

Download a model checkpoint from the [SAM GitHub Repository](https://github.com/facebookresearch/segment-anything#model-checkpoints).
The `default` model is recommended.

Next, open the created `preferences.json` and navigate to the `sam_checkpoint` key.

```json
...
"sam_checkpoint": {
    "model_type": "default",
    "checkpoint_path": "checkpoints/sam_vit_h_4b8939.pth",
    "auto_detect_masks": true
}
...
```

Set `model_type` to the name of the model you selected, and `checkpoint_path` to the path where you saved the model.

Everything is now ready to be used.

## Usage
Run `main.py`. This will open the main menu of the application.
From here, select the image (or segment manager save) you wish to work with.
After some time, you will be greeted with the segmentation interface. Left click to add a segment, and right click to delete a segment.
You can preview the flat image where each segment is filled with the median color of the pixels within.
You can also export to the `VectorNode` and `MaskNode` objects (with and without sub-polygon detail).
Finally, you can save the current segmentation to resume working later.

You can also pass in the filename to work on as a command line argument:
```shell
python main.py [filename]
```

The filename can either be a supported image format, or a previously saved segmentation manager.
