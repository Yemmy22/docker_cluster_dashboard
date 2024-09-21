import docker
from flask import Blueprint, request, jsonify
from engine.db_storage import storage
from models.cluster import Cluster

backend = Blueprint('backend', __name__)
client = docker.from_env()

@backend.route('/deploy_cluster', methods=['POST'])
def deploy_cluster():
    data = request.get_json()
    image_name = data.get('image_name')
    cluster_name = data.get('cluster_name')
    num_instances = data.get('num_instances')

    try:
        containers = []
        for _ in range(num_instances):
            container = client.containers.run(
                image_name,
                detach=True,
                labels={"cluster_name": cluster_name}
            )
            containers.append(container.id)

        # Save to DB
        new_cluster = Cluster(image_name=image_name, cluster_name=cluster_name, num_instances=num_instances)
        new_cluster.set_container_ids(containers)  # Use the set_container_ids method
        new_cluster.save(storage.session)

        return jsonify({"message": f"Deployed {num_instances} containers", "container_ids": containers}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@backend.route('/scale_cluster', methods=['POST'])
def scale_cluster():
    data = request.get_json()
    image_name = data.get('image_name')
    cluster_name = data.get('cluster_name')
    num_instances = data.get('num_instances')

    try:
        containers = client.containers.list(all=True, filters={"label": f"cluster_name={cluster_name}"})
        current_count = len(containers)

        if num_instances > current_count:
            num_to_add = num_instances - current_count
            new_containers = []
            for _ in range(num_to_add):
                container = client.containers.run(
                    image_name,
                    detach=True,
                    labels={"cluster_name": cluster_name}
                )
                new_containers.append(container.id)
            return jsonify({"message": f"Scaled up by {num_to_add} containers", "new_container_ids": new_containers}), 200

        elif num_instances < current_count:
            num_to_remove = current_count - num_instances
            removed_containers = []
            for container in containers[:num_to_remove]:
                container.remove(force=True)
                removed_containers.append(container.id)
            return jsonify({"message": f"Scaled down by {num_to_remove} containers", "removed_container_ids": removed_containers}), 200

        else:
            return jsonify({"message": "No scaling needed"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@backend.route('/cluster_status/<cluster_name>', methods=['GET'])
def get_cluster_status(cluster_name):
    try:
        containers = client.containers.list(all=True, filters={"label": f"cluster_name={cluster_name}"})
        container_info = [{"id": c.id, "status": c.status} for c in containers]
        return jsonify({"cluster_name": cluster_name, "containers": container_info}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

