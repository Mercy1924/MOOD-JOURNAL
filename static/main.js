// Wait for DOM
document.addEventListener("DOMContentLoaded", function () {
  // Chart.js context
  const ctx = document.getElementById("moodChart").getContext("2d");

  // Initialize chart
  let moodChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Mood score over time",
          data: [],
          borderColor: "rgba(75, 192, 192, 1)",
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          fill: true,
          tension: 0.2
        }
      ]
    },
    options: {
      scales: {
        x: {
          title: { display: true, text: "Date" }
        },
        y: {
          min: 0,
          max: 1,
          title: { display: true, text: "Score (0-1)" }
        }
      }
    }
  });

  // Fetch data from Flask API
  async function loadEntries() {
    try {
      const res = await fetch("/api/entries");
      const data = await res.json();

      // Map to labels and values
      const labels = data.map(e =>
        new Date(e.created_at).toLocaleDateString()
      );
      const scores = data.map(e => e.score);

      // Update chart
      moodChart.data.labels = labels;
      moodChart.data.datasets[0].data = scores;
      moodChart.update();
    } catch (err) {
      console.error("Error loading entries:", err);
    }
  }

  loadEntries();
});
