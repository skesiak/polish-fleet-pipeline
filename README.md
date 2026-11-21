# polish-fleet-pipeline

Pipeline nad rejestrem pojazdów CEPiK: 3,21 mln rejestracji z lat 2024–2025
wczytanych do DuckDB, oczyszczonych warstwowym SQL-em i podsumowanych
w tabelach analitycznych z testami jakości danych.

Pytanie badawcze: gdzie w Polsce najszybciej wzrośnie popyt na części
i serwis samochodowy?

- `sql/` — warstwy: wczytanie surowych danych, staging, tabela faktów, testy jakości
- `sql/analysis/` — zapytania analityczne stojące za wykresami
- `src/` — pobieranie danych z API CEPiK i generowanie wykresów
- `scripts/` — narzędzia jednorazowe
- `profiler/` — narzędzie do profilowania CSV, projekt zaliczeniowy z zaawansowanego Pythona; patrz `profiler/README.md`

Pełna przebudowa: `./run.sh`

Opis wyników i wnioski — w przygotowaniu.