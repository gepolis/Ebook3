 function search() {
    let input = document.getElementById("search");
    let filter = input.value.toUpperCase();
    let table = document.getElementById("table");
    let li = document.getElementsByClassName("user-row");
    let select = document.getElementById("role-filter")

    // Перебирайте все элементы списка и скрывайте те, которые не соответствуют поисковому запросу
    for (let i = 0; i < li.length; i++) {
        if (li[i].dataset.role === select.value || select.value === "all") {
            let a = li[i].getElementsByTagName("td")[0];
            if (a.innerHTML.toUpperCase().indexOf(filter) > -1) {
                li[i].style.display = "";
            } else {
                li[i].style.display = "none";
            }
        }
    }
}
