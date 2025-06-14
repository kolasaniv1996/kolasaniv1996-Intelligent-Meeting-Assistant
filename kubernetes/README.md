# Kubernetes Configuration

This directory contains Kubernetes configuration files (YAML) for deploying the Gen AI Work Buddy application and its services.
It also includes plans for Helm charts for streamlined deployment.

## Services

Basic Kubernetes deployment and service YAML files are provided for each microservice:

*   `auth-service.yaml`: Deploys the authentication service. It requires a ConfigMap and Secrets for configuration (examples provided within the file, should be managed securely and separately).
*   `integration-service.yaml`: Deploys the integration service. Requires ConfigMap and Secrets for Jira/Confluence API tokens and URLs.
*   `meeting-service.yaml`: Deploys the meeting management service. Configured to connect to `integration-service` and a Redis instance within the cluster.
*   `notification-service.yaml`: Deploys the conceptual notification service (Redis consumer). Configured to connect to a Redis instance.

## General Notes

*   **Docker Images**: You need to build Docker images for each service and push them to a container registry. Update the `image:` fields in the deployment YAMLs with your actual image paths.
*   **Configuration**:
    *   Sensitive data (API keys, secrets, passwords) are referenced via `secretKeyRef`. These Kubernetes Secrets must be created in your cluster *before* deploying the applications. Example secret structures are commented in the YAMLs for guidance but should **not** be committed with real values.
    *   Non-sensitive configuration is referenced via `configMapKeyRef`. Example ConfigMaps are included in the service YAML files but can also be managed separately.
    *   Service discovery within the cluster is assumed (e.g., `http://meeting-service:80` where `meeting-service` is the K8s service name and `80` is its ClusterIP port).
*   **Redis & Neo4j**: These configurations assume that Redis and Neo4j are running and accessible within the Kubernetes cluster (e.g., deployed via their own Helm charts or as managed services). The service names like `redis-master.default.svc.cluster.local` or `neo4j.default.svc.cluster.local` are examples and should be adjusted to your specific setup.
*   **Probes**: Basic `readinessProbe` and `livenessProbe` examples are included for services with HTTP endpoints. These should be customized.
*   **Ingress**: To expose services (like `auth-service`) externally, an Ingress controller and Ingress resources would be needed. This is not covered in these basic YAMLs.

## Applying Configurations

You can apply these configurations to your Kubernetes cluster using `kubectl apply -f <filename>.yaml`.
Remember to create ConfigMaps and Secrets first where specified.

Example for `auth-service` (after creating its ConfigMap and Secret):
```bash
kubectl apply -f kubernetes/auth-service.yaml
```

## Next Steps (Helm)

The next step in improving deployment is to use Helm charts. See the `helm/` directory (to be created) for packaging these configurations.

## Helm Chart

A basic Helm chart is available in the `helm/work-buddy-chart/` directory. This chart provides a templated way to deploy the application and its services. See the [Helm README](../helm/README.md) for more details.
