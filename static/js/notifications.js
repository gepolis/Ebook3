async function readNotifications() {
  let div = document.getElementById('notifications');
  let url = "https://mysite.com:8000/lk/notifications/read/";

  let response = await fetch(url);
  console.log(response.json())
}
async function listNotifications() {
  let div = document.getElementById('notifications');
  let url = "https://mysite.com:8000/lk/notifications/list/";
  let response = await fetch(url);
  let data = await response.json();
  let notifications = document.getElementById("notifications-list");
  notifications.innerHTML = '';
  for (var i = 0; i < data.notification.length; i++){
    notifications.innerHTML += '<a href="#" class="dropdown-item"><h6 class="fw-normal mb-0">' + data.notification[i].title + '</h6><small>' + data.notification[i].description + '</small></a>'
  }
}

listNotifications()
let timerId = setInterval(() => listNotifications(), 2000);