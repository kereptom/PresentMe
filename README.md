### README for PresentMe

#### Introduction
PresentMe is a Python tool for creating conference presentations. It overlays and blends webcam videos on PowerPoint slides, and synchronizes them with audio.

#### Installation

##### Prerequisites
- Anaconda or Miniconda installed

##### Steps
1. Create a new Conda environment:
    ```
    conda create --name presentme python=3.8
    ```
2. Activate the environment:
    ```
    conda activate presentme
    ```
3. Install required packages:
    ```
    pip install Pillow moviepy opencv-python pandas numpy pydub
    conda install -c conda-forge ffmpeg
    ```

#### How to Prepare Slides
- Create your presentation slides using PowerPoint.
- Export the slides as PNG files.
- If you want to enhance the resolution of exported slides, follow this [YouTube tutorial](https://www.youtube.com/watch?v=8gG3nDrGoTk).

#### Folder Structure
```
.
├── slides/
│   ├── slide1.png
│   ├── slide2.png
│   └── ...
├── webcams/
│   ├── webcam1.mp4
│   ├── webcam2.mp4
│   └── ...
├── setup.txt
└── presentMe.py
```

#### How to Run
Execute the following command:
```
python presentMe.py -w webcams -s slides -t setup.txt -o final.mp4 
```

#### Demonstration
1. Prepare your PowerPoint slides and export them as PNGs into the `slides` folder.
2. Record or place your webcam videos into the `webcams` folder.
3. Edit `setup.txt` to map each slide to its corresponding webcam video or duration.
4. Run the command mentioned in the "How to Run" section.
5. The output will be a single video file (`out/final.mp4`).
