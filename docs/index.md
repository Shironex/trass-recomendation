---
layout: home
hero:
  name: "Trass Recommendation"
  text: "System rekomendacji tras"
  tagline: "Zaawansowane narzędzie do rekomendacji tras oparte na PyQt6"
  image:
    src: /images/hero-image.svg
    alt: Trass Recommendation Logo
  actions:
    - theme: brand
      text: Rozpocznij
      link: /guide/
    - theme: alt
      text: Instalacja
      link: /installation
features:
  - icon: 🗺️
    title: Inteligentne rekomendacje
    details: Zaawansowany algorytm dobierający trasy odpowiednie dla użytkownika
  - icon: 🖥️
    title: Intuicyjny interfejs
    details: Przejrzysty i łatwy w obsłudze interfejs oparty na PyQt6
  - icon: 🧪
    title: Testowane rozwiązanie
    details: Kompleksowe testy zapewniające niezawodność aplikacji
---

<div class="custom-container">
  <div class="custom-section">
    <h1>Trass Recommendation System</h1>
    <p>System rekomendacji tras oparty na PyQt6, zaprojektowany z myślą o intuicyjności i efektywności.</p>
  </div>
  
  <div class="custom-section image-showcase">
    <h2>Zrzuty ekranu aplikacji</h2>
    <div class="screenshot-grid">
      <div class="screenshot">
        <img src="/images/manage_trail.png" alt="Zarządzanie trasami" class="thumbnail-image" />
        <p>Zarządzanie trasami</p>
      </div>
      <div class="screenshot">
        <img src="/images/manage_weather.png" alt="Zarządzanie trasami" class="thumbnail-image" />
        <p>Zarządzanie Pogodą</p>
      </div>
      <div class="screenshot">
        <img src="/images/recomendations_page.png" alt="Panel rekomendacji" class="thumbnail-image" />
        <p>Panel rekomendacji tras</p>
      </div>
    </div>
  </div>

  <div class="custom-section">
    <h2>O projekcie</h2>
    <p>Trass Recommendation to zaawansowany system rekomendacji tras, który pomaga użytkownikom w wyborze optymalnych ścieżek na podstawie różnych kryteriów. Aplikacja wykorzystuje framework PyQt6 do zapewnienia nowoczesnego i responsywnego interfejsu użytkownika.</p>
  </div>

  <div class="custom-section">
    <h2>Główne funkcje</h2>
    <ul>
      <li>Inteligentne rekomendacje tras</li>
      <li>Przyjazny dla użytkownika interfejs graficzny</li>
      <li>Możliwość personalizacji preferencji</li>
      <li>Kompletne rozwiązanie z dokumentacją i testami</li>
    </ul>
  </div>

  <div class="custom-section">
    <h2>Rozpocznij pracę</h2>
    <p>Aby rozpocząć pracę z projektem, przejdź do sekcji <a href="/guide/">Przewodnik</a> lub zapoznaj się z instrukcją <a href="/installation">Instalacji</a>.</p>
    <div style="margin-top: 1rem;">
      <a href="/demo" class="custom-button">Zobacz demo</a>
    </div>
  </div>
</div>

<style>
.custom-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.custom-section {
  margin-bottom: 3rem;
  padding: 1.5rem;
  border-radius: 8px;
  background-color: var(--vp-c-bg-soft);
}

.custom-section h1 {
  font-size: 2rem;
  margin-bottom: 1rem;
  color: var(--vp-c-brand);
}

.custom-section h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: var(--vp-c-brand);
  border-left: 4px solid var(--vp-c-brand);
  padding-left: 0.5rem;
}

.screenshot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.screenshot {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.screenshot:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.screenshot img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 8px 8px 0 0;
  aspect-ratio: 16 / 9;
  object-fit: cover;
}

.thumbnail-image {
  max-height: 200px;
  object-position: top;
}

.screenshot p {
  padding: 0.75rem;
  margin: 0;
  text-align: center;
  background-color: var(--vp-c-bg);
  font-weight: 500;
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

@media (max-width: 768px) {
  .screenshot-grid {
    grid-template-columns: 1fr;
  }
}
</style> 