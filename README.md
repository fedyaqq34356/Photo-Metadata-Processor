# 📸 Photo Metadata Processor

A batch photo processor with micro-modifications and Android EXIF injection. Applies subtle changes to bypass duplicate detection while maintaining visual quality. Built with PIL/Pillow and piexif.

## ✨ Key Features

* Micro-modifications (crop, shift, rotate, brightness, contrast)
* Android EXIF injection (Google Pixel, Samsung, OnePlus, Xiaomi)
* Timestamp randomization (±7 days)
* GPS removal option
* Batch processing up to 200 files
* ZIP archive with manifest.csv
* Shows only changed EXIF fields

## 🚀 Installation
```bash
git clone https://github.com/your-username/photo-metadata-processor.git
cd photo-metadata-processor
pip install -r requirements.txt
```

**Run the Processor**
```bash
python script.py
```

Place JPG files in `photo/` folder and choose processing mode (1-3). The script will create `Processed/` folder with output files or ZIP archive.

## 📊 Example Output
```
File: photo_001.jpg
  DateTime: 2025:12:18 10:30:45 → 2025:12:22 15:22:11
  Make: Apple → Samsung
  Model: iPhone 12 → Galaxy S22

Готово: photo_001.jpg
```

## 📄 License

GPL-3.0 license

## ⭐ If you find this project useful, consider giving it a star! Happy processing! 🚀