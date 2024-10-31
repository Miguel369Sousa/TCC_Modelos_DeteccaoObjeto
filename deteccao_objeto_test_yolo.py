from ultralytics import YOLO
import matplotlib.pyplot as plt

model = YOLO(r'C:\TCC\Treinamento\runs\detect\train_3_yolo11s_150epocas_640escala_2336data\weights\best.pt')

results = model.val(data=r"C:\TCC\Treinamento\deteccao_objeto_test.yaml",
                    imgsz=640,
                    batch=16,
                    split="test",
                    show=True,
                    save_frames=True,
                    save_txt=True,
                    save_conf=True,
                    save_crop=True
)
