import docker
import os
import time


def generate_base_image(file_path: str):
    # Ensure that Docker is set up from the environment
    client = docker.from_env()
    print("file_path", file_path)
    if not os.path.exists(
        os.path.join(file_path, "requirements.txt")
    ) and os.path.exists(os.path.join(file_path, "pyproject.toml")):
        print(file_path)
        # generate the requirements.txt from the pyproject.toml
        print("Generating requirements.txt from pyproject.toml")
        os.system(
            f"poetry export --without-hashes --format=requirements.txt > {file_path}/requirements.txt --directory {file_path}"
        )

    if os.path.exists(os.path.join(file_path, "requirements.txt")):
        # Use requirements.txt
        dockerfile_content = f"""
        FROM python:3.9-slim
        COPY {os.path.join(file_path.split("/")[-2], file_path.split("/")[-1], "requirements.txt")} /app/requirements.txt
        RUN pip install --no-cache-dir -r /app/requirements.txt
        WORKDIR /app
        """

    docker_base_image_path = os.path.dirname(os.path.dirname(file_path))
    dockerfile_path = os.path.join(docker_base_image_path, "Dockerfile")
    with open(dockerfile_path, "w") as f:
        f.write(dockerfile_content)

    print("Building base Docker image...")

    try:
        image, build_logs = client.images.build(
            path=docker_base_image_path, rm=True, tag="base_image"
        )
        for log in build_logs:
            if "stream" in log:
                print(log["stream"].strip())

        print("Base image built successfully.")
        return image.id

    except Exception as e:
        raise Exception(e)


def run_code_in_container(image_id: str, code: str):
    client = docker.from_env()

    # Define paths for mounting
    temp_code_dir = "./temp_code_dir"
    os.makedirs(temp_code_dir, exist_ok=True)

    # Write generated code to a temporary main.py
    temp_code_path = os.path.join(temp_code_dir, "main.py")
    with open(temp_code_path, "w") as f:
        f.write(code)

    print(f"Code written to {temp_code_path}")

    # Start the timer
    start_time = time.time()

    try:
        # Run the container, mounting the temporary code directory
        container = client.containers.run(
            image=image_id,
            command="python main.py",  # Run the main.py script inside the container
            volumes={
                os.path.abspath(temp_code_dir): {"bind": "/app", "mode": "rw"}
            },  # Mount the temp code directory
            working_dir="/app",
            detach=True,  # Run the container in detached mode
        )

        # Stream logs to get output from the script
        logs = container.logs(stream=True)
        print("Output:")
        for log in logs:
            print(log.strip())

        # Collect CPU and memory usage stats
        stats = container.stats(stream=False)

        # Check if CPU and memory usage stats are available
        print(stats)
        cpu_usage = (
            stats.get("cpu_stats", {}).get("cpu_usage", {}).get("total_usage", "N/A")
        )
        memory_usage = stats.get("memory_stats", {}).get("usage", "N/A")

        # Stop the timer
        end_time = time.time()

        execution_time = end_time - start_time

        # Stop and remove the container
        container.stop()
        container.remove()

        return {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "execution_time": execution_time,
        }
    except Exception as e:
        raise Exception(f"Error running the container: {e}")
