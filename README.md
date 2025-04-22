# Membrane Image Analysis

**Yuval Amir**  

---
## Project Description

Submission date: March 8, 2025Objective: Detect colored markers on a membrane filmed through varying water clarity.The camera is mounted above a water tank, capturing the membrane at the bottom under different turbidity levels. As water quality degrades, colored circular markers appear differently and must be accurately identified and tracked.

**Camera setup:** 
<img src="img/camera.jpg" alt="Camera mounted above the tank" width="300"/>  

**Membrane out of water:** 
<img src="img/membrane.jpg" alt="Membrane out of water" width="300"/>  

**Sample frames:**
<img src="img/frame1.jpg" alt="Sample frame 1" width="300"/>  
<img src="img/frame2.jpg" alt="Sample frame 2" width="300"/> 
<img src="img/frame3.jpg" alt="Sample frame 3" width="300"/>  


## Introduction

This project consists of two main parts:

1. **detect_colored_circles**  
   Detects colored circles in a single membrane image.

2. **track_circles_over_time**  
   Tracks circles over a sequence of images and produces a unified result table.

---

## Project Structure

Membrane_Image_Analysis/
├── src/
│   └── membrane_image_analysis.py
├── docs/
│   └── membrane_analysis_report.pdf
├── examples/
│   ├── seq_000.jpg...seq_009.jpg
│   ├── seq_000_detected.jpg...seq_009_detected.jpg
│	└── tracking_table.md
├── img/
│   ├── frame1.png
│	├── frame2.png
│	├── frame3.png
│	├── camera.jpg
│	└── membrane.jpg
├── main.py
├── .gitignore
├── requirements.txt
└── README.md

---

## Installation

1. **Clone the repository**  

   git clone https://github.com/YuvalAmir1551/Membrane_Image_Analysis.git
   cd Membrane_Image_Analysis

2. **Create and activate a virtual environment**  

   python -m venv env
   source env/bin/activate      # On Windows: env\Scripts\activate

3. **Install dependencies**  

   pip install -r requirements.txt

---

## Usage

Run the analysis via the provided main.py script.

### Prerequisites

- Python 3.7+
- Dependencies installed via `pip install -r requirements.txt`

### Single-frame detection:
	
	python main.py examples/seq_000.jpg
	
### Tracking over time:
	
	python main.py --track examples/seq_000.jpg examples/seq_001.jpg examples/seq_002.jpg

### Tracking + generate Markdown table
	
	python main.py --track --output-table examples/seq_000.jpg examples/seq_001.jpg examples/seq_002.jpg

---

## Examples

#### Single-frame detection

<img src="examples/seq_000.jpg" alt="Input image" width="300"/>  
<img src="examples/seq_000_detected.png" alt="Detected circles" width="300"/>

#### Tracking output (Markdown table)

| image | circle_id |   x  |   y  | radius | color  |
|:-----:|:---------:|:----:|:----:|:------:|:-------|
|  1    |     1     |  458 |  419 |   81   | blue   |
|  1    |     2     |  1425|  554 |   76   | red    |
|  1    |     3     |  1007|  971 |   76   | yellow |
|  1    |     4     |  1843|  145 |   78   | yellow |
|  1    |     5     |  54  |  837 |   74   | black  |
|  1    |     6     |  870 |  17  |   72   | black  |
|  2    |     1     |  458 |  419 |   80   | blue   |
|  2    |     2     |  1427|  556 |   76   | red    |
|  2    |     3     |  1008|  974 |   78   | yellow |
|  2    |     4     |  1843|  146 |   79   | yellow |
|  2    |     5     |  52  |  835 |   72   | black  |
|  2    |     6     |  874 |  13  |   71   | black  |
|  3    |     1     |  453 |  460 |   79   | blue   |
|  3    |     2     |  1423|  599 |   77   | red    |
|  3    |     3     |  1003|  1014|   79   | yellow |
|  3    |     4     |  1838|  180 |   83   | yellow |
|  3    |     5     |  48  |  879 |   70   | black  |
|  3    |     6     |  865 |  43  |   73   | black  |
