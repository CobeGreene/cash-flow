import { type App } from 'vue'
import { HttpService } from '@/service/http-service'

interface HttpPluginOptions {
  root: string
}

interface AppPluginsOptions {
  http: HttpPluginOptions
}

export default {
  install: (app: App, options: AppPluginsOptions) => {
    const httpService = new HttpService(options.http.root)

    app.provide('http', httpService)
  },
}
