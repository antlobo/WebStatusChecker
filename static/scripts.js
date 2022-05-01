function searchbar() {
    var input = document.getElementById("searchbar").value;
    var filter = input.toUpperCase();
    var cardContainer = document.getElementById("data");
    var cards = cardContainer.getElementsByClassName("col");
    
    for (i = 0; i < cards.length; i++) {
        title = cards[i].getElementsByClassName("card-title");
        body = cards[i].getElementsByClassName("card-text");
        if (title[0].innerText.toUpperCase().includes(filter) || body[0].innerText.toUpperCase().includes(filter)) {
            cards[i].classList.replace('d-none', '-');
        } else {
            cards[i].classList.add('d-none');
        }
    }
}

function update_service(app_id) {
    var myHeaders = new Headers();

    form = document.getElementById("form");
    var data = new URLSearchParams();
    for (const pair of new FormData(form)) {
        data.append(pair[0], pair[1]);
    }
    var myInit = { method: 'POST',
                   headers: myHeaders,
                   body: data,
                   mode: 'cors',
                   cache: 'default' };

    var myRequest = new Request("/admin/service/"+ app_id +"/update", myInit);

    fetch(myRequest).then(function(response) {
      if(response.ok) {
        response.json().then(function(result) {
            if (result["updated"] == true) {
                var content = document.getElementsByClassName("content");

                var container = document.getElementById("toasts");
                var toast = document.createElement("div");
                toast.classList.add("toast");
                toast.setAttribute("role", "alert");
                toast.setAttribute("aria-live", "assertive");
                toast.setAttribute("aria-atomic", "true");
                toast.innerHTML = '<div class="toast-header text-white bg-dark border-0"><strong class="me-auto">WSC</strong><button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button></div><div class="toast-body">' + result["message"] + '</div>';
                container.appendChild(toast);
                content[0].insertBefore(container, document.getElementById("form"));
                var bsAlert = new bootstrap.Toast(toast);
                bsAlert.show();
            }
        }).catch(function(error) {
            console.log('There was a problem with the fetch request:' + error.message);
        });
      } else {
        console.log("Net response was OK but HTTP response wasn't");
      }
    })
    .catch(function(error) {
      console.log('There was a problem with the fetch request:' + error.message);
    });
}

function change_service_status(app_id) {
    var myHeaders = new Headers();
    var myInit = { method: 'POST',
                   headers: myHeaders,
                   mode: 'cors',
                   cache: 'default' };

    var myRequest = new Request("/admin/service/"+ app_id +"/update_status", myInit);

    fetch(myRequest).then(function(response) {
      if(response.ok) {
        response.json().then(function(result) {
            if (result["updated"] == true) {
                if (result["status"] != "") {
                    var content = document.getElementsByClassName("content");

                    var container = document.getElementById("toasts");
                    var toast = document.createElement("div");
                    toast.classList.add("toast");
                    toast.setAttribute("role", "alert");
                    toast.setAttribute("aria-live", "assertive");
                    toast.setAttribute("aria-atomic", "true");
                    toast.innerHTML = '<div class="toast-header text-white bg-dark border-0"><strong class="me-auto">WSC</strong><button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button></div><div class="toast-body">' + result["message"] + '</div>';
                    container.appendChild(toast);
                    content[0].insertBefore(container, document.getElementById("form"));
                    var bsAlert = new bootstrap.Toast(toast);
                    bsAlert.show();

                    var cardContainer = document.getElementById(app_id);

                    if (result["status"] == "active") {
                        var cardHeader = cardContainer.querySelector(".card-header");
                        cardHeader.classList.replace('bg-light', 'bg-dark');

                        var cardTitle = cardContainer.querySelector(".card-title");
                        cardTitle.classList.replace("text-dark", "text-white");

                        var titleBadge = cardContainer.querySelector(".badge");
                        titleBadge.remove();

                        var status_link = cardContainer.querySelector(".update_status");
                        status_link.innerHTML = "Disable";
                    } else {
                        if (result["status"] == "inactive") {
                            var cardHeader = cardContainer.querySelector(".card-header");
                            cardHeader.classList.replace('bg-dark', 'bg-light');

                            var cardTitle = cardContainer.querySelector(".card-title");
                            cardTitle.classList.replace("text-white", "text-dark");

                            var span = document.createElement("span");
                            span.classList.add("badge");
                            span.classList.add("rounded-pill");
                            span.classList.add("bg-secondary");
                            span.innerHTML = "Disabled";
                            cardTitle.appendChild(span);

                            var status_link = cardContainer.querySelector(".update_status");
                            status_link.innerHTML = "Enable";
                        }
                    }
                }
            }

        }).catch(function(error) {
            console.log('There was a problem with the fetch request:' + error.message);
        });
      } else {
        console.log("Net response was OK but HTTP response wasn't");
      }
    })
    .catch(function(error) {
      console.log('There was a problem with the fetch request:' + error.message);
    });
}

function update_user(user_id) {
    var myHeaders = new Headers();

    form = document.getElementById("form");
    var data = new URLSearchParams();
    for (const pair of new FormData(form)) {
        data.append(pair[0], pair[1]);
    }
    var myInit = { method: 'POST',
                   headers: myHeaders,
                   body: data,
                   mode: 'cors',
                   cache: 'default' };

    var myRequest = new Request("/admin/user/"+ user_id +"/update", myInit);

    fetch(myRequest).then(function(response) {
      if(response.ok) {
        response.json().then(function(result) {
            if (result["updated"] == true) {
                var content = document.getElementsByClassName("content");

                var container = document.getElementById("toasts");
                var toast = document.createElement("div");
                toast.classList.add("toast");
                toast.setAttribute("role", "alert");
                toast.setAttribute("aria-live", "assertive");
                toast.setAttribute("aria-atomic", "true");
                toast.innerHTML = '<div class="toast-header text-white bg-dark border-0"><strong class="me-auto">WSC</strong><button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button></div><div class="toast-body">' + result["message"] + '</div>';
                container.appendChild(toast);
                content[0].insertBefore(container, document.getElementById("form"));
                var bsAlert = new bootstrap.Toast(toast);
                bsAlert.show();

                setTimeout(function() {
                    try {
                        var elem = content[0].querySelector(".alert .btn-close");
                        elem.click();
                    } catch (error) {}
                }, 10000);
            }
        }).catch(function(error) {
            console.log('There was a problem with the fetch request:' + error.message);
        });
      } else {
        console.log("Net response was OK but HTTP response wasn't");
      }
    })
    .catch(function(error) {
      console.log('There was a problem with the fetch request:' + error.message);
    });
}

function change_user_status(user_id) {
    var myHeaders = new Headers();

    var myInit = { method: 'POST',
                   headers: myHeaders,
                   mode: 'cors',
                   cache: 'default' };

    var myRequest = new Request("/admin/user/"+ user_id +"/update_status", myInit);

    fetch(myRequest).then(function(response) {
      if(response.ok) {
        response.json().then(function(result) {
            if (result["updated"] == true) {
                if (result["status"] != "") {
                    var content = document.getElementsByClassName("content");

                    var container = document.getElementById("toasts");
                    var toast = document.createElement("div");
                    toast.classList.add("toast");
                    toast.setAttribute("role", "alert");
                    toast.setAttribute("aria-live", "assertive");
                    toast.setAttribute("aria-atomic", "true");
                    toast.innerHTML = '<div class="toast-header text-white bg-dark border-0"><strong class="me-auto">WSC</strong><button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button></div><div class="toast-body">' + result["message"] + '</div>';
                    container.appendChild(toast);
                    content[0].insertBefore(container, document.getElementById("form"));
                    var bsAlert = new bootstrap.Toast(toast);
                    bsAlert.show();

                    var cardContainer = document.getElementById(user_id);

                    if (result["status"] == "active") {
                        var cardHeader = cardContainer.querySelector(".card-header");
                        cardHeader.classList.replace('bg-light', 'bg-dark');

                        var cardTitle = cardContainer.querySelector(".card-title");
                        cardTitle.classList.replace("text-dark", "text-white");

                        var titleBadge = cardContainer.querySelector(".badge");
                        titleBadge.remove();

                        var status_link = cardContainer.querySelector(".update_status");
                        status_link.innerHTML = "Disable";
                    } else {
                        if (result["status"] == "inactive") {
                            var cardHeader = cardContainer.querySelector(".card-header");
                            cardHeader.classList.replace('bg-dark', 'bg-light');

                            var cardTitle = cardContainer.querySelector(".card-title");
                            cardTitle.classList.replace("text-white", "text-dark");

                            var span = document.createElement("span");
                            span.classList.add("badge");
                            span.classList.add("rounded-pill");
                            span.classList.add("bg-secondary");
                            span.innerHTML = "Disabled";
                            cardTitle.appendChild(span);

                            var status_link = cardContainer.querySelector(".update_status");
                            status_link.innerHTML = "Enable";
                        }
                    }
                }
            }

        }).catch(function(error) {
            console.log('There was a problem with the fetch request:' + error.message);
        });
      } else {
        console.log("Net response was OK but HTTP response wasn't");
      }
    })
    .catch(function(error) {
      console.log('There was a problem with the fetch request:' + error.message);
    });
}

function get_service_information(app_id) {
    var myHeaders = new Headers();

    form = document.getElementById("form");
    var data = new URLSearchParams();
    for (const pair of new FormData(form)) {
        data.append(pair[0], pair[1]);
    }
    var myInit = { method: 'POST',
                   headers: myHeaders,
                   body: data,
                   mode: 'cors',
                   cache: 'default' };

    var myRequest = new Request("/service/" + app_id + "/callback", myInit);

    fetch(myRequest).then(function(response) {
      if(response.ok) {
        response.json().then(function(result) {
            var graphs = JSON.parse(result["graph_json"]);
            graphs.config = {displaylogo: false, modeBarButtonsToRemove: ['pan2d', 'zoom2d', 'lasso2d', 'autoScale2d', 'toggleSpikelines', 'hoverClosestCartesian', 'hoverCompareCartesian']}
            Plotly.newPlot('plot_chart', graphs);

            var logs = JSON.parse(result["logs"]);

            var section = document.getElementById("table");
            section.innerHTML = "";
            var table = document.createElement("table");
            var thead = document.createElement("thead");
            var tr = document.createElement('tr');
            var th1 = document.createElement('th');
            th1.innerText = "Status Date";
            th1.setAttribute("scope", "col")
            var th2 = document.createElement('th');
            th2.innerText = "Status Hour";
            th2.setAttribute("scope", "col")
            var th3 = document.createElement('th');
            th3.innerText = "Status";
            th3.setAttribute("scope", "col")
            var th4 = document.createElement('th');
            th4.innerText = "Other data";
            th4.setAttribute("scope", "col")

            table.classList.add("table", "table-hover", "table-sm", "text-center");
            thead.classList.add("table-dark");
            tr.appendChild(th1);
            tr.appendChild(th2);
            tr.appendChild(th3);
            tr.appendChild(th4);
            thead.appendChild(tr);
            table.appendChild(thead);

            var tbody = document.createElement("tbody");
            for (i = 0; i < logs.length; i++) {
                var tr = document.createElement('tr');

                var td1 = document.createElement('td');
                var td2 = document.createElement('td');
                var td3 = document.createElement('td');
                var td3_span = document.createElement('span');
                var td4 = document.createElement('td');

                const options = {year: 'numeric', month: 'short', day: 'numeric' };
                td1.innerText = new Date(Date.parse(logs[i]["status_date"])).toLocaleDateString('es-CO');
                if (logs[i]["status"] == "Running") {
                    tr.classList.add("table-success");
                    td3_span.setAttribute("style", "color: green");
                    td3_span.innerText = '▲';
                } else {
                    tr.classList.add("table-danger");
                    td3_span.setAttribute("style", "color: red");
                    td3_span.innerText = '▼';
                }
                td2.innerText = new Date(Date.parse(logs[i]["status_date"])).toLocaleTimeString('es-CO');
                if (logs[i]["other_data"] != "") {
                    td4.innerText = logs[i]["other_data"].split("-")[1];
                }

                td3.appendChild(td3_span);
                tr.appendChild(td1);
                tr.appendChild(td2);
                tr.appendChild(td3);
                tr.appendChild(td4);

                tbody.appendChild(tr);
            }
            table.appendChild(tbody);
            section.appendChild(table);
        }).catch(function(error) {
            console.log('There was a problem with the fetch request 1:' + error.message);
        });
      } else {
        console.log("Net response was OK but HTTP response wasn't");
      }
    })
    .catch(function(error) {
      console.log('There was a problem with the fetch request 2:' + error.message);
    });
}