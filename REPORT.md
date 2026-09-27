# 2.1 
https://github.com/DimaOshchepkov/house-pricing-service/actions/runs/36330462817/job/108651273606
https://github.com/DimaOshchepkov/house-pricing-service/pkgs/container/housing-service%2Fsha-896ca213e2dbc96099de563e5d71dd5e12e03740

# 2.2 Процесс: ветка и pull request
https://github.com/DimaOshchepkov/house-pricing-service/pull/24
# 2.3 Красные прогоны
1. Не прошли тесты, так как в них тестируется и сама модель
2. Возникнет ошибка на стадии deploy. Под не получит переменную окружения
3. Под останется в состоянии Pending

# Семь вопросов
1. вф
2. Deployment обновился. Создается новый replicaset, но старый replicaset существует некоторое время и тоже пытается пулить новый образ.
3. Gihub secrets -> GitHub actions -> kubectl create secret generic housing-env -> Secret housing-env -> Pod
4. Тесты провалились. Собрался образ с ошибками
5. main отвечает за продакшен. Только после попадания кода в прод нужно запускать сборку и деплой. Пул реквест будет обсуждаться командой вначале, поэтому еще рано билдить и деплоить.     if: github.ref == 'refs/heads/master',     needs: build
6. Не знаю. У меня не так. Я считаю нельзя использовать postgres в режиме несколькоих реплик таким образом. Нужно смотреть в сторону специализированных решений.
7. 1. Под не собрался. 2. Произошла ошибка в deploy. Pod в pending

Журнал ошибок в ERRORS.md