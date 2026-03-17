import argparse
import bz2
import os
import sys
import tarfile
import tempfile
import time
import zstandard as zstd
from pathlib import Path
from typing import Optional


# ---------- Утилиты ----------

def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}PB"


def print_progress(done: int, total: int):
    width = 30
    ratio = done / total if total else 1.0
    filled = int(width * ratio)
    bar = "#" * filled + "-" * (width - filled)
    percent = ratio * 100
    sys.stdout.write(f"\r[{bar}] {percent:6.2f}% ({human_size(done)}/{human_size(total)})")
    sys.stdout.flush()


# ---------- TAR ----------

def make_tar(src: Path, tar_path: Path):
    with tarfile.open(tar_path, "w") as tf:
        tf.add(src, arcname=src.name)


def extract_tar(tar_path: Path, dst: Path):
    with tarfile.open(tar_path, "r") as tf:
        tf.extractall(dst)


# ---------- BZ2 ----------

def compress_bz2(src: Path, dst: Path, progress: bool):
    total = src.stat().st_size
    done = 0

    with open(src, "rb") as fin, bz2.open(dst, "wb") as fout:
        while True:
            chunk = fin.read(1024 * 1024)
            if not chunk:
                break
            fout.write(chunk)
            if progress:
                done += len(chunk)
                print_progress(done, total)

    if progress:
        print()


def decompress_bz2(src: Path, dst: Path, progress: bool):
    total = src.stat().st_size
    done = 0

    with bz2.open(src, "rb") as fin, open(dst, "wb") as fout:
        while True:
            chunk = fin.read(1024 * 1024)
            if not chunk:
                break
            fout.write(chunk)
            if progress:
                done += len(chunk)
                print_progress(done, total)

    if progress:
        print()


# ---------- ZSTD (через стандартную библиотеку Python 3.14) ----------

def compress_zstd(src: Path, dst: Path, progress: bool, compression_level: int = 3):
    """
    Сжатие с использованием zstd из стандартной библиотеки
    compression_level: 1-22 (по умолчанию 3)
    """
    total = src.stat().st_size
    done = 0
    
    cctx = zstd.ZstdCompressor(level=compression_level)
    
    with open(src, "rb") as fin, open(dst, "wb") as fout:
        compressor = cctx.stream_writer(fout)
        while True:
            chunk = fin.read(1024 * 1024)
            if not chunk:
                break
            compressor.write(chunk)
            if progress:
                done += len(chunk)
                print_progress(done, total)
        
        compressor.flush(zstd.FLUSH_FRAME)
    
    if progress:
        print()


def decompress_zstd(src: Path, dst: Path, progress: bool):
    """
    Распаковка с использованием zstd из стандартной библиотеки
    """
    total = src.stat().st_size
    done = 0
    
    dctx = zstd.ZstdDecompressor()
    
    with open(src, "rb") as fin, open(dst, "wb") as fout:
        decompressor = dctx.stream_reader(fin)
        while True:
            chunk = decompressor.read(1024 * 1024)
            if not chunk:
                break
            fout.write(chunk)
            if progress:
                done += min(len(chunk), 1024 * 1024) 
                print_progress(done, total)
    
    if progress:
        print()


def get_zstd_info(src: Path) -> dict:
    """
    Получение информации о zstd-файле (сжатый/несжатый размер, уровень сжатия)
    """
    with open(src, "rb") as f:
        header = zstd.get_frame_parameters(f.read(30))
        
        return {
            "content_size": header.content_size,
            "window_size": header.window_size,
            "dict_id": header.dict_id,
            "has_checksum": header.has_checksum,
        }


# ---------- Основная логика ----------

def main():
    parser = argparse.ArgumentParser(
        description="Консольный архиватор / распаковщик (bz2, zstd из Python 3.14)"
    )
    parser.add_argument("source", type=Path, help="Источник (файл или директория)")
    parser.add_argument("target", type=Path, help="Целевой файл или директория")
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Показать время выполнения"
    )
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Показать прогресс-бар"
    )
    parser.add_argument(
        "--level",
        type=int,
        default=3,
        choices=range(1, 23),
        help="Уровень сжатия для zstd (1-22, по умолчанию 3)"
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Показать информацию о zstd-файле (только для .zst)"
    )

    args = parser.parse_args()

    start = time.perf_counter()

    src = args.source
    dst = args.target

    if not src.exists():
        sys.exit("Источник не существует")

    # -------- Информация о zstd-файле --------
    if args.info and src.suffix == ".zst":
        try:
            info = get_zstd_info(src)
            print(f"Информация о файле {src}:")
            print(f"  Размер содержимого: {human_size(info['content_size'])}")
            print(f"  Размер окна: {info['window_size']} байт")
            print(f"  ID словаря: {info['dict_id']}")
            print(f"  Контрольная сумма: {'есть' if info['has_checksum'] else 'нет'}")
        except Exception as e:
            print(f"Не удалось получить информацию: {e}")
        return

    # -------- Архивация --------
    if dst.suffix in (".bz2", ".zst"):
        if src.is_dir():
            with tempfile.TemporaryDirectory() as tmpdir:
                tar_path = Path(tmpdir) / (src.name + ".tar")
                print(f"Создание tar-архива {src.name}.tar...")
                make_tar(src, tar_path)

                if dst.suffix == ".bz2":
                    compress_bz2(tar_path, dst, args.progress)
                else:  
                    compress_zstd(tar_path, dst, args.progress, args.level)
        else:
            if dst.suffix == ".bz2":
                compress_bz2(src, dst, args.progress)
            else:  
                compress_zstd(src, dst, args.progress, args.level)

        if args.benchmark:
            elapsed = time.perf_counter() - start
            print(f"Сжатие завершено за {elapsed:.3f} сек.")

    # -------- Распаковка --------
    elif src.suffix in (".bz2", ".zst"):
        dst.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpfile = Path(tmpdir) / src.stem

            if src.suffix == ".bz2":
                decompress_bz2(src, tmpfile, args.progress)
            else:  
                decompress_zstd(src, tmpfile, args.progress)

            if tmpfile.exists() and tarfile.is_tarfile(tmpfile):
                print(f"Распаковка tar-архива в {dst}...")
                extract_tar(tmpfile, dst)
            elif tmpfile.exists():
                final = dst / tmpfile.name
                tmpfile.replace(final)
                print(f"Распаковано в {final}")
            else:
                sys.exit("Ошибка: файл после распаковки не найден")

        if args.benchmark:
            elapsed = time.perf_counter() - start
            print(f"Распаковка завершена за {elapsed:.3f} сек.")

    else:
        sys.exit("Не удалось определить режим по расширению файла. Используйте .bz2 или .zst")


if __name__ == "__main__":
    main()