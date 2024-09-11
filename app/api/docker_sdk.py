import docker
import uuid

# Initialize Docker client
client = docker.from_env()

#----------------Cluster Management----------------

def deploy_cluster(image_name, cluster_name, num_instances, command=None):
    """
    Deploy a cluster of containers with the specified image and cluster name.
    Creates multiple containers with a given image and attaches them to a cluster.
    """
    try:
        containers = []
        for _ in range(num_instances):
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

def scale_cluster(cluster_name, new_num_instances, image_name, command=None):
    """
    Scales a Docker cluster by adjusting the number of instances of a given container.
    Creates or removes containers to match the desired number of instances in the cluster.
    """
    try:
        containers = client.containers.list(all=True, filters={"label": f"cluster_name={cluster_name}"})
        current_count = len(containers)
        
        if new_num_instances > current_count:
            num_to_add = new_num_instances - current_count
            created_containers = []
            
            for i in range(num_to_add):
                new_container_name = f"{cluster_name}_{current_count + i + 1}"
                container = client.containers.run(
                    image_name,
                    name=new_container_name,
                    command=command,
                    detach=True
                )
                created_containers.append(container)
            updated_containers = containers + created_containers
        else:
            updated_containers = containers
        
        return updated_containers, None
    except Exception as e:
        return None, str(e)

def delete_cluster(cluster_name):
    """
    Deletes all containers in the specified cluster.
    Removes all containers associated with the cluster name.
    """
    try:
        containers = client.containers.list(all=True, filters={"label": f"cluster_name={cluster_name}"})
        for container in containers:
            container.remove(force=True)
        return True, None
    except docker.errors.APIError as e:
        return False, str(e)

def restart_cluster(cluster_name):
    """
    Restarts all containers in the specified cluster.
    Restarts each container associated with the cluster name.
    """
    try:
        containers = client.containers.list(all=True, filters={"label": f"cluster_name={cluster_name}"})
        for container in containers:
            container.restart()
        return True, None
    except docker.errors.APIError as e:
        return False, str(e)

#----------------Cluster State Management----------------

def save_cluster_state(cluster_name):
    """
    Saves the current state of the cluster by committing each container to a new image.
    Creates snapshot images from the current state of each container in the cluster.
    """
    try:
        containers = client.containers.list(all=True, filters={"label": f"cluster_name={cluster_name}"})
        saved_images = []
        for container in containers:
            image_tag = f"{cluster_name}_snapshot_{container.short_id}"
            container.commit(repository=image_tag)
            saved_images.append(image_tag)
        return saved_images, None
    except docker.errors.APIError as e:
        return None, str(e)

def restore_cluster_state(cluster_name, image_tags):
    """
    Restores a cluster's state by creating containers from saved images.
    Recreates containers from the provided list of image tags.
    """
    try:
        containers = []
        for tag in image_tags:
            image = client.images.get(tag)
            container_name = f"{cluster_name}_{tag}"
            container = client.containers.run(
                image.id,
                name=container_name,
                detach=True
            )
            containers.append(container)
        return containers, None
    except docker.errors.APIError as e:
        return None, str(e)

def rollback_cluster(cluster_name, previous_state_images):
    """
    Rolls back the cluster to a previous state using saved images.
    Restores containers from a list of previously saved image tags.
    """
    try:
        client.containers.prune()
        containers = []
        for tag in previous_state_images:
            image = client.images.get(tag)
            container_name = f"{cluster_name}_{tag}"
            container = client.containers.run(
                image.id,
                name=container_name,
                detach=True
            )
            containers.append(container)
        return containers, None
    except docker.errors.APIError as e:
        return None, str(e)

#----------------Container Management category ----------------

def list_containers_in_cluster(cluster_name):
    """
    Lists all containers that belong to a specified cluster.
    Retrieves details of containers associated with the given cluster name.
    """
    try:
        all_containers = client.containers.list(all=True)
        cluster_containers = [container for container in all_containers if container.labels.get('cluster_name') == cluster_name]
        
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

def stop_node(container_name):
    """
    Stops a running container by its name.
    Attempts to stop the container with the given name.
    """
    try:
        container = client.containers.get(container_name)
        container.stop()
        return {"message": f"Container {container_name} stopped successfully."}, None
    except docker.errors.NotFound:
        return None, f"Container {container_name} not found."
    except Exception as e:
        return None, str(e)

def remove_node_from_cluster(container_name):
    """
    Removes a node (container) from the cluster.
    Deletes the specified container from Docker.
    """
    try:
        container = client.containers.get(container_name)
        container.remove(force=True)
        return True, None
    except docker.errors.NotFound:
        return False, f"Container {container_name} not found."
    except docker.errors.APIError as e:
        return False, str(e)

def cluster_status_overview(cluster_name):
    """
    Provides a summarized status of the cluster.
    Returns the count of running and stopped containers within the specified cluster.
    """
    try:
        status = {"running": 0, "stopped": 0}
        containers = client.containers.list(all=True, filters={"label": f"cluster_name={cluster_name}"})
        for container in containers:
            if container.status == "running":
                status["running"] += 1
            else:
                status["stopped"] += 1
        return status, None
    except docker.errors.APIError as e:
        return None, str(e)
