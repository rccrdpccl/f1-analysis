docker-build:
	docker build -t "fastf1:latest" .
docker-run: docker-build
	xhost +local:fastf1
	docker run --rm -it \
	-h fastf1 \
	--env="DISPLAY=$$DISPLAY" \
	--env="QT_X11_NO_MITSHM=1" \
	--volume="$$(pwd):/app" \
	--volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
	fastf1:latest python3 /app/test_analysis.py
docker-run-test: docker-build
	xhost +local:fastf1
	docker run --rm -it \
	-h fastf1 \
	--env="DISPLAY=$$DISPLAY" \
	--volume="$$(pwd):/app" \
	--volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
	--entrypoint=/bin/bash \
	fastf1:latest

