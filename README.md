# Housing pricing service

## Get started
```bash
cp .env.example .env
docker compose up
```

Swagger ui:
`http://localhost:8000/docs`


Запустить тесты:
```bash
uv sync
uv run pytest
```

## ДЗ 
Пример данных таблицы predictions

aa346c03-23d1-448f-94d6-2be9b770d476,225a4cb6-6b01-49bb-9dd0-aa5143361f53,"{""MedInc"": 3.53, ""AveOccup"": 2.82, ""AveRooms"": 5.23, ""HouseAge"": 29, ""Latitude"": 34.26, ""AveBedrms"": 1.05, ""Longitude"": -118.49, ""Population"": 1166}",2.115159566047026,true,model_v20260914_165745.cbm,4.48,2026-09-16 19:55:58.714128 +00:00
06aabd3c-a5bd-7a8f-8000-afdac89a066d,abc6387c-629c-46bc-b674-fc708e2275de,"{""MedInc"": 3.53, ""HouseAge"": 29, ""AveRooms"": 5.23, ""AveBedrms"": 1.05, ""Population"": 1166, ""AveOccup"": 2.82, ""Latitude"": 34.26, ""Longitude"": -118.49}",2.115159566047026,true,model_v20260914_165745.cbm,8.88,2026-09-17 11:49:30.358853 +00:00
06aabd3c-f6d6-71db-8000-d0baa05a6d95,9d0146dc-f125-47ac-bcb6-2d407b9fd407,"{""MedInc"": 3.53, ""HouseAge"": 29, ""AveRooms"": 5.23, ""AveBedrms"": 1.05, ""Population"": 1166, ""AveOccup"": 2.82, ""Latitude"": 34.26, ""Longitude"": -118.49}",2.115159566047026,true,model_v20260914_165745.cbm,0.68,2026-09-17 11:49:35.427316 +00:00
06aabd7f-5381-7571-8000-9993ce7b6056,d93d013c-e56f-44d1-a685-6060b49133e0,"{""MedInc"": 3.53, ""HouseAge"": 29, ""AveRooms"": 5.23, ""AveBedrms"": 1.05, ""Population"": 1166, ""AveOccup"": 2.82, ""Latitude"": 34.26, ""Longitude"": -118.49}",2.115159566047026,true,model_v20260914_165745.cbm,5.18,2026-09-17 12:07:17.219104 +00:00
