const socket = new WebSocket('ws://localhost:8000/ws');

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    const tableBody = document.getElementById('data-table').querySelector('tbody');
    const row = document.createElement('tr');
    const timeCell = document.createElement('td');
    const latitudeCell = document.createElement('td');
    const longitudeCell = document.createElement('td');
    const photoCell = document.createElement('td');

    timeCell.textContent = data.time;
    latitudeCell.textContent = data.latitude;
    longitudeCell.textContent = data.longitude;
    if (data.photo_url) {
        const photoLink = document.createElement('a');
        photoLink.href = data.photo_url;
        photoLink.textContent = 'Посмотреть фото';
        photoCell.appendChild(photoLink);
    }

    row.appendChild(timeCell);
    row.appendChild(latitudeCell);
    row.appendChild(longitudeCell);
    row.appendChild(photoCell);
    tableBody.insertBefore(row, tableBody.firstChild);  // Добавление новой строки в начало таблицы
    fetchData();
};

async function fetchData() {
    const response = await fetch('/api/data');
    const data = await response.json();
    const tableBody = document.getElementById('data-table').querySelector('tbody');
    tableBody.innerHTML = '';  // Очистка таблицы перед добавлением новых данных

    data.forEach(item => {
        const row = document.createElement('tr');
        const timeCell = document.createElement('td');
        const latitudeCell = document.createElement('td');
        const longitudeCell = document.createElement('td');
        const photoCell = document.createElement('td');

        timeCell.textContent = item.time;
        latitudeCell.textContent = item.latitude;
        longitudeCell.textContent = item.longitude;
        if (item.photo_path) {
            const photoLink = document.createElement('a');
            photoLink.href = item.photo_path;
            photoLink.textContent = 'View photo';
            photoCell.appendChild(photoLink);
        }

        row.appendChild(timeCell);
        row.appendChild(latitudeCell);
        row.appendChild(longitudeCell);
        row.appendChild(photoCell);
        tableBody.appendChild(row);
    });
}

// Вызов функции fetchData для получения и отображения данных
fetchData();