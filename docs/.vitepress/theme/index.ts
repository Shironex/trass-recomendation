import { h } from 'vue'
import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import './custom.css'

// Możesz zdefiniować własne komponenty
const CustomLayout = {
  setup() {
    return () => {
      return h(DefaultTheme.Layout, null, {
        // Możesz dodać niestandardowe sloty tutaj
      })
    }
  }
}

// Eksportuj motyw
export default {
  extends: DefaultTheme,
  Layout: CustomLayout,
  enhanceApp({ app, router, siteData }) {
    // Rejestracja komponentów, dyrektyw, itp.
    // app.component('MyCustomComponent', MyCustomComponent)
  }
} as Theme 