/**
 * Префиксует путь к статике базовым URL сборки (import.meta.env.BASE_URL).
 * Нужно для деплоя в подпапку (например, GitHub Pages: /DnsConf/),
 * где «/img/...» иначе резолвится от корня домена.
 */
export const asset = (p: string): string =>
  import.meta.env.BASE_URL + p.replace(/^\//, '')
