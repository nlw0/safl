all: camera_model.so

camera_model.so: camera_model-setup.py camera_model.pyx
	python2.7 camera_model-setup.py build_ext --inplace --force


