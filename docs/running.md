# Uruchamianie aplikacji

Ta strona zawiera instrukcje dotyczące uruchamiania aplikacji Trass Recommendation.

## Przygotowanie środowiska

Przed uruchomieniem aplikacji upewnij się, że ukończyłeś [Instalacje](/installation)

## Uruchomienie aplikacji

Po aktywacji środowiska wirtualnego, możesz uruchomić aplikację za pomocą polecenia:

```bash
python src/main.py
```

## Uruchamianie aplikacji jako plik EXE (Windows)

Jeśli wcześniej zbudowałeś aplikację jako plik EXE (zobacz [Budowanie EXE](/building-exe)), możesz ją uruchomić bezpośrednio bez konieczności aktywacji środowiska wirtualnego:

```bash
# Jeśli zbudowałeś jako pojedynczy plik
dist/TrassRecommendation.exe

# Lub jeśli zbudowałeś jako katalog
dist/TrassRecommendation/TrassRecommendation.exe
```

Dzięki temu użytkownicy, którzy nie znają Pythona, mogą łatwo uruchomić aplikację.

## Uruchamianie dokumentacji VitePress

Aby uruchomić lokalnie dokumentację VitePress z TypeScript, wykonaj:

```bash
pnpm docs:dev
```

Dokumentacja będzie dostępna pod adresem `http://localhost:5173`.

### Budowanie dokumentacji do wdrożenia

Aby zbudować statyczną wersję dokumentacji gotową do wdrożenia:

```bash
pnpm docs:build
```

Wygenerowane pliki będą dostępne w katalogu `docs/.vitepress/dist`.

### Podgląd zbudowanej dokumentacji

Aby zobaczyć podgląd zbudowanej dokumentacji przed wdrożeniem:

```bash
pnpm docs:preview
```

## Następne kroki

Po pomyślnym uruchomieniu aplikacji możesz:
- Przejść do korzystania z aplikacji
- Rozpocząć [testowanie](/testing)
- Rozwijać nowe funkcje 