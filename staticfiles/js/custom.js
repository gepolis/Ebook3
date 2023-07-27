const full_name_text = document.getElementById("full_name_model")
const email_text = document.getElementById("email_model")
const role_text = document.getElementById("role_model")
const join_date_text = document.getElementById("join_date_model")
const last_login_text = document.getElementById("last_login_model")
const received = document.getElementById("received")
const modal = document.getElementById("exampleModal")
const loader = document.getElementById("modal_loader")
const modal_data = document.getElementById("information")
const modal_footer = document.getElementById("modal_footer")
const url = `${window.location.protocol}//${window.location.host}/lk/users/data/`
let interv = null;
console.log(url)

function open_user_detail(pk) {
    if (interv == null) {
        modal_data.style = "display: None;"
        loader.style = "display: block;"
        modal_footer.style = "display: None;"
        setTimeout(function () {
            get_user_detail(pk)
            interv = setInterval(get_user_detail, 10000, pk)
        }, 500)

    } else {
        console.warn("error!")
    }

}

function close_user_detail() {
    if (interv !== null) {
        clearInterval(interv)
        console.log("c")
        interv = null
    }
    console.log("close")

}

function get_user_detail(pk) {
    if (!modal.classList.contains("show")) {
        if (interv) {

            clearInterval(interv)
            interv = null
        }
        return null
    } else {
        loader.style = "display: None;"
        modal_footer.style = "display: block;"
        modal_data.style = "display: block;"
    }
    fetch(url + pk.toString()).then((response) => {
        return response.json()
    }).then((data) => {
        full_name_text.innerHTML = data.user.full_name
        email_text.innerHTML = data.user.email
        role_text.innerHTML = data.user.role.display
        join_date_text.innerHTML = data.user.date_joined
        last_login_text.innerHTML = data.user.last_login
        received.innerHTML = data.received
    })

}

