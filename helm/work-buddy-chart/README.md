# Gen AI Work Buddy Helm Chart (work-buddy-chart)

This Helm chart deploys the Gen AI Work Buddy application and its microservices onto a Kubernetes cluster.

## Prerequisites

1.  **Kubernetes Cluster**: A running Kubernetes cluster (e.g., Minikube, Kind, GKE, EKS, AKS).
2.  **Helm**: Helm 3 installed and configured to talk to your cluster.
3.  **Docker Images**: Before deploying with this chart, you must build and push Docker images for each service to a container registry accessible by your Kubernetes cluster.
    *   Each service (`auth-service`, `integration-service`, `meeting-service`, `notification-service`, `ai-processing-service`) has a `Dockerfile` in its respective directory (e.g., `services/auth-service/Dockerfile`).
    *   **Build Example** (for `auth-service`):
        ```bash
        cd services/auth-service
        docker build -t <your-registry>/auth-service:<tag> .
        # e.g., mydockerhub/auth-service:0.1.0
        cd ../..
        ```
        Repeat for all services.
    *   **Push Example** (for `auth-service`):
        ```bash
        docker push <your-registry>/auth-service:<tag>
        ```
    *   Update the `image.repository` and `image.tag` values in `values.yaml` (or override them during Helm installation) to point to your images.
4.  **External Dependencies (Assumed)**:
    *   **Redis**: A Redis instance should be running and accessible. Connection details can be configured in `values.yaml` (see `global.redis`).
    *   **Neo4j**: A Neo4j instance should be running and accessible. Connection details can be configured in `values.yaml` (see `global.neo4j`). You might deploy these using their own Helm charts or use managed services.
5.  **Kubernetes Secrets**: For production deployments, sensitive data (API keys, passwords, client secrets) should be stored in Kubernetes Secrets *before* deploying the chart. The `values.yaml` file has placeholders for these secrets (e.g., `authService.secrets.googleClientSecret`). For development, these can be set in `values.yaml` directly, but **this is not secure for production**. The Helm templates assume these secrets will be provided. You might need to create these secrets manually in your cluster.

## Chart Structure

*   `Chart.yaml`: Metadata about the chart.
*   `values.yaml`: Default configuration values. This is the primary file you'll modify to configure your deployment.
*   `templates/`: Contains the Kubernetes manifest templates.
    *   `_helpers.tpl`: Common helper templates.
    *   `auth-service.yaml`: Template for the authentication service (more services to be added here).
*   `charts/`: For sub-chart dependencies (currently empty).

## Installation

To install the chart with the release name `my-work-buddy`:

```bash
helm install my-work-buddy ./helm/work-buddy-chart -f ./helm/work-buddy-chart/values.yaml
```
Or, to override values directly:
```bash
helm install my-work-buddy ./helm/work-buddy-chart \
  --set authService.image.tag=0.1.1 \
  --set global.redis.host=my-redis-host
```

## Uninstallation

To uninstall/delete the `my-work-buddy` deployment:

```bash
helm uninstall my-work-buddy
```

## Configuration

The primary way to configure this chart is by modifying the `values.yaml` file or by overriding values using the `--set` flag during installation or upgrade.

Key configurable items in `values.yaml`:
*   `replicaCount`
*   `imagePullSecrets`
*   Global settings for `redis` and `neo4j`.
*   Service-specific settings for each enabled service (`authService`, `integrationService`, etc.), including:
    *   `enabled`: Toggle deployment of the service.
    *   `image.repository`, `image.tag`, `image.pullPolicy`.
    *   Ports and service types.
    *   `config`: Non-sensitive configuration values.
    *   `secrets`: Placeholders for sensitive values (should be managed securely).

Refer to the comments in `values.yaml` for more details on each parameter.
