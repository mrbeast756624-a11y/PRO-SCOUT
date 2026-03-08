import streamlit as st
import cv2
from ultralytics import YOLO
import tempfile
import random
import base64  # <--- ADD THIS NEW IMPORT

st.set_page_config(page_title="PRO SCOUT", page_icon="🏆", layout="wide")

# --- CUSTOM BACKGROUND CODE ---
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/{"jpg"};base64,{encoded_string.decode()});
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        /* This makes the background slightly darker so your text is easier to read */
        .stApp:before {{
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(0, 0, 0, 0.6); 
            z-index: -1;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Change "bgmi_bg.jpg" to whatever you named your downloaded image!
add_bg_from_local('bgmi_bg.jpg')
# ------------------------------

st.title("PRO SCOUT: AI Esports Analyst")
st.markdown("Advanced Tier-1 Tactical Analysis for Competitive BGMI Athletes.")
st.divider()

with st.sidebar:
    st.header("Coach Settings")
    st.selectbox("Select Analysis Mode", ["Basic", "T1 Scrim Analysis"])
    conf_slider = st.slider("AI Confidence Threshold (%)", 0, 100, 30)

@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")

model = load_model()

uploaded_video = st.file_uploader("Upload Gameplay Video (.mp4, .mov)", type=["mp4", "mov"])

if uploaded_video is not None:
    st.success("Video uploaded successfully! The AI Engine is ready to deploy.")
    
    if st.button("Deploy Pro Scout AI"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            stframe = st.empty()
            
        with col2:
            st.markdown("### 📊 Live Match Stats")
            target_metric = st.empty()
            coach_alert = st.empty()
        
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_video.read())
        cap = cv2.VideoCapture(tfile.name)
        
        ai_confidence = conf_slider / 100.0
        
        # --- ADVANCED PRO METRICS TRACKERS ---
        frames_in_combat = 0
        max_enemies_faced = 0
        current_exposure_streak = 0
        max_exposure_streak = 0
        crossfire_frames = 0
        cqc_threats_detected = False

        frame_count = 0  # <--- 1. We start the counter here

        while cap.isOpened():
            success, frame = cap.read()
            
            # <--- 2. We check if the video is over first
            if not success:
                break
                
            frame_count += 1
            
            # <--- 3. We skip frames to stop the server from freezing
            if frame_count % 3 != 0:
                continue
            
            # The rest of your AI logic continues normally below this
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            frame_width = small_frame.shape[1]
            frame_area = small_frame.shape[0] * small_frame.shape[1]
                
            results = model.predict(source=small_frame, conf=ai_confidence, verbose=False,)
                
            players_in_sight = 0
            has_cover = False
            left_side_threats = 0
            right_side_threats = 0
                
            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                coords = box.xyxy[0].tolist()
                
                if cls_id == 0:
                    players_in_sight += 1
                    box_width = coords[2] - coords[0]
                    box_height = coords[3] - coords[1]
                    box_area = box_width * box_height
                    center_x = (coords[0] + coords[2]) / 2
                    
                    if box_area > (frame_area * 0.05):
                        cqc_threats_detected = True
                        
                    if center_x < (frame_width / 2):
                        left_side_threats += 1
                    else:
                        right_side_threats += 1
                        
                elif cls_id in [2, 5, 7]:
                    has_cover = True
            
            if players_in_sight > 0:
                frames_in_combat += 1
                if players_in_sight > max_enemies_faced:
                    max_enemies_faced = players_in_sight
                
                if left_side_threats > 0 and right_side_threats > 0:
                    crossfire_frames += 1
                
                if not has_cover:
                    current_exposure_streak += 1
                    if current_exposure_streak > max_exposure_streak:
                        max_exposure_streak = current_exposure_streak
                else:
                    current_exposure_streak = 0
            
            target_metric.metric(label="Active Threats", value=players_in_sight)
            
            if left_side_threats > 0 and right_side_threats > 0:
                coach_alert.warning("🚨 PINCH DETECTED: Angle Split.")
            else:
                coach_alert.empty()
            
            annotated_frame = results[0].plot()
            final_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            stframe.image(final_frame, channels="RGB", use_container_width=True)
        
        cap.release()
        
        # --- THE MASSIVE BRAIN BANK (DYNAMIC LOGIC) ---
        st.divider()
        st.header("🧠 PRO SCOUT: TIER 1 DEBRIEF")
        
        is_wide_swinging = max_exposure_streak > 15
        is_1vX = max_enemies_faced > 1
        
        # Core Banks (These apply to every fight)
        base_exec = [
            "🎯 **Target Acquisition:** Excellent reaction time. You immediately acquired targets upon visual contact.",
            "⚡ **First Contact:** You successfully generated engagement momentum, forcing the enemy to react to you.",
            "🔭 **Crosshair Placement:** You kept your crosshair pre-aimed at head-level during the engagement.",
            "💪 **Aggression & Pacing:** High-value aggressive playstyle. You dictate the pace of the fight.",
            "🛡️ **Damage Output:** The opening damage and knocks you provided are what win tournaments. Great raw mechanics."
        ]
        base_vuln = [
            "⏱️ **Extended TTK Exposure:** Staying scoped in for prolonged seconds invites third-party flanks.",
            "🔄 **Failure to Re-Anchor:** After the initial engagement, you stayed in the exact same spot. Predictability is lethal.",
            "👁️ **Tunnel Vision:** Hyper-focusing on one target rather than instantly scanning for the trade-fragger.",
            "🏃 **Movement Predictability:** Lack of vertical/horizontal mix-ups (crouch/prone) during the spray transfer.",
            "🛡️ **Utility Negligence:** Engaging in a raw aim duel without prepping the area with throwables first."
        ]
        base_playbook = [
            "📘 **The 'Rule of 3 Seconds':** If you haven't killed them in 3 seconds of spraying, drop cover, reload, and change angles.",
            "📘 **Post-Knock Rotation:** The millisecond you get a knock, assume a nade is flying at you. Relocate immediately.",
            "📘 **Pre-Fire Discipline:** Always fire 2-3 bullets before your crosshair fully clears the corner.",
            "📘 **Information Gathering:** Use the TPP camera advantage to gather info before ever exposing your hitbox.",
            "📘 **Ammo Management:** Do not instantly reload after a knock if you have 15+ bullets left; hold the angle for the trade."
        ]

        # Context-Specific Additions based on the AI's math
        if is_1vX:
            base_exec.extend([
                f"🔥 **Clutch Mentality:** You didn't back down from a {max_enemies_faced}-man disadvantage. Massive entry-fragging potential.",
                "⚔️ **Angle Isolation:** You attempted to break down a multi-man push into a series of 1v1s."
            ])
            base_playbook.append("📘 **Clutch Isolation:** In a 1vX, drop smokes at your feet to physically block the line-of-sight of the 2nd and 3rd pushers.")

        if is_wide_swinging:
            base_vuln.extend([
                f"⚠️ **Lethal Wide-Swings:** You committed to an open angle for {max_exposure_streak} consecutive frames out of cover.",
                "⚠️ **Over-Commitment:** Pushing entirely out of cover to secure a thirst/finish, exposing yourself to the whole map."
            ])
            base_playbook.append("📘 **The Jiggle Peek Drill:** Never commit to a spray in the open. Pre-fire the corner, deal chip damage, and instantly un-peek (desync advantage).")
        else:
            base_exec.append("🧱 **Micro-Peeking Efficiency:** Excellent exposure management. You kept your peek windows tight, denying pre-aimed headshots.")

        if crossfire_frames > 5:
            base_vuln.extend([
                "📐 **Pinching Vulnerability:** You remained aimed-in while enemies occupied both left and right sectors. You gave them a free crossfire.",
                "🛑 **Positional Trap:** You allowed the enemy squad to take spatial control and surround your hard cover."
            ])
            base_playbook.append("📘 **Dynamic Repositioning:** When an angle split is detected, immediately drop smoke and rotate to the flank to stack their pushes.")

        if cqc_threats_detected:
            base_exec.append("💥 **CQC Composure:** You maintained mechanical discipline when the enemy crashed your personal space.")
            base_vuln.append("🏃 **Panic Retreat:** Walking backward while shooting in CQC ruins your movement speed and spray accuracy.")

        # Safely sample exactly 5 unique points for the final output
        final_exec = random.sample(base_exec, min(5, len(base_exec)))
        final_vuln = random.sample(base_vuln, min(5, len(base_vuln)))
        final_playbook = random.sample(base_playbook, min(5, len(base_playbook)))

        col_right, col_wrong, col_advice = st.columns(3)
        
        with col_right:
            st.subheader("✅ Execution")
            if frames_in_combat == 0:
                st.info("No combat detected.")
            else:
                for point in final_exec:
                    st.success(point)
                
        with col_wrong:
            st.subheader("❌ Vulnerabilities")
            if frames_in_combat == 0:
                st.info("No combat detected.")
            else:
                for point in final_vuln:
                    st.error(point)
                
        with col_advice:
            st.subheader("📋 The Playbook")
            if frames_in_combat == 0:
                st.info("No combat detected.")
            else:
                for point in final_playbook:

                    st.info(point)

