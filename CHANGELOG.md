# Changelog

## [0.2.0](https://github.com/elpalmeral-org/meridian-orders/compare/v0.1.0...v0.2.0) (2026-11-13)


### Nuevas funcionalidades

* aidlc-implement, el disparo de implementer+validadores del motor A (F5) ([#37](https://github.com/elpalmeral-org/meridian-orders/issues/37)) ([dbbefa8](https://github.com/elpalmeral-org/meridian-orders/commit/dbbefa8f311edc947ee48ac5d57108ef3ee13c9f))
* aidlc-propose, el disparo del motor A desde Port (F5) ([#36](https://github.com/elpalmeral-org/meridian-orders/issues/36)) ([2e021cc](https://github.com/elpalmeral-org/meridian-orders/commit/2e021cc08f82307e1d1ee03c862c75ff037e3a32))
* **backend:** filtrar pedidos por correo del cliente ([#31](https://github.com/elpalmeral-org/meridian-orders/issues/31)) ([db0f99b](https://github.com/elpalmeral-org/meridian-orders/commit/db0f99b457b4c581eebd59778c1c0e86feddec41))
* **backend:** trazas OTel hacia el obs-stack de docker01 (F6.1, ADR 0032) ([#40](https://github.com/elpalmeral-org/meridian-orders/issues/40)) ([18db60a](https://github.com/elpalmeral-org/meridian-orders/commit/18db60a7b60f3ffac7ea27ab966bef6eeff0c043))
* consumir el harness corporativo ([#24](https://github.com/elpalmeral-org/meridian-orders/issues/24)) ([f551f44](https://github.com/elpalmeral-org/meridian-orders/commit/f551f442e73193ddff648ecfe838e242ed92fe2f))
* PR automático de upgrade del harness (F4.4, ADR 0029) ([#26](https://github.com/elpalmeral-org/meridian-orders/issues/26)) ([e70f751](https://github.com/elpalmeral-org/meridian-orders/commit/e70f751fa67194a8bb7a612067f933dff0958089))
* publicar el estado del harness en Port al fusionar en main (F4.8) ([#33](https://github.com/elpalmeral-org/meridian-orders/issues/33)) ([81ce5fd](https://github.com/elpalmeral-org/meridian-orders/commit/81ce5fdde2adb7285f59f94c9444da099ac3059b))
* workflow de prueba de humo para el runner scale set de ARC (F5, ADR 0031) ([#34](https://github.com/elpalmeral-org/meridian-orders/issues/34)) ([b02c09f](https://github.com/elpalmeral-org/meridian-orders/commit/b02c09f8bb1fe915f2587fcdd2d8ffc8903a3804))


### Correcciones

* conventional-commits acepta el tipo spec: (lo exige /feature, fase A) ([#29](https://github.com/elpalmeral-org/meridian-orders/issues/29)) ([e776270](https://github.com/elpalmeral-org/meridian-orders/commit/e77627070e5ad8f31c228e7cad251d4df2eb3ceb))
* GET /v1/harnesses devuelve {harnesses: [...]}, no un array suelto (F4.7) ([#44](https://github.com/elpalmeral-org/meridian-orders/issues/44)) ([53ed979](https://github.com/elpalmeral-org/meridian-orders/commit/53ed9793edb345d743dba6e257ba73e2a6b94c49))
* prefijo real de la API y filtro por name en aidlc-* (F4.7, ADR 0033) ([#43](https://github.com/elpalmeral-org/meridian-orders/issues/43)) ([2b384e1](https://github.com/elpalmeral-org/meridian-orders/commit/2b384e1340d0e4920ef5516317049cb00412e1c0))

## 0.1.0 (2026-10-26)


### Nuevas funcionalidades

* Meridian Orders base (API FastAPI, panel Angular y spec de pedidos) ([#1](https://github.com/elpalmeral-org/meridian-orders/issues/1)) ([f955eda](https://github.com/elpalmeral-org/meridian-orders/commit/f955eda3eeea5e592460a617b15c26266f803357))


### Correcciones

* **frontend:** aplicar parches de Alpine en la imagen, quitar curl y analizar con Grype en el PR ([#11](https://github.com/elpalmeral-org/meridian-orders/issues/11)) ([4529801](https://github.com/elpalmeral-org/meridian-orders/commit/4529801eace81c8090b1fd845ed9bedc1de90738))
