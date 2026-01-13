import argparse
import bz2
import os
import sys
import tarfile
import tempfile
import time
import subprocess
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


# ---------- ZSTD (через subprocess) ----------

def check_zstd():
    try:
        subprocess.run(["zstd", "--version"],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       check=True)
    except Exception:
        sys.exit("Ошибка: бинарник `zstd` не найден в системе.")


def compress_zstd(src: Path, dst: Path):
    check_zstd()
    with open(dst, "wb") as fout:
        subprocess.run(
            ["zstd", "-q", "-c", str(src)],
            stdout=fout,
            check=True
        )


def decompress_zstd(src: Path, dst: Path):
    check_zstd()
    with open(dst, "wb") as fout:
        subprocess.run(
            ["zstd", "-q", "-d", "-c", str(src)],
            stdout=fout,
            check=True
        )


# ---------- Основная логика ----------

def main():
    parser = argparse.ArgumentParser(
        description="Консольный архиватор / распаковщик (bz2, zstd)"
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
        help="Показать прогресс-бар (для bz2)"
    )

    args = parser.parse_args()

    start = time.perf_counter()

    src = args.source
    dst = args.target

    if not src.exists():
        sys.exit("Источник не существует")

    # -------- Архивация --------
    if dst.suffix in (".bz2", ".zst"):
        # Если источник — директория, сначала tar
        if src.is_dir():
            with tempfile.TemporaryDirectory() as tmpdir:
                tar_path = Path(tmpdir) / (src.name + ".tar")
                make_tar(src, tar_path)

                if dst.suffix == ".bz2":
                    compress_bz2(tar_path, dst, args.progress)
                else:
                    compress_zstd(tar_path, dst)
        else:
            if dst.suffix == ".bz2":
                compress_bz2(src, dst, args.progress)
            else:
                compress_zstd(src, dst)

    # -------- Распаковка --------
    elif src.suffix in (".bz2", ".zst"):
        dst.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpfile = Path(tmpdir) / src.stem

            if src.suffix == ".bz2":
                decompress_bz2(src, tmpfile, args.progress)
            else:
                decompress_zstd(src, tmpfile)

            # Если внутри tar — распаковать
            if tarfile.is_tarfile(tmpfile):
                extract_tar(tmpfile, dst)
            else:
                final = dst / tmpfile.name
                tmpfile.replace(final)

    else:
        sys.exit("Не удалось определить режим по расширению файла")

    if args.benchmark:
        elapsed = time.perf_counter() - start
        print(f"Время выполнения: {elapsed:.3f} сек.")


if __name__ == "__main__":
    main()
