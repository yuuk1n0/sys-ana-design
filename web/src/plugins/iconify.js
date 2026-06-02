import { addCollection, addIcon } from '@iconify/vue/offline'

let setupPromise

export function setupOfflineIconify() {
  if (setupPromise) return setupPromise

  setupPromise = Promise.all([
    import('@iconify/json/json/material-symbols.json'),
    import('@iconify/json/json/mdi.json'),
    import('@iconify/json/json/icon-park-outline.json'),
    import('@iconify/json/json/solar.json'),
    import('@iconify/json/json/tabler.json'),
    import('@iconify/json/json/clarity.json'),
    import('@iconify/json/json/carbon.json'),
  ]).then(([materialSymbols, mdi, iconParkOutline, solar, tabler, clarity, carbon]) => {
    const collections = [
      materialSymbols.default,
      mdi.default,
      iconParkOutline.default,
      solar.default,
      tabler.default,
      clarity.default,
      carbon.default,
    ]

    collections.forEach((collection) => addCollection(collection))

    const profileIcon = mdi.default?.icons?.['account-circle-outline']
    if (profileIcon) {
      addIcon('user', profileIcon)
    }
  })

  return setupPromise
}
