let chart, tempGauge, humGauge;
let running = false;

function createChart() {
  const ctx = document.getElementById("sensorChart").getContext("2d");
  return new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        { label: "Teplota", data: [], borderColor: "red" },
        { label: "Vlhkosť", data: [], borderColor: "blue" }
      ]
    },
    options: {
      scales: {
        y: { beginAtZero: true },
        x: { ticks: { autoSkip: true, maxTicksLimit: 10 } }
      }
    }
  });
}

function createGauge(id, max, units) {
  const g = new RadialGauge({
    renderTo: id,
    width: 250,
    height: 250,
    units,
    minValue: 0,
    maxValue: max,
    majorTicks: max === 100 ? ["0","20","40","60","80","100"] : ["0","10","20","30","40","50"],
    animation: true,
    value: 0
  });
  g.draw();
  return g;
}

function fetchData() {
  if (!running) return;
  fetch("/data").then(res => res.json()).then(json => {
    const data = json.data.sort((a, b) => new Date(a[2]) - new Date(b[2]));
    const temps = data.map(d => d[0]);
    const hums = data.map(d => d[1]);
    const times = data.map(d => new Date(d[2]).toLocaleTimeString());

    // Tabuľka
    document.getElementById("table-body").innerHTML = data.map(d =>
      `<tr><td>${d[2]}</td><td>${d[0]}</td><td>${d[1]}</td></tr>`).reverse().join("");

    // Graf
    chart.data.labels = times;
    chart.data.datasets[0].data = temps;
    chart.data.datasets[1].data = hums;
    chart.update();

    // Ciferníky
    const latestTemp = temps[temps.length - 1];
    const latestHum = hums[hums.length - 1];
    document.getElementById("temp-text").innerText = latestTemp;
    document.getElementById("hum-text").innerText = latestHum;
    tempGauge.value = latestTemp;
    humGauge.value = latestHum;
  });
}

function updateStatus(text) {
  document.getElementById("status").innerText = text;
}

window.onload = () => {
  chart = createChart();
  tempGauge = createGauge("tempGauge", 50, "°C");
  humGauge = createGauge("humGauge", 100, "%");

  document.getElementById("open-btn").onclick = () => {
    fetch("/open").then(() => {
      updateStatus("Pripojenie úspešné.");
    });
  };

  document.getElementById("start-btn").onclick = () => {
    fetch("/start").then(() => {
      running = true;
      updateStatus("Meranie prebieha.");
      document.getElementById("monitoring-section").style.display = "block";
    });
  };

  document.getElementById("stop-btn").onclick = () => {
    fetch("/stop").then(() => {
      running = false;
      updateStatus("⏸ Meranie pozastavené.");
    });
  };

  document.getElementById("close-btn").onclick = () => {
    fetch("/close").then(() => {
      running = false;
      updateStatus("Systém zatvorený.");
      document.getElementById("monitoring-section").style.display = "none";
    });
  };

  setInterval(fetchData, 1000);
};
