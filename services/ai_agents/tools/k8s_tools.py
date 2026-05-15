"""Kubernetes tools with real kubectl commands."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from langchain_core.tools import BaseTool, tool


class K8sCommandInput(BaseModel):
    command: str = ""
    namespace: str = "default"
    resource_type: str = "pods"
    resource_name: Optional[str] = None
    extra_args: str = ""


def _run_kubectl(command: str) -> str:
    """Execute kubectl command."""
    import subprocess
    try:
        result = subprocess.run(
            f"kubectl {command}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout if result.stdout else result.stderr
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except Exception as e:
        return f"Error: {str(e)}"


@tool("k8s_list_pods")
def k8s_list_pods(namespace: str = "default") -> str:
    """List all pods in a Kubernetes namespace.
    
    Args:
        namespace: The Kubernetes namespace (default: default)
    """
    return _run_kubectl(f"get pods -n {namespace} -o wide")


@tool("k8s_get_pod")
def k8s_get_pod(pod_name: str, namespace: str = "default") -> str:
    """Get detailed information about a specific pod.
    
    Args:
        pod_name: Name of the pod
        namespace: The Kubernetes namespace
    """
    return _run_kubectl(f"get pod {pod_name} -n {namespace} -o yaml")


@tool("k8s_describe_pod")
def k8s_describe_pod(pod_name: str, namespace: str = "default") -> str:
    """Get detailed description of a pod including events.
    
    Args:
        pod_name: Name of the pod
        namespace: The Kubernetes namespace
    """
    return _run_kubectl(f"describe pod {pod_name} -n {namespace}")


@tool("k8s_get_pod_logs")
def k8s_get_pod_logs(pod_name: str, namespace: str = "default", lines: int = 50) -> str:
    """Get logs from a pod.
    
    Args:
        pod_name: Name of the pod
        namespace: The Kubernetes namespace
        lines: Number of log lines to retrieve
    """
    return _run_kubectl(f"logs {pod_name} -n {namespace} --tail={lines}")


@tool("k8s_list_services")
def k8s_list_services(namespace: str = "default") -> str:
    """List all services in a Kubernetes namespace."""
    return _run_kubectl(f"get svc -n {namespace}")


@tool("k8s_list_deployments")
def k8s_list_deployments(namespace: str = "default") -> str:
    """List all deployments in a Kubernetes namespace."""
    return _run_kubectl(f"get deployments -n {namespace}")


@tool("k8s_scale_deployment")
def k8s_scale_deployment(deployment_name: str, replicas: int, namespace: str = "default") -> str:
    """Scale a deployment to a specific number of replicas.
    
    Args:
        deployment_name: Name of the deployment
        replicas: Number of replicas
        namespace: The Kubernetes namespace
    """
    return _run_kubectl(f"scale deployment {deployment_name} -n {namespace} --replicas={replicas}")


@tool("k8s_get_node_status")
def k8s_get_node_status() -> str:
    """Get status of all nodes in the cluster."""
    return _run_kubectl("get nodes -o wide")


@tool("k8s_get_events")
def k8s_get_events(namespace: str = "default") -> str:
    """Get recent events in a namespace."""
    return _run_kubectl(f"get events -n {namespace} --sort-by='.lastTimestamp'")


def get_all_k8s_tools() -> List[BaseTool]:
    """Get all Kubernetes tools."""
    return [
        k8s_list_pods,
        k8s_get_pod,
        k8s_describe_pod,
        k8s_get_pod_logs,
        k8s_list_services,
        k8s_list_deployments,
        k8s_scale_deployment,
        k8s_get_node_status,
        k8s_get_events,
    ]
