Сначала пробовал вручную настроить постгрес. Часто путался

kubectl create secret generic house-secrets --from-literal=POSTGRES_PASSWORD=postgres
kubectl apply -f postgres.yaml
Почему-то не могу подключится к серверу приложения
Помогло kubectl port-forward svc/housing-service 8080:80
Но почему запрос приниматься стал все равно на 8080 портe
Потому что 
  ports:
    - port: 80           # ← порт Service
      targetPort: 8000   # ← порт приложения в поде

root@postgres-6594f4c95d-864l2:/# psql -U postgres -d house -c "\dt"
Did not find any relations.
кажется нет миграций

root@housing-service-9d8fb46b9-zlh8n:/app# uv run alembic upgrade head
Bytecode compiled 8360 files in 2.44s
  FAILED: No 'script_location' key found in configuration.

Не понятно как выполнить миграции

Попробую добавить alembic
COPY alembic.ini ./
COPY alembic/ alembic/

kubectl rollout restart deployment housing

надо сначала пересобрать образ 
docker build -t house-pricing-service:latest .

надо загрузить теперь
kind load docker-image house-pricing-service:latest

Затем при исправлении домашнего добавил Tilt. Теперь запуск описан в Tiltfile
Можно запустить все с помощью tilt up

В ci лучше не использовать tilt up. Это для локальной разработки.
Не получилось слить в main. упали тесты
Отсутсвует модель. Это критично
Временно буду хранить в lfs

Ошибка при сборке:
Error: buildx failed with: ERROR: failed to build: invalid tag "ghcr.io/DimaOshchepkov/housing-service/sha-642ffa366ef00b55789104fa2d36664e43d01408": repository name must be lowercase