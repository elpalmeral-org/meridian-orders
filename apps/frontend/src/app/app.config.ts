import { registerLocaleData } from '@angular/common';
import { provideHttpClient, withFetch } from '@angular/common/http';
import localeEs from '@angular/common/locales/es';
import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';

registerLocaleData(localeEs);

export const appConfig: ApplicationConfig = {
  providers: [provideBrowserGlobalErrorListeners(), provideHttpClient(withFetch())],
};
