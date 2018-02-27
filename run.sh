if [ $# -eq 0 ]
	then
		echo "Use default blender path"
		blender_path="/c/Program\ Files/Blender\\ Foundation/Blender/"
		pip="pip"
		virtualenv="virtualenv"
	else
		blender_path=$1
fi
root=$PWD
python_path="${blender_path}/2.79/python/bin"
if [ $# -eq 1 ]
	then
		pip="pip"
		virtualenv="virtualenv"
	elif [ $2 == "true" ]
	then
		pip="${python_path}/python -m pip"
		virtualenv="${python_path}/python -m virtualenv"
	else
		pip="pip"
		virtualenv="virtualenv"
fi

echo "Python executable: ${python_path}/python"
echo "change directory to StoneEdgeGeneration"
cd StoneEdgeGeneration
eval "${pip} install virtualenv"

if [ ! -d "virtualenv/Lib" ]; then
  eval "${virtualenv} virtualenv"
fi
echo "change directory to virtualenv"
cd virtualenv
source Scripts/activate
eval "${pip} install -r requirements.txt"
echo "change directory to ${root}"
cd $root
eval "${blender_path}/blender main.blend"
 