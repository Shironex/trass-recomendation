import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Trass Recommendation',
  description: 'System rekomendacji tras oparty na PyQt6',
  lang: 'pl-PL',
  lastUpdated: true,
  head: [
    ['link', { rel: 'icon', href: '/images/hero-image.svg' }],
    ['meta', { name: 'author', content: 'Trass Team' }],
    ['meta', { name: 'keywords', content: 'trasy, rekomendacje, PyQt6, system rekomendacji, turystyka' }],
    ['meta', { property: 'og:title', content: 'Trass Recommendation System' }],
    ['meta', { property: 'og:description', content: 'System rekomendacji tras oparty na PyQt6' }],
    ['meta', { property: 'og:image', content: '/images/recomendations_page.png' }],
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }]
  ],
  themeConfig: {
    logo: '/images/hero-image.svg',
    nav: [
      { text: 'Strona główna', link: '/' },
      { text: 'Przewodnik', link: '/guide/' },
      { text: 'Demo', link: '/demo' },
      { text: 'Instalacja', link: '/installation' },
      { text: 'Struktura projektu', link: '/structure' },
    ],
    sidebar: [
      {
        text: 'Przewodnik',
        items: [
          { text: 'Wprowadzenie', link: '/guide/' },
          { text: 'Demo aplikacji', link: '/demo' },
          { text: 'Instalacja', link: '/installation' },
          { text: 'Struktura projektu', link: '/structure' },
          { text: 'Uruchamianie aplikacji', link: '/running' },
          { text: 'Testy', link: '/testing' },
          { text: 'Rozwiązywanie problemów', link: '/troubleshooting' },
        ]
      }
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/your-username/trass-recomendation' }
    ],
    footer: {
      message: 'System rekomendacji tras',
      copyright: '© 2023-2024 Trass Recommendation'
    }
  }
}) 