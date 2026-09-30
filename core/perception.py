import cv2
import os
from ultralytics import YOLO

def process_frames_to_video(input_folder, output_path, fps=30):
    """
    Reads .bmp frames from a directory, processes them through YOLOv8, 
    and outputs an annotated MP4 video.
    """
    print(f"Initializing processing for: {input_folder}")
    
    # 1. Load the pre-trained YOLOv8 model (Nano version for speed)
    model = YOLO('yolov8n.pt') 
    
    # 2. Retrieve and sequentially sort all .bmp frames
    # Assuming frames are named like 0001.bmp, 0002.bmp, etc.
    frames = [f for f in os.listdir(input_folder) if f.endswith('.bmp')]
    frames.sort()
    
    if not frames:
        print(f"Error: No .bmp files found in {input_folder}")
        return

    # 3. Read the first frame to establish video dimensions
    first_frame_path = os.path.join(input_folder, frames[0])
    frame = cv2.imread(first_frame_path)
    height, width, layers = frame.shape
    size = (width, height)

    # 4. Initialize the Video Writer (mp4v codec)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, size)

    # 5. Process each frame
    for i, frame_name in enumerate(frames):
        frame_path = os.path.join(input_folder, frame_name)
        img = cv2.imread(frame_path)
        
        # Run YOLOv8 inference. We focus on class 0 ('person') for the folks walking.
        results = model.predict(source=img, classes=[0], verbose=False)
        
        # Plot the bounding boxes and confidence scores directly onto the frame
        annotated_frame = results[0].plot()
        
        # Write the annotated frame to the video
        out.write(annotated_frame)
        
        # Simple progress tracker
        if i % 50 == 0:
            print(f"Processed {i}/{len(frames)} frames...")

    out.release()
    print(f"Successfully saved annotated video to {output_path}\n")

if __name__ == "__main__":
    # Define absolute paths based on your machine
    thermal_dir = 'assets/1a'
    color_dir = 'assets/1b'
    
    # Ensure assets directory exists for outputs
    os.makedirs('assets', exist_ok=True)
    
    thermal_output = 'assets/thermal_processed.mp4'
    color_output = 'assets/color_processed.mp4'
    
    # Execute the processing pipeline
    process_frames_to_video(thermal_dir, thermal_output)
    process_frames_to_video(color_dir, color_output)