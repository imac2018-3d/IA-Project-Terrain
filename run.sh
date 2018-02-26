if [ $# -eq 0 ]
	then
		echo "Use default blender path"
		blender_path="/c/Program\ Files/Blender\\ Foundation/Blender/"
	else
		blender_path=$2
fi
root=$PWD
python_path="${blender_path}/2.79/python/bin"
echo "Python executable: ${python_path}/python"
echo "change directory to StoneEdgeGeneration"
cd StoneEdgeGeneration
eval "${python_path}/python -m pip install virtualenv"

if [ ! -d "virtualenv" ]; then
  eval "${python_path}/python -m virtualenv virtualenv"
fi
echo "change directory to virtualenv"
cd virtualenv
source Scripts/activate
eval "${python_path}/python -m pip install -r requirements.txt"
echo "change directory to ${root}"
cd $root
eval "${blender_path}/blender main.blend"
 