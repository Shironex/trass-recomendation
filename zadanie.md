1. Wprowadzenie ogólne
1.1. Temat projektu
Rekomendator tras turystycznych w oparciu o preferencje pogodowe

1.2. Cel projektu
Stworzenie systemu rekomendującego trasy turystyczne na podstawie preferencji użytkownika dotyczących warunków pogodowych (temperatura, nasłonecznienie, opady) i parametrów trasy (długość, trudność, rodzaj terenu).

1.3. Ogólna funkcjonalność
System będzie wczytywał dane o trasach turystycznych i historyczne dane pogodowe, analizował je pod kątem dopasowania do preferencji użytkownika przy użyciu prostych metod statystycznych, a następnie generował spersonalizowane rekomendacje tras.

2. Etapy projektu
Projekt zostanie podzielony na etapy zgodnie z wymaganiami. Poniżej znajduje się opis pierwszego etapu, kolejne będą dodawane w miarę postępu prac.

3. Wymagania dla poszczególnych etapów
Etap 1: Obsługa danych i podstawowe przetwarzanie
3.1.1. Opis funkcjonalności
Pierwszy etap skupia się na implementacji podstawowych mechanizmów wczytywania i przetwarzania danych z wykorzystaniem wyrażeń lambda i elementów programowania funkcyjnego. W ramach tego etapu zostanie stworzona struktura projektu oraz zaimplementowane funkcje do obsługi plików z danymi o trasach turystycznych i danych pogodowych.

3.1.2. Wymagania funkcjonalne
WF1.1: System musi umożliwiać wczytywanie danych o trasach turystycznych z plików CSV/JSON.
WF1.2: System musi umożliwiać wczytywanie historycznych danych pogodowych dla lokalizacji tras z plików CSV/JSON.
WF1.3: System musi udostępniać funkcje filtrowania tras według podstawowych parametrów (długość, trudność, region).
WF1.4: System musi implementować funkcje obliczające podstawowe statystyki dla danych pogodowych (średnia temperatura, suma opadów, liczba dni słonecznych).
WF1.5: System musi umożliwiać zapisywanie wyników przetwarzania do plików wyjściowych.
3.1.3. Wymagania techniczne
WT1.1: Implementacja musi wykorzystywać mechanizmy obsługi plików i katalogów dostępne w bibliotece standardowej Pythona.
WT1.2: Kod musi zawierać elementy programowania funkcyjnego, w tym wykorzystanie funkcji map(), filter(), reduce() oraz wyrażeń lambda.
WT1.3: Dane wejściowe o trasach muszą zawierać co najmniej: identyfikator trasy, nazwę, lokalizację (współrzędne geograficzne), długość w kilometrach, przewyższenie, poziom trudności, typ terenu.
WT1.4: Dane pogodowe muszą zawierać co najmniej: datę, lokalizację, temperaturę minimalną/maksymalną/średnią, sumę opadów, zachmurzenie.
WT1.5: Implementacja musi wykorzystywać wyrażenia listowe i słownikowe (list comprehensions, dictionary comprehensions) do efektywnego przetwarzania danych.
WT1.6: Kod musi być zorganizowany w moduły z odpowiednim podziałem odpowiedzialności (obsługa danych, analiza, interfejs użytkownika).
4. Przykładowe dane i źródła
4.1. Dane o trasach turystycznych
Przykładowe źródła:

OpenStreetMap - dane można pobrać za pomocą Overpass API
Wikiloc - serwis z trasami turystycznymi (może wymagać API)
AllTrails - baza szlaków i tras turystycznych
Lokalne serwisy turystyczne dla poszczególnych regionów
Uproszczona struktura przykładowych danych:

id,name,region,start_lat,start_lon,end_lat,end_lon,length_km,elevation_gain,difficulty,terrain_type,tags
1,"Dolina Kościeliska",Tatry,49.2798,19.8675,49.2336,19.8747,7.2,320,2,mountain,"waterfalls,forest"
2,"Ścieżka wokół jeziora Solińskiego",Bieszczady,49.3983,22.4675,49.3983,22.4675,15.5,50,1,lakeside,"lake,family"
4.2. Dane pogodowe
Przykładowe źródła:

OpenWeatherMap - historyczne dane pogodowe (wymaga API key)
Meteostat - otwarty dostęp do historycznych danych
European Climate Assessment & Dataset - dane klimatyczne dla Europy
Instytut Meteorologii i Gospodarki Wodnej (IMGW) - dane dla Polski
Uproszczona struktura przykładowych danych:

date,location_id,avg_temp,min_temp,max_temp,precipitation,sunshine_hours,cloud_cover
2023-07-01,Tatry,22.5,15.2,26.8,0.0,12.5,10
2023-07-02,Tatry,24.1,16.5,28.3,2.5,8.2,45