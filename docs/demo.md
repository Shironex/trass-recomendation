# Demo aplikacji

Na tej stronie znajdziesz demonstrację funkcjonalności aplikacji Trass Recommendation. Poniższe zrzuty ekranu przedstawiają główne funkcje systemu.

## Ekran główny

Ekran główny aplikacji Trass Recommendation zawiera listę dostępnych tras z możliwością zarządzania i przeglądania. Użytkownik może dodawać, edytować i usuwać trasy.

<div class="demo-container">
  <img src="/home-page.png" alt="Ekran główny aplikacji" class="demo-image" />
  <div class="demo-description">
    <h3>Główne funkcje ekranu:</h3>
    <ul>
      <li>Przegląd wszystkich tras w systemie</li>
      <li>Nawigacja do pozostałych sekcji aplikacji</li>
      <li>Dostęp do narzędzi zarządzania</li>
      <li>Szybki dostęp do rekomendacji</li>
    </ul>
  </div>
</div>

## Zarządzanie trasami

Ekran zarządzania trasami pozwala na kompleksową edycję informacji o dostępnych trasach, w tym ich parametrów, trudności i szczegółów.

<div class="demo-container">
  <img src="/manage_trail.png" alt="Zarządzanie trasami" class="demo-image" />
  <div class="demo-description">
    <h3>Główne funkcje zarządzania:</h3>
    <ul>
      <li>Dodawanie nowych tras do systemu</li>
      <li>Edycja parametrów istniejących tras</li>
      <li>Kategoryzacja tras według trudności</li>
      <li>Zarządzanie dodatkowymi atrybutami</li>
      <li>Możliwość usuwania tras z systemu</li>
    </ul>
  </div>
</div>

## Panel rekomendacji

System rekomendacji analizuje preferencje użytkownika i historię jego aktywności, aby przedstawić spersonalizowane propozycje tras. Trasy są sortowane według stopnia dopasowania do profilu użytkownika.

<div class="demo-container">
  <img src="/recomendations_page.png" alt="Panel rekomendacji" class="demo-image" />
  <div class="demo-description">
    <h3>Główne funkcje panelu:</h3>
    <ul>
      <li>Spersonalizowane rekomendacje tras</li>
      <li>Ranking tras według stopnia dopasowania</li>
      <li>Prezentacja kluczowych informacji o trasach</li>
      <li>Filtrowanie według preferencji użytkownika</li>
    </ul>
  </div>
</div>

## Zarządzanie pogodą

System uwzględnia również warunki pogodowe przy rekomendacji tras. Moduł zarządzania pogodą pozwala na integrację i aktualizację danych pogodowych.

<div class="demo-container">
  <img src="/manage_weather.png" alt="Zarządzanie pogodą" class="demo-image" />
  <div class="demo-description">
    <h3>Główne funkcje modułu:</h3>
    <ul>
      <li>Integracja z serwisami pogodowymi</li>
      <li>Uwzględnianie warunków pogodowych w rekomendacjach</li>
      <li>Alerty o niesprzyjających warunkach</li>
      <li>Prognoza dla wybranych lokalizacji</li>
    </ul>
  </div>
</div>

## Technologie

Aplikacja Trass Recommendation została zbudowana przy użyciu następujących technologii:

<div class="tech-grid">
  <div class="tech-item">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1869px-Python-logo-notext.svg.png" alt="Python" width="50" />
    <h3>Python</h3>
    <p>Główny język programowania aplikacji</p>
  </div>
  <div class="tech-item">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Python_and_Qt.svg/1200px-Python_and_Qt.svg.png" alt="PyQt6" width="50" />
    <h3>PyQt6</h3>
    <p>Framework do tworzenia interfejsu użytkownika</p>
  </div>
  <div class="tech-item">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1869px-Python-logo-notext.svg.png" alt="Python" width="50" />
    <h3>pytest</h3>
    <p>Biblioteka do pisania testów</p>
  </div>
  <div class="tech-item">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/PyInstaller_Icon.svg/2048px-PyInstaller_Icon.svg.png" alt="PyInstaller" width="50" />
    <h3>PyInstaller</h3>
    <p>Narzędzie do tworzenia plików EXE</p>
  </div>
  <div class="tech-item">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Typescript_logo_2020.svg/1200px-Typescript_logo_2020.svg.png" alt="TypeScript" width="50" />
    <h3>TypeScript</h3>
    <p>Język dla konfiguracji dokumentacji</p>
  </div>
  <div class="tech-item">
    <img src="https://vitepress.dev/vitepress-logo-large.webp" alt="VitePress" width="50" />
    <h3>VitePress</h3>
    <p>Framework do tworzenia dokumentacji</p>
  </div>
  <div class="tech-item">
    <img src="https://pillow.readthedocs.io/en/stable/_static/pillow-logo-248x250.png" alt="Pillow" width="50" />
    <h3>Pillow</h3>
    <p>Biblioteka do przetwarzania obrazów</p>
  </div>
  <div class="tech-item">
    <img src="https://raw.githubusercontent.com/tartley/colorama/master/.github/logo.png" alt="Colorama" width="50" />
    <h3>Colorama</h3>
    <p>Biblioteka do kolorowych logów konsolowych</p>
  </div>
</div>

<div class="action-section">
  <h2>Wypróbuj sam</h2>
  
  <p>Aby samodzielnie wypróbować aplikację Trass Recommendation:</p>
  <p>Zainstaluj projekt zgodnie z <a href="/trass-recomendation/installation">instrukcją instalacji</a></p>
</div>

<style>
.demo-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin: 2.5rem 0;
  padding: 2rem;
  border-radius: 8px;
  background-color: var(--vp-c-bg-soft);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.demo-container:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.demo-image {
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  object-position: top;
  max-height: 400px;
}

.demo-image:hover {
  transform: scale(1.02);
}

.demo-description {
  padding: 0 1rem;
  text-align: center;
}

.demo-description h3 {
  color: var(--vp-c-brand);
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--vp-c-brand-light);
}

.demo-description ul {
  text-align: left;
  margin: 1rem auto;
  display: inline-block;
}

.tech-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  margin: 2.5rem 0;
}

.tech-item {
  padding: 2rem 1.5rem;
  border-radius: 8px;
  background-color: var(--vp-c-bg-soft);
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.tech-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.tech-item h3 {
  margin: 1rem 0 0.5rem;
  color: var(--vp-c-brand);
}

.tech-item p {
  margin: 0;
  font-size: 0.9rem;
}

.action-section {
  margin: 3rem 0;
  padding: 2rem;
  border-radius: 8px;
  background-color: var(--vp-c-bg-soft);
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.action-section h2 {
  text-align: center;
  border-bottom: 2px solid var(--vp-c-brand-light);
  padding-bottom: 0.5rem;
  margin: 0 auto 1.5rem;
  max-width: 50%;
}

.action-section ol {
  text-align: left;
  margin: 1.5rem auto;
  max-width: 80%;
  padding-left: 2rem;
}

.buttons-container {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
}

.custom-button {
  display: inline-block;
  padding: 0.75rem 1.5rem;
  background-color: var(--vp-c-brand);
  color: white !important;
  border-radius: 4px;
  text-decoration: none !important;
  font-weight: 500;
  transition: background-color 0.3s ease, transform 0.3s ease;
  border-bottom: none !important;
}

.custom-button:hover {
  background-color: var(--vp-c-brand-dark);
  transform: translateY(-2px);
}

.secondary-button {
  background-color: var(--vp-c-bg);
  color: var(--vp-c-brand) !important;
  border: 1px solid var(--vp-c-brand);
}

.secondary-button:hover {
  background-color: var(--vp-c-bg-soft);
}

@media (min-width: 768px) {
  .demo-container {
    flex-direction: row;
    align-items: center;
  }
  
  .demo-image {
    width: 60%;
  }
  
  .demo-description {
    width: 40%;
  }
}

@media (max-width: 768px) {
  .demo-container {
    padding: 1.5rem;
    gap: 1.5rem;
  }
  
  .demo-image {
    max-height: 300px;
  }
  
  .tech-grid {
    grid-template-columns: 1fr;
  }
  
  .buttons-container {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .action-section h2 {
    max-width: 100%;
  }
  
  .action-section ol {
    max-width: 100%;
  }
}
</style> 