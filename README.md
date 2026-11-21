# polish-fleet-pipeline

Repozytorium zawiera dwie części. Pierwsza to pipeline nad rejestrem pojazdów
CEPiK — 3,21 mln rejestracji wczytanych do DuckDB, oczyszczonych warstwowym
SQL-em, z testami jakości danych i wykresami; pełna przebudowa komendą `./run.sh`.
Druga to opisany poniżej projekt zaliczeniowy w katalogu `profiler/`.

## Profiler plików CSV

Narzędzie, które przechodzi po plikach CSV i liczy, co w nich jest: ile
wierszy, ile pustych wartości w każdej kolumnie, ile wartości unikalnych.
Sprawdza formaty plików i mierzy, ile zajmuje ta sama praca wykonana
sekwencyjnie, na wątkach i na procesach.

Profiler Leży w repozytorium mojego prywatnego projektu analitycznego
`polish-fleet-pipeline` i profiluje jego dane: 3,21 mln rejestracji
pojazdów z CEPiK, wyeksportowanych z bazy pipeline'u do szesnastu plików
CSV, po jednym na województwo, razem 534 MB. Pomiar zrównoleglenia jest
więc zrobiony na prawdziwych danych.

## Uruchomienie

Python 3.14.6, zależności z `requirements.txt`, komendy z katalogu głównego repozytorium.

Najpierw dane testowe — eksport szesnastu plików z bazy `fleet.duckdb`:

    python scripts/export_samples.py

Potem, do wyboru:

    python -m profiler.parallel      # trzy tryby wykonania i pomiar GIL
    python -m profiler.profiling     # profilowanie jednego pliku
    python -m profiler.validation    # test wzorców regex
    python -m profiler.iterators     # test iteratora paczkowego

## Mapowanie zagadnień

| # | Zagadnienie | Plik | Element |
|---|---|---|---|
| 1a | Dekorator funkcji | `profiler/decorators.py` | `timed` |
| 1b | Dekorator z parametrem | `profiler/decorators.py` | `benchmark(repeats=n)` |
| 2 | Dekorator metody, `@property` | `profiler/decorators.py`, `profiler/dataset.py` | `requires_data`, `Dataset.empty_threshold` |
| 3 | Klasa iteratora | `profiler/iterators.py` | `BatchIterator` |
| 4 | Generatory, `yield from` | `profiler/reader.py` | `iter_rows`, `iter_all_rows` |
| 5 | Wyrażenia regularne z grupami nazwanymi | `profiler/validation.py` | `PERIOD_PATTERN`, `FILENAME_PATTERN` |
| 6 | Wątki i synchronizacja | `profiler/parallel.py` | `run_threads`, `ProfileAccumulator` |
| 7 | Procesy | `profiler/parallel.py` | `run_processes` |
| 8 | Pomiar wpływu GIL | `profiler/parallel.py`, `profiler/profiling.py` | `run_hash`, `hash_one_file` |

Klasy: `Dataset`, `ProfileAccumulator`, `BatchIterator`.

## Pomiar wpływu GIL

Mierzone są dwa obciążenia. Pierwsze to profilowanie CSV, czyli czysty kod
Pythona. Drugie to liczenie skrótu SHA-256 modułem `hashlib`, który jest
napisany w C i na czas obliczeń GIL-a zwalnia. Oba przetwarzają ten sam
zestaw szesnastu plików, więc różni je tylko to, gdzie idzie czas.

Każdy wynik to najlepszy z trzech przebiegów — zakłócenia pomiaru czasu
działają tylko w jedną stronę, więc najkrótszy przebieg jest najbliższy
prawdy. Hashowanie liczone jest pięć razy na plik, żeby obliczenia
przeważyły nad kosztem uruchomienia procesów.

Sprzęt: Macbook Pro M5 Pro, macOS, cztery wątki i cztery procesy robocze.

| Tryb | Profilowanie CSV (Python) | Hashowanie SHA-256 (C) |
|---|---|---|
| Sekwencyjnie | 6,353 s | 0,919 s |
| 4 wątki | 6,775 s (0,94×) | 0,295 s (3,12×) |
| 4 procesy | 2,045 s (3,11×) | 0,349 s (2,63×) |

### Wnioski

Wątki nie przyspieszyły profilowania CSV, a nawet spowolniły je o 6,6%.
Parsowanie CSV to kod Pythona, a kod Pythona wykonuje naraz jeden wątek —
pozostałe czekają na GIL-a. Pracy równoległej nie ma, a koszt przełączania
wątków i pobierania blokady zostaje.

Te same cztery wątki przyspieszyły hashowanie 3,12 razy, bo `hashlib`
oddaje GIL-a na czas liczenia i inne wątki mogą wtedy pracować. GIL
ogranicza więc wykonywanie kodu Pythona, a nie korzystanie z procesora.

Procesy przyspieszyły oba obciążenia, bo każdy ma własnego GIL-a, ale
płacą za uruchomienie i za przesyłanie danych. Przy hashowaniu wychodzi
to na jaw: są o 18% wolniejsze od wątków, choć robią dokładnie to samo.
Procesów warto więc użyć wtedy, gdy GIL faktycznie przeszkadza, a nie
z zasady. Co ciekawe, wątki na obciążeniu w C i procesy na obciążeniu
w Pythonie dają niemal identyczny wynik — w obu przypadkach pracują
cztery rdzenie, różni je tylko sposób obejścia GIL-a.

Żadne przyspieszenie nie doszło do czterokrotności i nie z winy GIL-a.
Największy plik to około 20% całej pracy w jednym kawałku, a szesnastu plików
o różnych rozmiarach nie da się rozłożyć równo na czterech workerów.
To ograniczenie danych, nie interpretera.

## Architektura

Zależności idą w jedną stronę:

    validation.py ─┐
    reader.py ─────┼──→ profiling.py ──→ parallel.py
    decorators.py ─┘

`profiling.py` nie wie nic o zrównoleglaniu, więc profilowanie da się
uruchomić i sprawdzić bez wątków i procesów.

Każdy z trzech trybów profiluje pliki **tą samą funkcją** `profile_one_file`
i dostaje te same szesnaście plików. Różni je wyłącznie to, jak praca jest
rozdzielana: jeden wątek po kolei, cztery wątki albo cztery procesy. Dzięki
temu porównanie czasów mierzy sposób zrównoleglenia, a nie różnicę w kodzie.

## Napotkane problemy

**Wątki i procesy nie dają się napisać tak samo.** Wątki działają w jednym
procesie i widzą tą samą pamięć, więc mogą dopisywać wyniki do wspólnego
akumulatora — pod warunkiem że robią to pod blokadą. Procesy mają własną,
osobną pamięć: proces potomny zmieniałby swoją kopię akumulatora, której
rodzic nigdy nie zobaczy. Dlatego w trybie procesów wyniki wracają do
rodzica i dopiero on je scala.

**Wynik funkcji trzeba było zaprojektować pod pomiar.** Pierwotnie
`profile_one_file` miała zwracać to samo co `profile_rows`, czyli zbiory
wartości unikalnych. Przy 3,21 mln wierszy zbiory są duże, a wszystko,
co wraca z procesu potomnego, przechodzi przez `pickle` — pomiar mierzyłby
wtedy serializację, nie zrównoleglenie. Funkcja zwraca więc same liczby.

**Pierwszy pomiar hashowania był zbyt krótki, żeby coś znaczył.**
Przeliczenie 534 MB przez SHA-256 zajmuje około pół sekundy, a uruchomienie
czterech procesów około trzech dziesiątych — narzut byłby porównywalny
z mierzoną pracą i wynik wyszedłby przypadkowy. Dlatego `hash_one_file`
liczy skrót pięć razy na plik. Praca rośnie do półtorej sekundy i koszt
startu procesów przestaje dominować nad tym, co się mierzy.

## Ograniczenia

Pomiar zrobiony na jednej maszynie, przy czterech workerach i jednym
rozmiarze danych. Nie sprawdzałem, jak przyspieszenie zmienia się z liczbą
workerów ani jak wygląda w Pythonie z wyłączonym GIL-em (PEP 703).

`BatchIterator` nie jest używany w ścieżce przetwarzania. Obecny podział
pracy opiera się na tym, że dane leżą w szesnastu plikach. Przy jednym
dużym pliku jednostką musiałaby być paczka wierszy, wtedy ten iterator
być wykorzystany.
