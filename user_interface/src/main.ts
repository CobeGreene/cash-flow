import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from '@/App.vue'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'bootstrap-icons/font/bootstrap-icons.css'
import router from '@/router'
import moment from 'moment'

import AppPlugins from './plugins/app-plugins'

const pinia = createPinia()
const app = createApp(App)

app.config.globalProperties.$moment = moment
app.use(router)
app.use(pinia)
app.use(AppPlugins, {
  http: {
    root: 'http://localhost:5000',
  },
})

app.mount('#app')
