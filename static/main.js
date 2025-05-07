let limits = {
    min_temp: 18,
    max_temp: 30,
    min_hum: 30,
    max_hum: 60
};

const socket = io();
const table = document.getElementById("data-table");
const statusText = document.getElementById("status-text");

function sendCommand(cmd) {
    socket.emit(cmd);
    if (cmd === "close_system") resetDisplay();
}

function resetDisplay() {
    document.getElementById("temp-text").innerText = "--";
    document.getElementById("hum-text").innerText = "--";
    tempGauge.value = 0;
    humGauge.value = 0;
    table.innerHTML = "";
    chart.data.labels = [];
    chart.data.datasets.forEach(ds => ds.data = []);
    chart.update();
}

const chart = new Chart(document.getElementById("sensorChart").getContext("2d"), {
    type: "line",
    data: {
        labels: [],
        datasets: [
        { label: "Teplota (°C)", data: [], borderColor: "red", fill: false },
        { label: "Vlhkosť (%)", data: [], borderColor: "blue", fill: false }
        ]
    },
    options: { responsive: true, scales: { y: { beginAtZero: true } } }
});


const tempGauge = new RadialGauge({
    renderTo: "tempGauge",
    minValue: 0,
    maxValue: 50,
    units: "°C",
    value: 0,
    majorTicks: ["0","10","20","30","40","50"],
    animation: true,
    valueInt: 2,
    valueDec: 1,
    valueTextShadow: false,
    colorValueText: "#000"
}).draw();


const humGauge = new RadialGauge({
    renderTo: "humGauge",
    minValue: 0,
    maxValue: 100,
    units: "%",
    value: 0,
    majorTicks: ["0","20","40","60","80","100"],
    animation: true,
    valueInt: 2,
    valueDec: 1,
    valueTextShadow: false,
    colorValueText: "#000"
}).draw();


socket.on("connect", () => {
    socket.emit("get_current_limits");  
});

socket.on("current_limits", (data) => {
    document.getElementById("min-temp").value = data.min_temp;
    document.getElementById("min-hum").value = data.min_hum;
});


socket.on("new_data", (data) => {
    const time = new Date(data.cas).toLocaleTimeString('sk-SK');
    const temp = data.teplota;
    const hum = data.vlhkost;
    document.getElementById("temp-text").innerText = temp;
    document.getElementById("hum-text").innerText = hum;
    tempGauge.value = temp;
    humGauge.value = hum;
    tempGauge.update({ colorValueText: (temp < limits.min_temp || temp > limits.max_temp) ? "red" : "black" });
    humGauge.update({ colorValueText: (hum < limits.min_hum || hum > limits.max_hum) ? "red" : "black" });
    let tempClass = "";
    let humClass = "";

    if (temp < limits.min_temp || temp > limits.max_temp) tempClass = "table-danger";
    if (hum < limits.min_hum || hum > limits.max_hum) humClass = "table-danger";

    const minTemp = parseFloat(document.getElementById("min-temp").value);
    const minHum = parseFloat(document.getElementById("min-hum").value);

    if (temp < minTemp || hum < minHum) return;  


    const row = `<tr>
        <td>${time}</td>
        <td class="${tempClass}">${temp}</td>
        <td class="${humClass}">${hum}</td>
    </tr>`;

    table.insertAdjacentHTML("afterbegin", row);
    if (table.rows.length > 10) table.deleteRow(-1);
    chart.data.labels.push(time);
    chart.data.datasets[0].data.push(temp);
    chart.data.datasets[1].data.push(hum);
    if (chart.data.labels.length > 20) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
        chart.data.datasets[1].data.shift();
    }
    chart.update();
});

socket.on("status_update", (data) => {
    statusText.textContent = data.status;
});

function setLimits(e) {
    e.preventDefault();
    limits.min_temp = parseFloat(document.getElementById("minTemp").value);
    limits.max_temp = parseFloat(document.getElementById("maxTemp").value);
    limits.min_hum = parseFloat(document.getElementById("minHum").value);
    limits.max_hum = parseFloat(document.getElementById("maxHum").value);

    socket.emit("set_limits", {
        min_temp: limits.min_temp,
        min_hum: limits.min_hum
    });
}

socket.on("limit_status", data => {
    document.getElementById("limit-status").innerText = data.message;
    document.getElementById("save-status").innerText = data.message;
});

function submitMinLimits() {
    const minTemp = parseFloat(document.getElementById("min-temp").value);
    const minHum = parseFloat(document.getElementById("min-hum").value);

    socket.emit("set_min_thresholds", {
        min_temp: minTemp,
        min_hum: minHum
    });
}

function exportChart() {
    const canvas = document.getElementById("sensorChart");
    const link = document.createElement("a");
    link.download = "graf_senzorov.png";
    link.href = canvas.toDataURL("image/png", 1.0);
    link.click();
}

