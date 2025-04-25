let elements = document.querySelectorAll('.time_p');
let el = elements[0]

async function get_time(el, typeCapsule) {
    let url = "/api/get_time";
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    });
    const comment = await response.json();
    el.innerText = "Текущее время: " + comment.time_now.slice(0,16);
}
function closure_passing_arguments(func, ...args) {
    function inner () {
        return func(...args)
    }
    return inner
}

let timerId = setInterval(closure_passing_arguments(get_time, el), 5000);


async function get_post(num_page, typeCapsule, sorted_by, search) {
    // "Type-Capsule": typeCapsule, // "Private" "Public"
    //         "sorted": sorted_by,
    //         "Search": search,
    const params = new URLSearchParams();
    params.append("search", search);
    params.append("typeCapsule", typeCapsule);
    params.append("sorted_by", sorted_by,);
    params.append("page", num_page);
    let url = `/api/get_private_capsule?${params}`
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    });
    console.log("sorted_by", sorted_by);
    let result = await response.json();
    console.log(result);
    return result
}

let init_capsules_list = async (num_page, typeCapsule, sorted_by, search) => {
    let result = await get_post(num_page, typeCapsule, sorted_by, search);
    let container_capsules = document.querySelectorAll('.container_capsules')[0];
    let table_capsule_title = document.createElement("div");

    let serachButton = document.getElementById("capsule-search-button");
    let serachField = document.getElementById("capsule-search");
    // serachField.oninput = function() {
    //     console.log("serachField.value", serachField.value);
    //     console.log("result.current_num_page", result.current_num_page);
    //     console.log("typeCapsule", typeCapsule);
    //     console.log("sorted_by", sorted_by);
    //     console.log("Запуск поиска",init_capsules_list(result.current_num_page, typeCapsule, sorted_by, serachField.value))
    // }
    serachButton.onclick = function() {
        console.log("serachField.value", serachField.value);
        console.log("result.current_num_page", result.current_num_page);
        console.log("typeCapsule", typeCapsule);
        console.log("sorted_by", sorted_by);
        console.log("Запуск поиска",init_capsules_list(result.current_num_page, typeCapsule, sorted_by, serachField.value))
    };

    let privateCapsule = document.getElementById("PrivateCapsule");
    // privateCapsule.style.textDecoration = "underline white";
    let publicCapsule = document.getElementById("PublicCapsule");
    publicCapsule.onclick = function() {
        init_capsules_list(result.current_num_page, "Public", sorted_by, search);
        publicCapsule.className = "capsule_type_selected";
        privateCapsule.className = "";
    };
    privateCapsule.onclick = function() {
        init_capsules_list(result.current_num_page, "Private", sorted_by, search);
        privateCapsule.className = "capsule_type_selected";
        publicCapsule.className = "";
    };


    table_capsule_title.className = "table_capsule_title"
    let capsule_title = document.createElement("p");
    capsule_title.innerText = "Название";
    let capsule_open_after = document.createElement("a");
    capsule_open_after.innerText = "Открыть после";
    capsule_open_after.onclick = function() {
        if (sorted_by === "opening_after_date"){
            init_capsules_list(result.current_num_page, typeCapsule, "-opening_after_date", search);
        } else {
            init_capsules_list(result.current_num_page, typeCapsule, "opening_after_date", search);
        }
    };
    let capsule_date_creation = document.createElement("a");
    capsule_date_creation.innerText = "Дата создания";
    capsule_date_creation.onclick = function() {
        if (sorted_by === "create_data"){
            init_capsules_list(result.current_num_page, typeCapsule, "-create_data", search);
        } else {
            init_capsules_list(result.current_num_page, typeCapsule, "create_data", search);
        }
    };
    table_capsule_title.append(capsule_title, capsule_open_after, capsule_date_creation)


    container_capsules.innerHTML = ""
    container_capsules.append(table_capsule_title)
    console.log(container_capsules);
    //href="detail/{{capsule.id}}"
    result.capsules.forEach(element => {
        let a_capsule = document.createElement('a');
        a_capsule.className = "linkOnDetailCapsule";
        a_capsule.href = `detail/${element[3]}`
        a_capsule.innerHTML = `<div>${element[0]}</div><div>${element[1].slice(0,16)}</div><div>${element[2].slice(0,16)}</div>`
        container_capsules.append(a_capsule);
    });
    let div_pagination = document.createElement('div');
    div_pagination.className = "div_pagination"
    if  (result.previous_page_number){
        let a_back = document.createElement('a');
        a_back.innerText = "Предыдущая";
        div_pagination.append(a_back);
        a_back.onclick = function() {
            init_capsules_list(result.current_num_page - 1, typeCapsule, sorted_by, search);
        };
    } else {
        let a_back = document.createElement('p');
        a_back.innerText = "Предыдущая";
        a_back.className = "linkrepclace"
        div_pagination.append(a_back);
    }
    let p_pag = document.createElement('p');
    p_pag.innerText = `Страница ${result.current_num_page} из ${result.num_all_page}`;
    div_pagination.append(p_pag);
    if  (result.next_page_number){
        let a_next = document.createElement('a');
        a_next.innerText = "Следующая";
        div_pagination.append(a_next);
        a_next.onclick = function() {
            init_capsules_list(result.current_num_page + 1, typeCapsule, sorted_by, search);
        };
    } else {
        let a_next = document.createElement('p');
        a_next.innerText = "Следующая";
        a_next.className = "linkrepclace"
        div_pagination.append(a_next);
    }
    container_capsules.append(div_pagination);
    return result
};

let container_capsules = document.querySelectorAll('.container_capsules')[0];
if (container_capsules) {
    init_capsules_list(1, typeCapsule="Private", sorted_by="-create_data", search = ""); // "Private" "Public"
}

let deleteButtonOnly = document.getElementById("delete_button_only");
if ( !(document.querySelector("#details-detail")) && document.querySelector("#textarea-detail") && deleteButtonOnly){
    deleteButtonOnly.onclick = function(event) {
        event.preventDefault()
        let sure = confirm("Удалить капсулу времени ?");
        if (sure){
            location.assign(this.href);
        }
    }    
}

let deleteButton = document.getElementById("delete_button");
if (deleteButton){
    deleteButton.onclick = function(event) {
        event.preventDefault()
        let sure = confirm("Удалить капсулу времени ?");
        if (sure){
            location.assign(this.href);
        }
    } 
}


// Страница detail
let nav_back = document.getElementById("nav_back");
if (nav_back){
    nav_back.onclick = function(){
        history.back();
    }
}
