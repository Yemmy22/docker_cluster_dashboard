Docker Cluster Dashboard

Introduction:
============
Docker Cluster Dashboard is a web-based application designed to simplify the deployment, management, and scaling of Docker clusters. The dashboard provides an intuitive interface to manage multiple containers, scale clusters, restart services, and monitor container status. Built with Flask, jQuery, HTML, and CSS, it serves as a powerful tool for Docker-based server cluster management.

Deployed Site
www.bitflux.tech

Project Blog Article
Read the full journey of building this project in my blog: Project Blog

Author
Your Name
LinkedIn
GitHub
Installation
To run this project locally, follow these steps:

Clone the repository:

bash
Copy code
git clone https://github.com/your-username/docker-cluster-dashboard.git
cd docker-cluster-dashboard
Set up a virtual environment (optional but recommended):

bash
Copy code
python3 -m venv venv
source venv/bin/activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Install Docker: Ensure that Docker is installed and running on your machine. Docker Installation Guide

Run the application:

bash
Copy code
python app/app.py
Access the app: Open your browser and navigate to http://localhost:5000.

Usage
The application allows you to manage Docker containers through a simple and clean user interface. Here are the key features:

Deploy Docker Cluster: Deploy multiple containers with a specified image, cluster name, and number of instances.
Scale Clusters: Adjust the number of instances running in your Docker cluster.
View Cluster Status: Check the status of running and stopped containers within a cluster.
Stop and Remove Containers: Manage individual nodes within the cluster.
Save and Restore Cluster State: Take snapshots of cluster states and restore them as needed.
API Routes
The backend provides the following API routes to interact with the Docker SDK:

POST /api/deploy_cluster: Deploy a new Docker cluster.
POST /api/scale_cluster: Scale an existing cluster.
DELETE /api/delete_cluster: Delete a Docker cluster.
GET /api/cluster_status_overview: Get the status overview of a cluster.
POST /api/restart_cluster: Restart a cluster.
POST /api/stop_node: Stop a specific container.
DELETE /api/remove_node_from_cluster: Remove a container from the cluster.
Frontend Pages
Homepage: A general overview of the app and its features.
Deploy Page: Create a new cluster by specifying an image and the number of instances.
Manage Page: View, scale, or manage running Docker clusters.
About Page: Overview and contact information.
Contributing
We welcome contributions to this project! To get involved:

Fork the repository.
Create a new branch (git checkout -b feature/your-feature-name).
Commit your changes (git commit -am 'Add some feature').
Push to the branch (git push origin feature/your-feature-name).
Open a Pull Request.
Please make sure to update tests as appropriate.

Related Projects
Docker Compose
Portainer
Kubernetes
License
This project is licensed under the MIT License - see the LICENSE file for details.
