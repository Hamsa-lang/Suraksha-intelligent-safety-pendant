import cv2 
import time 
from flask import Flask, Response 
from ultralytics import YOLO 

# ESP32-CAM stream URL 
STREAM_URL = "http://192.168.1.13/stream" 

# Load YOLOv8 nano for speed 
# Replace with "best.pt" if you have a custom weapon-trained model m
odel = YOLO("yolov8n.pt") 

app = Flask(__name__) 

# Define keywords for weapons 
WEAPON_KEYWORDS = {"knife", "gun", "pistol", "revolver", "rifle", "firearm", "blade", "scissors"} 

def is_weapon(label: str):     
  return any(k in label.lower() for k in WEAPON_KEYWORDS)  
  def gen_frames():    
    cap = cv2.VideoCapture(STREAM_URL)     
    if not cap.isOpened():        
      print("Cannot open stream")         
      return      
      
      frame_count = 0     
      while True:         
        ret, frame = cap.read()         
        if not ret:             
          continue         

          # Skip every other frame for performance         
          frame_count += 1        
          if frame_count % 2 != 0:             
            continue          

            # Resize for faster detection        
            frame = cv2.resize(frame, (320, 240))         

            # YOLO detection         
            results = model(frame)         
            res = results[0]          
            
            if hasattr(res, "boxes") and res.boxes is not None:             
            for i in range(len(res.boxes)):                 
              box = res.boxes[i]                
              xyxy = box.xyxy[0].cpu().numpy() if hasattr(box.xyxy[0], "cpu") else box.xyxy[0]                 
              conf = float(box.conf[0])                 
              cls_index = int(box.cls[0])                 
              class_name = model.names[cls_index] if hasattr(model, "names") else str(cls_index)                  

              # Determine type: face or weapon                 
              if class_name.lower() in ["person", "face"]:                    
                label_type = "Face"                    
                color = (0, 255, 0)  # Green                 
              elif is_weapon(class_name):                     
                label_type = "Weapon"                     
                color = (0, 0, 255)  # Red                 
              else:                     
                continue  # Ignore other classe 
              x1, y1, x2, y2 = map(int, xyxy)                 
              cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)                 
              cv2.putText(frame, f"{label_type} {conf*100:.1f}%",                              
                          (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)         
          # Encode frame as JPEG        
          ret, buffer = cv2.imencode('.jpg', frame)        
          frame_bytes = buffer.tobytes()        
          yield (b'--frame\r\n'               
                 b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')  
          
@app.route('/video_feed') 
def video_feed():    
  return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')  
  
  @app.route('/')
  def index():     
    return """     
    <html>         
    <head><title>ESP32-CAM Detection</title></head>         
    <body style="text-align:center;">             
    <h1>Live Face & Weapon Detection</h1>            
    <img src="/video_feed" width="640" height="480">         
    </body>     
    </html>     
    """  
    if __name__ == "__main__":    
      app.run(host="0.0.0.0", port=5000)                                                                                              Page | 26          WEAPON_KEYWORDS = {"knife", "gun", "pistol", "revolver", "rifle", "firearm", "blade", "scissors"}  def is_weapon(label: str):     return any(k in label.lower() for k in WEAPON_KEYWORDS)  def gen_frames():     cap = cv2.VideoCapture(STREAM_URL)     if not cap.isOpened():         print("Cannot open stream")         return      frame_count = 0     while True:         ret, frame = cap.read()         if not ret:             continue          # Skip every other frame for performance         frame_count += 1         if frame_count % 2 != 0:             continue          # Resize for faster detection         frame = cv2.resize(frame, (320, 240))          # YOLO detection         results = model(frame)         res = results[0]          if hasattr(res, "boxes") and res.boxes is not None:             for i in range(len(res.boxes)):                 box = res.boxes[i]                 xyxy = box.xyxy[0].cpu().numpy() if hasattr(box.xyxy[0], "cpu") else box.xyxy[0]                 conf = float(box.conf[0])                 cls_index = int(box.cls[0])                 class_name = model.names[cls_index] if hasattr(model, "names") else str(cls_index)                  # Determine type: face or weapon                 if class_name.lower() in ["person", "face"]:                     label_type = "Face"                     color = (0, 255, 0)  # Green                 elif is_weapon(class_name):                     label_type = "Weapon"                     color = (0, 0, 255)  # Red                 else:                     continue  # Ignore other classeM
