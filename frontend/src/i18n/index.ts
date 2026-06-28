import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import zhCN from './locales/zh-CN'
import en from './locales/en'
import hu from './locales/hu'
import vi from './locales/vi'
import esMX from './locales/es-MX'

i18n.use(initReactI18next).init({
  resources: {
    'zh-CN': zhCN,
    en,
    hu,
    vi,
    'es-MX': esMX,
  },
  lng: 'zh-CN',
  fallbackLng: 'en',
  interpolation: {
    escapeValue: false,
  },
})

export default i18n