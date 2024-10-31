import os
import cv2


# Função para criar diretório se ele não existir
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


# Função para ler as labels YOLO e converter em coordenadas ajustadas após a rotação
def rotate_yolo_coordinates(x_center, y_center, width, height, angle):
    if angle == 270:
        return (y_center, 1 - x_center, height, width)
    elif angle == 180:
        return (1 - x_center, 1 - y_center, width, height)
    elif angle == 90:
        return (1 - y_center, x_center, height, width)
    else:
        return (x_center, y_center, width, height)


# Função para rotacionar a imagem
def rotate_image(image, angle):
    if angle == 90:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(image, cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return image


# Caminhos das imagens e labels
image_dir = r"C:\TCC\Treinamento\data_deteccao_objeto_320_teste_iluminacao_led\images"
label_dir = r"C:\TCC\Treinamento\data_deteccao_objeto_320_teste_iluminacao_led\labels"
output_image_dir = r"C:\TCC\Treinamento\data_deteccao_objeto_320_teste_iluminacao_led\images\images"
output_label_dir = r"C:\TCC\Treinamento\data_deteccao_objeto_320_teste_iluminacao_led\labels\labels"

# Criar os diretórios de saída, se não existirem
ensure_dir(output_image_dir)
ensure_dir(output_label_dir)

# Angulos de rotação
angles = [90, 180, 270]

# Loop pelas imagens no diretório
for image_file in os.listdir(image_dir):
    if image_file.endswith(".jpg"):
        image_path = os.path.join(image_dir, image_file)
        label_path = os.path.join(label_dir, image_file.replace(".jpg", ".txt"))

        # Ler a imagem
        image = cv2.imread(image_path)

        # Verificar se o rótulo existe
        if not os.path.exists(label_path):
            continue

        # Ler o arquivo de rótulo
        with open(label_path, 'r') as f:
            lines = f.readlines()

        # Para cada ângulo de rotação
        for angle in angles:
            # Rotacionar a imagem
            rotated_image = rotate_image(image, angle)

            # Salvar a nova imagem rotacionada
            rotated_image_name = image_file.replace(".jpg", f"_{angle}.jpg")
            cv2.imwrite(os.path.join(output_image_dir, rotated_image_name), rotated_image)

            # Processar o arquivo de rótulo correspondente
            rotated_label_name = image_file.replace(".jpg", f"_{angle}.txt")
            with open(os.path.join(output_label_dir, rotated_label_name), 'w') as f:
                for line in lines:
                    parts = line.strip().split()
                    class_id = parts[0]
                    x_center, y_center, width, height = map(float, parts[1:])

                    # Calcular novas coordenadas para a rotação
                    new_x_center, new_y_center, new_width, new_height = rotate_yolo_coordinates(
                        x_center, y_center, width, height, angle
                    )

                    # Escrever as novas coordenadas no arquivo de rótulo
                    f.write(f"{class_id} {new_x_center:.6f} {new_y_center:.6f} {new_width:.6f} {new_height:.6f}\n")

print("Imagens e labels rotacionadas geradas com sucesso!")
