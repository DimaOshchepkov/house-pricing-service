local('kubectl create secret generic housing-env --from-env-file=.env.kubernetes --dry-run=client -o yaml | kubectl apply -f -')


docker_build(
    'housing-service',
    '.',
    live_update=[
        sync('./src', '/app/src'),
        sync('./alembic', '/app/alembic'),
        run('uv sync --locked --no-dev', trigger='./pyproject.toml'),
        run('uv run alembic upgrade head', trigger='./alembic'),
        run('pkill -f "uvicorn app.main:app" || true', trigger=['./src']),
    ]
)


k8s_yaml('k8s/postgres.yaml')
k8s_yaml('k8s/deployment.yaml')
k8s_yaml('k8s/service.yaml')

k8s_resource('postgres')
k8s_resource(
    'housing-service',
    port_forwards='8080:8000',
    resource_deps=['postgres']
)