from flask import Blueprint, jsonify, request
import api.docker_sdk as docker

# Create a blueprint for backend routes
backend = Blueprint('backend', __name__)

# ------------------ Cluster Management Routes ------------------

@backend.route('/deploy_cluster', methods=['POST'])
def deploy_cluster():
    """
    Route to deploy a cluster with the specified image, name, and number of instances.
    """
    data = request.json
    image_name = data.get('image_name')
    cluster_name = data.get('cluster_name')
    num_instances = data.get('num_instances')
    command = data.get('command', None)
    
    containers, err = docker.deploy_cluster(image_name, cluster_name, num_instances, command)
    if err:
        return jsonify({'error': err}), 500
    
    return jsonify({'containers': [c.short_id for c in containers]}), 200

@backend.route('/scale_cluster', methods=['POST'])
def scale_cluster():
    """
    Route to scale a cluster by adjusting the number of instances.
    """
    data = request.json
    cluster_name = data.get('cluster_name')
    new_num_instances = data.get('new_num_instances')
    image_name = data.get('image_name')
    command = data.get('command', None)

    updated_containers, err = docker.scale_cluster(cluster_name, new_num_instances, image_name, command)
    if err:
        return jsonify({'error': err}), 500

    return jsonify({'name': cluster_name, 'updated_containers': [c.short_id for c in updated_containers]}), 200

@backend.route('/delete_cluster', methods=['DELETE'])
def delete_cluster():
    """
    Route to delete a cluster and its containers.
    """
    data = request.json
    cluster_name = data.get('cluster_name')
    
    success, err = docker.delete_cluster(cluster_name)
    if err:
        return jsonify({'error': err}), 500
    
    return jsonify({'status': 'Cluster deleted successfully' if success else 'Error deleting cluster'}), 200

@backend.route('/restart_cluster', methods=['POST'])
def restart_cluster():
    """
    Route to restart all containers in a cluster.
    """
    data = request.json
    cluster_name = data.get('cluster_name')
    
    success, err = docker.restart_cluster(cluster_name)
    if err:
        return jsonify({'error': err}), 500
    
    return jsonify({'status': 'Cluster restarted successfully' if success else 'Error restarting cluster'}), 200

@backend.route('/cluster_status_overview', methods=['GET'])
def cluster_status_overview():
    """
    Route to get an overview of the status of a cluster.
    """
    cluster_name = request.args.get('cluster_name')
    
    status, err = docker.cluster_status_overview(cluster_name)
    if err:
        return jsonify({'error': err}), 500
    
    return jsonify(status), 200

@backend.route('/list_clusters', methods=['GET'])
def list_clusters():
    """
    Route to list all available cluster names.
    """
    cluster_names, err = docker.list_clusters()
    if err:
        return jsonify({'error': err}), 500
    
    return jsonify({'clusters': cluster_names}), 200

# ------------------ Node Management Routes ------------------

@backend.route('/stop_node', methods=['POST'])
def stop_node():
    """
    Route to stop a specific container (node).
    """
    data = request.json
    container_name = data.get('container_name')

    if not container_name:
        return {"error": "container_name is required."}, 400

    result, err = docker.stop_node(container_name)
    if err:
        return {"error": err}, 500
    
    return result, 200

@backend.route('/remove_node_from_cluster', methods=['DELETE'])
def remove_node_from_cluster():
    """
    Route to remove a specific container (node) from the cluster.
    """
    data = request.json
    container_name = data.get('container_name')
    
    success, err = docker.remove_node_from_cluster(container_name)
    if err:
        return jsonify({'error': err}), 500
    
    return jsonify({'status': 'Node removed successfully' if success else 'Error removing node'}), 200

@backend.route('/list_nodes_in_cluster', methods=['GET'])
def list_nodes_in_cluster():
    """
    Route to list all containers (nodes) in a specified cluster.
    """
    cluster_name = request.args.get('cluster_name')
    
    containers, err = docker.list_containers_in_cluster(cluster_name)
    if err:
        return jsonify({'error': err}), 500
    
    return jsonify({'containers': containers}), 200

# ------------------ State Management Routes ------------------

@backend.route('/save_cluster_state', methods=['POST'])
def save_cluster_state():
    """
    Route to save the current state of a cluster by committing each container to a new image.
    """
    data = request.json
    cluster_name = data.get('cluster_name')
    
    saved_images, err = docker.save_cluster_state(cluster_name)
    if err:
        return jsonify({'error': err}), 500
    
    return jsonify({'name': cluster_name, 'saved_images': saved_images}), 200

@backend.route('/restore_cluster_state', methods=['POST'])
def restore_cluster_state():
    """
    Route to restore a cluster's state from saved images.
    """
    data = request.json
    cluster_name = data.get('cluster_name')
    images = data.get('images')
    
    containers, err = docker.restore_cluster_state(cluster_name, images)
    if err:
        return jsonify({'error': err}), 500
    
    return jsonify({'name': cluster_name, 'restored_containers': [c.short_id for c in containers]}), 200

@backend.route('/rollback_cluster', methods=['POST'])
def rollback_cluster():
    """
    Route to roll back a cluster to a previous state using saved images.
    """
    data = request.json
    cluster_name = data.get('cluster_name')
    previous_state_images = data.get('previous_state_images')
    
    containers, err = docker.rollback_cluster(cluster_name, previous_state_images)
    if err:
        return jsonify({'error': err}), 500
    
    return jsonify({'rolled_back_containers': [c.short_id for c in containers]}), 200

