import time
import cv2
from ultralytics import YOLO
import RPi.GPIO as GPIO
from hx711 import HX711
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.image import Image


# salvar o fator de escala em um arquivo .txt
def save_scale_ratio(scale_ratio, file_name='scale_ratio.txt'):
    with open(file_name, 'w') as file:
        file.write(str(scale_ratio))
    print(f"Fator de escala salvo: {scale_ratio}")


# carregar o fator de escala salvo
def load_scale_ratio(file_name='scale_ratio.txt'):
    try:
        with open(file_name, 'r') as file:
            return float(file.read())
    except FileNotFoundError:
        print(f"Arquivo {file_name} nÃ£o encontrado. Calibrando novamente.")
        return None


# ConfiguraÃ§Ã£o da balanÃ§a
GPIO.setmode(GPIO.BCM)
hx = HX711(dout_pin=6, pd_sck_pin=5)

# Tentar carregar o fator de escala
scale_ratio = load_scale_ratio()

# Tara a bandeja ao iniciar
hx.zero()

# Se o fator de escala nÃ£o for encontrado, fazer a calibraÃ§Ã£o
if scale_ratio is None:

    # input("Precione ENTER para tarar a bandeja")
    hx.zero()
    input("Precione ENTER para tarar a bandeja")
    input("Por favor, coloque um peso conhecido na balanÃ§a e precione ENTER.")
    leitura = hx.get_data_mean(readings=100)
    peso_em_gramas = float(input("Entre com um peso conhecido em gramas e precione ENTER: "))
    scale_ratio = leitura / peso_em_gramas
    save_scale_ratio(scale_ratio)  # Salva o fator de escala
    hx.set_scale_ratio(scale_ratio)
else:
    hx.set_scale_ratio(scale_ratio)  # Usa o fator de escala salvo

# Carregar o modelo YOLO fora da funÃ§Ã£o update (carregado uma vez)
model = YOLO(
    r'/home/miguel/Yolo/Yolo/TCC_Teste-master/scripts/runs/detect/train_3_yolo11s_150epocas_640escala_2336data/weights/best.pt')

# lista de valores por Kg
precos_por_kg = {
    'BATATA_BOLINHA': 11.99,
    'BATATA_MONALISA': 6.99,
    'BATATINHA_ROSA': 10.99,
    'LARANJA_PERA_RIO': 9.99,
    'MACA_FUJI': 13.99,
    'MACA_PINK': 14.99,
    'MACA_RED': 15.99,
    'TANGERINA': 12.99
}

peso_anterior = None
diferenca_peso_minimo = 6
confidence_minima = 0.70


# Classe principal do Kivy App
class DetectorApp(App):
    def build(self):
        # Layout principal
        self.layout = BoxLayout(orientation='vertical')

        # Labels para exibir o peso e a classe
        self.peso_label = Label(text="Peso: Calculando...", font_size='20sp', size_hint=(1, 0.25))
        self.classe_label = Label(text="Classe: Detectando...", font_size='20sp', size_hint=(1, 0.1))
        self.preco_label = Label(text="Preco: Calculando...", font_size='20sp', size_hint=(1, 0.25))
        self.foto_fruta = Image(source='', size_hint=(0.2, 0.4), pos_hint={'center_x': 0.5})

        # Adicionar labels ao layout
        self.layout.add_widget(self.peso_label)
        self.layout.add_widget(self.classe_label)
        self.layout.add_widget(self.preco_label)
        self.layout.add_widget(self.foto_fruta)

        # Agendar a atualizaÃ§Ã£o dos dados de peso e classe
        Clock.schedule_once(self.monitor_peso)  # Atualiza a cada 0.1 segundos

        return self.layout

    def monitor_peso(self, dt):
        global peso_anterior  # Para manter o valor entre as chamadas de update

        # Capturar o peso atual
        peso_atual = hx.get_weight_mean()

        # Verificar se hÃ¡ uma diferenÃ§a significativa de peso
        if peso_anterior is None or abs(peso_atual - peso_anterior) > diferenca_peso_minimo:

            if abs(peso_atual) < diferenca_peso_minimo:
                self.peso_label.text = f"Peso: {int(0)}  g"
            else:
                self.peso_label.text = f"Peso: {int(peso_atual)} g"

            # Iniciar captura de vÃ­deo apenas quando a diferenÃ§a de peso for suficiente
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 384)
            ret, frame = cap.read()
            cap.release()

            if ret:
                # Realizar a detecÃ§Ã£o de objetos
                results = model(frame, stream=True)

                # verificar se ha deteco
                detections_found = False

                # Atualizar a classe detectada
                for result in results:
                    boxes = result.boxes
                    if len(boxes) > 0:
                        detections_found = True
                        best_box = None
                        highest_confidence = 0
                        for box in boxes:
                            confidence = float(box.conf[0])
                            clss = int(box.cls[0])
                            print(f"Classe: {model.names[clss]}, Confianca: {box.conf}")
                            # print(box.conf[0])
                            if confidence > confidence_minima and confidence > highest_confidence:
                                highest_confidence = confidence
                                best_box = box
                        print(f"Maior Confianca: {highest_confidence}")

                        if best_box:
                            cls = int(best_box.cls[0])
                            self.classe_label.text = f"Classe: {model.names[cls]}"

                            # Calculo do preco
                            preco_quilo = precos_por_kg.get(model.names[cls], 0)
                            preco = (peso_atual / 1000) * preco_quilo
                            self.preco_label.text = f"Preco: R$ {preco:.2f}"

                            # Atualizar a imagem correspondente a fruta
                            caminho_pasta = f"/home/miguel/Yolo/Yolo/TCC_Teste-master/scripts/runs/fotos_carregar/{model.names[cls]}.png"
                            self.foto_fruta.source = caminho_pasta
                            self.foto_fruta.reload()

                if not detections_found or highest_confidence < confidence_minima or abs(
                        peso_atual) < diferenca_peso_minimo:
                    self.classe_label.text = "Nao Detectado, insira o peso novamente."
                    self.preco_label.text = "Preco: --"
                    self.foto_fruta.source = ''

            # Atualizar o peso anterior para a prÃ³xima verificaÃ§Ã£o
            peso_anterior = peso_atual
        # Continuar monitorando o peso
        Clock.schedule_once(self.monitor_peso, 0.1)


# Rodar o aplicativo
if __name__ == "__main__":
    DetectorApp().run()

    # Liberar recursos ao encerrar
    GPIO.cleanup()

