if [ $# -eq 0 ]
	then
		echo "Use default blender path"
		blender_path="/c/Program\ Files/Blender\\ Foundation/Blender/"
	else
		blender_path=$1
fi
root=$PWD
python_blender="${blender_path}/2.79/python/bin/python"
python="python"

echo "change directory to StoneEdgeGeneration"
cd StoneEdgeGeneration

echo "Python executable: ${python} - ${python_blender}"

eval "${python} -m pip install -r requirements-client.txt"
eval "${python_blender} -m pip install -r requirements-server.txt"

echo "change directory to ${root}"
cd $root
eval "${blender_path}/blender main.blend --python StoneEdgeGeneration/Communication/process_server.py"
 