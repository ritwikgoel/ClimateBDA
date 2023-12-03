const app = {
  init: () => {
    document.getElementById('btnGet').addEventListener('click', app.fetchWeather);
    document.getElementById('btnCurrent').addEventListener('click', app.getLocation);

    // Populate date selector and update weather on change
    const dateSelector = document.getElementById('dateSelector');
    dateSelector.addEventListener('change', app.updateWeatherByDate);
    app.populateDateSelector();
  },

  fetchWeather: (ev) => {
    let lat = document.getElementById('latitude').value;
    let lon = document.getElementById('longitude').value;
    let key = '30b11b3640b39d0cadcb19e2689709e7';
    let lang = 'en';
    let units = 'metric';

    app.fetchWeatherData(lat, lon, key, units, lang, app.showWeather);
  },

  getLocation: (ev) => {
    let opts = {
      enableHighAccuracy: true,
      timeout: 1000 * 10, // 10 seconds
      maximumAge: 1000 * 60 * 5, // 5 minutes
    };
    navigator.geolocation.getCurrentPosition(app.ftw, app.wtf, opts);
  },

  ftw: (position) => {
    document.getElementById('latitude').value = position.coords.latitude.toFixed(2);
    document.getElementById('longitude').value = position.coords.longitude.toFixed(2);
  },

  wtf: (err) => {
    console.error(err);
  },

  showWeather: (resp) => {
    let weatherContainer = document.getElementById('weatherContainer');
    weatherContainer.innerHTML = '';

    resp.daily.slice(0, 3).forEach((day) => {
      let dt = new Date(day.dt * 1000);
      let sr = new Date(day.sunrise * 1000).toTimeString();
      let ss = new Date(day.sunset * 1000).toTimeString();

      let card = document.createElement('div');
      card.className = 'col';
      card.innerHTML = `<div class="card">
        <h5 class="card-title p-2">${dt.toDateString()}</h5>
        <img src="http://openweathermap.org/img/wn/${day.weather[0].icon}@4x.png"
          class="card-img-top" alt="${day.weather[0].description}" />
        <div class="card-body">
          <h3 class="card-title">${day.weather[0].main}</h3>
          <p class="card-text">High ${day.temp.max}&deg;C Low ${day.temp.min}&deg;C</p>
          <p class="card-text">High Feels like ${day.feels_like.day}&deg;C</p>
          <p class="card-text">Pressure ${day.pressure}mb</p>
          <p class="card-text">Humidity ${day.humidity}%</p>
          <p class="card-text">UV Index ${day.uvi}</p>
          <p class="card-text">Precipitation ${day.pop * 100}%</p>
          <p class="card-text">Dewpoint ${day.dew_point}</p>
          <p class="card-text">Wind ${day.wind_speed}m/s, ${day.wind_deg}&deg;</p>
          <p class="card-text">Sunrise ${sr}</p>
          <p class="card-text">Sunset ${ss}</p>
        </div>
      </div>`;

      weatherContainer.appendChild(card);
    });
  },

  populateDateSelector: () => {
    const dateSelector = document.getElementById('dateSelector');
    const today = new Date();
    
    for (let i = 0; i < 3; i++) {
      let date = new Date(today);
      date.setDate(today.getDate() - i);
      let formattedDate = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
      let option = document.createElement('option');
      option.value = i;
      option.text = formattedDate;
      dateSelector.add(option);
    }

    app.updateWeatherByDate();
  },

  updateWeatherByDate: async () => {
    let dateSelector = document.getElementById('dateSelector');
    let selectedDateIndex = dateSelector.value;
    let weatherCards = document.getElementById('weatherContainer');
    weatherCards.innerHTML = '';

    try {
      let selectedDate = dateSelector.options[selectedDateIndex].text;
      const weatherData = await app.getWeatherData(selectedDate);
      
      for (let i = selectedDateIndex; i >= selectedDateIndex - 2; i--) {
        let day = weatherData.daily[i];
        let dt = new Date(day.dt * 1000);
        let sr = new Date(day.sunrise * 1000).toTimeString();
        let ss = new Date(day.sunset * 1000).toTimeString();

        let card = document.createElement('div');
        card.className = 'col';
        card.innerHTML = `<div class="card">
          <h5 class="card-title p-2">${dt.toDateString()}</h5>
          <img src="http://openweathermap.org/img/wn/${day.weather[0].icon}@4x.png"
            class="card-img-top" alt="${day.weather[0].description}" />
          <div class="card-body">
            <h3 class="card-title">${day.weather[0].main}</h3>
            <p class="card-text">High ${day.temp.max}&deg;C Low ${day.temp.min}&deg;C</p>
            <p class="card-text">High Feels like ${day.feels_like.day}&deg;C</p>
            <p class="card-text">Pressure ${day.pressure}mb</p>
            <p class="card-text">Humidity ${day.humidity}%</p>
            <p class="card-text">UV Index ${day.uvi}</p>
            <p class="card-text">Precipitation ${day.pop * 100}%</p>
            <p class="card-text">Dewpoint ${day.dew_point}</p>
            <p class="card-text">Wind ${day.wind_speed}m/s, ${day.wind_deg}&deg;</p>
            <p class="card-text">Sunrise ${sr}</p>
            <p class="card-text">Sunset ${ss}</p>
          </div>
        </div>`;

        weatherCards.appendChild(card);
      }
    } catch (error) {
      console.error(`Error fetching weather data: ${error.message}`);
    }
  },

  getWeatherData: async (selectedDate) => {
    let lat = document.getElementById('latitude').value;
    let lon = document.getElementById('longitude').value;
    let key = '30b11b3640b39d0cadcb19e2689709e7';
    let lang = 'en';
    let units = 'metric';

    let url = `http://api.openweathermap.org/data/2.5/onecall?lat=${lat}&lon=${lon}&appid=${key}&units=${units}&lang=${lang}&date=${selectedDate}`;
    
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(response.statusText);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      throw new Error(`Error fetching weather data: ${error.message}`);
    }
  },

  fetchWeatherData: async (lat, lon, key, units, lang, callback) => {
    let url = `http://api.openweathermap.org/data/2.5/onecall?lat=${lat}&lon=${lon}&appid=${key}&units=${units}&lang=${lang}`;
    
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(response.statusText);
      }
      const data = await response.json();
      callback(data);
    } catch (error) {
      console.error(`Error fetching weather data: ${error.message}`);
    }
  },
};

app.init();
