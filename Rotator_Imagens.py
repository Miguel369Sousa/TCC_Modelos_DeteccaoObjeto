import os
from PIL import Image

# Caminho da pasta contendo as imagens
input_folder = r'D:\Downloads\SEM_DETECCAO-20241007T184939Z-001\SEM_DETECCAO'  # Altere para o caminho da sua pasta de imagens

# Criar uma pasta de saída se não existir
output_folder = os.path.join(input_folder, 'rotated_images')
os.makedirs(output_folder, exist_ok=True)


# Função para rotacionar e salvar as imagens
def rotate_and_save(image_path, angle, output_folder):
    # Abrir a imagem
    img = Image.open(image_path)

    # Rotacionar a imagem
    rotated_img = img.rotate(angle, expand=True)

    # Nome do arquivo de saída
    base_name = os.path.basename(image_path)
    name, ext = os.path.splitext(base_name)
    output_path = os.path.join(output_folder, f'{name}_{angle}{ext}')

    # Salvar a imagem rotacionada
    rotated_img.save(output_path)


# Percorrer todos os arquivos na pasta
for filename in os.listdir(input_folder):
    if filename.endswith('.jpg'):
        image_path = os.path.join(input_folder, filename)

        # Rotacionar e salvar em 90, 180 e 270 graus
        for angle in [90, 180, 270]:
            rotate_and_save(image_path, angle, output_folder)

print("Imagens rotacionadas e salvas com sucesso!")