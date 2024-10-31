from ultralytics import YOLO
model = YOLO(r"C:\TCC\Treinamento\yolo11n.pt")

# Inicia o treinamento do modelo com o dataset
model.train(data=r"C:\TCC\Treinamento\deteccao_objeto.yaml", epochs=500, imgsz=640,  optimizer="AdamW", patience=350)