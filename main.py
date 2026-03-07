import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")

# Put your exact video name here!
video_name = "clutch.mov" 
cap = cv2.VideoCapture(video_name)

print("Starting Pro Scout Coach Logic...")

while cap.isOpened():
    success, frame = cap.read()
    if success:
        # Shrink frame to prevent lag
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        
        # Run AI
        results = model.predict(source=small_frame, verbose=False)
        
        # --- NEW: THE COACH LOGIC ENGINE ---
        for box in results[0].boxes:
            # Get what the AI thinks the object is
            class_id = int(box.cls[0])
            object_name = model.names[class_id]
            
            # Only trigger logic if it spots a "person"
            if object_name == "person":
                # Grab the X and Y coordinates of the box
                coords = box.xyxy[0].tolist()
                x_left = int(coords[0]) # How far left the person is
                
                # BASIC RULE: If a person is on the extreme left of your screen
                if x_left < 100:
                    print(f"🚨 COACH WARNING: Enemy flanking on extreme LEFT! (X: {x_left})")
                else:
                    print(f"🎯 Tracking player at X-coordinate: {x_left}")
        # -----------------------------------
                    
        # Show the video
        cv2.imshow("Pro Scout Vision", results[0].plot())
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()