import os
import random
import datetime
import zipfile
import csv
from PIL import Image, ImageEnhance, ExifTags
import piexif

def apply_micro_changes(img):
    ops = []
    for op in random.sample(['crop', 'shift', 'rotate', 'brightness', 'contrast'], random.randint(2, 4)):
        if op == 'crop':
            w, h = img.size
            c = random.choice([1, 2])
            l, t = random.randint(0, c), random.randint(0, c)
            img = img.crop((l, t, w - (c - l), h - (c - t)))
            ops.append(f'crop_{c}px')
        elif op == 'shift':
            img = img.transform(img.size, Image.AFFINE, (1, 0, random.uniform(-1, 1), 0, 1, random.uniform(-1, 1)), resample=Image.BICUBIC)
            ops.append('shift')
        elif op == 'rotate':
            img = img.rotate(random.uniform(-0.3, 0.3), resample=Image.BICUBIC, expand=False)
            ops.append('rotate')
        elif op == 'brightness':
            img = ImageEnhance.Brightness(img).enhance(random.uniform(0.95, 1.05))
            ops.append('brightness')
        elif op == 'contrast':
            img = ImageEnhance.Contrast(img).enhance(random.uniform(0.95, 1.05))
            ops.append('contrast')
    return img, ops

def generate_exif_bytes(original_exif, output_name, remove_gps):
    exif_dict = piexif.load(original_exif) if original_exif else {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    now = datetime.datetime.now()
    dt_str = (now + datetime.timedelta(days=random.randint(-7, 7), hours=random.randint(-12, 12), minutes=random.randint(-30, 30))).strftime("%Y:%m:%d %H:%M:%S")
    exif_dict['0th'][piexif.ImageIFD.DateTime] = dt_str.encode()
    exif_dict['0th'][piexif.ImageIFD.ImageDescription] = output_name.encode()
    make, model = random.choice([('Google', 'Pixel 6'), ('Google', 'Pixel 7'), ('Google', 'Pixel 8'), ('Samsung', 'Galaxy S21'), ('Samsung', 'Galaxy S22'), ('Samsung', 'Galaxy S23'), ('OnePlus', '9 Pro'), ('OnePlus', '10 Pro'), ('Xiaomi', 'Mi 11'), ('Xiaomi', '13')])
    exif_dict['0th'][piexif.ImageIFD.Make] = make.encode()
    exif_dict['0th'][piexif.ImageIFD.Model] = model.encode()
    if remove_gps and 'GPS' in exif_dict:
        exif_dict['GPS'] = {}
    return piexif.dump(exif_dict)

def get_exif_info(img_path):
    try:
        img = Image.open(img_path)
        info = {}
        exif_data = img._getexif()
        if exif_data:
            for tag_id, value in exif_data.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                info[tag] = "<binary>" if isinstance(value, bytes) else value
        return info
    except:
        return {}

def print_exif_comparison(original_path, processed_path):
    print(f"\nФайл: {os.path.basename(original_path)}")
    orig, proc = get_exif_info(original_path), get_exif_info(processed_path)
    changed = {k: (orig.get(k, "Нет"), proc.get(k, "Нет")) for k in set(orig.keys()) | set(proc.keys()) if orig.get(k) != proc.get(k)}
    if changed:
        for k, (old, new) in changed.items():
            print(f"  {k}: {old} → {new}")
    else:
        print("  Изменений нет")

def process_files(files, input_dir, output_dir, remove_gps):
    os.makedirs(output_dir, exist_ok=True)
    batch_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if len(files) == 1:
        old_name = files[0]
        img = Image.open(os.path.join(input_dir, old_name))
        img, ops = apply_micro_changes(img)
        exif_bytes = generate_exif_bytes(img.info.get('exif'), old_name[:-4], remove_gps)
        output_path = os.path.join(output_dir, old_name)
        img.save(output_path, 'JPEG', quality=random.randint(90, 98), exif=exif_bytes, optimize=True)
        print_exif_comparison(os.path.join(input_dir, old_name), output_path)
        print(f"Готово: {old_name}")
    else:
        temp_dir = os.path.join(output_dir, f"temp_{batch_id}")
        os.makedirs(temp_dir, exist_ok=True)
        zip_path = os.path.join(output_dir, f"{batch_id}.zip")
        manifest, used = [], set()
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for old_name in files:
                num = random.randint(145, 8000)
                while num in used:
                    num = random.randint(145, 8000)
                used.add(num)
                new_name = f"IMG_{num}.jpg"
                
                img = Image.open(os.path.join(input_dir, old_name))
                img, ops = apply_micro_changes(img)
                exif_bytes = generate_exif_bytes(img.info.get('exif'), new_name[:-4], remove_gps)
                temp_path = os.path.join(temp_dir, new_name)
                img.save(temp_path, 'JPEG', quality=random.randint(90, 98), exif=exif_bytes, optimize=True)
                zf.write(temp_path, new_name)
                manifest.append([old_name, new_name, ','.join(ops), 'real_android' if not remove_gps else 'real_android_no_gps'])
                print_exif_comparison(os.path.join(input_dir, old_name), temp_path)
            
            manifest_path = os.path.join(temp_dir, "manifest.csv")
            with open(manifest_path, 'w', newline='', encoding='utf-8') as cf:
                csv.writer(cf).writerows([['old_name', 'new_name', 'ops', 'exif_policy']] + manifest)
            zf.write(manifest_path, 'manifest.csv')
        
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))
        os.rmdir(temp_dir)
        print(f"\nАрхив: {zip_path}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(script_dir, "photo")
    output_dir = os.path.join(script_dir, "Processed")
    
    if not os.path.exists(input_dir):
        return print("Создайте папку 'photo' и добавьте JPG-файлы")
    
    files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(('.jpg', '.jpeg'))])
    if not files:
        return print("Нет JPG-файлов в папке 'photo'")
    if len(files) > 200:
        return print("Максимум 200 файлов за раз")
    
    print(f"Найдено {len(files)} фото\n1. Полная обработка\n2. Обработка + удаление GPS\n3. Только переименование")
    choice = input("\nВыбор (1-3): ").strip()
    
    if choice == "3":
        batch_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_path = os.path.join(output_dir, f"{batch_id}_only_rename.zip")
        os.makedirs(output_dir, exist_ok=True)
        used = set()
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for old_name in files:
                num = random.randint(145, 8000)
                while num in used:
                    num = random.randint(145, 8000)
                used.add(num)
                zf.write(os.path.join(input_dir, old_name), f"IMG_{num}.jpg")
        return print(f"Архив: {zip_path}")
    
    if choice in ["1", "2"]:
        process_files(files, input_dir, output_dir, choice == "2")
    else:
        print("Неверный выбор")

if __name__ == "__main__":
    main()