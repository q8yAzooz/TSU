console_archiver.py

Консольная утилита архиватор/распаковщик.

Только стандартная библиотека Python 3.14.

Поддерживаемые алгоритмы:

- bz2  (встроенный модуль)
- zstd (через внешний бинарник `zstd`, вызывается с помощью subprocess)

Если источник — директория, предварительно используется tarfile.

Режим (архивация / распаковка) и алгоритм определяются по расширению:

- .bz2
- .zst

Примеры:

  Архивация файла:

    python console_archiver.py input.txt output.bz2

  Архивация директории:

    python console_archiver.py mydir archive.tar.zst

  Распаковка:

    python console_archiver.py archive.tar.bz2 .

  Benchmark:

    python console_archiver.py input.txt output.zst --benchmark

  С прогресс-баром:

    python console_archiver.py input.txt output.bz2 --progress
