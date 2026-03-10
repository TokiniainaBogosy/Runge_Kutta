const ctx = document.getElementById("myChart");
fetch("/api/capital")
  .then(res => res.json())
  .then(data => {
      new Chart(ctx, {
          type: 'line',
          data: {
              labels: data["mois"],
              datasets: [{
                  label: 'Capital',
                  data: data["capital"],
                  borderWidth: 3,
              }]
          },
          options:{
            responsive: true,
          }
      });
  });
  
