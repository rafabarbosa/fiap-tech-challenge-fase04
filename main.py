import cv2
import numpy as np
from deepface import DeepFace
import mediapipe as mp
import time
from collections import defaultdict

class ActivityDetector:
    def __init__(self):
        self.activities = {
            'standing': self.is_standing,
            'sitting': self.is_sitting,
            'walking': self.is_walking,
            'raising_arms': self.is_raising_arms
        }
        self.previous_positions = []
        
    def is_standing(self, landmarks):
        # Verifica se a pessoa está em pé baseado na posição vertical dos quadris e joelhos
        hip_y = landmarks[24].y  # Quadril direito
        knee_y = landmarks[26].y  # Joelho direito
        ankle_y = landmarks[28].y  # Tornozelo direito
        return knee_y > hip_y and ankle_y > knee_y and (ankle_y - hip_y) > 0.3
    
    def is_sitting(self, landmarks):
        # Verifica se a pessoa está sentada baseado na posição relativa dos quadris e joelhos
        hip_y = landmarks[24].y  # Quadril direito
        knee_y = landmarks[26].y  # Joelho direito
        return abs(hip_y - knee_y) < 0.2
    
    def is_walking(self, landmarks):
        if len(self.previous_positions) < 5:
            return False
        
        # Calcula o movimento horizontal dos quadris
        current_hip_x = landmarks[24].x
        movement = abs(current_hip_x - self.previous_positions[-1])
        return movement > 0.01
    
    def is_raising_arms(self, landmarks):
        # Verifica se os braços estão levantados acima dos ombros
        shoulder_y = (landmarks[11].y + landmarks[12].y) / 2  # Média dos ombros
        wrist_y = (landmarks[15].y + landmarks[16].y) / 2     # Média dos pulsos
        return wrist_y < shoulder_y
    
    def detect_activity(self, landmarks):
        if not landmarks:
            return 'unknown'
        
        # Atualiza posições anteriores para detecção de movimento
        self.previous_positions.append(landmarks[24].x)
        if len(self.previous_positions) > 10:
            self.previous_positions.pop(0)
        
        # Verifica cada atividade e retorna a primeira detectada
        for activity, detector in self.activities.items():
            if detector(landmarks):
                return activity
        
        return 'unknown'

class VideoAnalyzer:
    def __init__(self, video_path):
        self.video_path = video_path
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.total_frames = 0
        self.anomalies = 0
        self.emotion_history = defaultdict(int)
        self.activity_history = defaultdict(int)
        self.previous_poses = []
        self.activity_detector = ActivityDetector()
        
    def detect_anomaly(self, current_pose, threshold=50):
        """Detecta movimentos bruscos comparando poses consecutivas"""
        if len(self.previous_poses) < 2:
            return False
        
        # Calcula a diferença média de movimento
        movement = np.mean(np.abs(current_pose - self.previous_poses[-1]))
        avg_movement = np.mean([np.mean(np.abs(self.previous_poses[i] - self.previous_poses[i-1])) 
                              for i in range(1, len(self.previous_poses))])
        
        # Se o movimento atual for muito maior que a média, é considerado anômalo
        return movement > (avg_movement * threshold)

    def analyze_video(self):
        cap = cv2.VideoCapture(self.video_path)
        
        # Configurar o writer para salvar o vídeo processado
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter('output.mp4', 
                            fourcc, 
                            cap.get(cv2.CAP_PROP_FPS),
                            (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                             int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
        
        with self.mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection, \
             self.mp_pose.Pose(min_detection_confidence=0.5) as pose_detection:
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                self.total_frames += 1
                print(f"Processando frame {self.total_frames}", end='\r')
                
                # Converte BGR para RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detecção facial e análise de emoções
                face_results = face_detection.process(rgb_frame)
                if face_results.detections:
                    for detection in face_results.detections:
                        bbox = detection.location_data.relative_bounding_box
                        h, w, _ = frame.shape
                        x, y, width, height = int(bbox.xmin * w), int(bbox.ymin * h), \
                                           int(bbox.width * w), int(bbox.height * h)
                        
                        # Análise de emoções usando DeepFace
                        try:
                            emotion_analysis = DeepFace.analyze(frame, 
                                                              actions=['emotion'],
                                                              enforce_detection=False)
                            dominant_emotion = emotion_analysis[0]['dominant_emotion']
                            self.emotion_history[dominant_emotion] += 1
                            
                            # Adicionar texto com a emoção no frame
                            cv2.putText(frame, f"Emotion: {dominant_emotion}", (10, 90),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        except Exception as e:
                            print(f"Erro na análise de emoção: {str(e)}")
                        
                        # Desenha retângulo ao redor do rosto
                        cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 2)
                
                # Detecção de pose e atividades
                pose_results = pose_detection.process(rgb_frame)
                if pose_results.pose_landmarks:
                    # Desenha os pontos do esqueleto
                    self.mp_drawing.draw_landmarks(
                        frame, pose_results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
                    
                    # Detecta atividade atual
                    current_activity = self.activity_detector.detect_activity(
                        pose_results.pose_landmarks.landmark)
                    self.activity_history[current_activity] += 1
                    
                    # Adiciona texto com a atividade detectada
                    cv2.putText(frame, f"Activity: {current_activity}", (10, 60),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
                    
                    pose_array = np.array([[lm.x, lm.y, lm.z] for lm in pose_results.pose_landmarks.landmark])
                    
                    # Detecta anomalias
                    if self.detect_anomaly(pose_array):
                        self.anomalies += 1
                        # Adicionar indicador visual de anomalia
                        cv2.putText(frame, "ANOMALIA DETECTADA!", (10, 30),
                                  cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    
                    self.previous_poses.append(pose_array)
                    if len(self.previous_poses) > 10:  # Mantém histórico limitado
                        self.previous_poses.pop(0)
                
                # Salvar o frame processado
                out.write(frame)
        
        cap.release()
        out.release()
        
        return self.generate_report()
    
    def generate_report(self):
        """Gera relatório com as análises"""
        report = {
            "total_frames": self.total_frames,
            "anomalies_detected": self.anomalies,
            "emotion_summary": dict(self.emotion_history),
            "activity_summary": dict(self.activity_history)
        }
        return report

def main():
    print("Iniciando análise do vídeo...")
    video_analyzer = VideoAnalyzer("video.mp4")
    report = video_analyzer.analyze_video()
    
    # Imprime relatório
    print("\n=== RELATÓRIO DE ANÁLISE DE VÍDEO ===")
    print(f"Total de frames analisados: {report['total_frames']}")
    print(f"Número de anomalias detectadas: {report['anomalies_detected']}")
    
    print("\nDistribuição de emoções detectadas:")
    for emotion, count in report['emotion_summary'].items():
        print(f"- {emotion}: {count}")
    
    print("\nDistribuição de atividades detectadas:")
    for activity, count in report['activity_summary'].items():
        print(f"- {activity}: {count}")
    
    print("\nVídeo processado salvo como 'output.mp4'")

if __name__ == "__main__":
    main()