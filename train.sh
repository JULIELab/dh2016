WORKER=8
EPOCHS=10
HS=0
NEG=5
SAMPLE="1e-3"

if [ $# -ne 2 ]; 
    then echo "Provide corpus and results paths"
    exit 1
fi
_CORPUS=$1
_TARGET=$2/models

function train {
	size=$1
	min=$2

	corpus=$_CORPUS/${size}M
	name="${size}M_${min}min"
	target=$_TARGET/$name

	what=$(
		what=""
		cd $corpus
		for x in *_*
		do
			what="$what $x"
		done
		echo $what
	)

	mkdir -p $target logs
	python python/trainFixedParams.py $target $corpus $WORKER $EPOCHS $min $HS $NEG $SAMPLE $what &> logs/$name
	echo $name >> completed
}

rm completed

train 1 5 &