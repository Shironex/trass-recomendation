import { defineConfig } from 'vitepress'
import { siteConfig } from './siteConfig'

export default defineConfig({
  title: siteConfig.title,
  description: siteConfig.description,
  lang: siteConfig.lang,
  lastUpdated: true,
  base: `${ siteConfig.base}/`,
  head: [
    ['link', { rel: 'icon', href: `${ siteConfig.base}/hero-image.svg` }],
    ['meta', { name: 'author', content: 'Trass Team' }],
    ['meta', { name: 'keywords', content: 'trasy, rekomendacje, PyQt6, system rekomendacji, turystyka' }],
    ['meta', { property: 'og:title', content: 'Trass Recommendation System' }],
    ['meta', { property: 'og:description', content: 'System rekomendacji tras oparty na PyQt6' }],
    ['meta', { property: 'og:image', content: `${ siteConfig.base}/recomendations_page.png` }],
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }]
  ],
  themeConfig: {
    logo: `${ siteConfig.base}/hero-image.svg`,
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
          { text: 'Budowanie EXE (Windows)', link: '/building-exe' },
          { text: 'Testy', link: '/testing' },
          { text: 'Rozwiązywanie problemów', link: '/troubleshooting' },
        ]
      }
    ],
    socialLinks: siteConfig.socialLinks,
    footer: {
      message: siteConfig.footer.message,
      copyright: siteConfig.footer.copyright,
    },
  }
}) 