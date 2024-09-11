import docker
import uuid

# Initialize Docker client
client = docker.from_env()

def generate_unique_name(base_name):
    """Generate a unique name for the container."""
    return f"{base_name}_{uuid.uuid4().hex[:6]}"


def deploy_cluster(image_name, cluster_name, num_instances, command=None):
    """
    Deploy a cluster of containers with the specified image and cluster name.
    """
    try:
        containers = []
        for i in range(num_instances):
            container = client.containers.run(
                image_name,
                command=command,
                detach=True,
                labels={"cluster_name": cluster_name}
            )
            containers.append(container)
        return containers, None
    except Exception as e:
        return None, str(e)

def list_clusters():
    """
    List all cluster names from Docker containers.
    """
    try:
        containers = client.containers.list(all=True)
        clusters = set()
        for container in containers:
            cluster_name = container.labels.get('cluster_name')
            if cluster_name:
                clusters.add(cluster_name)
        return list(clusters), None
    except Exception as e:
        return None, str(e)

def scale_cluster(cluster_name, new_num_instances, image_name, command=None):
    """
    Scales a Docker cluster by adjusting the number of instances of a given container.
    """
    client = docker.from_env()
    containers = client.containers.list(all=True)
    
    # Filter containers by cluster name
    cluster_containers = [container for container in containers if cluster_name in container.name]
    
    # If scaling up, create more containers
    if len(cluster_containers) < new_num_instances:
        num_to_add = new_num_instances - len(cluster_containers)
        created_containers = []
        
        for i in range(num_to_add):
            new_container_name = f"{cluster_name}_{len(cluster_containers) + i + 1}"
            container = client.containers.run(
                image_name,
                name=new_container_name,
                command=command,
                detach=True
            )
            created_containers.append(container)
        # Return both the existing and newly created containers
        updated_containers = cluster_containers + created_containers
    else:
        updated_containers = cluster_containers
    
    return updated_containers, None


def list_containers_in_cluster(cluster_name):
    """
    Lists all containers that belong to a specified cluster.
    """
    try:
        # List all containers
        all_containers = client.containers.list(all=True)
        
        # Filter containers by the cluster name
        cluster_containers = [container for container in all_containers if cluster_name in container.name]
        
        # Create a list of container details to return
        container_details = []
        for container in cluster_containers:
            container_details.append({
                'id': container.id,
                'name': container.name,
                'status': container.status
            })
        
        return container_details, None
    except Exception as e:
        return None, str(e)

def delete_cluster(cluster_name):
    """
    Deletes all containers in the cluster and removes associated images if any.
    :param cluster_name: Name of the cluster.
    :return: Success status and error message if any.
    """
    success = False
    err = None
    try:
        containers = client.containers.list(all=True, filters={"name": cluster_name})
        for container in containers:
            container.remove(force=True)
        
        success = True
    except docker.errors.APIError as e:
        err = str(e)
    
    return success, err

def save_cluster_state(cluster_name):
    """
    Saves the current state of the cluster by committing each container to a new image.
    :param cluster_name: Name of the cluster.
    :return: List of saved image tags and error message if any.
    """
    saved_images = []
    err = None
    try:
        containers = client.containers.list(all=True, filters={"name": cluster_name})
        for container in containers:
            image_tag = f"{cluster_name}_snapshot_{container.short_id}"
            container.commit(repository=image_tag)
            saved_images.append(image_tag)
    except docker.errors.APIError as e:
        err = str(e)
    
    return saved_images, err

def restore_cluster_state(cluster_name, image_tags):
    """
    Restores a cluster's state by creating containers from saved images.
    :param cluster_name: Name of the cluster.
    :param image_tags: List of image tags to restore from.
    :return: List of created containers and error message if any.
    """
    containers = []
    err = None
    try:
        for tag in image_tags:
            image = client.images.get(tag)
            container_name = f"{cluster_name}_{tag}"
            container = client.containers.run(
                image.id,
                name=container_name,
                detach=True
            )
            containers.append(container)
    except docker.errors.APIError as e:
        err = str(e)
    
    return containers, err

def rollback_cluster(cluster_name, previous_state_images):
    """
    Rolls back the cluster to a previous state using saved images.
    :param cluster_name: Name of the cluster.
    :param previous_state_images: List of previous state image tags.
    :return: List of rolled-back containers and error message if any.
    """
    containers = []
    err = None
    try:
        client.containers.prune()  # Optionally remove all existing containers
        for tag in previous_state_images:
            image = client.images.get(tag)
            container_name = f"{cluster_name}_{tag}"
            container = client.containers.run(
                image.id,
                name=container_name,
                detach=True
            )
            containers.append(container)
    except docker.errors.APIError as e:
        err = str(e)
    
    return containers, err

def restart_cluster(cluster_name):
    """
    Restarts all containers in the cluster.
    :param cluster_name: Name of the cluster.
    :return: Success status and error message if any.
    """
    success = False
    err = None
    try:
        containers = client.containers.list(all=True, filters={"name": cluster_name})
        for container in containers:
            container.restart()
        success = True
    except docker.errors.APIError as e:
        err = str(e)
    
    return success, err

def stop_node(container_name):
    try:
        container = client.containers.get(container_name)
        container.stop()
        return {"message": f"Container {container_name} stopped successfully."}, None
    except docker.errors.NotFound as e:
        return None, f"Container {container_name} not found."
    except Exception as e:
        return None, str(e)

def remove_node_from_cluster(container_name):
    """
    Removes a node (container) from the cluster.
    :param container_name: Name of the container to remove.
    :return: Success status and error message if any.
    """
    success = False
    err = None
    try:
        container = client.containers.get(container_name)
        container.remove()
        success = True
    except docker.errors.NotFound as e:
        err = f"Container {container_name} not found"
    except docker.errors.APIError as e:
        err = str(e)
    
    return success, err

def cluster_status_overview(cluster_name):
    """
    Provides a summarized status of the cluster.
    :param cluster_name: Name of the cluster.
    :return: Status dictionary and error message if any.
    """
    status = {"running": 0, "stopped": 0}
    err = None
    try:
        containers = client.containers.list(all=True, filters={"name": cluster_name})
        for container in containers:
            if container.status == "running":
                status["running"] += 1
            else:
                status["stopped"] += 1
    except docker.errors.APIError as e:
        err = str(e)
    
    return status, err

