function updateSecondSelector() {
    var firstSelector = document.getElementById("kafter");
    var secondSelector = document.getElementById("group");
  
    // Очистка текущих значений второго селектора
    secondSelector.innerHTML = "";
  
    // Получение выбранного значения первого селектора
    var selectedValue = firstSelector.value;
  
    // В зависимости от выбранного значения первого селектора, изменяем второй селектор
    switch (selectedValue) {
      case "СИ":
        // Добавляем новые опции второго селектора для "Опции 1"
        secondSelector.innerHTML += "<option value='ПГС'>ПГС</option>";
        secondSelector.innerHTML += "<option value='ГСХ'>ГСХ</option>";
        secondSelector.innerHTML += "<option value='ПСК'>ПСК</option>";
        secondSelector.innerHTML += "<option value='АД'>АД</option>";
        secondSelector.innerHTML += "<option value='ТГСВ'>ТГСВ</option>";
        secondSelector.innerHTML += "<option value='СМиДС'>СМиДС</option>";
        break;
      case "ИЛКЛАТиЭ":
        // Добавляем новые опции второго селектора для "Опции 2"
        secondSelector.innerHTML += "<option value='ММ'>ММ</option>";
        secondSelector.innerHTML += "<option value='САТ'>САТ</option>";
        secondSelector.innerHTML += "<option value='ТД'>ТД</option>";
        secondSelector.innerHTML += "<option value='ТО'>ТО</option>";
        secondSelector.innerHTML += "<option value='ЛХ'>ЛХ</option>";
        secondSelector.innerHTML += "<option value='ЛА'>ЛА</option>";
        secondSelector.innerHTML += "<option value='САД'>САД</option>";
        secondSelector.innerHTML += "<option value='МЛП'>МЛП</option>";
        secondSelector.innerHTML += "<option value='ТБ'>ТБ</option>";
        break;
      case "ИЭИ":
        // Добавляем новые опции второго селектора для "Опции 3"
        secondSelector.innerHTML += "<option value='ЭБ'>ЭБ</option>";
        secondSelector.innerHTML += "<option value='ЭКОН'>ЭКОН</option>";
        secondSelector.innerHTML += "<option value='ПИ'>ПИ</option>";
        secondSelector.innerHTML += "<option value='ПрИ'>ПрИ</option>";
        secondSelector.innerHTML += "<option value='ИВТ'>ИВТ</option>";
        secondSelector.innerHTML += "<option value='ИСТ'>ИСТ</option>";
        break;
    }
  }
  
  // Вызываем функцию updateSecondSelector() в начале, чтобы установить начальные значения второго селектора
  updateSecondSelector();