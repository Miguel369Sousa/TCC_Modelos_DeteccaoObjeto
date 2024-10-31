import os
import xml.etree.ElementTree as ET

# Defina as classes que serão usadas no dataset
classes = ['dog', 'person', 'cat', 'tv', 'car', 'meatballs', 'marinara sauce', 'tomato soup']  # Substitua pelas classes reais


def convert_box(size, box):
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[1]) / 2.0 - 1
    y = (box[2] + box[3]) / 2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)


def convert_annotation(xml_path, output_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Tamanho da imagem
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    with open(output_path, 'w') as out_file:
        for obj in root.iter('object'):
            difficult = obj.find('difficult').text
            cls = obj.find('name').text
            if cls not in classes or int(difficult) == 1:
                continue
            cls_id = classes.index(cls)
            xmlbox = obj.find('bndbox')
            b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text),
                 float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
            bb = convert_box((w, h), b)
            out_file.write(f"{cls_id} " + " ".join([str(a) for a in bb]) + '\n')


def convert_all_xml_to_yolo(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith('.xml'):
            xml_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename.replace('.xml', '.txt'))
            convert_annotation(xml_path, output_path)
            print(f"Convertido {filename} para {output_path}")


# Diretórios de entrada e saída
input_dir = r'D:\FOTOS_ILUMINACAO_TRATAR\xml'  # Substitua com o caminho correto
output_dir = r'D:\FOTOS_ILUMINACAO_TRATAR\yolo'  # Substitua com o caminho correto

convert_all_xml_to_yolo(input_dir, output_dir)
