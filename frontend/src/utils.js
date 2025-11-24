export function makeRequest(page) {
    //  ---filipchuk.al 24.11.2025---
    // Адрес сервера изменён с 0.0.0.0 на localhost для локального запуска в браузере
    // let server_url = 'http://0.0.0.0:8000/'
    let server_url = 'http://localhost:8000/'
    //  -----------------------------

    return fetch(server_url + page, {
        headers:{"Content-Type": "application/json"}
      })
      .then((response) => response.json());
}